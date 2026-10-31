"""E101 (Arham, Reddit R2 follow-up): where are glued words? (A) line ends, (B) the bathing section. See reports/E101_PREREG.md.

GLUED token: length >= 4, its word occurs <= 2 times (Part A: in the whole text; Part B: once in the subsample), and it
cuts into two pieces of >= 2 characters each occurring >= 2 times (single-glyph pieces such as y, s, d excluded).
Part A: lines of >= 3 words; D = glued rate of line-last tokens - glued rate of middle tokens. Controls are poured into the
Voynich line lengths. Known answers: in 10 generator stretches and 5 languages, with probability 0.15 per line, the last two
words are joined. Validity: planted generator D p10 > unplanted generator D max.
  SQUEEZE-LIKE  Voynich D >= planted-generator p10 and > unplanted-generator max
  NO SQUEEZE    Voynich D <= unplanted-generator p90
  BETWEEN / VOID otherwise
Part B: lines labelled H, S, B (controls inherit the label of the Voynich line they are poured into). Per section, rate =
share of its tokens (length >= 4) that are GLUED (whole-text counts, as Part A), standardised to the text's own length mix
of such tokens (lengths 4..10, 10 = 10+). d = rate_B - mean(rate_H, rate_S); Z = d / sd, sd from 200 bootstraps of lines
within each section. Known answers: 10 generator stretches and 5 languages, with 15% of within-line spaces deleted in the
B-labelled lines only. Validity: planted generator Z > 2 in >= 8 of 10 and unplanted generator Z <= 2 in >= 8 of 10.
  B GLUES MORE  Voynich Z > 2;  B NOT SPECIAL  Voynich Z <= 2;  VOID if validity fails.
Neither part carries a Bayes factor (pre-registered). Rule 8 as in the prereg.
Run: caffeinate -ims .venv/bin/python experiments/e101_glue_where.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e099_phrase_repeats_v2 as P  # noqa: E402
from e011_twin_search import parse, locked_test_leaves  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED = 101101
OUT = ROOT / "experiments/results/e101.json"
PJ, ZT = 0.15, 2.0
PLANT = ["latVUC", "ita1885", "deu1912", "ces1613", "turytc"]
log = P.log


def glued(w, c, maxc):
    if len(w) < 4 or c[w] > maxc:
        return False
    return any(c.get(w[:i], 0) >= 2 and c.get(w[i:], 0) >= 2 for i in range(2, len(w) - 1))


def part_a(lines):
    c = Counter(w for l in lines for w in l)
    L3 = [l for l in lines if len(l) >= 3]
    last = [l[-1] for l in L3 if len(l[-1]) >= 4]
    mid = [w for l in L3 for w in l[1:-1] if len(w) >= 4]
    rl = float(np.mean([glued(w, c, 2) for w in last])); rm = float(np.mean([glued(w, c, 2) for w in mid]))
    return {"D": rl - rm, "last": rl, "mid": rm, "len_last": float(np.mean([len(l[-1]) for l in L3])),
            "len_mid": float(np.mean([len(w) for l in L3 for w in l[1:-1]]))}


def plant_a(lines, rng):
    out = []
    for l in lines:
        l = list(l)
        if len(l) >= 3 and rng.random() < PJ:
            l[-2] = l[-2] + l[-1]; l.pop()
        out.append(l)
    return out


def join_within(l, rng):
    cur = list(l[:1])
    for w in l[1:]:
        if rng.random() < PJ:
            cur[-1] += w
        else:
            cur.append(w)
    return cur


def part_b(lines, labels, rng, nboot=200):
    c = Counter(w for l in lines for w in l)
    sec = {x: [l for l, y in zip(lines, labels) if y == x] for x in "HSB"}
    mix = Counter(min(len(w), 10) for x in "HSB" for l in sec[x] for w in l if len(w) >= 4)
    tot = sum(mix.values()); ref = {k: v / tot for k, v in mix.items()}
    g = {x: [[(min(len(w), 10), glued(w, c, 2)) for w in l if len(w) >= 4] for l in sec[x]] for x in "HSB"}

    def rate(ls):
        byL = defaultdict(list)
        for l in ls:
            for L, v in l:
                byL[L].append(v)
        ok = {L: np.mean(v) for L, v in byL.items() if len(v) >= 5}
        return float(sum(ref[L] * ok[L] for L in ok) / sum(ref[L] for L in ok))
    r = {x: rate(g[x]) for x in "HSB"}
    d0 = r["B"] - (r["H"] + r["S"]) / 2
    bd = []
    for _ in range(nboot):
        rb = {x: rate([g[x][rng.randrange(len(g[x]))] for _ in g[x]]) for x in "HSB"}
        bd.append(rb["B"] - (rb["H"] + rb["S"]) / 2)
    sd = float(np.std(bd, ddof=1))
    return {"Z": d0 / sd, "gap": d0, "sd": sd, **{f"rate_{x}": v for x, v in r.items()}}


def voynich():
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L, sec = defaultdict(list), {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t.eva if t.is_clean else None)
            sec.setdefault((t.folio, t.line_no), str(t.illustration))
    order = sorted(L, key=lambda k: (int("".join(ch for ch in k[0] if ch.isdigit()) or 0), k))
    keep = [k for k in order if any(L[k])]
    return [[w for w in L[k] if w] for k in keep], [sec[k] for k in keep], sorted(locked)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    vl, vlab, locked = voynich()
    lens = [len(l) for l in vl]; N = sum(lens)
    log(f"Voynich lines {len(vl)} tokens {N} | H {sum(n for n, s in zip(lens, vlab) if s == 'H')} S {sum(n for n, s in zip(lens, vlab) if s == 'S')} B {sum(n for n, s in zip(lens, vlab) if s == 'B')}")
    gflat = [w for l in gen_lines() for w in l]
    gens = {f"gen{g}": gflat[g * N:(g + 1) * N] for g in range(10)}
    langs = {b: P.cut(P.tok(b), N, rng) for b in PLANT}
    if a.smoke:
        gens = dict(list(gens.items())[:2]); langs = dict(list(langs.items())[:2])
    R = {"A": {"gen": {}, "gen_planted": {}, "lang": {}, "lang_planted": {}},
         "B": {"gen": {}, "gen_planted": {}, "lang": {}, "lang_planted": {}}}
    for fam, d in (("gen", gens), ("lang", langs)):
        for k, t in d.items():
            lines = P.pour(t, lens)
            R["A"][fam][k] = part_a(lines); R["A"][fam + "_planted"][k] = part_a(plant_a(lines, rng))
            R["B"][fam][k] = part_b(lines, vlab, rng)
            pl = [join_within(l, rng) if s == "B" else l for l, s in zip(lines, vlab)]
            R["B"][fam + "_planted"][k] = part_b(pl, vlab, rng)
            log(f"{fam} {k:8s} A: D {R['A'][fam][k]['D']:+.4f} planted {R['A'][fam + '_planted'][k]['D']:+.4f} | "
                f"B: Z {R['B'][fam][k]['Z']:+.2f} planted {R['B'][fam + '_planted'][k]['Z']:+.2f}")
    uA = np.array([v["D"] for v in R["A"]["gen"].values()]); pA = np.array([v["D"] for v in R["A"]["gen_planted"].values()])
    A_p10, A_umax, A_u90 = float(np.percentile(pA, 10)), float(uA.max()), float(np.percentile(uA, 90))
    validA = A_p10 > A_umax
    zB_u = [v["Z"] for v in R["B"]["gen"].values()]; zB_p = [v["Z"] for v in R["B"]["gen_planted"].values()]
    need = 8 if not a.smoke else 1
    validB = sum(z > ZT for z in zB_p) >= need and sum(z <= ZT for z in zB_u) >= need
    log(f"A: planted-gen p10 {A_p10:+.4f} unplanted max {A_umax:+.4f} p90 {A_u90:+.4f} VALID {validA} | "
        f"B: planted-gen Z>2 {sum(z > ZT for z in zB_p)}/{len(zB_p)}, unplanted Z<=2 {sum(z <= ZT for z in zB_u)}/{len(zB_u)} VALID {validB}")
    res = {"experiment": "E101", "seed": SEED, "N": N, "results": R, "A_planted_p10": A_p10, "A_unplanted_max": A_umax,
           "A_unplanted_p90": A_u90, "validA": bool(validA), "validB": bool(validB), "locked_test_excluded": locked}
    if not a.smoke:
        VA = part_a(vl)
        boot = []
        for s in range(200):
            r2 = random.Random(SEED + 7 + s); boot.append(part_a([vl[r2.randrange(len(vl))] for _ in vl])["D"])
        VA["sd"] = float(np.std(boot, ddof=1))
        VA["by_section"] = {s: part_a([l for l, x in zip(vl, vlab) if x == s]) for s in "HSB"}

        def vA(x):
            if x >= A_p10 and x > A_umax:
                return "SQUEEZE-LIKE"
            if x <= A_u90:
                return "NO SQUEEZE"
            return "BETWEEN"
        va = vA(VA["D"]) if validA else "VOID"
        if validA and min(abs(VA["D"] - b) for b in (A_p10, A_umax, A_u90)) < 0.5 * VA["sd"]:
            reps = [vA(part_a([vl[r2.randrange(len(vl))] for _ in vl])["D"]) for r2 in (random.Random(SEED + 900 + s) for s in range(10))]
            VA["seed_check"] = reps
            if sum(r == va for r in reps) < 8:
                va = "BETWEEN"
        VB = part_b(vl, vlab, rng)
        vb = ("B GLUES MORE" if VB["Z"] > ZT else "B NOT SPECIAL") if validB else "VOID"
        if validB and abs(VB["Z"] - ZT) < 0.5:
            reps = []
            for s_ in range(10):
                r2 = random.Random(SEED + 500 + s_); ix = [r2.randrange(len(vl)) for _ in vl]
                reps.append(part_b([vl[i] for i in ix], [vlab[i] for i in ix], r2)["Z"] > ZT)
            VB["seed_check"] = reps
            if sum(r == (vb == "B GLUES MORE") for r in reps) < 8:
                vb = "B UNDECIDED"
        res.update(voynich_A=VA, verdict_A=va, voynich_B=VB, verdict_B=vb)
        log(f"VOYNICH A: last {VA['last']:.3f} mid {VA['mid']:.3f} D {VA['D']:+.4f} (sd {VA['sd']:.4f}) -> {va} | by section "
            + " ".join(f"{s} {v['D']:+.3f}" for s, v in VA["by_section"].items()))
        log(f"VOYNICH B: rates H {VB['rate_H']:.3f} S {VB['rate_S']:.3f} B {VB['rate_B']:.3f} gap {VB['gap']:+.3f} Z {VB['Z']:+.2f} -> {vb}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e101_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
