"""E048: does word ORDER inside Voynich lines carry information, or does it look scrambled (a within-line
transposition)? See reports/E048_PREREG.md.

Words are reduced to classes for counting: the 300 commonest types of each text stay themselves, rarer types become
'<R:last character>'. I(adjacent) = plug-in mutual information (bits) between neighbouring classes within lines.
  D_int = I(observed) - mean I over 20 INTERIOR shuffles (words 2..L-1 of each line permuted; first and last kept)
Q = D_int(Voynich) / median D_int(real, unscrambled texts). Texts are cut into pseudo-lines from Voynich DEV line
lengths (generator: own lines) and measured on windows of Currier A's token count (8,806; up to 10; seed 48048).
Run: caffeinate -ims .venv/bin/python experiments/e048_word_order.py LL_DIR
"""
from __future__ import annotations

import json, math, random, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e030_reduplication import tokens as e030_tokens  # noqa: E402
from e042_language_shortlist import words as e042_words  # noqa: E402
from e043_line_recurrence import bible_books, gen_lines, ll_files, pseudo, windows  # noqa: E402

SEED, NSH, TOPN = 48048, 20, 300
OUT = ROOT / "experiments/results/e048.json"


def classes(lines):
    wc = Counter(w for l in lines for w in l)
    top = {w for w, _ in wc.most_common(TOPN)}
    return [[w if w in top else "<R:%s>" % w[-1] for w in l] for l in lines]


def mi(lines):
    pc = Counter((a, b) for l in lines for a, b in zip(l, l[1:]))
    n = sum(pc.values())
    if not n:
        return 0.0
    left, right = Counter(), Counter()
    for (a, b), c in pc.items():
        left[a] += c; right[b] += c
    return sum(c / n * math.log2(c * n / (left[a] * right[b])) for (a, b), c in pc.items())


def interior_shuffle(lines, rng):
    out = []
    for l in lines:
        if len(l) > 3:
            mid = l[1:-1]; rng.shuffle(mid); out.append([l[0]] + mid + [l[-1]])
        else:
            out.append(l)
    return out


def full_shuffle(lines, rng):
    out = []
    for l in lines:
        m = l[:]; rng.shuffle(m); out.append(m)
    return out


def d_int(lines, rng):
    c = classes(lines)
    obs = mi(c)
    sh = [mi(interior_shuffle(c, rng)) for _ in range(NSH)]
    return obs - float(np.mean(sh)), obs, float(np.std(sh))


def main():
    lld = sys.argv[1]
    rng = random.Random(SEED)
    lines, cur, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines]
    lens = [len(l) for l in vl if l]
    VA = [l for l, c in zip(vl, cur) if l and c == "A"]; VB = [l for l, c in zip(vl, cur) if l and c == "B"]
    nA = sum(len(l) for l in VA)
    V = {"A": d_int(VA, random.Random(SEED))}
    bs = []
    for _ in range(10):
        s = rng.randrange(len(VB)); sel, k, i = [], 0, s
        while k < nA:
            sel.append(VB[i % len(VB)]); k += len(VB[i % len(VB)]); i += 1
        bs.append(d_int(sel, random.Random(SEED)))
    V["B"] = tuple(float(np.mean([b[j] for b in bs])) for j in range(3))
    REAL = {
        "Hebrew Genesis-Exodus": [w for l in bible_books("hboWLC", ["GEN", "EXO"]) for w in l],
        "Hebrew Psalms": [w for l in bible_books("hboWLC", ["PSA"]) for w in l],
        "Latin Genesis-Exodus": [w for l in bible_books("latVUC", ["GEN", "EXO"]) for w in l],
        "Latin hymns": [w for l in ll_files(lld, ["hymni.txt", "ambrose/hymns.txt"] + [f"prudentius/prud{i}.txt" for i in range(1, 15)]) for w in l],
        "Apicius + Cato + Varro": [w for l in ll_files(lld, [f"apicius/apicius{i}.txt" for i in range(1, 6)] + ["cato/cato.agri.txt", "varro.rr1.txt", "varro.rr2.txt", "varro.rr3.txt"]) for w in l],
        "Turkish Bible": e042_words("turytc"),
        "Indonesian Bible": e030_tokens("indayt"),
    }
    R = {}
    for name, w in REAL.items():
        W = windows(pseudo(w, lens, rng), nA, rng)
        G = [d_int(x, rng) for x in W]
        S = [d_int(full_shuffle(x, rng), rng) for x in W[:3]]          # scrambled control from the same text
        R[name] = {"D_int": float(np.mean([g[0] for g in G])), "I_obs": float(np.mean([g[1] for g in G])),
                   "n_windows": len(G), "scrambled_D_int": float(np.mean([s[0] for s in S]))}
    G = [d_int(x, rng) for x in windows(gen_lines(), nA, rng)]
    gen = {"D_int": float(np.mean([g[0] for g in G])), "I_obs": float(np.mean([g[1] for g in G]))}
    med = float(np.median([r["D_int"] for r in R.values()]))
    Q = {t: V[t][0] / med for t in ("A", "B")}
    Qreal = {n: r["D_int"] / med for n, r in R.items()}
    Qscr = {n: r["scrambled_D_int"] / med for n, r in R.items()}
    valid = max(Qscr.values()) <= 0.2 and min(Qreal.values()) >= 0.5
    qa = Q["A"]
    if not valid:
        verdict, bf = "VOID (method does not separate real from scrambled order)", {}
    elif qa <= 0.2:
        verdict, bf = "ORDER LOOKS SCRAMBLED", {"ORDER-SCRAMBLED": 10.0}
    elif qa >= 0.5:
        verdict, bf = "ORDER INTACT", {"ORDER-SCRAMBLED": 0.1}
    else:
        verdict, bf = "PARTIAL ORDER", {}
    print(f"Voynich A: D_int {V['A'][0]:.4f} (I {V['A'][1]:.3f}, shuffle sd {V['A'][2]:.4f}) Q {Q['A']:.2f} | B (A-size): D_int {V['B'][0]:.4f} Q {Q['B']:.2f}")
    for n, r in R.items():
        print(f"  {n:24s} D_int {r['D_int']:.4f} Q {Qreal[n]:.2f} | scrambled copy Q {Qscr[n]:.2f}")
    print(f"  copy generator          D_int {gen['D_int']:.4f} Q {gen['D_int'] / med:.2f}")
    print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E048", "voynich": {t: list(V[t]) for t in V}, "Q": Q, "real": R,
                               "Q_real": Qreal, "Q_scrambled": Qscr, "generator": gen, "median_real_D_int": med,
                               "valid": valid, "verdict": verdict, "bayes_factors": bf,
                               "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
