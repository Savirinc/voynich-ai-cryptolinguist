"""E116 (Arham, move 2): do repeated phrases appear once the five spelling families are merged? See reports/E116_PREREG.md.

Merge MU (EVA): drop a word-initial q; drop every d; l -> r; k -> t; any run of e -> e. A word left empty becomes "_".
MU is applied to the Voynich and to every EVA control (copy generator: E032 x 10, E100 grid x 50; dice books: E114's
best set x 10). Meaningful texts (E099's 69) are used as written. Statistic: E100's Q3 = (RP3 + 1) / (shuffle RP3 + 1),
in the Voynich line shape, 28,841 tokens. Matching: types within +-15% of the MERGED Voynich's types.
Validity: |G*| >= 10, |L*| >= 8, L* Q3 p10 > G* Q3 max.
  PHRASES APPEAR  merged Voynich Q3 >= L* p10 and > G* max -> M x 1/3
  NO PHRASES      merged Voynich Q3 <= G* max and < L* min -> M x 3
  BETWEEN / VOID                                           -> none
Rule 8: if Q3 is within 0.5 shuffle-sd of a boundary, 10 fresh shuffle seeds must agree (>= 8), else BETWEEN.
Unscored: power check (matched meaningful texts with five planted free spelling variants, unmerged: how far do raw
repeated triples RP3 fall?);
RP4; each merge step alone on the Voynich.
Run: caffeinate -ims .venv/bin/python experiments/e116_merged_phrases.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, re, sys, time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e093_explanation_model as E93  # noqa: E402
import e099_phrase_repeats_v2 as P  # noqa: E402
import e114_dice_generator as D  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED = 116116
OUT = ROOT / "experiments/results/e116.json"
E100W = ROOT / "experiments/results/e100_work"
BAND = 0.15
DICE_SET = ("2d6", "page", (20, 60, 40))
STEPS = {"q": lambda w: w[1:] if w.startswith("q") else w, "d": lambda w: w.replace("d", ""),
         "l": lambda w: w.replace("l", "r"), "k": lambda w: w.replace("k", "t"), "e": lambda w: re.sub("e+", "e", w)}
log = P.log


def mu(w, steps=("q", "d", "l", "k", "e")):
    for s in steps:
        w = STEPS[s](w)
    return w or "_"


def plant_variants(toks, rng):
    """five free spelling variants, as the Voynich hypothesis says: two letter swaps, a doubled vowel, a dropped
    consonant, an optional first letter; each applied to each occurrence with probability 1/2"""
    lc = Counter(c for w in toks[:50000] for c in w)
    ranked = [c for c, _ in lc.most_common()]
    vow = [c for c in ranked if c in "aeiouyáéíóúàèìòùäöüœæ"]
    con = [c for c in ranked if c not in vow]
    a, b, c2, d2 = con[0], con[1], con[2], con[3]
    v, drop, pre = (vow[0] if vow else ranked[0]), con[4], con[5]

    def f(w):
        w = "".join((b if ch == a else a if ch == b else ch) if ch in (a, b) and rng.random() < .5 else ch for ch in w)
        w = "".join((d2 if ch == c2 else c2 if ch == d2 else ch) if ch in (c2, d2) and rng.random() < .5 else ch for ch in w)
        w = "".join(ch * 2 if ch == v and rng.random() < .5 else ch for ch in w)
        w = "".join(ch for ch in w if not (ch == drop and rng.random() < .5))
        return (pre + w if rng.random() < .5 else w) or "_"
    return [f(w) for w in toks]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, _, locked = P.E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]; N = sum(lens); vt = [w for l in vl for w in l]
    mt = [mu(w) for w in vt]
    vtypes = len(set(mt)); lo, hi = vtypes * (1 - BAND), vtypes * (1 + BAND)
    log(f"Voynich tokens {N} types {len(set(vt))} merged types {vtypes} | band {lo:.0f}-{hi:.0f}")
    texts = {}
    for bid in sorted(d.name for d in P.BIB.iterdir() if d.is_dir() and d.name not in P.SKIP):
        texts["bible:" + bid] = P.tok(bid)
    for k, p in P.OTHER.items():
        texts["other:" + k] = P.clean_tokens(p)
    texts["other:latin_farming"] = P.farm_tokens()
    gens = {}
    gflat = [w for l in gen_lines() for w in l]
    for g in range(10):
        gens[f"e032_gen{g}"] = gflat[g * N:(g + 1) * N]
    for d in sorted(E100W.iterdir()):
        gens["e100_" + d.name] = [w for ln in (d / "generate/generated_text.txt").read_text().splitlines()
                                  if ln.strip() and not ln.startswith("#") for w in ln.split()][:N]
    pages, _, _ = E93.voynich()
    ms = D.masters(pages, DICE_SET[2]); shape = [[len(l) for l in p] for p in pages]
    for s in range(1, 11):
        gens[f"dice_seed{s}"] = [w for p in D.book(DICE_SET, ms, shape, s) for l in p for w in l]
    if a.smoke:
        texts = {k: v for k, v in texts.items() if k in ("bible:hrv", "bible:slk", "bible:eng-kjv", "bible:latVUC", "other:culpeper")}
        gens = {k: v for i, (k, v) in enumerate(gens.items()) if i % 7 == 0}
    R = {"meaningful": {}, "generator": {}, "power": {}}
    for k, t in texts.items():
        c = P.cut(t, N, rng)
        if c is None:
            log(f"skip {k}"); continue
        m = P.measure(c, lens, rng); m["types"] = len(set(c)); R["meaningful"][k] = m
        line = f"{k:26s} types {m['types']:6d} Q3 {m[3]['Q']:7.2f} RP3 {m[3]['RP']}"
        if lo <= m["types"] <= hi or a.smoke:
            pv = plant_variants(c, random.Random(SEED + len(R["power"])))
            pm = P.measure(pv, lens, rng); pm["types"] = len(set(pv)); R["power"][k] = pm
            line += f" | with 5 planted variants: types {pm['types']} Q3 {pm[3]['Q']:.2f} RP3 {pm[3]['RP']}"
        log(line)
    for k, t in gens.items():
        assert len(t) == N, (k, len(t))
        g = [mu(w) for w in t]
        m = P.measure(g, lens, rng); m["types"] = len(set(g)); m["types_raw"] = len(set(t)); R["generator"][k] = m
        log(f"{k:26s} types {m['types_raw']:6d} -> merged {m['types']:6d} Q3 {m[3]['Q']:7.2f} RP4 {m[4]['RP']}")
    inb = lambda d: {k: v for k, v in d.items() if lo <= v["types"] <= hi}
    Ls, Gs = inb(R["meaningful"]), inb(R["generator"])
    lq = np.array([v[3]["Q"] for v in Ls.values()]); gq = np.array([v[3]["Q"] for v in Gs.values()])
    p10 = float(np.percentile(lq, 10)) if len(lq) else float("nan")
    lmin = float(lq.min()) if len(lq) else float("nan"); gmax = float(gq.max()) if len(gq) else float("nan")
    valid = len(Gs) >= 10 and len(Ls) >= 8 and p10 > gmax
    log(f"matched: L* {len(Ls)} {sorted(Ls)} | G* {len(Gs)} | L* p10 {p10:.3f} min {lmin:.3f} | G* max {gmax:.3f} | VALID {valid}")
    res = {"experiment": "E116", "seed": SEED, "N": N, "voynich_merged_types": vtypes, "band": [lo, hi], "results": R,
           "L_star": sorted(Ls), "G_star": sorted(Gs), "p10": p10, "L_min": lmin, "G_max": gmax, "valid": bool(valid),
           "locked_test_excluded": locked}
    if not a.smoke:
        V = P.measure(mt, lens, rng); res["voynich"] = V
        q, sd = V[3]["Q"], V[3]["Q_sd"]
        log(f"VOYNICH merged Q3 {q:.3f} (RP3 {V[3]['RP']}, shuffle {V[3]['shuffle_mean']:.1f}) RP4 {V[4]['RP']}")

        def verdict(q):
            if q >= p10 and q > gmax:
                return "PHRASES APPEAR"
            if q <= gmax and q < lmin:
                return "NO PHRASES"
            return "BETWEEN"
        v = verdict(q) if valid else "VOID"
        if valid and min(abs(q - b) for b in (p10, gmax, lmin)) < 0.5 * sd:
            reps = [verdict(P.measure(mt, lens, random.Random(SEED + 100 + s))[3]["Q"]) for s in range(10)]
            res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "BETWEEN"
        fM = {"PHRASES APPEAR": 1 / 3, "NO PHRASES": 3.0}.get(v, 1.0)
        res.update(verdict=v, factor_M=fM)
        log(f"VERDICT {v} | M x {fM:.3g}")
        steps = {}
        for s in STEPS:
            x = [mu(w, (s,)) for w in vt]; m = P.measure(x, lens, rng)
            steps[s] = {"types": len(set(x)), "Q3": m[3]["Q"], "RP3": m[3]["RP"], "RP4": m[4]["RP"]}
        res["steps_alone"] = steps; log(f"steps alone {steps}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e116_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
