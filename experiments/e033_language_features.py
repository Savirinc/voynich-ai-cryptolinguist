"""E033 (ledger test 4): the counterpart of E032 for real languages. Does any real-language text match Voynich on
the WORD-LEVEL features of E032, i.e. those unchanged by how words are spelled? See reports/E033_PREREG.md.

Features (8): R, types, I_word, top_word, PERS_30, COV_30, type_hapax, zipf_slope (code as in E032).
Texts: the 12 E030 Bibles with word tokens (10 primary + 2 anchors). Samples = non-overlapping consecutive windows of
28,841 tokens (Voynich DEV size), 10 chosen at random (seed 33033) or all if fewer (minimum 3).
z rule, sd floor and pass/fail thresholds as E032 (scaled to 8 features).
Run: caffeinate -ims .venv/bin/python experiments/e033_language_features.py
"""
from __future__ import annotations

import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e019_unit_burstiness import burst  # noqa: E402
from e021_persistence import persistence  # noqa: E402
from e030_reduplication import ANCHORS, PRIMARY, tokens  # noqa: E402
from e031_copy_pairs import stats as pair_stats  # noqa: E402

SEED, N, KMAX, KMIN, Z_OK = 33033, 28841, 10, 3, 3.0
FEATS = ["R", "types", "I_word", "top_word", "PERS_30", "COV_30", "type_hapax", "zipf_slope"]
OUT = ROOT / "experiments/results/e033.json"


def feats(lines, seed):
    toks = [w for l in lines for w in l]
    wc = Counter(toks)
    fr = np.array(sorted(wc.values(), reverse=True)[:100], float)
    Iw, Tw, _ = burst(toks)
    pe = persistence(toks)
    return {"R": pair_stats(lines, random.Random(seed))["R"], "types": float(len(wc)), "I_word": Iw, "top_word": Tw,
            "PERS_30": pe["PERS_30"], "COV_30": pe["COV_30"],
            "type_hapax": sum(v == 1 for v in wc.values()) / len(wc),
            "zipf_slope": float(np.polyfit(np.log(np.arange(1, len(fr) + 1)), np.log(fr), 1)[0])}


def run(task):
    bid, i, s = task
    w = tokens(bid)
    return bid, feats([w[s:s + N]], SEED + i)


def zscore(V, G):
    M = {k: float(np.mean([g[k] for g in G])) for k in FEATS}
    S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in FEATS}
    return M, S, {k: round((V[k] - M[k]) / S[k], 2) for k in FEATS}


def main():
    rng = random.Random(SEED)
    lines, _, dev_words, locked = E.voynich_lines()
    assert len(dev_words) == N
    V = feats([[w for w in l if w] for l in lines if any(l)], SEED)
    tasks = []
    for bid in ANCHORS + PRIMARY:
        nwin = len(tokens(bid)) // N
        starts = [j * N for j in range(nwin)]
        pick = sorted(rng.sample(starts, min(KMAX, nwin)))
        assert len(pick) >= KMIN, bid
        tasks += [(bid, i, s) for i, s in enumerate(pick)]
    with Pool(3) as pool:
        res = pool.map(run, tasks)
    T = {}
    for bid in ANCHORS + PRIMARY:
        G = [f for b, f in res if b == bid]
        M, S, Z = zscore(V, G)
        T[bid] = {"n_windows": len(G), "mean": M, "sd": S, "z": Z, "fail": [k for k in FEATS if abs(Z[k]) > Z_OK]}
    best = min(T, key=lambda b: (len(T[b]["fail"]), float(np.sqrt(np.mean([T[b]["z"][k] ** 2 for k in FEATS])))))
    nf = len(T[best]["fail"])
    if nf <= 1:
        verdict, bf = "A LANGUAGE MATCHES", {"L": 3.0}
    elif nf == 2:
        verdict, bf = "PARTIAL", {}
    else:
        verdict, bf = "NO LANGUAGE MATCHES", {"L": 1 / 3}
    e032 = json.loads((ROOT / "experiments/results/e032.json").read_text())
    gen = {k: e032["z"][k] for k in FEATS}
    out = {"experiment": "E033", "voynich": V, "texts": T, "best": best, "best_fails": T[best]["fail"],
           "verdict": verdict, "bayes_factors": bf, "e032_generator_z_same_features": gen,
           "e032_generator_fails_same_features": [k for k in FEATS if abs(gen[k]) > Z_OK], "locked_test_excluded": locked}
    OUT.write_text(json.dumps(out, indent=1))
    print("Voynich", {k: round(v, 3) for k, v in V.items()})
    for b in ANCHORS + PRIMARY:
        print(f"{b:9s} n={T[b]['n_windows']:2d} fails {len(T[b]['fail'])}: " + " ".join(f"{k} {T[b]['z'][k]:+.1f}" for k in FEATS))
    print(f"{'generator':9s} (E032)    fails {len(out['e032_generator_fails_same_features'])}: " + " ".join(f"{k} {gen[k]:+.1f}" for k in FEATS))
    print("best", best, T[best]["fail"], "|", verdict, bf)


if __name__ == "__main__":
    main()
