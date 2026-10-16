"""E009: Neural decipherer v1 (Qwen2.5-0.5B + LoRA, MLX) on the frozen known-answer benchmark.

Two variants, each run as its own process (one heavy job at a time):
  --variant sft   adapters from vcl.neural.train_sft
  --variant grpo  adapters from vcl.neural.train_grpo (SFT + GRPO)
then `--combine` merges them into experiments/results/e009.json with gates and the comparison to solver v1 (E003)
and solver v2 (E005), and appends ledger rows.

Per variant:
  1. Dev / calibration set: N_DEV tasks generated here from 'tune'-role books of TRAIN language families with TRAIN
     encodings (+10% one_time_pad noise). Same seed for both variants. Used to choose the aggregation per predicted
     family, fit the confidence calibrator / operating threshold, and set the self-null margin. Nothing from any
     test split, secret file, held-out family or decoy generator is used.
  2. Test: every task of test_in, test_lang, test_enc, test_both, test_null (no subsetting), scored ONLY through
     vcl.eval.score.evaluate.

Run:
  caffeinate -ims .venv/bin/python experiments/e009_neural_decipherer.py --variant sft
  caffeinate -ims .venv/bin/python experiments/e009_neural_decipherer.py --variant grpo
  .venv/bin/python experiments/e009_neural_decipherer.py --combine
"""
from __future__ import annotations

import argparse
import json
import random
import resource
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vcl.eval import gates  # noqa: E402
from vcl.eval.ledger import append  # noqa: E402
from vcl.eval.score import evaluate  # noqa: E402
from vcl.neural import data  # noqa: E402
from vcl.neural.predict import (Calibrator, decode_tasks, feature_row, final_text, fit_calibrator,  # noqa: E402
                                predict_tasks, predicted_family, self_null_tasks, to_prediction)
from vcl.neural.reward import char_acc  # noqa: E402  (own scoring copy, self-generated answers only)
from vcl.synthetic.encoders import comparable  # noqa: E402
from vcl.synthetic.schema import PublicTask, load_jsonl  # noqa: E402

BENCH = ROOT / "data/derived/benchmark_v1"
RES = ROOT / "experiments/results"
SPLITS = ["test_in", "test_lang", "test_enc", "test_both", "test_null"]
TRAIN_ENC = ["mono", "homophonic", "vigenere", "columnar", "nulls"]
ADAPTERS = {"sft": ROOT / "checkpoints/neural_sft_v1.safetensors",
            "grpo": ROOT / "checkpoints/neural_grpo_v1.safetensors"}
DEV_SEED = 90090
MODEL_NAME = {"sft": "neural_v1_sft", "grpo": "neural_v1_sft_grpo"}


def dev_tasks(n: int):
    rng = random.Random(DEV_SEED)
    out = []
    for i in range(n):
        fam = "noise" if i % 10 == 9 else TRAIN_ENC[(i - i // 10) % len(TRAIN_ENC)]
        t = data.gen_task(rng, "tune", family=fam, lengths=(150, 300, 1000, 3000))
        out.append((PublicTask(f"dev-{i:04d}", t["symbols"], "dev"), t))
    return out


def peak_rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9   # bytes on macOS


def run_variant(variant: str, n_dev: int, batch: int):
    import mlx.core as mx
    from vcl.neural import model as M
    t0 = time.time()
    path = ADAPTERS[variant]
    sha = M.sha256_file(path)
    mx.set_cache_limit(1 << 30)
    model, _ = M.build(adapters=path)
    meta = json.loads(path.with_suffix(".json").read_text())
    rep = {"variant": variant, "adapters": str(path.relative_to(ROOT)), "adapter_sha256": sha,
           "adapter_bytes": path.stat().st_size, "base_model": M.BASE_MODEL, "adapter_meta": {
               k: v for k, v in meta.items() if k != "vocab"}, "command": " ".join(sys.argv)}

    # ------------------------------------------------ 1. dev calibration (tune-role books only)
    td0 = time.time()
    dev = dev_tasks(n_dev)
    decs = decode_tasks(model, [p for p, _ in dev], batch=batch)
    rows = []
    for (p, t), d in zip(dev, decs):
        fam = t["family"]
        gold = comparable(fam, t["recov"]) if t["recov"] is not None else None
        accs = {agg: (char_acc(comparable(fam, d.texts.get(agg)), gold) if gold is not None else 0.0)
                for agg in ("concat", "vote")}
        rows.append({"family": fam, "pred_family": predicted_family(d), "length": t["length"], "accs": accs,
                     "is_noise": fam == "noise", "n_letters": d.n_letters})
    agg_by_family = {}
    for f in TRAIN_ENC:
        r = [x for x in rows if x["pred_family"] == f and not x["is_noise"]]
        if r:
            c, v = np.mean([x["accs"]["concat"] for x in r]), np.mean([x["accs"]["vote"] for x in r])
            agg_by_family[f] = "vote" if v > c else "concat"
    usable = [i for i, d in enumerate(decs) if d.feats]
    X = np.array([feature_row(decs[i]) for i in usable])
    y = np.array([0 if rows[i]["is_noise"] else int(rows[i]["accs"][agg_by_family.get(rows[i]["pred_family"],
                                                                                         "concat")] >= 0.9)
                  for i in usable])
    lr, thr, oof = fit_calibrator(X, y)
    cal = Calibrator(lr, thr, margin=0.0, agg_by_family=agg_by_family)
    # self-null margin: 5th percentile of (conf_real - conf_null) over CORRECT answered dev tasks (as solver v2)
    answered = [i for i in usable if lr is not None and cal.confidence(decs[i]) >= thr]
    gaps_ok, gaps_bad = [], []
    if answered:
        nd = decode_tasks(model, self_null_tasks([dev[i][0] for i in answered], seed=1), batch=batch)
        for i, d in zip(answered, nd):
            gap = cal.confidence(decs[i]) - cal.confidence(d)
            (gaps_ok if y[usable.index(i)] else gaps_bad).append(gap)
    cal.margin = float(np.percentile(gaps_ok, 5)) if gaps_ok else 0.0
    by_fam = {}
    for f in TRAIN_ENC + ["noise"]:
        r = [x for x in rows if x["family"] == f]
        by_fam[f] = {"n": len(r), "concat_char_acc": float(np.mean([x["accs"]["concat"] for x in r])),
                     "vote_char_acc": float(np.mean([x["accs"]["vote"] for x in r])),
                     "family_id_acc": float(np.mean([x["pred_family"] == f for x in r]))}
    rep["dev"] = {"n": len(dev), "seed": DEV_SEED, "role": "tune", "agg_by_family": agg_by_family,
                  "threshold": thr, "margin": cal.margin, "solved_rate": float(y.mean()),
                  "oof_answered_rate": float((oof >= thr).mean()) if oof is not None else None,
                  "oof_selective_solved": float(y[oof >= thr].mean()) if oof is not None and (oof >= thr).any()
                  else None, "selfnull_gaps_correct": sorted(map(float, gaps_ok)),
                  "selfnull_gaps_wrong": sorted(map(float, gaps_bad)), "by_family": by_fam,
                  "seconds": round(time.time() - td0, 1)}
    print(json.dumps(rep["dev"], indent=1), flush=True)

    # ------------------------------------------------ 2. frozen test splits
    summaries, all_rows, forced = {}, [], {}
    for split in SPLITS:
        ts = time.time()
        tasks = load_jsonl(BENCH / "public" / f"{split}.jsonl", PublicTask)
        preds, decs_t = predict_tasks(model, tasks, cal, batch=batch, self_null=True)
        srows, summ = evaluate(BENCH, split, preds)
        summ["seconds"] = round(time.time() - ts, 1)
        summaries[split] = summ
        # DIAGNOSTIC ONLY (not the operating point): same decodes, never abstain unless < MIN_LETTERS / noise
        # family. Measures what the network actually outputs; scored through vcl.eval.score.evaluate as well.
        forced_cal = Calibrator(None, -1.0, 0.0, agg_by_family)
        fpreds = [to_prediction(t, d, forced_cal) for t, d in zip(tasks, decs_t)]
        for fp_ in fpreds:
            if fp_.plaintext is None and not fp_.abstain:
                fp_.abstain = True
        _, fsumm = evaluate(BENCH, split, fpreds)
        forced[split] = fsumm
        pm = {p.task_id: p for p in preds}
        for r in srows:
            all_rows.append(r | {"split": split, "variant": variant, "pred_family": pm[r["task_id"]].family})
        print(split, {k: summ.get(k) for k in ["n", "mean_char_acc", "solved_rate", "abstention_rate",
                                                "null_false_discovery_rate", "seconds"]}, flush=True)
    rep["summaries"] = summaries
    rep["forced_answer_diagnostic"] = forced
    rep["wall_seconds"] = round(time.time() - t0, 1)
    rep["peak_mlx_gb"] = round(mx.get_peak_memory() / 1e9, 2)
    rep["peak_rss_gb"] = round(peak_rss_gb(), 2)
    rep["calibrator"] = {"features": list(__import__("vcl.neural.predict", fromlist=["x"]).CONF_FEATURES),
                         "coef": (lr[-1].coef_[0].round(3).tolist() if lr is not None else None)}
    (RES / f"e009_{variant}.json").write_text(json.dumps(rep, indent=1))
    with open(RES / f"e009_{variant}_rows.jsonl", "w") as f:
        for r in all_rows:
            f.write(json.dumps(r) + "\n")
    print("done", variant, rep["wall_seconds"], "s", flush=True)


def freq_rank_baseline():
    """No-learning reference: glyph of frequency rank k -> k-th most frequent letter of the pooled TRAIN-family
    tune/ref text; boundary -> space; always answers. Tells us what char accuracy pure frequency analysis gets."""
    from collections import Counter
    from vcl.synthetic.schema import BOUNDARY, Prediction
    cc = data.train_char_counts()
    letters = [c for c, _ in cc.most_common() if c != " "]
    out = {}
    for split in SPLITS:
        tasks = load_jsonl(BENCH / "public" / f"{split}.jsonl", PublicTask)
        preds = []
        for t in tasks:
            cnt = Counter(x for x in t.symbols if x != BOUNDARY)
            order = {g: letters[min(i, len(letters) - 1)] for i, (g, _) in enumerate(cnt.most_common())}
            txt = "".join(" " if x == BOUNDARY else order[x] for x in t.symbols)
            preds.append(Prediction(t.task_id, 0.5, plaintext=txt, abstain=False, confidence=0.0))
        _, summ = evaluate(BENCH, split, preds)
        out[split] = summ
    (RES / "e009_freq_baseline.json").write_text(json.dumps(out, indent=1))
    return out


def variant_gates(s: dict) -> dict:
    g = {"gate0": gates.gate0_reproducibility(),
         "gate1": gates.gate1_positive_control(s["test_in"], TRAIN_ENC),
         "gate2": {ax: gates.gate2_ood_transfer(s["test_in"], s[ax], ax) for ax in ["test_lang", "test_enc",
                                                                                   "test_both"]},
         "gate3": gates.gate3_nonsense(s["test_null"])}
    return g


KEYS = ["mean_char_acc", "solved_rate", "abstention_rate", "selective_solved_rate", "family_id_acc", "ece"]


def combine():
    e003 = json.loads((RES / "e003.json").read_text())
    e005 = json.loads((RES / "e005.json").read_text())
    out = {"experiment": "e009_neural_decipherer", "protocol": "eval/PROTOCOL_v1.md", "variants": {},
           "baselines": {}, "comparison": {}}
    for v in ["sft", "grpo"]:
        p = RES / f"e009_{v}.json"
        if not p.exists():
            continue
        rep = json.loads(p.read_text())
        rep["gates"] = variant_gates(rep["summaries"])
        if rep.get("forced_answer_diagnostic"):
            f = rep["forced_answer_diagnostic"]
            rep["gate2_forced_answer_diagnostic"] = {ax: gates.gate2_ood_transfer(f["test_in"], f[ax], ax)
                                                     for ax in ["test_lang", "test_enc", "test_both"]}
        out["variants"][v] = rep
    for sp in SPLITS:
        out["baselines"].setdefault("solver_v1_e003_R1", {})[sp] = {
            k: e003["summaries"][f"R1/{sp}"].get(k) for k in KEYS + ["null_false_discovery_rate"]}
        if f"R2/{sp}" in e003["summaries"]:
            out["baselines"].setdefault("solver_v1_e003_R2_trainlang_lms_only", {})[sp] = {
                k: e003["summaries"][f"R2/{sp}"].get(k) for k in KEYS}
        if sp in e005["splits"]:
            out["baselines"].setdefault("solver_v2_e005", {})[sp] = {
                k: e005["splits"][sp].get(k) for k in KEYS + ["null_false_discovery_rate"]}
    fb = json.loads((RES / "e009_freq_baseline.json").read_text()) if (RES / "e009_freq_baseline.json").exists() \
        else freq_rank_baseline()
    out["baselines"]["freq_rank_no_learning_always_answers"] = {
        sp: {k: fb[sp].get(k) for k in ["mean_char_acc", "solved_rate", "null_false_discovery_rate"]} for sp in SPLITS}
    table = {}
    for sp in SPLITS:
        key = "null_false_discovery_rate" if sp == "test_null" else "mean_char_acc"
        row = {"metric": key}
        for name, b in out["baselines"].items():
            row[name] = b.get(sp, {}).get(key)
        for v, rep in out["variants"].items():
            row[MODEL_NAME[v]] = rep["summaries"][sp].get(key)
            if sp != "test_null":
                row[MODEL_NAME[v] + "_solved"] = rep["summaries"][sp].get("solved_rate")
                row[MODEL_NAME[v] + "_forced_char_acc_DIAG"] = rep.get("forced_answer_diagnostic", {}).get(
                    sp, {}).get("mean_char_acc")
        table[sp] = row
    out["comparison"] = table
    out["note"] = ("Neural models are trained on TRAIN language families only and cannot emit Greek/Hebrew/Telugu "
                   "letters; the like-for-like solver baseline on test_lang/test_both is solver v1 R2 (train-family "
                   "LMs only). R1 used LMs from ref books of every benchmark language.")
    (RES / "e009.json").write_text(json.dumps(out, indent=1))
    ledger = []
    for v, rep in out["variants"].items():
        for sp, s in rep["summaries"].items():
            for metric in (["null_false_discovery_rate"] if sp == "test_null" else
                           ["mean_char_acc", "solved_rate", "abstention_rate"]):
                ledger.append({"experiment": "E009", "model": MODEL_NAME[v], "checkpoint_sha256": rep["adapter_sha256"],
                               "split": sp, "metric": metric, "value": s.get(metric),
                               "command": f"experiments/e009_neural_decipherer.py --variant {v}",
                               "notes": f"Qwen2.5-0.5B LoRA adapters {rep['adapters']}; calibrated on tune-role "
                                        "self-generated tasks only; noise=one_time_pad-style abstention training"})
    append(ledger)
    print(json.dumps(table, indent=1))
    for v, rep in out["variants"].items():
        g = rep["gates"]
        print(v, "gate1", g["gate1"]["status"], {ax: x["status"] for ax, x in g["gate2"].items()},
              "gate3", g["gate3"]["status"], g["gate3"]["fdr"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["sft", "grpo"])
    ap.add_argument("--combine", action="store_true")
    ap.add_argument("--freq-baseline", action="store_true")
    ap.add_argument("--n-dev", type=int, default=250)
    ap.add_argument("--batch", type=int, default=48)
    a = ap.parse_args()
    if a.freq_baseline:
        print(json.dumps({k: v.get("mean_char_acc") for k, v in freq_rank_baseline().items()}))
    elif a.combine:
        combine()
    else:
        run_variant(a.variant, a.n_dev, a.batch)


if __name__ == "__main__":
    main()
