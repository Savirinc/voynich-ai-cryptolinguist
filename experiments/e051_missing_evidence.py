"""E051: the missing-evidence audit, scored fairly for M and L. See reports/E051_PREREG.md.

Part 1 (scored)  C21 on FRESH references. AS = sum O / sum E (E045 exact formula) on pseudo-lines that follow Voynich
  DEV's line lengths. Meaningful: 30 eBible translations in languages never used before (drawn by seed 51051 from
  the 92 that qualify; list in scratchpad/e051_ids.txt, given as argument), 28,841 tokens after skipping 2,000.
  Meaningless: 10 fresh copy-generator samples (Timm & Schinner, shipped conf, seeds 11..20, own lines, 28,841 tokens).
  p_L = (k_L + 0.5) / (n_L + 1), p_M = (k_M + 0.5) / (n_M + 1), k = texts with AS >= 0.85. BF(M:L) = p_M / p_L.
Part 2 (descriptive, no factor) "dogs that did not bark":
  (a) zodiac labels (12 zodiac pages, DEV): share of label tokens whose word is also a label on ANOTHER zodiac page;
  (b) labels vs their own page: for DEV pages with labels and running text, share of label words (>= 3 glyphs) that
      occur in the same page's text, against the same share for frequency-matched random words (20 draws).
Run: caffeinate -ims .venv/bin/python experiments/e051_missing_evidence.py IDS_FILE GEN_DIR JAVA
"""
from __future__ import annotations

import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e032_copy_generator import generate  # noqa: E402
from e042_language_shortlist import words as bible_words  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED, N, THR = 51051, 28841, 0.85
OUT = ROOT / "experiments/results/e051.json"
ZODIAC = ["f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v"]


def OE(lines):
    o = sum(a == b for l in lines for a, b in zip(l, l[1:]))
    e = sum(sum(c * (c - 1) for c in Counter(l).values()) / len(l) for l in lines if len(l) >= 2)
    return o, e


def pseudo(words, lens):
    out, i, j = [], 0, 0
    while i < len(words):
        L = lens[j % len(lens)]; out.append(words[i:i + L]); i += L; j += 1
    return out


def bands(bf):
    if bf >= 10: return 10.0
    if bf >= 3: return 3.0
    if bf <= 0.1: return 0.1
    if bf <= 1 / 3: return 1 / 3
    return None


def main():
    ids = [l.strip() for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    gen_dir, java = Path(sys.argv[2]), sys.argv[3]
    lines, cur, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines]
    lens = [len(l) for l in vl if l]
    V = {}
    for t in ("A", "B"):
        o, e = OE([l for l, c in zip(vl, cur) if c == t and len(l) >= 2]); V[t] = o / e
    L, excluded = {}, []
    for b in ids:
        w = bible_words(b)[2000:2000 + N]
        if len(w) < N or np.mean([len(x) for x in w]) > 15:
            excluded.append(b); continue
        o, e = OE(pseudo(w, lens)); L[b] = o / e
    work = ROOT / "experiments/results/e051_work"
    G = {}
    for s in range(11, 21):
        gl = generate(gen_dir, java, s, N, work)
        o, e = OE(gl); G[f"seed{s}"] = o / e
    kL = sum(v >= THR for v in L.values()); kM = sum(v >= THR for v in G.values())
    pL = (kL + 0.5) / (len(L) + 1); pM = (kM + 0.5) / (len(G) + 1)
    bf = pM / pL; f = bands(bf)
    print(f"Voynich AS: A {V['A']:.2f}, B {V['B']:.2f}")
    print(f"meaningful (fresh, n={len(L)}): k(AS>=0.85)={kL}; median {np.median(list(L.values())):.2f}, max {max(L.values()):.2f}; excluded {excluded}")
    for b, v in sorted(L.items(), key=lambda x: -x[1])[:6]:
        print(f"   {b:10s} {v:.2f}")
    print(f"generator (fresh seeds, n={len(G)}): k={kM}; values {[round(v, 2) for v in G.values()]}")
    print(f"p_M {pM:.3f} p_L {pL:.3f} BF(M:L) {bf:.2f} -> factor on M: {f}")
    # Part 2
    _, toks = parse(); lk = set(locked_test_leaves(toks))
    T = [t for t in toks if t.leaf not in lk and t.is_clean]
    zl = defaultdict(list)
    for t in T:
        if t.folio in ZODIAC and t.mode == "label":
            zl[t.folio].append(t.eva)
    rep = []
    for f_, ws in zl.items():
        others = {w for g, x in zl.items() if g != f_ for w in x}
        rep += [w in others for w in ws]
    zod = {"label_tokens": len(rep), "share_also_on_other_zodiac_page": float(np.mean(rep)) if rep else None,
           "label_types": len({w for x in zl.values() for w in x})}
    pages_lab, pages_txt = defaultdict(list), defaultdict(Counter)
    for t in T:
        if t.mode == "label":
            pages_lab[t.folio].append(t.eva)
        else:
            pages_txt[t.folio][t.eva] += 1
    allc = Counter(w for c in pages_txt.values() for w, n in c.items() for _ in range(n))
    bycount = defaultdict(list)
    for w, c in allc.items():
        bycount[min(c, 50)].append(w)
    rng = random.Random(SEED)
    hit, base = [], []
    for f_, labs in pages_lab.items():
        if sum(pages_txt[f_].values()) < 20:
            continue
        for w in labs:
            if len(w) < 3:
                continue
            hit.append(w in pages_txt[f_])
            c = min(allc.get(w, 0), 50)
            pool = bycount.get(c) or bycount[1]
            base.append(float(np.mean([rng.choice(pool) in pages_txt[f_] for _ in range(20)])))
    lab = {"label_tokens": len(hit), "share_in_own_page_text": float(np.mean(hit)) if hit else None,
           "frequency_matched_expectation": float(np.mean(base)) if base else None}
    print("Part 2 (a) zodiac labels:", zod); print("Part 2 (b) labels in own page text:", lab)
    OUT.write_text(json.dumps({"experiment": "E051", "voynich_AS": V, "meaningful": L, "excluded": excluded,
                               "generator": G, "kL": kL, "kM": kM, "pL": pL, "pM": pM, "BF_M_L": bf,
                               "factor_M": f, "zodiac_labels": zod, "labels_own_page": lab,
                               "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
