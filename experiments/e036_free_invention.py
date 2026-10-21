"""E036 (ledger test 7): FREE INVENTION of spellings, with the seed check built in. See reports/E036_PREREG.md.

Variation model (one parameter, p): the first time a word appears it is written in its base spelling; after that each
use is, with probability p, written with a FRESH spelling (one random edit of the base, as E035, never used before
for that word), otherwise in the base spelling. Fresh spellings are not reused, so most of them occur once.
Everything else is E035b: same 12 Bibles, same E033 windows, p fitted on types per replicate, same 9 features, same
z rule; 10 replicates, fit seed 36100 + r, eval seed 36600 + r. A replicate MATCHES if its best text fails <= 1 of 9.
Run: caffeinate -ims .venv/bin/python experiments/e036_free_invention.py
"""
from __future__ import annotations

import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e030_reduplication import ANCHORS, PRIMARY, tokens  # noqa: E402
from e031_copy_pairs import stats as pair_stats  # noqa: E402
from e033_language_features import N, SEED as E033_SEED, Z_OK, feats  # noqa: E402
from e035_spelling_variation import ALL, edit, windows  # noqa: E402

REPS = 10
GRID = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]
OUT = ROOT / "experiments/results/e036.json"
TEXTS = ANCHORS + PRIMARY


def vary(toks, p, rng):
    lc = Counter(c for w in toks for c in w)
    letters, weights = list(lc), list(lc.values())
    used = {}
    out = []
    for w in toks:
        if w not in used:
            used[w] = {w}; out.append(w); continue
        if rng.random() < p:
            v = edit(w, rng, letters, weights, used[w]); used[w].add(v); out.append(v)
        else:
            out.append(w)
    return out


def fit_task(task):
    bid, i, s, fs = task
    w = tokens(bid)[s:s + N]
    return bid, [len(set(vary(w, a, random.Random(fs + 1000 * i + j)))) for j, a in enumerate(GRID)]


def eval_task(task):
    bid, i, s, p, es = task
    v = vary(tokens(bid)[s:s + N], p, random.Random(es + i))
    f = feats([v], E033_SEED + i)
    f["NR"] = pair_stats([v], random.Random(es + 7 * i))["NR"]
    return bid, f


def replicate(r, V0, vl, W, pool):
    fs, es = 36100 + r, 36600 + r
    V = dict(V0); V["NR"] = pair_stats(vl, random.Random(es))["NR"]
    tasks = [(b, i, s) for b in TEXTS for i, s in enumerate(W[b])]
    fr = pool.map(fit_task, [t + (fs,) for t in tasks])
    pfit = {}
    for b in TEXTS:
        m = np.mean([t for bb, t in fr if bb == b], axis=0)
        pfit[b] = GRID[int(np.argmin(np.abs(m - V["types"])))]
    res = pool.map(eval_task, [(b, i, s, pfit[b], es) for b, i, s in tasks])
    T = {}
    for b in TEXTS:
        G = [f for bb, f in res if bb == b]
        M = {k: float(np.mean([g[k] for g in G])) for k in ALL}
        S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in ALL}
        Z = {k: round((V[k] - M[k]) / S[k], 2) for k in ALL}
        T[b] = {"p": pfit[b], "mean": M, "z": Z, "fail": [k for k in ALL if abs(Z[k]) > Z_OK]}
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
            b = x["best"]; t = x["texts"][b]
            print(f"rep {r:2d} best {b:8s} p {t['p']} fails {x['best_fails']} match {x['match']} | z: "
                  + " ".join(f"{k} {t['z'][k]:+.1f}" for k in ALL), flush=True)
            ti = x["texts"]["indayt"]
            print(f"        indayt p {ti['p']} fails {ti['fail']} | means: "
                  + " ".join(f"{k} {ti['mean'][k]:.3g}" for k in ALL), flush=True)
    k = sum(x["match"] for x in reps)
    if k >= 8:
        verdict, bf = "ROBUST MATCH", {"L": 10.0, "C": 3.0}
    elif k >= 3:
        verdict, bf = "UNSTABLE", {}
    else:
        verdict, bf = "NO MATCH", {}
    out = {"experiment": "E036", "grid": GRID, "replicates": reps, "n_match": k, "verdict": verdict,
           "bayes_factors": bf, "locked_test_excluded": locked}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"matches {k}/{REPS} | {verdict} {bf}")


if __name__ == "__main__":
    main()
