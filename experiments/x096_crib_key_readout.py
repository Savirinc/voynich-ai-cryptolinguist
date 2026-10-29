"""X096 (exploratory, unscored; Arham 2026-10-29): read passages with the best zodiac-crib keys.
For each language and section, the TRUE crib's partial key saved by E095b is completed on the whole section (same E047
annealer and settings, best mapping kept) and used to decode passages: one zodiac crib page (f71r), one herbal-A page
(f2r) and one B page (f76r). As a reference the same is done for wrong crib no. 0 (meanings shuffled), and for the
decoder with no crib at all. No claim rule: Arham judges whether a reading makes sense.
Run: caffeinate -ims .venv/bin/python experiments/x096_crib_key_readout.py
"""
from __future__ import annotations

import json, random, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import e095b_crib_fullbook as B  # noqa: E402
from e049_attack_voynich import voynich_seqs  # noqa: E402

SEED = 96096
PASSAGES = {"A": ["f71r", "f2r"], "B": ["f71r", "f76r"]}
NLINES = 8
OUT = ROOT / "experiments/results/x096.json"; MD = ROOT / "reports/CRIB_KEY_READOUT.md"


def complete_map(seq, lm, fixed, rs):
    """B.complete, but returning the best mapping as well as its score per sign"""
    sc = B.K.FullScorer(seq, lm)
    p = lm.unigram[1:] ** 0.5; p = p / p.sum(); cum = np.cumsum(p)
    free = [u for u in range(1, B.K.NSIGN + 1) if u not in fixed]
    m0 = B.freq_init(seq, B.K.NSIGN, lm, injective=False)
    for u, l in fixed.items():
        m0[u] = l
    best, bm = -1e18, m0.copy()
    for _ in range(B.R2):
        m = m0.copy(); cur = sc(m); T = max(1.0, 0.03 * len(seq)); ratio = (0.05 / T) ** (1.0 / B.IT2)
        for _ in range(B.IT2):
            c = m.copy()
            if rs.random() < 0.3 and len(free) > 1:
                i, j = rs.choice(free, 2, replace=False)
                if m[i] == m[j]:
                    T *= ratio; continue
                c[i], c[j] = m[j], m[i]
            else:
                i = free[int(rs.integers(len(free)))]; L = 1 + int(np.searchsorted(cum, rs.random() * cum[-1]))
                if L == m[i]:
                    T *= ratio; continue
                c[i] = L
            s = sc(c); d = s - cur
            if d >= 0 or rs.random() < np.exp(d / T):
                m, cur = c, s
                if cur > best:
                    best, bm = cur, m.copy()
            T *= ratio
    return best / max(1, int((seq > 0).sum())), bm


def page_lines(folio):
    signs, _ = B.K.voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    _, toks = B.parse(); locked = set(B.locked_test_leaves(toks))
    lines = {}
    for t in toks:
        if t.folio == folio and t.is_clean and t.leaf not in locked:
            lines.setdefault(t.line_no, []).append(t.eva)
    out = []
    for ln in sorted(lines)[:NLINES]:
        ws = [tuple(idx[x] for x in B.A24.segment(B.n1(w), B.A24.SEGS["S3"]) if x in idx) for w in lines[ln]]
        out.append((lines[ln], ws))
    return out


def decode(ws, m, lm):
    return " ".join("".join(lm.alphabet[m[u]] for u in w) or "·" for w in ws)


def main():
    rs = np.random.default_rng(SEED); rng = random.Random(SEED)
    E = json.loads((ROOT / "experiments/results/e095b.json").read_text())["results"]
    VA, _, _, _ = voynich_seqs("A"); VB, _, _, _ = voynich_seqs("B"); seqs = {"A": B.flat(VA), "B": B.flat(VB)}
    wrong = B.perms(1, rng)[0]
    pages = {f: page_lines(f) for f in {f for v in PASSAGES.values() for f in v}}
    res, md = {}, ["# X096: Voynich passages read with the zodiac-crib keys (exploratory, unscored)\n",
                   "Keys: E095b true-crib partial keys completed on the whole section. Reference rows: a wrong crib, and no crib.",
                   "Glyph units with no key letter are dropped; '·' marks a word left empty.\n"]
    for lang in B.LANGS:
        lm = B.K.SpaceLM(B.lm_words(lang), B.LANGS[lang][0]); lm.idx = {c: i for i, c in enumerate(lm.alphabet)}
        lm.LB = B.lm_bigram(lm, B.lm_words(lang)); tg = B.targets(lang, lm); cand = B.candidates(B.zodiac_seqs(), tg)
        for sec in ("A", "B"):
            cfg = f"{lang}/{sec}"; seq = seqs[sec]
            true_fixed = {int(u): l for u, l in (E[cfg]["true_key"] or {}).items()}
            C = B.bigram_tables(seq, lm)
            wk, _ = B.stage1(cand, wrong, random.Random(SEED), C, lm.LB)
            keys = {"true crib": true_fixed, "wrong crib": wk[0] if wk else {}, "no crib": {}}
            res[cfg] = {}
            md.append(f"\n## {lang}, Voynich {sec}\n")
            for name, fx in keys.items():
                s, m = complete_map(seq, lm, fx, rs)
                res[cfg][name] = {"score": s, "fixed": {str(k): int(v) for k, v in fx.items()}, "map": [int(x) for x in m],
                                  "passages": {}}
                md.append(f"**{name}** (whole-book score {s:+.3f} per sign; {len(fx)} signs fixed by the crib)\n")
                for f in PASSAGES[sec]:
                    dec = [decode(ws, m, lm) for _, ws in pages[f]]
                    res[cfg][name]["passages"][f] = dec
                    md.append(f"{f}:\n```\n" + "\n".join(dec) + "\n```")
            print(cfg, {k: round(v["score"], 3) for k, v in res[cfg].items()}, flush=True)
    md.insert(3, "\nVoynich lines (EVA) used:\n" + "\n".join(f"{f}:\n```\n" + "\n".join(" ".join(e) for e, _ in pages[f]) + "\n```"
                                                       for f in sorted(pages)))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False)); MD.write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
