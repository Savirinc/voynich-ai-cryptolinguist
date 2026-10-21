"""E035b: is E035's narrow match robust to the random seeds? See reports/E035B_PREREG.md.
Repeats the E035 procedure exactly (same 12 Bibles, same E033 windows, same grid, same fit on types, same 9 features,
same z rule and verdict rule), changing ONLY the two seeds: replicate r = 1..10 uses fit seed 35100 + r and eval
seed 35600 + r (in E035 these were 35035 and 35535).
Run: caffeinate -ims .venv/bin/python experiments/e035b_seed_replicates.py
"""
from __future__ import annotations

import json, random, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e030_reduplication import ANCHORS, PRIMARY, tokens  # noqa: E402
from e031_copy_pairs import stats as pair_stats  # noqa: E402
from e033_language_features import N, SEED as E033_SEED, Z_OK, feats  # noqa: E402
from e035_spelling_variation import ALL, GRID, vary, windows  # noqa: E402

REPS = 10
OUT = ROOT / "experiments/results/e035b.json"
TEXTS = ANCHORS + PRIMARY


def fit_task(task):
    bid, i, s, fs = task
    w = tokens(bid)[s:s + N]
    return bid, [len(set(vary(w, a, random.Random(fs + 1000 * i + j)))) for j, a in enumerate(GRID)]


def eval_task(task):
    bid, i, s, alpha, es = task
    v = vary(tokens(bid)[s:s + N], alpha, random.Random(es + i))
    f = feats([v], E033_SEED + i)
    f["NR"] = pair_stats([v], random.Random(es + 7 * i))["NR"]
    return bid, f


def replicate(r, V0, vl, W, pool):
    fs, es = 35100 + r, 35600 + r
    V = dict(V0); V["NR"] = pair_stats(vl, random.Random(es))["NR"]
    tasks = [(b, i, s) for b in TEXTS for i, s in enumerate(W[b])]
    fr = pool.map(fit_task, [t + (fs,) for t in tasks])
    alpha = {}
    for b in TEXTS:
        m = np.mean([t for bb, t in fr if bb == b], axis=0)
        alpha[b] = GRID[int(np.argmin(np.abs(m - V["types"])))]
    res = pool.map(eval_task, [(b, i, s, alpha[b], es) for b, i, s in tasks])
    T = {}
    for b in TEXTS:
        G = [f for bb, f in res if bb == b]
        M = {k: float(np.mean([g[k] for g in G])) for k in ALL}
        S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in ALL}
        Z = {k: round((V[k] - M[k]) / S[k], 2) for k in ALL}
        T[b] = {"alpha": alpha[b], "z": Z, "fail": [k for k in ALL if abs(Z[k]) > Z_OK]}
    best = min(T, key=lambda b: (len(T[b]["fail"]), float(np.sqrt(np.mean([T[b]["z"][k] ** 2 for k in ALL])))))
    return {"rep": r, "fit_seed": fs, "eval_seed": es, "V_NR": V["NR"], "texts": T, "best": best,
            "best_fails": T[best]["fail"], "match": len(T[best]["fail"]) <= 1}


def main():
    lines, _, dev_words, locked = E.voynich_lines()
    assert len(dev_words) == N
    vl = [[w for w in l if w] for l in lines if any(l)]
    V0 = feats(vl, E033_SEED)
    W = windows()
    reps = []
    with Pool(3) as pool:
        for r in range(1, REPS + 1):
            x = replicate(r, V0, vl, W, pool); reps.append(x)
            t = x["texts"]["indayt"]
            print(f"rep {r:2d} best {x['best']:8s} fails {x['best_fails']} match {x['match']} | indayt alpha "
                  f"{t['alpha']} fails {t['fail']} PERS_30 z {t['z']['PERS_30']:+.2f} hapax z {t['z']['type_hapax']:+.2f}",
                  flush=True)
    k = sum(x["match"] for x in reps)
    if k >= 8:
        verdict, bf = "ROBUST", {}
    elif k >= 3:
        verdict, bf = "FRAGILE", {"L": 1 / 3, "C": 1 / 3}
    else:
        verdict, bf = "NOT REPLICATED", {"L": 1 / 10, "C": 1 / 3}
    out = {"experiment": "E035b", "replicates": reps, "n_match": k, "verdict": verdict,
           "bayes_factors_correction": bf, "locked_test_excluded": locked}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"matches {k}/{REPS} | {verdict} {bf}")


if __name__ == "__main__":
    main()
