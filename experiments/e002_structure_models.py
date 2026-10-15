"""E002: Voynich-native structure models (System A, Gate 4; structural only, no semantics).

Stages (run in this order; the two transformer CV stages may run in parallel):
  .venv/bin/python experiments/e002_structure_models.py --stage cv-ngram
  .venv/bin/python experiments/e002_structure_models.py --stage cv-tf --size small  --device cpu
  .venv/bin/python experiments/e002_structure_models.py --stage cv-tf --size medium --device mps
  .venv/bin/python experiments/e002_structure_models.py --stage final

cv-*  : 5-fold leaf-grouped DEV cross-validation (LOCKED_TEST never loaded).
final : merge CV -> experiments/results/e002.json; freeze the best model of each class
        (unigram / Kneser-Ney / Transformer, chosen by pooled DEV-CV bits/glyph) retrained on
        all DEV leaves; posterior predictive checks vs DEV; then ONE call to
        `score_locked_test_once` which scores every frozen model on LOCKED_TEST, appends the
        rows to experiments/LEDGER.csv, and compares the same samples with LOCKED_TEST statistics.
        Writes experiments/results/e002_ppc.json. Refuses to run twice (a re-score would be a
        new model under the protocol).
"""
from __future__ import annotations

import argparse
import os
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import DOCX_SHA256  # noqa: E402
from vcl.eval import ledger  # noqa: E402
from vcl.models import content_free as cf  # noqa: E402
from vcl.models.ngram import KneserNey, Unigram, VarietyMixKN  # noqa: E402
from vcl.models.stream import (_tokens, dev_fold_split, dev_lines, inner_split, locked_set,  # noqa: E402
                               locked_test_lines, stream_stats)
from vcl.models.transformer import TConfig, TransformerLM, describe  # noqa: E402

RES = ROOT / "experiments/results"
CK = ROOT / "checkpoints"
K = 5
SIZES = {"small": dict(d_model=96, n_layers=3, d_ff=384, lr=3e-3),
         "medium": dict(d_model=160, n_layers=4, d_ff=640, lr=2e-3)}
TF_COMMON = dict(max_epochs=40, patience=4, batch_size=64, dropout=0.2, seed=0)
CMD = ".venv/bin/python " + " ".join(sys.argv)


def _r(d):
    return {k: (round(v, 5) if isinstance(v, float) else v) for k, v in d.items()}


def pooled(folds):
    bits = sum(f["bits"] for f in folds)
    ev = sum(f["events"] for f in folds)
    w = sum(f["words"] for f in folds)
    bpg = [f["bits_per_glyph"] for f in folds]
    return {"bits_per_glyph": bits / ev, "bits_per_word": bits / w, "events": ev, "words": w,
            "fold_mean_bpg": float(np.mean(bpg)), "fold_sd_bpg": float(np.std(bpg, ddof=1))}


# ----------------------------------------------------------------------------- CV stages
def cv_ngram():
    out = {}
    for fold in range(K):
        tr, te = dev_fold_split(fold)
        a, b = inner_split(tr)
        models = [("unigram", Unigram().fit(tr))]
        for n in range(2, 7):
            models.append((f"kn{n}", KneserNey(n).fit(tr)))
            models.append((f"kn{n}+variety", VarietyMixKN(n).fit(tr, val_lines=b)))
        for name, m in models:
            r = m.score(te)
            if hasattr(m, "lam"):
                r["lambda"] = m.lam
            out.setdefault(name, []).append(_r(r))
        # ablation: uncertain spaces (',') NOT treated as word boundaries -> different event stream
        trm, tem = dev_fold_split(fold, merge_uncertain=True)
        out.setdefault("kn4[merge_uncertain_spaces]", []).append(_r(KneserNey(4).fit(trm).score(tem)))
        print(f"fold {fold}: " + ", ".join(f"{k} {v[-1]['bits_per_glyph']:.4f}" for k, v in out.items()), flush=True)
    (RES / "e002_cv_ngram.json").write_text(json.dumps(out, indent=1))


def cv_tf(size: str, device: str):
    if device == "cpu":
        torch.set_num_threads(4)
    out = {}
    for cond in (False, True):
        for fold in range(K):
            tr, te = dev_fold_split(fold)
            a, b = inner_split(tr)
            m = TransformerLM(TConfig(**SIZES[size], **TF_COMMON, cond=cond), device=device)
            t0 = time.time()
            m.fit(a, b, log=None)
            r = _r(m.score(te))
            r.update(params=m.net.n_params(), epochs=m.epochs_trained, inner_val_bpg=round(m.best_val_bpg, 5),
                     train_seconds=round(time.time() - t0, 1), device=device)
            out.setdefault(m.name, []).append(r)
            print(f"{m.name} fold {fold}: {r['bits_per_glyph']:.4f} b/g {r['bits_per_word']:.3f} b/w "
                  f"({r['epochs']} ep, {r['train_seconds']}s)", flush=True)
    (RES / f"e002_cv_tf_{size}.json").write_text(json.dumps(out, indent=1))


# ----------------------------------------------------------------------------- freezing
def build(name: str, device: str):
    if name == "unigram":
        return Unigram()
    if name.startswith("kn"):
        n = int(name[2])
        return VarietyMixKN(n) if name.endswith("+variety") else KneserNey(n)
    cond = name.endswith("+variety")
    size = "small" if name.startswith(f"tf_d{SIZES['small']['d_model']}_") else "medium"
    return TransformerLM(TConfig(**SIZES[size], **TF_COMMON, cond=cond), device=device)


def freeze(name: str, dev: list, device: str) -> tuple[object, str, str]:
    m = build(name, device)
    a, b = inner_split(dev)
    if isinstance(m, TransformerLM):
        m.fit(a, b, log=print)
        path = CK / f"e002_frozen_{name.replace('+', '_')}.pt"
    else:
        m.fit(dev, val_lines=b) if isinstance(m, VarietyMixKN) else m.fit(dev)
        path = CK / f"e002_frozen_{name.replace('+', '_')}.pkl"
    sha = m.save(path)
    Path(str(path) + ".sha256").write_text(f"{sha}  {path.name}\n")
    return m, sha, os.path.relpath(path, ROOT)


def conditioned_name(name: str) -> str:
    return name if name.endswith("+variety") or name == "unigram" else name + "+variety"


# ----------------------------------------------------------------------------- PPC helpers
def sample(model, templates, seed=0):
    conds = [(l.currier, l.para_start) for l in templates]
    wl = model.sample_lines(conds, seed=seed)
    return cf.sample_stats(wl, [c for c, _ in conds])


def reference_from(tokens, leaves_ok, lines):
    prose = [t for t in tokens if t.mode == "prose" and leaves_ok(t.leaf)]
    labels = [t for t in tokens if t.mode == "label" and leaves_ok(t.leaf)]
    words = [w for l in lines for w in l.words]
    byv = {v: [t for t in prose if t.currier == v] for v in ("A", "B")}
    byv = {v: ts for v, ts in byv.items() if ts}
    return cf.reference_stats(prose, labels, words, by_variety=byv if len(byv) == 2 else None)


def strip(d):
    return {k: v for k, v in d.items() if k != "words"}


# ----------------------------------------------------------------------------- LOCKED_TEST (once)
def score_locked_test_once(frozen: dict, samples: dict, cond_for: dict) -> dict:
    """The single LOCKED_TEST entry point. Scores each frozen model once, logs to the ledger,
    and evaluates the (already drawn) PPC samples against LOCKED_TEST statistics."""
    marker = RES / "e002_locked_scored.json"
    if marker.exists():
        raise RuntimeError("LOCKED_TEST already scored for e002 frozen models; re-scoring = new model (protocol 1)")
    toks = _tokens()
    locked = locked_set(toks)
    lines = locked_test_lines(toks, confirm_final_scoring=True)
    out = {"stream": stream_stats(lines), "scores": {}, "ppc": {}}
    rows = []
    for name, (m, sha, path) in frozen.items():
        r = m.score(lines)
        out["scores"][name] = _r(r) | {"checkpoint": path, "checkpoint_sha256": sha}
        for metric in ("bits_per_glyph", "bits_per_word"):
            rows.append(dict(experiment="e002", model=name, checkpoint_sha256=sha, split="LOCKED_TEST", metric=metric,
                             value=f"{r[metric]:.5f}", command=CMD,
                             notes=f"frozen on all DEV leaves; {path}; events={r['events']} words={r['words']}; "
                                   f"protocol v1 default stream; first and only scoring"))
    ref = reference_from(toks, lambda l: l in locked, lines)
    out["reference"] = strip(ref)
    for name, st in samples.items():
        out["ppc"][name] = cf.run_checks(st, ref, samples.get(cond_for[name]))
        rows.append(dict(experiment="e002", model=name, checkpoint_sha256=frozen[name][1], split="LOCKED_TEST",
                         metric="ppc_n_pass_of_6", value=str(out["ppc"][name]["n_pass"]), command=CMD,
                         notes="posterior predictive checks P1-P6 vs LOCKED_TEST statistics; see e002_ppc.json"))
    ledger.append(rows)
    marker.write_text(json.dumps({"scored": sorted(frozen), "date": time.strftime("%Y-%m-%d %H:%M:%S")}))
    return out


def final():
    cv = json.loads((RES / "e002_cv_ngram.json").read_text())
    tf_meta = {}
    for size in SIZES:
        p = RES / f"e002_cv_tf_{size}.json"
        if p.exists():
            d = json.loads(p.read_text())
            cv.update(d)
            for k, v in d.items():
                tf_meta[k] = {"params": v[0]["params"], "mean_train_seconds": float(np.mean([f["train_seconds"] for f in v])),
                              "epochs": [f["epochs"] for f in v], "device": v[0]["device"]}
    table = {k: _r(pooled(v)) for k, v in cv.items()}
    classes = {"unigram": [k for k in cv if k == "unigram"],
               "kneser_ney": [k for k in cv if k.startswith("kn") and "[" not in k],
               "transformer": [k for k in cv if k.startswith("tf")]}
    best = {c: min(ks, key=lambda k: table[k]["bits_per_glyph"]) for c, ks in classes.items() if ks}
    overall = min(best.values(), key=lambda k: table[k]["bits_per_glyph"])
    print("pooled DEV CV:")
    for k in sorted(table, key=lambda k: table[k]["bits_per_glyph"]):
        print(f"  {k:28s} {table[k]['bits_per_glyph']:.4f} b/g  {table[k]['bits_per_word']:.3f} b/w")
    print("best per class:", best, "overall:", overall)

    dev = dev_lines()
    toks = _tokens()
    locked = locked_set(toks)
    assert not ({l.leaf for l in dev} & locked)
    device = os.environ.get("VCL_DEVICE") or ("mps" if torch.backends.mps.is_available() else "cpu")
    # models to freeze: best of each class + its variety-conditioned counterpart (needed for P4)
    to_freeze = []
    for c, k in best.items():
        to_freeze.append(k)
        if c != "unigram" and conditioned_name(k) not in to_freeze:
            to_freeze.append(conditioned_name(k))
    frozen = {}
    for name in to_freeze:
        print("freezing", name, flush=True)
        frozen[name] = freeze(name, dev, device)

    # PPC samples (drawn once, before LOCKED_TEST is touched); templates = DEV lines x2 for matched-length TTR
    templates = dev + dev
    samples = {name: sample(m, templates, seed=1) for name, (m, _, _) in frozen.items() if name != "unigram"}
    cond_for = {name: conditioned_name(name) for name in samples}
    ref_dev = reference_from(toks, lambda l: l not in locked, dev)
    ppc_dev = {name: cf.run_checks(st, ref_dev, samples.get(cond_for[name])) for name, st in samples.items()}

    res = {"protocol": "eval/PROTOCOL_v1.md", "corpus_docx_sha256": DOCX_SHA256,
           "stream": {"dev": stream_stats(dev), "description": "prose, clean tokens, lines; events = glyphs + one "
                      "end symbol per word ('_' or line-final '$'); vocab a-z,_,$ (28)"},
           "cv_folds": K, "per_fold": cv, "pooled_dev_cv": table, "transformer_meta": tf_meta,
           "best_per_class": best, "best_overall": overall,
           "frozen": {k: {"checkpoint": p, "sha256": s} for k, (_, s, p) in frozen.items()},
           "notes": ["kn4[merge_uncertain_spaces] uses a different event stream (fewer words); not comparable "
                     "to the default-stream rows.", "Not comparable to the external 11.01 bits/word figure."]}
    for name, (m, _, _) in frozen.items():
        if isinstance(m, TransformerLM):
            res["frozen"][name].update(describe(m) | {"epochs": m.epochs_trained, "inner_val_bpg": m.best_val_bpg})
        if isinstance(m, VarietyMixKN):
            res["frozen"][name]["lambda"] = m.lam
    (RES / "e002.json").write_text(json.dumps(res, indent=1))

    locked_res = score_locked_test_once(frozen, samples, cond_for)
    res["locked_test"] = locked_res["scores"]
    (RES / "e002.json").write_text(json.dumps(res, indent=1))
    ppc = {"protocol_section": "2 (P1-P6)", "primary_model": overall,
           "generator": "ancestral sampling (T=1) from frozen model; templates = DEV lines (variety, para-start) x2",
           "p4_uses_variety_conditioned_counterpart": cond_for,
           "reference_dev": strip(ref_dev), "reference_locked_test": locked_res["reference"],
           "models": {name: {"sample_stats": strip(st), "vs_dev": ppc_dev[name], "vs_locked_test": locked_res["ppc"][name]}
                      for name, st in samples.items()},
           "notes": ["P5 samples are prose-model words (the models never see labels); the threshold is absolute.",
                     "PPCs are threshold checks fixed in the protocol, not p-values; no Holm correction applies."]}
    (RES / "e002_ppc.json").write_text(json.dumps(ppc, indent=1, default=float))
    for name in samples:
        print(name, "DEV:", {k: v.get("pass") for k, v in ppc_dev[name].items() if isinstance(v, dict)})
        print(name, "LOCKED:", {k: v.get("pass") for k, v in locked_res["ppc"][name].items() if isinstance(v, dict)})
    for name, r in locked_res["scores"].items():
        print(f"LOCKED_TEST {name}: {r['bits_per_glyph']:.4f} b/g {r['bits_per_word']:.3f} b/w")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["cv-ngram", "cv-tf", "final"])
    ap.add_argument("--size", choices=list(SIZES), default="small")
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else "cpu")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    {"cv-ngram": cv_ngram, "cv-tf": lambda: cv_tf(a.size, a.device), "final": final}[a.stage]()
