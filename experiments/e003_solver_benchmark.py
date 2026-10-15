"""E003: frozen classical solver (src/vcl/solvers, version solver-v1) on the known-answer benchmark v1.

Regimes
  R1 full library (every language with ref books) on test_in, test_lang, test_enc, test_both, test_null.
  R2 TRAIN-family-only library (all held-out language families absent) on test_lang, test_both.

The solver sees only PublicTask rows (public/*.jsonl); scoring is done afterwards by vcl.eval.score.evaluate,
which is the only code that reads secret/*.jsonl. Gates come from vcl.eval.gates.

Outputs: experiments/results/e003.json, experiments/results/e003_rows.jsonl, rows appended to experiments/LEDGER.csv.
Run:     .venv/bin/python experiments/e003_solver_benchmark.py [--workers 10] [--limit N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vcl.synthetic.schema import PublicTask, Prediction, load_jsonl  # noqa: E402

BENCH = ROOT / "data/derived/benchmark_v1"
OUT = ROOT / "experiments/results"
TRAIN_ENC = ["mono", "homophonic", "vigenere", "columnar", "nulls"]
RUNS = [("R1", s) for s in ["test_in", "test_lang", "test_enc", "test_both", "test_null"]] + \
       [("R2", s) for s in ["test_lang", "test_both"]]


def solver_sha256() -> str:
    """Checkpoint hash of the frozen solver: source files + trained artifacts (classifier, calibrator)."""
    h = hashlib.sha256()
    files = sorted((ROOT / "src/vcl/solvers").glob("*.py")) + \
        [ROOT / "data/derived/solver_v1/family_classifier.pkl", ROOT / "data/derived/solver_v1/calibrator.pkl"]
    for f in files:
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def _work(args):
    regime, task = args
    from vcl.solvers.api import solve
    from vcl.solvers.lm import Library
    lib = Library.full() if regime == "R1" else Library.train_families_only()
    t0 = time.time()
    try:
        p = solve(task, lib)
    except Exception as ex:  # noqa: BLE001 - a crash is an abstention, recorded
        p = Prediction(task.task_id, 0.5, family="unknown", abstain=True, log=[f"ERROR {type(ex).__name__}: {ex}"])
    return regime, task.split, p, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0, help="debug only: first N tasks per split")
    a = ap.parse_args()
    command = ".venv/bin/python experiments/e003_solver_benchmark.py " + " ".join(sys.argv[1:])
    sha = solver_sha256()
    jobs = []
    for regime, split in RUNS:
        tasks = load_jsonl(BENCH / "public" / f"{split}.jsonl", PublicTask)
        if a.limit:
            tasks = tasks[: a.limit]
        jobs += [(regime, t) for t in tasks]
    # longest first for load balance
    jobs.sort(key=lambda j: -len(j[1].symbols))
    t0 = time.time()
    preds: dict[tuple[str, str], list] = {}
    secs: dict[str, float] = {}
    with Pool(a.workers) as pool:
        for i, (regime, split, p, dt) in enumerate(pool.imap_unordered(_work, jobs, chunksize=1)):
            preds.setdefault((regime, split), []).append(p)
            secs[p.task_id + regime] = dt
            if (i + 1) % 50 == 0:
                print(f"{i + 1}/{len(jobs)} done, {time.time() - t0:.0f}s", flush=True)
    wall = time.time() - t0

    from vcl.eval.score import evaluate
    from vcl.eval import gates
    from vcl.eval.ledger import append
    summaries, all_rows = {}, []
    for (regime, split), ps in sorted(preds.items()):
        rows, summ = evaluate(BENCH, split, ps)
        if a.limit:
            ids = {p.task_id for p in ps}
            rows = [r for r in rows if r["task_id"] in ids]
            from vcl.eval.score import summarise
            summ = summarise(rows)
        pm = {p.task_id: p for p in ps}
        for r in rows:
            p = pm[r["task_id"]]
            chosen = next((x for x in p.log if isinstance(x, dict) and "chosen" in x), {})
            r.update({"regime": regime, "split": split, "pred_family": p.family, "pred_language": p.language,
                      "solver_family": chosen.get("chosen", {}).get("family"),
                      "seconds": round(secs.get(r["task_id"] + regime, 0.0), 2),
                      "error": next((x for x in p.log if isinstance(x, str) and x.startswith("ERROR")), None)})
        summ["mean_seconds"] = sum(r["seconds"] for r in rows) / max(1, len(rows))
        summaries[f"{regime}/{split}"] = summ
        all_rows += rows
    s_in = summaries.get("R1/test_in", {})
    gate_out = {
        "gate0": gates.gate0_reproducibility(),
        "gate1": gates.gate1_positive_control(s_in, TRAIN_ENC),
        "gate2": {k: gates.gate2_ood_transfer(s_in, summaries[k], axis=k)
                  for k in ["R1/test_lang", "R1/test_enc", "R1/test_both", "R2/test_lang", "R2/test_both"]
                  if k in summaries},
        "gate3": gates.gate3_nonsense(summaries.get("R1/test_null", {})),
    }
    report = {"experiment": "e003_solver_benchmark", "solver_version": "solver-v1", "checkpoint_sha256": sha,
              "command": command, "wall_seconds": round(wall, 1), "workers": a.workers, "limit": a.limit,
              "summaries": summaries, "gates": gate_out}
    OUT.mkdir(parents=True, exist_ok=True)
    suffix = "" if not a.limit else "_debug"
    (OUT / f"e003{suffix}.json").write_text(json.dumps(report, indent=1, default=str))
    with open(OUT / f"e003{suffix}_rows.jsonl", "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, default=str) + "\n")
    if not a.limit:
        led = []
        for key, s in summaries.items():
            for m in ["mean_char_acc", "solved_rate", "family_id_acc", "language_id_acc", "abstention_rate",
                      "selective_solved_rate", "ece", "null_false_discovery_rate"]:
                if s.get(m) is not None:
                    led.append({"experiment": "e003", "model": "solver-v1", "checkpoint_sha256": sha, "split": key,
                                "metric": m, "value": round(float(s[m]), 4), "command": command,
                                "notes": "classical SA/n-gram solver; R1 full library, R2 train-family library"})
        g1 = gate_out["gate1"]
        led.append({"experiment": "e003", "model": "solver-v1", "checkpoint_sha256": sha, "split": "R1/test_in",
                    "metric": "gate1_status", "value": g1["status"], "command": command,
                    "notes": "void families: " + ",".join(g1["void_families_for_voynich"])})
        for k, g in gate_out["gate2"].items():
            led.append({"experiment": "e003", "model": "solver-v1", "checkpoint_sha256": sha, "split": k,
                        "metric": "gate2_status", "value": g["status"], "command": command,
                        "notes": f"ratio={g['ratio']} solved={g['ood_solved']}"})
        led.append({"experiment": "e003", "model": "solver-v1", "checkpoint_sha256": sha, "split": "R1/test_null",
                    "metric": "gate3_status", "value": gate_out["gate3"]["status"], "command": command,
                    "notes": f"fdr={gate_out['gate3']['fdr']}"})
        append(led)
    keys = ["n", "mean_char_acc", "solved_rate", "family_id_acc", "language_id_acc", "abstention_rate",
            "selective_solved_rate", "ece", "null_false_discovery_rate", "mean_seconds"]
    print(f"wall {wall:.0f}s  sha {sha[:12]}")
    for k, s in summaries.items():
        print(k, {m: (round(s[m], 3) if isinstance(s.get(m), float) else s.get(m)) for m in keys})
    print(json.dumps({k: (v["status"] if "status" in v else {kk: vv["status"] for kk, vv in v.items()})
                      for k, v in gate_out.items()}, indent=1))


if __name__ == "__main__":
    main()
