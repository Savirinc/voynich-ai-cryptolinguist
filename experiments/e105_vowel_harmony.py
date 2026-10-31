"""E105 (Arham, Reddit idea R11): do Voynich "vowels" (o, a, y) agree within words, like vowel harmony? See reports/E105_PREREG.md.

Unit: word TYPES of a 28,841-token cut. Vowel sequence of a word = its vowel characters in order (consonants skipped).
I = mutual information (bits) between consecutive vowels within words. Null: vowels are permuted among words within
cells of (word length, character position), which keeps where vowels sit in words and destroys word-level agreement;
20 permutations. EXCESS = I - mean I_null.
Vowels: Latin-script languages, letters whose base (NFD) is in a e i o u y, plus i-dotless, schwa, ae, oe. Voynich and
generator (EVA): o, a, y (the Reddit claim).
Known answers: HARMONY languages turytc (Turkish), hun (Hungarian), azb (Azerbaijani); NON-HARMONY: 22 Latin-script
languages listed in NONH. Validity: min EXCESS of harmony languages > max EXCESS of non-harmony languages.
Generator: 60 stretches (E032 x 10, E100 grid x 50).
  HARMONY-LIKE  Voynich EXCESS >= harmony min and > generator max  -> M x 1/3
  otherwise (NO HARMONY / BETWEEN) or VOID                        -> none (most languages lack harmony)
Rule 8: Voynich within 0.5 sd (permutation sd) of a boundary -> 10 fresh permutation seeds, >= 8 agree.
Unscored: Voynich with o, a, y, e as vowels; per-text I and null.
Run: caffeinate -ims .venv/bin/python experiments/e105_vowel_harmony.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e099_phrase_repeats_v2 as P  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED = 105105
OUT = ROOT / "experiments/results/e105.json"
E100W = ROOT / "experiments/results/e100_work"
HARM = ["turytc", "hun", "azb"]
NONH = ["latVUC", "ita1885", "deu1912", "ces1613", "polubg", "eng-kjv", "fraLSG", "nld", "dan1931", "swe", "ron1924",
        "hrv", "slk", "lit", "indayt", "tglulb", "hausa", "mri2012", "haw1868", "cebulb", "hil", "iloulb"]
EVA_V = set("oay")
NPERM = 20
log = P.log


def is_vowel_latin(ch):
    if ch in "ıəæœ":
        return True
    b = unicodedata.normalize("NFD", ch)[0]
    return b in "aeiouy"


def mi(pairs):
    if not pairs:
        return 0.0
    j = Counter(pairs); n = len(pairs); a = Counter(x for x, _ in pairs); b = Counter(y for _, y in pairs)
    return float(sum(c / n * np.log2(c * n / (a[x] * b[y])) for (x, y), c in j.items()))


def harmony(types, isv, rng, nperm=NPERM):
    words = [list(w) for w in types]
    pos = [(i, k) for i, w in enumerate(words) for k, ch in enumerate(w) if isv(ch)]

    def pairs_of(ws):
        out = []
        for w in ws:
            v = [ch for ch in w if isv(ch)]
            out += list(zip(v, v[1:]))
        return out
    I = mi(pairs_of(words))
    cells = defaultdict(list)
    for i, k in pos:
        cells[(len(words[i]), k)].append((i, k))
    nulls = []
    for _ in range(nperm):
        ws = [list(w) for w in words]
        for cell in cells.values():
            vals = [words[i][k] for i, k in cell]; rng.shuffle(vals)
            for (i, k), v in zip(cell, vals):
                ws[i][k] = v
        nulls.append(mi(pairs_of(ws)))
    return {"I": I, "null": float(np.mean(nulls)), "null_sd": float(np.std(nulls, ddof=1)), "excess": I - float(np.mean(nulls)),
            "pairs": len(pairs_of(words)), "types": len(words)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, _, locked = P.E.voynich_lines()
    vt = [w for l in lines for w in l if w]; N = len(vt)
    gflat = [w for l in gen_lines() for w in l]
    gens = {f"e032_gen{g}": gflat[g * N:(g + 1) * N] for g in range(10)}
    for d in sorted(E100W.iterdir()):
        gens["e100_" + d.name] = [w for ln in (d / "generate/generated_text.txt").read_text().splitlines()
                                  if ln.strip() and not ln.startswith("#") for w in ln.split()][:N]
    harm, nonh = HARM, NONH
    if a.smoke:
        nonh = NONH[:3]; gens = dict(list(gens.items())[:3])
    R = {"harmony": {}, "nonharmony": {}, "generator": {}}
    for grp, ids in (("harmony", harm), ("nonharmony", nonh)):
        for b in ids:
            c = P.cut(P.tok(b), N, rng)
            R[grp][b] = m = harmony(sorted(set(c)), is_vowel_latin, rng)
            log(f"{grp:10s} {b:10s} I {m['I']:.4f} null {m['null']:.4f} excess {m['excess']:+.4f} pairs {m['pairs']}")
    for k, t in gens.items():
        assert len(t) == N, k
        R["generator"][k] = m = harmony(sorted(set(t)), lambda ch: ch in EVA_V, rng)
        log(f"generator  {k:24s} I {m['I']:.4f} null {m['null']:.4f} excess {m['excess']:+.4f}")
    hmin = min(v["excess"] for v in R["harmony"].values()); nmax = max(v["excess"] for v in R["nonharmony"].values())
    gmax = max(v["excess"] for v in R["generator"].values())
    valid = hmin > nmax
    log(f"harmony min {hmin:+.4f} | non-harmony max {nmax:+.4f} | generator max {gmax:+.4f} | VALID {valid}")
    res = {"experiment": "E105", "seed": SEED, "N": N, "results": R, "harmony_min": hmin, "nonharmony_max": nmax,
           "generator_max": gmax, "valid": bool(valid), "locked_test_excluded": locked}
    if not a.smoke:
        V = harmony(sorted(set(vt)), lambda ch: ch in EVA_V, rng)
        V4 = harmony(sorted(set(vt)), lambda ch: ch in set("oaye"), rng)
        e = V["excess"]
        verdict = lambda x: "HARMONY-LIKE" if (x >= hmin and x > gmax) else ("NO HARMONY" if x <= nmax else "BETWEEN")
        v = verdict(e) if valid else "VOID"
        if valid and min(abs(e - b) for b in (hmin, gmax, nmax)) < 0.5 * V["null_sd"]:
            reps = [verdict(harmony(sorted(set(vt)), lambda ch: ch in EVA_V, random.Random(SEED + 100 + s))["excess"]) for s in range(10)]
            res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "BETWEEN"
        fM = 1 / 3 if v == "HARMONY-LIKE" else 1.0
        res.update(voynich=V, voynich_oaye=V4, verdict=v, factor_M=fM)
        log(f"VOYNICH (o,a,y) I {V['I']:.4f} null {V['null']:.4f} excess {e:+.4f} (sd {V['null_sd']:.4f}) | (o,a,y,e) excess {V4['excess']:+.4f}")
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e105_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
