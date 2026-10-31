"""E106 (Arham, Reddit idea R7): are paragraph-initial gallows decorative capitals? See reports/E106_PREREG.md.

PARA words: the first word of each DEV paragraph-start line (ZL para_start), clean, starting with a gallows t/k/p/f.
MID words: clean words starting with t/k/p/f that are neither line-first nor in a paragraph-start line.
REMAINDER = the word without its first glyph. KNOWN = the remainder occurs >= 2 times among all tokens that are not
paragraph-first words. R_para = KNOWN share of PARA words; R_mid = KNOWN share of MID words, standardised to the PARA
length mix (lengths 2..9, 9 = 9+). D = R_para - R_mid; sd from 200 bootstraps of PARA and MID words.
Known answer: 10 copy-generator stretches poured into the Voynich lines; in Voynich paragraph-start lines, with
probability 0.85 the first word gets a gallows prefixed (p/t/k/f in the Voynich paragraph proportions 280:146:68:26).
Validity: planted D > 2 sd in >= 9 of 10, and unplanted generator |D| / sd <= 2 in >= 8 of 10 (unplanted PARA words
are the generator's own gallows-initial paragraph-first words).
  DECORATIVE  Voynich D > 2 sd and D >= planted-generator D p10
  PARTLY      Voynich D > 2 sd but below planted p10
  INTEGRAL    Voynich D <= 2 sd
No Bayes factor. Unscored: commonest remainders vs commonest line-initial words of non-paragraph lines; per gallows.
Run: caffeinate -ims .venv/bin/python experiments/e106_gallows_capitals.py [--smoke]
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

SEED = 106106
OUT = ROOT / "experiments/results/e106.json"
GAL = "tkpf"
GW = {"p": 280, "t": 146, "k": 68, "f": 26}
PLANT_P = 0.85
log = P.log


def voynich():
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L = defaultdict(list)
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t)
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    lines = [[t.eva if (t.is_clean and t.eva) else None for t in L[k]] for k in order]
    para = [bool(L[k][0].para_start) for k in order]
    return lines, para, sorted(locked)


def measure(lines, para, rng, nboot=200):
    pf = [l[0] for l, p in zip(lines, para) if p and l and l[0]]
    pf_set_tokens = Counter(pf)
    allc = Counter(w for l in lines for w in l if w)
    other = allc - pf_set_tokens
    PARA = [w for w in pf if w[0] in GAL and len(w) >= 2]
    MID = [w for l, p in zip(lines, para) if not p for w in l[1:] if w and w[0] in GAL and len(w) >= 2]
    known = lambda w: other.get(w[1:], 0) >= 2
    Lk = lambda w: min(len(w), 9)
    mix = Counter(Lk(w) for w in PARA)

    def rates(pa, mi):
        rp = float(np.mean([known(w) for w in pa]))
        by = defaultdict(list)
        for w in mi:
            by[Lk(w)].append(known(w))
        ok = {k: np.mean(v) for k, v in by.items() if len(v) >= 5}
        wt = sum(mix[k] for k in ok)
        rm = float(sum(mix[k] * ok[k] for k in ok) / wt)
        return rp, rm
    rp, rm = rates(PARA, MID)
    bs = []
    for _ in range(nboot):
        a, b = rates([PARA[rng.randrange(len(PARA))] for _ in PARA], [MID[rng.randrange(len(MID))] for _ in MID])
        bs.append(a - b)
    sd = float(np.std(bs, ddof=1))
    rem = Counter(w[1:] for w in PARA if known(w))
    return {"R_para": rp, "R_mid": rm, "D": rp - rm, "sd": sd, "z": (rp - rm) / sd, "n_para": len(PARA), "n_mid": len(MID),
            "top_remainders": rem.most_common(12),
            "by_gallows": {g: float(np.mean([known(w) for w in PARA if w[0] == g])) if any(w[0] == g for w in PARA) else None for g in GAL}}


def plant(lines, para, rng):
    gs = [g for g, n in GW.items() for _ in range(n)]
    out = []
    for l, p in zip(lines, para):
        l = list(l)
        if p and l and l[0] and rng.random() < PLANT_P:
            l[0] = rng.choice(gs) + l[0]
        out.append(l)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    vl, para, locked = voynich()
    lens = [sum(1 for w in l if w) for l in vl]
    keep = [i for i, n in enumerate(lens) if n > 0]
    lens_k = [lens[i] for i in keep]; para_k = [para[i] for i in keep]; N = sum(lens_k)
    log(f"Voynich lines {len(keep)} paragraph-start lines {sum(para_k)} tokens {N}")
    gflat = [w for l in gen_lines() for w in l]
    G = {"unplanted": {}, "planted": {}}
    for g in range(2 if a.smoke else 10):
        lines = P.pour(gflat[g * N:(g + 1) * N], lens_k)
        G["unplanted"][g] = m0 = measure(lines, para_k, rng)
        G["planted"][g] = m1 = measure(plant(lines, para_k, rng), para_k, rng)
        log(f"gen{g}: unplanted D {m0['D']:+.3f} z {m0['z']:+.2f} (n {m0['n_para']}) | planted R_para {m1['R_para']:.3f} R_mid {m1['R_mid']:.3f} D {m1['D']:+.3f} z {m1['z']:+.2f}")
    pz = [m["z"] for m in G["planted"].values()]; uz = [m["z"] for m in G["unplanted"].values()]
    pD = [m["D"] for m in G["planted"].values()]
    need9, need8 = (9, 8) if not a.smoke else (1, 1)
    valid = sum(z > 2 for z in pz) >= need9 and sum(abs(z) <= 2 for z in uz) >= need8
    p10 = float(np.percentile(pD, 10))
    log(f"planted z>2 {sum(z > 2 for z in pz)}/{len(pz)} | unplanted |z|<=2 {sum(abs(z) <= 2 for z in uz)}/{len(uz)} | planted D p10 {p10:+.3f} | VALID {valid}")
    res = {"experiment": "E106", "seed": SEED, "generator": G, "planted_D_p10": p10, "valid": bool(valid), "locked_test_excluded": locked}
    if not a.smoke:
        V = measure(vl, para, rng)
        v = ("DECORATIVE" if V["D"] >= p10 else "PARTLY") if V["z"] > 2 else "INTEGRAL"
        v = v if valid else "VOID"
        # unscored: compare remainders with first words of ordinary lines
        lf = Counter(l[0] for l, p in zip(vl, para) if not p and l and l[0])
        V["top_line_first_nonpara"] = lf.most_common(12)
        res.update(voynich=V, verdict=v)
        log(f"VOYNICH R_para {V['R_para']:.3f} R_mid {V['R_mid']:.3f} D {V['D']:+.3f} z {V['z']:+.2f} (n {V['n_para']}, {V['n_mid']}) by gallows {V['by_gallows']}")
        log(f"  top remainders {V['top_remainders']}\n  top first words of other lines {V['top_line_first_nonpara']}")
        log(f"VERDICT {v} (no factor)")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e106_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
