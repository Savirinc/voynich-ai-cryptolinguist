"""E044: are Voynich's spaces between SYLLABLES rather than words? Syllable-spaced writing (Vietnamese; Chinese as
characters and as toned pinyin) through E043's statistics plus vocabulary size. See reports/E044_PREREG.md.
Targets: Voynich Currier A and Currier B (raw EVA, as E043), separately. Windows of A's token count (8,806),
pseudo-lines from Voynich DEV line lengths, up to 10 windows (seed 44044). Statistics: SL, AS (E043 code), types.
z = (V - mean) / max(window sd, 2%|V|, 0.01). FITS(text, target) iff |z| <= 3 on SL, AS and types.
Run: caffeinate -ims .venv/bin/python experiments/e044_syllable_spacing.py
"""
from __future__ import annotations

import json, random, re, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e027_simple_syllables import bible_text  # noqa: E402
from e030_reduplication import tokens  # noqa: E402
from e043_line_recurrence import pseudo, stats, windows  # noqa: E402

SEED, Z_OK = 44044, 3.0
OUT = ROOT / "experiments/results/e044.json"
K = ["SL", "AS", "types"]


def hanzi():
    return re.findall(r"[一-鿿]", bible_text("cmn-cu89s"))


def st(lines, rng):
    s = stats(lines, rng); s["types"] = float(len(Counter(w for l in lines for w in l))); return s


def main():
    rng = random.Random(SEED)
    lines, cur, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines]
    lens = [len(l) for l in vl if l]
    VA = [l for l, c in zip(vl, cur) if l and c == "A"]; VB = [l for l, c in zip(vl, cur) if l and c == "B"]
    nA = sum(len(l) for l in VA)
    # B at A's size: 10 runs of consecutive B lines, averaged (types depend on size)
    bs = []
    for _ in range(10):
        s = rng.randrange(len(VB)); sel, k, i = [], 0, s
        while k < nA:
            sel.append(VB[i % len(VB)]); k += len(VB[i % len(VB)]); i += 1
        bs.append(st(sel, random.Random(SEED)))
    V = {"A": st(VA, random.Random(SEED)), "B": {k: float(np.mean([b[k] for b in bs])) for k in bs[0]}}
    print("Voynich", {t: {k: round(v[k], 2) for k in K} for t, v in V.items()}, flush=True)
    TEXTS = {"Vietnamese (syllables)": tokens("vie1934"), "Chinese characters": hanzi(),
             "Mandarin pinyin (toned syllables)": tokens("cmn-cu89s"),
             "Latin (word-spaced control)": tokens("latVUC"), "Indonesian (word-spaced, doubling)": tokens("indayt")}
    R = {}
    for name, w in TEXTS.items():
        W = windows(pseudo(w, lens, rng), nA, rng)
        G = [st(x, rng) for x in W]
        M = {k: float(np.mean([g[k] for g in G])) for k in K}
        sd = {k: float(np.std([g[k] for g in G], ddof=1)) for k in K}
        r = {"n_windows": len(G), "mean": M, "sd": sd, "fits": {}, "z": {}}
        for t in ("A", "B"):
            z = {k: round((V[t][k] - M[k]) / max(sd[k], 0.02 * abs(V[t][k]), 0.01), 2) for k in K}
            r["z"][t] = z; r["fits"][t] = all(abs(z[k]) <= Z_OK for k in K)
        R[name] = r
        print(f"{name:36s} SL {M['SL']:.2f} AS {M['AS']:.2f} types {M['types']:.0f} | z(A) " +
              " ".join(f"{k} {r['z']['A'][k]:+.1f}" for k in K) + f" fits A {r['fits']['A']} | fits B {r['fits']['B']}", flush=True)
    syl = ["Vietnamese (syllables)", "Chinese characters", "Mandarin pinyin (toned syllables)"]
    fit = [n for n in syl if R[n]["fits"]["A"] or R[n]["fits"]["B"]]
    as_ok = [n for n in syl if abs(R[n]["z"]["A"]["AS"]) <= Z_OK or abs(R[n]["z"]["B"]["AS"]) <= Z_OK]
    if fit:
        verdict, bf = "SYLLABLE SPACING FITS", {"SYLL-UNIT": 3.0}
    elif not as_ok:
        verdict, bf = "SYLLABLE TEXTS AVOID ADJACENCY TOO", {"SYLL-UNIT": 1 / 3}
    else:
        verdict, bf = "PARTIAL (adjacency fits, other features do not)", {}
    print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E044", "voynich": V, "texts": R, "verdict": verdict,
                               "bayes_factors": bf, "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
