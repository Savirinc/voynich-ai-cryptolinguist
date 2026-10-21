"""E035 (ledger test 6): does FREE SPELLING VARIATION, added to a real language, reproduce Voynich's word habits?
See reports/E035_PREREG.md.

Variation model (one parameter, alpha), applied inside each window, token by token in reading order:
  the first time a word appears it is written in its base spelling; after that it reuses one of the spellings already
  used for that word (chosen in proportion to how often each was used) or, with probability alpha / (n + alpha)
  (n = times the word has been seen), gets a NEW spelling = one random edit of the base (substitute 2 : insert 1 :
  delete 1, letters drawn from the window's own letter frequencies; never equal to an existing spelling of that word).
  (A Chinese-restaurant process per word: frequent words get ~alpha*ln(n) spellings, rare words keep one.)
Fit: per text, alpha from a fixed grid, chosen so the window-mean number of distinct words is closest to Voynich
  DEV's 6,077 (fit seed). Nothing else is fitted.
Evaluate: at the fitted alpha with a fresh seed, E033's 8 features + NR (E031) per window; z rule as E033.
Texts and windows: E033's 12 Bibles and exactly E033's windows (same seed 33033 draw).
Run: caffeinate -ims .venv/bin/python experiments/e035_spelling_variation.py
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
from e033_language_features import FEATS, KMAX, KMIN, N, SEED as E033_SEED, Z_OK, feats  # noqa: E402

FIT_SEED, EVAL_SEED = 35035, 35535
GRID = [0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.65, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
ALL = FEATS + ["NR"]          # 9 features scored; 'types' is the fitted one
OUT = ROOT / "experiments/results/e035.json"


def edit(w, rng, letters, weights, taken):
    for _ in range(100):
        op = rng.choices(("sub", "ins", "del"), (2, 1, 1))[0]
        if op == "del" and len(w) < 2:
            continue
        c = rng.choices(letters, weights)[0]
        if op == "sub":
            i = rng.randrange(len(w)); v = w[:i] + c + w[i + 1:]
        elif op == "ins":
            i = rng.randrange(len(w) + 1); v = w[:i] + c + w[i:]
        else:
            i = rng.randrange(len(w)); v = w[:i] + w[i + 1:]
        if v != w and v not in taken:
            return v
    return w + rng.choices(letters, weights)[0] * (len(taken) + 1)


def vary(toks, alpha, rng):
    lc = Counter(c for w in toks for c in w)
    letters, weights = list(lc), list(lc.values())
    sp = {}                                   # word -> [spellings], [counts]
    out = []
    for w in toks:
        if w not in sp:
            sp[w] = ([w], [1]); out.append(w); continue
        forms, cnt = sp[w]
        n = sum(cnt)
        if rng.random() * (n + alpha) < alpha:
            v = edit(w, rng, letters, weights, set(forms)); forms.append(v); cnt.append(1)
        else:
            k = rng.choices(range(len(forms)), cnt)[0]; v = forms[k]; cnt[k] += 1
        out.append(v)
    return out


def windows():
    rng = random.Random(E033_SEED)          # reproduces E033's window draw exactly
    W = {}
    for bid in ANCHORS + PRIMARY:
        nwin = len(tokens(bid)) // N
        starts = [j * N for j in range(nwin)]
        W[bid] = sorted(rng.sample(starts, min(KMAX, nwin)))
        assert len(W[bid]) >= KMIN, bid
    return W


def fit_task(task):
    bid, i, s = task
    w = tokens(bid)[s:s + N]
    return bid, [len(set(vary(w, a, random.Random(FIT_SEED + 1000 * i + j)))) for j, a in enumerate(GRID)]


def eval_task(task):
    bid, i, s, alpha = task
    v = vary(tokens(bid)[s:s + N], alpha, random.Random(EVAL_SEED + i))
    f = feats([v], E033_SEED + i)
    f["NR"] = pair_stats([v], random.Random(EVAL_SEED + 7 * i))["NR"]
    return bid, f


def main():
    lines, _, dev_words, locked = E.voynich_lines()
    assert len(dev_words) == N
    vl = [[w for w in l if w] for l in lines if any(l)]
    V = feats(vl, E033_SEED)
    V["NR"] = pair_stats(vl, random.Random(EVAL_SEED))["NR"]
    W = windows()
    tasks = [(b, i, s) for b in ANCHORS + PRIMARY for i, s in enumerate(W[b])]
    with Pool(3) as pool:
        fr = pool.map(fit_task, tasks)
    fit = {}
    for b in ANCHORS + PRIMARY:
        m = np.mean([t for bb, t in fr if bb == b], axis=0)
        j = int(np.argmin(np.abs(m - V["types"])))
        fit[b] = {"alpha": GRID[j], "types_by_alpha": dict(zip(map(str, GRID), m.round(1).tolist()))}
    with Pool(3) as pool:
        res = pool.map(eval_task, [(b, i, s, fit[b]["alpha"]) for b, i, s in tasks])
    T = {}
    for b in ANCHORS + PRIMARY:
        G = [f for bb, f in res if bb == b]
        M = {k: float(np.mean([g[k] for g in G])) for k in ALL}
        S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in ALL}
        Z = {k: round((V[k] - M[k]) / S[k], 2) for k in ALL}
        T[b] = {"alpha": fit[b]["alpha"], "n_windows": len(G), "mean": M, "sd": S, "z": Z,
                "fail": [k for k in ALL if abs(Z[k]) > Z_OK], "types_by_alpha": fit[b]["types_by_alpha"]}
    best = min(T, key=lambda b: (len(T[b]["fail"]), float(np.sqrt(np.mean([T[b]["z"][k] ** 2 for k in ALL])))))
    nf = len(T[best]["fail"])
    if nf <= 1:
        verdict, bf = "VARIATION MATCHES", {"L": 10.0, "C": 3.0}
    elif nf == 2:
        verdict, bf = "PARTIAL", {}
    else:
        verdict, bf = "NO MATCH", {}
    # check: at alpha = 0 the fit reproduces E033's mean number of distinct words
    e033 = json.loads((ROOT / "experiments/results/e033.json").read_text())
    check = {b: [T[b]["types_by_alpha"]["0"], round(e033["texts"][b]["mean"]["types"], 1)] for b in T}
    out = {"experiment": "E035", "voynich": V, "grid": GRID, "texts": T, "best": best, "best_fails": T[best]["fail"],
           "verdict": verdict, "bayes_factors": bf, "alpha0_types_vs_e033": check, "locked_test_excluded": locked}
    OUT.write_text(json.dumps(out, indent=1))
    print("Voynich", {k: round(float(v), 3) for k, v in V.items()})
    for b in ANCHORS + PRIMARY:
        t = T[b]
        print(f"{b:9s} alpha {t['alpha']:<4} fails {len(t['fail'])}: " + " ".join(f"{k} {t['z'][k]:+.1f}" for k in ALL))
        print(" " * 10 + "means: " + " ".join(f"{k} {t['mean'][k]:.3g}" for k in ALL))
    print("alpha=0 types vs E033:", check)
    print("best", best, T[best]["fail"], "|", verdict, bf)


if __name__ == "__main__":
    main()
