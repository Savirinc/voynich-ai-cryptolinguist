"""E003 tuning: train the encoding-family classifier and calibrate solver confidence / abstention.

Leakage controls (solver brief + eval/PROTOCOL_v1.md section 3):
  * Uses ONLY tasks generated here with vcl.synthetic.encoders from books whose PUBLIC role is 'tune', in TRAIN
    language families (germanic, romance, slavic), with TRAIN encodings (mono, homophonic, vigenere, columnar,
    nulls). No held-out encoding, held-out language family, decoy generator, test book, or secret file is used.
  * The public tune split (data/derived/benchmark_v1/public/tune.jsonl) has no labels; it is used only as an
    unlabeled check that the classifier's predicted-family mix looks sane.
  * Scoring of self-generated tasks uses vcl.eval.score.char_acc / encoders.comparable on answers WE generated.

Outputs (data/derived/solver_v1/): family_classifier.pkl, calibrator.pkl, tune_report.json, calib_rows.jsonl

Run: .venv/bin/python experiments/e003_tune.py [--n-clf 1500] [--n-cal 300] [--workers 10]
"""
from __future__ import annotations

import argparse
import json
import pickle
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vcl.synthetic.corpora import load_books  # noqa: E402
from vcl.synthetic.encoders import ENCODERS, comparable  # noqa: E402
from vcl.synthetic.schema import PublicTask, load_jsonl  # noqa: E402
from vcl.eval.score import char_acc  # noqa: E402  (scoring OUR OWN generated tasks only)

TRAIN_FAMILIES = ("germanic", "romance", "slavic")
TRAIN_ENC = ["mono", "homophonic", "vigenere", "columnar", "nulls"]
ART = ROOT / "data/derived/solver_v1"
SEED = 3003

_BOOKS = None


def tune_books():
    global _BOOKS
    if _BOOKS is None:
        roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
        _BOOKS = [b for b in load_books()
                  if roles[b["id"]]["role"] == "tune" and roles[b["id"]]["family"] in TRAIN_FAMILIES]
        assert _BOOKS and all(b["family"] in TRAIN_FAMILIES for b in _BOOKS)
    return _BOOKS


def sample_plaintext(text, length, rng):
    start = rng.randrange(0, max(1, len(text) - length - 50))
    sp = text.find(" ", start)
    chunk = text[sp + 1: sp + 1 + length]
    return chunk[: chunk.rfind(" ")] if " " in chunk else chunk


def gen_task(i, seed, lengths):
    rng = random.Random(seed)
    books = tune_books()
    langs = sorted({b["lang"] for b in books})
    lang = langs[i % len(langs)]
    book = rng.choice([b for b in books if b["lang"] == lang])
    fam = TRAIN_ENC[(i // len(langs)) % len(TRAIN_ENC)] if i % 3 != 2 else rng.choice(TRAIN_ENC)
    length = rng.choice(lengths)
    plain = sample_plaintext(book["text"], length, rng)
    syms, key, ident, recov = ENCODERS[fam](plain, rng)
    return {"id": f"selftune-{i:05d}", "symbols": syms, "family": fam, "lang": lang, "plain": plain,
            "recov": recov, "length": len(plain)}


def _feat(t):
    from vcl.solvers.features import feature_vector
    x, names = feature_vector(t["symbols"])
    return x, names


def _solve(t):
    from vcl.solvers.api import solve
    from vcl.solvers.lm import Library
    p = solve(PublicTask(t["id"], t["symbols"], "selftune"), Library.full(), force_answer=True)
    rec = next((x for x in p.log if isinstance(x, dict) and "conf_features" in x), None)
    if rec is None:   # too short: solver refuses; counts as unsolved with no features
        return None
    ca = char_acc(comparable(t["family"], p.plaintext), comparable(t["family"], t["recov"]))
    return {"id": t["id"], "family": t["family"], "lang": t["lang"], "length": t["length"],
            "pred_family": p.family, "pred_lang": p.language, "char_acc": ca, "solved": ca >= 0.9,
            "conf_features": rec["conf_features"], "chosen": rec["chosen"], "seconds": rec["seconds"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-clf", type=int, default=1500)
    ap.add_argument("--n-cal", type=int, default=300)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--skip-clf", action="store_true")
    a = ap.parse_args()
    ART.mkdir(parents=True, exist_ok=True)
    report = {"command": " ".join(sys.argv), "seed": SEED}

    # ---------------- 1. family classifier
    if not a.skip_clf:
        t0 = time.time()
        rng = random.Random(SEED)
        tasks = [gen_task(i, rng.randrange(2**31), [100, 150, 300, 600, 1000, 2000, 3000]) for i in range(a.n_clf)]
        with Pool(a.workers) as pool:
            feats = pool.map(_feat, tasks, chunksize=20)
        X = np.array([f[0] for f in feats]); names = feats[0][1]
        y = [t["family"] for t in tasks]
        n_tr = int(0.8 * len(tasks))
        from vcl.solvers.classifier import FamilyClassifier
        clf = FamilyClassifier().fit(X[:n_tr], y[:n_tr], X[n_tr:], y[n_tr:], names)
        report["classifier"] = {"n_train": n_tr, "n_cal": len(tasks) - n_tr, "heldout_acc": clf.cal_acc,
                                "d_lo": float(clf.d_lo), "d_hi": float(clf.d_hi), "seconds": round(time.time() - t0, 1)}
        # refit closed-set model on all data, keep calibrated distance thresholds from the held-out slice
        d_lo, d_hi, acc = clf.d_lo, clf.d_hi, clf.cal_acc
        clf = FamilyClassifier().fit(X, y, X[n_tr:], y[n_tr:], names)
        clf.d_lo, clf.d_hi, clf.cal_acc = d_lo, d_hi, acc
        clf.save(ART / "family_classifier.pkl")
        # unlabeled sanity check on the public tune split
        pub = load_jsonl(ROOT / "data/derived/benchmark_v1/public/tune.jsonl", PublicTask)
        mix = Counter(str(max(clf.predict(p.symbols)["family_probs"].items(), key=lambda kv: kv[1])[0]) for p in pub)
        report["classifier"]["public_tune_predicted_mix"] = dict(mix)
        print("classifier", report["classifier"], flush=True)

    # ---------------- 2. confidence calibration (full solver on fresh self-generated tasks)
    cal_path = ART / "calibrator.pkl"
    if cal_path.exists():
        cal_path.unlink()          # solve() must run with the heuristic placeholder while collecting features
    rng = random.Random(SEED + 1)
    tasks = [gen_task(100000 + i, rng.randrange(2**31), [60, 100, 150, 300, 1000, 3000]) for i in range(a.n_cal)]
    t0 = time.time()
    with Pool(a.workers) as pool:
        rows = [r for r in pool.map(_solve, tasks, chunksize=1) if r is not None]
    report["calibration_solve_seconds"] = round(time.time() - t0, 1)
    with open(ART / "calib_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    feats = ["gap", "lex", "has_lex", "log_n", "margin", "p_family", "p_unknown", "types_per_sqrt_n"]
    X = np.array([[r["conf_features"][k] for k in feats] for r in rows])
    y = np.array([r["solved"] for r in rows], dtype=int)
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
    cv = cross_val_predict(model, X, y, cv=5, method="predict_proba")[:, 1]
    # operating threshold: smallest t such that, on out-of-fold predictions, answered tasks are >= 95% solved
    thr = 0.5
    for t in np.linspace(0.3, 0.99, 70):
        m = cv >= t
        if m.sum() >= 5 and y[m].mean() >= 0.95:
            thr = float(t); break
    model.fit(X, y)
    with open(cal_path, "wb") as f:
        pickle.dump({"model": model, "features": feats, "threshold": thr, "version": "cal-v1"}, f)
    by_fam = {}
    for fam in TRAIN_ENC:
        idx = [i for i, r in enumerate(rows) if r["family"] == fam]
        by_fam[fam] = {"n": len(idx), "solved_rate": float(np.mean([rows[i]["solved"] for i in idx])),
                       "mean_char_acc": float(np.mean([rows[i]["char_acc"] for i in idx])),
                       "family_id_acc": float(np.mean([rows[i]["pred_family"] == fam for i in idx])),
                       "lang_id_acc": float(np.mean([rows[i]["pred_lang"] == rows[i]["lang"] for i in idx]))}
    from vcl.eval.score import ece
    report["calibration"] = {
        "n": len(rows), "solved_rate": float(y.mean()), "threshold": thr,
        "oof_answered_rate": float((cv >= thr).mean()),
        "oof_selective_solved": float(y[cv >= thr].mean()) if (cv >= thr).any() else None,
        "oof_ece": ece(cv, y), "by_family": by_fam,
        "by_length": {str(L): float(np.mean([r["solved"] for r in rows if abs(r["length"] - L) < L * 0.2 + 5]))
                      for L in [60, 100, 150, 300, 1000, 3000]},
        "mean_seconds": float(np.mean([r["seconds"] for r in rows])),
        "coef": dict(zip(feats, model[-1].coef_[0].round(3).tolist())),
    }
    print(json.dumps(report["calibration"], indent=1))
    (ART / "tune_report.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
