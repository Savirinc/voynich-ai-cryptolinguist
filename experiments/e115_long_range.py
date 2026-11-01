"""X115 (Arham, move 1; EXPLORATORY, unscored): how far does the link reach? See reports/LONG_RANGE.md.
Not pre-registered: both candidate yardsticks failed band separation in development (controls only), so the test was
not locked. The scored statistic below became MIDMI (glyph MI over 48..512 characters); DECAY is kept for reference.

E(d) = (word matches at distance d) / (matches expected if the block were shuffled) - 1, pooled over blocks, for
d in LAGS (in words, within a block only). Expected per block: sum n_w (n_w - 1) / (N (N - 1)) x pairs at lag d.
Voynich blocks: one per scribe, that scribe's DEV prose pages in page order (sizes 8,061 / 8,838 / 10,074 / 869 / 539 /
460). Every control is cut to 28,841 tokens and chopped into blocks of the same sizes.
DECAY = mean E over d 256..2048 / mean E over d 16..64 (how much of the short-range link survives at long range).
L band = meaningful DECAY [p10, p90]; G band = generator DECAY [p10, p90] (copy generator x 60, dice x 10).
Validity: the bands do not overlap.
  LANGUAGE-LIKE   Voynich in L band, outside G band -> M x 1/3
  GENERATOR-LIKE  Voynich in G band, outside L band -> M x 3
  NEITHER / VOID                                   -> none
Rule 8: Voynich within 0.5 sd (10 jackknife replicates, each dropping every 10th page from a different start) of a
band edge -> the 10 replicates must give the same verdict >= 8 times, else NEITHER.
Unscored: E(d) curves; glyph-level mutual information I(d) (Lin & Tegmark), shuffle-corrected, per group.
Run: caffeinate -ims .venv/bin/python experiments/e115_long_range.py [--smoke]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time
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

SEED = 115115
OUT = ROOT / "experiments/results/e115.json"
E100W = ROOT / "experiments/results/e100_work"
LAGS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
SHORT, LONG = (16, 32, 64), (256, 512, 1024, 2048)
CLAGS = [1, 2, 4, 8, 16, 32, 48, 64, 96, 128, 192, 256, 384, 512, 1024, 2048, 4096]
MID = (48, 64, 96, 128, 192, 256, 384, 512)   # characters; the scored range
N_SH = 3
DICE_SET = ("2d6", "page", (20, 60, 40))          # E114's best set on the Voynich
log = P.log


def curve(blocks):
    obs, exp = Counter(), Counter()
    for b in blocks:
        N = len(b)
        if N < 2:
            continue
        c = Counter(b); q = sum(v * (v - 1) for v in c.values()) / (N * (N - 1))
        for d in LAGS:
            if d < N:
                obs[d] += sum(1 for i in range(N - d) if b[i] == b[i + d]); exp[d] += q * (N - d)
    return {d: (obs[d] / exp[d] - 1 if exp[d] else float("nan")) for d in LAGS}


def decay(E):
    s, l = np.mean([E[d] for d in SHORT]), np.mean([E[d] for d in LONG])
    return float(l / s) if s > 0 else float("nan")


def glyph_mi(blocks, rng):
    """I(d) between characters d apart (spaces kept), minus the same on a character-shuffled copy"""
    def mi(s, d):
        a, b = s[:-d], s[d:]
        pa, pb, pab = Counter(a), Counter(b), Counter(zip(a, b)); n = len(a)
        return sum(v / n * math.log2(v * n / (pa[x] * pb[y])) for (x, y), v in pab.items())
    out = {}
    s = [ch for b in blocks for ch in " ".join(b) + " "]
    shs = []
    for _ in range(N_SH):
        sh = s[:]; rng.shuffle(sh); shs.append(sh)
    for d in CLAGS:
        out[d] = mi(s, d) - float(np.mean([mi(sh, d) for sh in shs]))
    return out


def chop(toks, sizes):
    out, i = [], 0
    for n in sizes:
        out.append(toks[i:i + n]); i += n
    return out


def measure(blocks, rng):
    E = curve(blocks); I = glyph_mi(blocks, rng)
    return {"MIDMI": float(np.mean([I[d] for d in MID])), "MI": I, "DECAY": decay(E), "E": E}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    pages, meta, locked = E93.voynich()
    hands = sorted({m["hand"] for m in meta}, key=lambda h: -sum(sum(map(len, p)) for p, m in zip(pages, meta) if m["hand"] == h))
    vblocks = [[w for p, m in zip(pages, meta) if m["hand"] == h for l in p for w in l] for h in hands]
    sizes = [len(b) for b in vblocks]; N = sum(sizes)
    log(f"Voynich blocks {dict(zip(hands, sizes))} N {N}")
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
    shape = [[len(l) for l in p] for p in pages]
    ms = D.masters(pages, DICE_SET[2])
    for s in range(1, 11):
        bk = D.book(DICE_SET, ms, shape, s)
        gens[f"dice_seed{s}"] = [w for p, m in zip(bk, meta) for h in [m["hand"]] for l in p for w in l]
    R = {"meaningful": {}, "generator": {}}
    for k, t in texts.items():
        c = P.cut(t, N, rng)
        if c is None:
            log(f"skip {k}"); continue
        R["meaningful"][k] = m = measure(chop(c, sizes), rng); log(f"{k:28s} MIDMI {1e4 * m['MIDMI']:.2f}e-4 | DECAY {m['DECAY']:.3f}")
    for k, t in gens.items():
        assert len(t) == N, (k, len(t))
        if k.startswith("dice"):          # dice books keep the Voynich's own scribe blocks
            bl = [[w for p, m in zip(D.book(DICE_SET, ms, shape, int(k[9:])), meta) if m["hand"] == h for l in p for w in l] for h in hands]
        else:
            bl = chop(t, sizes)
        R["generator"][k] = m = measure(bl, rng); log(f"{k:28s} MIDMI {1e4 * m['MIDMI']:.2f}e-4 | DECAY {m['DECAY']:.3f}")
    le = np.array([v["MIDMI"] for v in R["meaningful"].values()]); ge = np.array([v["MIDMI"] for v in R["generator"].values()])
    Lb = (float(np.nanpercentile(le, 10)), float(np.nanpercentile(le, 90))); Gb = (float(np.nanpercentile(ge, 10)), float(np.nanpercentile(ge, 90)))
    valid = Lb[1] < Gb[0] or Gb[1] < Lb[0]
    log(f"L band {Lb[0]:.3f}..{Lb[1]:.3f} | G band {Gb[0]:.3f}..{Gb[1]:.3f} | VALID {valid}")
    res = {"experiment": "E115", "seed": SEED, "N": N, "sizes": sizes, "results": R, "L_band": Lb, "G_band": Gb,
           "valid": bool(valid), "locked_test_excluded": locked}
    if not a.smoke:
        V = measure(vblocks, rng)
        reps = []
        for j in range(10):
            keep = [i for i in range(len(pages)) if i % 10 != j]
            bl = [[w for i in keep if meta[i]["hand"] == h for l in pages[i] for w in l] for h in hands]
            reps.append(float(np.mean([v for d, v in glyph_mi(bl, random.Random(SEED + j)).items() if d in MID])))
        V["sd"] = float(np.std(reps, ddof=1)) * math.sqrt(9)      # jackknife sd
        V["jackknife"] = reps
        inL = lambda x: Lb[0] <= x <= Lb[1]; inG = lambda x: Gb[0] <= x <= Gb[1]

        def verdict(x):
            if inL(x) and not inG(x):
                return "LANGUAGE-LIKE"
            if inG(x) and not inL(x):
                return "GENERATOR-LIKE"
            return "NEITHER"
        v = verdict(V["MIDMI"]) if valid else "VOID"
        if valid and min(abs(V["MIDMI"] - b) for b in (*Lb, *Gb)) < 0.5 * V["sd"]:
            rv = [verdict(x) for x in reps]; res["seed_check"] = rv
            if sum(r == v for r in rv) < 8:
                v = "NEITHER"
        fM = {"LANGUAGE-LIKE": 1 / 3, "GENERATOR-LIKE": 3.0}.get(v, 1.0)
        res.update(voynich=V, verdict=v, factor_M=fM)
        log(f"VOYNICH MIDMI {1e4 * V['MIDMI']:.2f}e-4 (sd {1e4 * V['sd']:.2f}e-4) | DECAY {V['DECAY']:.3f} | MI " + " ".join(f"{d}:{1e4 * V['MI'][d]:.1f}" for d in CLAGS))
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e115_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
