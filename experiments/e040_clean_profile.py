"""E040 (attack step 1d): Voynich's core profile re-measured on the cleaned sign inventory. See reports/E040_PREREG.md.

Normalisation N1 (from E038/E039): every run of e (e, ee, eee) -> e ; every t -> k (so cth -> ckh).
d and q are NOT normalised (d: scribe habit, handled by measuring Currier A and B separately; q: location habit,
kept). r and l are kept apart.
Texts: Voynich DEV prose (all), Currier A, Currier B; each RAW (EVA as is) and N1.
Measures:
  units   h1, h2, L at segmentation S2 (E024/E027 code), checked against E027's simple-syllable range, nearest text
  words   types, type_hapax, zipf_slope (top 100), R and NR (E031), NSUF95 and ENDS_PER_STEM (E026 segmenter / E037)
A-vs-B: word measures depend on size, so B is also measured on 10 random runs of consecutive B lines with A's token
count (seed 40040); the mean is reported as "B (A-size)".
Run: caffeinate -ims .venv/bin/python experiments/e040_clean_profile.py
"""
from __future__ import annotations

import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e024_atoms as A  # noqa: E402
from e026_endings import SEG  # noqa: E402
from e031_copy_pairs import stats as pair_stats  # noqa: E402
from vcl.solvers.segment import segment_types  # noqa: E402

SEED, BDRAWS = 40040, 10
OUT = ROOT / "experiments/results/e040.json"
E027 = json.loads((ROOT / "experiments/results/e027.json").read_text())
SD = E027["sd33"]


def n1(w):
    return re.sub(r"e+", "e", w).replace("t", "k")


def profile(lines, rng):
    toks = [w for l in lines for w in l]
    m = A.metrics([A.segment(w, A.SEGS["S2"]) for w in toks])
    simple = {t: x for t, x in E027["texts"].items() if t.split("/")[0] in ("haw1868", "ton", "mri2012", "vie1934", "cmn-cu89s")}
    dist = {t: float(np.sqrt(sum(((m[k] - x[k]) / SD[k]) ** 2 for k in ("h1", "h2", "L")))) for t, x in simple.items()}
    rs = E027["range_simple"]
    wc = Counter(toks)
    fr = np.array(sorted(wc.values(), reverse=True)[:100], float)
    ps = pair_stats(lines, rng)
    split = segment_types(wc, seed=SEED, **SEG)
    end = {w: w[b:] for w, b in split.items()}; stem = {w: w[:b] for w, b in split.items()}
    suf = Counter(end[w] for w in toks if end[w])
    acc = nsuf = 0
    for _, c in suf.most_common():
        if acc >= 0.95 * sum(suf.values()):
            break
        acc += c; nsuf += 1
    stc = Counter(stem[w] for w in toks); by = defaultdict(set)
    for w in wc:
        by[stem[w]].add(end[w])
    eps = float(np.mean([len(by[s]) for s, c in stc.items() if c >= 10])) if any(c >= 10 for c in stc.values()) else float("nan")
    return {"tokens": len(toks), "h1": m["h1"], "h2": m["h2"], "L": m["L"],
            "inside_simple": all(rs[k][0] <= m[k] <= rs[k][1] for k in ("h1", "h2", "L")),
            "nearest": sorted(dist, key=dist.get)[:3], "nearest_dist": round(min(dist.values()), 2),
            "types": len(wc), "type_hapax": sum(v == 1 for v in wc.values()) / len(wc),
            "zipf_slope": float(np.polyfit(np.log(np.arange(1, len(fr) + 1)), np.log(fr), 1)[0]),
            "R": ps["R"], "NR": ps["NR"], "NSUF95": nsuf, "ENDS_PER_STEM": eps}


def b_asize(blines, n_tok, rng, f):
    out = []
    for _ in range(BDRAWS):
        s = rng.randrange(len(blines)); sel, k, i = [], 0, s
        while k < n_tok:
            sel.append(blines[i % len(blines)]); k += len(blines[i % len(blines)]); i += 1
        out.append(f(sel))
    return {k: float(np.mean([o[k] for o in out])) for k in out[0] if isinstance(out[0][k], (int, float)) and not isinstance(out[0][k], bool)}


def main():
    rng = random.Random(SEED)
    lines, cur, dev_words, locked = E.voynich_lines()
    clean = [[w for w in l if w] for l in lines]
    sets = {"DEV": [l for l in clean if l], "A": [l for l, c in zip(clean, cur) if l and c == "A"],
            "B": [l for l, c in zip(clean, cur) if l and c == "B"]}
    res = {}
    for norm, fn in (("RAW", lambda w: w), ("N1", n1)):
        for name, L in sets.items():
            LL = [[fn(w) for w in l] for l in L]
            r = profile(LL, random.Random(SEED)); res[f"{name}/{norm}"] = r
            print(f"{name:3s} {norm:3s} " + " ".join(f"{k} {r[k]:.3g}" for k in
                  ["tokens", "h1", "h2", "L", "types", "type_hapax", "zipf_slope", "R", "NR", "NSUF95", "ENDS_PER_STEM"])
                  + f" inside {r['inside_simple']} nearest {r['nearest'][0]} ({r['nearest_dist']})", flush=True)
        nA = res[f"A/{norm}"]["tokens"]
        BL = [[fn(w) for w in l] for l in sets["B"]]
        rb = b_asize(BL, nA, rng, lambda sel: profile(sel, random.Random(SEED)))
        res[f"B(A-size)/{norm}"] = rb
        print(f"B(A-size) {norm} " + " ".join(f"{k} {rb[k]:.3g}" for k in
              ["tokens", "h2", "types", "type_hapax", "zipf_slope", "R", "NR", "NSUF95", "ENDS_PER_STEM"]), flush=True)
    res["c11_bible_steepest_flattest"] = [-1.12, -0.79]
    res["locked_test_excluded"] = locked
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
