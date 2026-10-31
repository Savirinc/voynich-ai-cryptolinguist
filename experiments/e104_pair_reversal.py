"""E104 (Arham, Reddit idea R13): do Voynich word pairs occur in both orders (AB and BA) more than in languages? See reports/E104_PREREG.md.

Pairs: adjacent within-line word pairs A B with A != B (Voynich lines are broken at unclean tokens). For each unordered
pair {A, B} with n = n_AB + n_BA >= 6: asym = |n_AB - n_BA| / n - E|2X - n| / n, X ~ Binomial(n, 1/2) (exact), i.e.
order preference beyond what a coin would give. ASYM = mean asym over such pairs (0 = order-free, > 0 = fixed order).
Every control is cut to 28,841 tokens and poured into the Voynich line lengths.
Groups: 69 meaningful texts (E099 set); 60 copy-generator stretches (E032 x 10, E100 grid x 50).
L band = meaningful ASYM [p10, p90]; G band = generator ASYM [p10, p90]. Validity: the bands do not overlap.
  LANGUAGE-LIKE   Voynich in L band, outside G band -> M x 1/3
  GENERATOR-LIKE  Voynich in G band, outside L band -> M x 3
  NEITHER / VOID                                   -> none
Rule 8: Voynich within 0.5 sd (200 line bootstraps) of a band edge -> 10 bootstraps, >= 8 agree, else NEITHER.
Unscored: REV = share of the pairs seen in both orders; number of pairs; the most reversible Voynich pairs.
Run: caffeinate -ims .venv/bin/python experiments/e104_pair_reversal.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter
from functools import lru_cache
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e099_phrase_repeats_v2 as P  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED = 104104
OUT = ROOT / "experiments/results/e104.json"
E100W = ROOT / "experiments/results/e100_work"
MINN = 6
log = P.log


@lru_cache(maxsize=None)
def e_sym(n):
    return sum(comb(n, x) * abs(2 * x - n) for x in range(n + 1)) / (2 ** n * n)


def measure(segs):
    c = Counter()
    for l in segs:
        for a, b in zip(l, l[1:]):
            if a != b:
                c[(a, b)] += 1
    seen, vals, rev, ex = set(), [], 0, []
    for (a, b), x in c.items():
        k = (a, b) if a < b else (b, a)
        if k in seen:
            continue
        seen.add(k)
        y = c.get((b, a), 0); n = x + y
        if n >= MINN:
            vals.append(abs(x - y) / n - e_sym(n)); rev += (x > 0 and y > 0); ex.append((min(x, y) / n, n, k))
    ex.sort(reverse=True)
    return {"ASYM": float(np.mean(vals)) if vals else float("nan"), "REV": rev / len(vals) if vals else float("nan"),
            "pairs": len(vals), "top_reversible": [(f"{k[0]} {k[1]}", n, round(r, 2)) for r, n, k in ex[:10]]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, _, locked = P.E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]; N = sum(lens)
    segs = []
    for l in lines:
        cur = []
        for w in l:
            if w:
                cur.append(w)
            else:
                if len(cur) > 1:
                    segs.append(cur)
                cur = []
        if len(cur) > 1:
            segs.append(cur)
    texts = {}
    for bid in sorted(d.name for d in P.BIB.iterdir() if d.is_dir() and d.name not in P.SKIP):
        texts["bible:" + bid] = P.tok(bid)
    for k, p in P.OTHER.items():
        texts["other:" + k] = P.clean_tokens(p)
    texts["other:latin_farming"] = P.farm_tokens()
    gflat = [w for l in gen_lines() for w in l]
    gens = {f"e032_gen{g}": gflat[g * N:(g + 1) * N] for g in range(10)}
    for d in sorted(E100W.iterdir()):
        gens["e100_" + d.name] = [w for ln in (d / "generate/generated_text.txt").read_text().splitlines()
                                  if ln.strip() and not ln.startswith("#") for w in ln.split()][:N]
    if a.smoke:
        texts = {k: v for k, v in texts.items() if k in ("bible:latVUC", "bible:eng-kjv", "other:culpeper", "bible:hboWLC")}
        gens = dict(list(gens.items())[:3])
    R = {"meaningful": {}, "generator": {}}
    for k, t in texts.items():
        c = P.cut(t, N, rng)
        if c is None:
            log(f"skip {k}"); continue
        R["meaningful"][k] = m = measure(P.pour(c, lens)); log(f"{k:28s} ASYM {m['ASYM']:.3f} REV {m['REV']:.3f} pairs {m['pairs']}")
    for k, t in gens.items():
        assert len(t) == N, k
        R["generator"][k] = m = measure(P.pour(t, lens)); log(f"{k:28s} ASYM {m['ASYM']:.3f} REV {m['REV']:.3f} pairs {m['pairs']}")
    le = np.array([v["ASYM"] for v in R["meaningful"].values()]); ge = np.array([v["ASYM"] for v in R["generator"].values()])
    Lb = (float(np.percentile(le, 10)), float(np.percentile(le, 90))); Gb = (float(np.percentile(ge, 10)), float(np.percentile(ge, 90)))
    valid = Lb[1] < Gb[0] or Gb[1] < Lb[0]
    log(f"L band {Lb[0]:.3f}..{Lb[1]:.3f} | G band {Gb[0]:.3f}..{Gb[1]:.3f} | VALID {valid}")
    res = {"experiment": "E104", "seed": SEED, "N": N, "results": R, "L_band": Lb, "G_band": Gb, "valid": bool(valid),
           "locked_test_excluded": locked}
    if not a.smoke:
        V = measure(segs)
        boot = []
        for s in range(200):
            r2 = random.Random(SEED + 7 + s); boot.append(measure([segs[r2.randrange(len(segs))] for _ in segs])["ASYM"])
        V["sd"] = float(np.std(boot, ddof=1))
        inL = lambda x: Lb[0] <= x <= Lb[1]; inG = lambda x: Gb[0] <= x <= Gb[1]

        def verdict(x):
            if inL(x) and not inG(x):
                return "LANGUAGE-LIKE"
            if inG(x) and not inL(x):
                return "GENERATOR-LIKE"
            return "NEITHER"
        v = verdict(V["ASYM"]) if valid else "VOID"
        if valid and min(abs(V["ASYM"] - b) for b in (*Lb, *Gb)) < 0.5 * V["sd"]:
            reps = [verdict(x) for x in boot[:10]]; res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "NEITHER"
        fM = {"LANGUAGE-LIKE": 1 / 3, "GENERATOR-LIKE": 3.0}.get(v, 1.0)
        res.update(voynich=V, verdict=v, factor_M=fM)
        log(f"VOYNICH ASYM {V['ASYM']:.3f} (sd {V['sd']:.3f}) REV {V['REV']:.3f} pairs {V['pairs']} top {V['top_reversible'][:5]}")
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e104_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
