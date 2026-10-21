"""E037 (attack step 1): the grammatical shape of Voynich, key-free. A MEASUREMENT, not a ledger test.
See reports/E037_PREREG.md.

Texts: Voynich DEV (all, Currier A, Currier B; within-line pairs) and four references, the first E033 window of
Indonesian, Malay, Latin, Swahili (one sequence each).
Segmentation: E026's segmenter, settings fixed (SEG), run on each text's word types.

G1 stems and endings
   NSUF95                 endings covering 95% of suffixed tokens (E026)
   ENDS_PER_STEM          mean distinct endings per stem, stems with >= 10 tokens
   I_EXCESS               [I(ending; stem) - mean I after shuffling endings across tokens (5x)] / H(ending),
                          tokens whose stem has >= 5 tokens
G2 what gets doubled (adjacent exact repeats)
   DBL_RHO                Spearman rho over types with >= 5 tokens: log(count) vs doubling rate
                          (doubling rate = times the word is immediately followed by itself / count)
   DBL_SUFFIXED           share of doubled pairs whose word has a non-empty ending, / share of all tokens that do
   (Voynich only) DBL_LINE_FIRST  rate of doubling in a line's first pair / rate in its other pairs
G3 where neighbouring near-copies differ (adjacent pairs at edit distance 1)
   ENDZ                   share of adjacent near-copy pairs whose difference lies in the last 2 units of the longer
                          word, / the same share among adjacent near-copy pairs after shuffling (5x, line lengths kept)
   SAMESTEM               share of adjacent near-copy pairs with the same segmenter stem, / the same share shuffled
   (Voynich only) top 12 edits in adjacent near-copies (descriptive)
Run: caffeinate -ims .venv/bin/python experiments/e037_grammar_profile.py
"""
from __future__ import annotations

import json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e026_endings import SEG  # noqa: E402
from e030_reduplication import ed1, tokens  # noqa: E402
from e033_language_features import N  # noqa: E402
from e035_spelling_variation import windows  # noqa: E402
from vcl.solvers.segment import segment_types  # noqa: E402

SEED, SHUF = 37037, 5
REFS = {"Indonesian": "indayt", "Malay": "zlmKSZI", "Latin": "latVUC", "Swahili": "swhulb"}
OUT = ROOT / "experiments/results/e037.json"


def H(c):
    t = sum(c.values())
    return -sum(v / t * math.log2(v / t) for v in c.values() if v)


def mi(stems, ends):
    joint = Counter(zip(stems, ends))
    return H(Counter(stems)) + H(Counter(ends)) - H(joint)


def edit_info(a, b):
    """-> (position of the difference counted from the end of the longer word, (from, to))."""
    if len(a) == len(b):
        i = next(k for k in range(len(a)) if a[k] != b[k])
        return len(a) - 1 - i, (a[i], b[i])
    s, l = (a, b) if len(a) < len(b) else (b, a)
    i = next((k for k in range(len(s)) if s[k] != l[k]), len(s))
    return len(l) - 1 - i, ("" if l is b else l[i], l[i] if l is b else "")


def near_pairs(seqs):
    return [(a, b) for s in seqs for a, b in zip(s, s[1:]) if ed1(a, b)]


def g3_shares(pairs, stem):
    if not pairs:
        return float("nan"), float("nan")
    endz = np.mean([edit_info(a, b)[0] < 2 for a, b in pairs])
    same = np.mean([stem[a] == stem[b] for a, b in pairs])
    return float(endz), float(same)


def profile(seqs, rng, lines_known):
    toks = [w for s in seqs for w in s]
    wc = Counter(toks)
    split = segment_types(wc, seed=SEED, **SEG)
    stem = {w: w[:b] for w, b in split.items()}
    end = {w: w[b:] for w, b in split.items()}
    # G1
    suf = Counter(end[w] for w in toks if end[w])
    acc = nsuf = 0
    for _, c in suf.most_common():
        if acc >= 0.95 * sum(suf.values()):
            break
        acc += c; nsuf += 1
    stc = Counter(stem[w] for w in toks)
    by_stem = defaultdict(set)
    for w in wc:
        by_stem[stem[w]].add(end[w])
    eps = float(np.mean([len(by_stem[s]) for s, c in stc.items() if c >= 10]))
    keep = [w for w in toks if stc[stem[w]] >= 5]
    S, Eg = [stem[w] for w in keep], [end[w] for w in keep]
    i_obs = mi(S, Eg); i_sh = []
    for _ in range(SHUF):
        e2 = Eg[:]; rng.shuffle(e2); i_sh.append(mi(S, e2))
    i_exc = (i_obs - float(np.mean(i_sh))) / H(Counter(Eg))
    # G2
    dbl, pairs_n = Counter(), 0
    for s in seqs:
        for a, b in zip(s, s[1:]):
            pairs_n += 1
            if a == b:
                dbl[a] += 1
    types5 = [w for w, c in wc.items() if c >= 5]
    rho = float(spearmanr([math.log(wc[w]) for w in types5], [dbl[w] / wc[w] for w in types5])[0])
    nd = sum(dbl.values())
    dsuf = (sum(c for w, c in dbl.items() if end[w]) / nd) / (sum(1 for w in toks if end[w]) / len(toks)) if nd else float("nan")
    out = {"tokens": len(toks), "types": len(wc), "doubled_pairs": nd, "near_pairs": 0,
           "NSUF95": nsuf, "ENDS_PER_STEM": eps, "I_EXCESS": i_exc, "DBL_RHO": rho, "DBL_SUFFIXED": dsuf}
    if lines_known:
        first = [s[0] == s[1] for s in seqs if len(s) >= 2]
        rest = [a == b for s in seqs if len(s) >= 3 for a, b in zip(s[1:], s[2:])]
        out["DBL_LINE_FIRST"] = float(np.mean(first) / np.mean(rest)) if np.mean(rest) else float("nan")
        out["top_doubled"] = dbl.most_common(15)
    # G3
    adj = near_pairs(seqs)
    out["near_pairs"] = len(adj)
    e_adj, s_adj = g3_shares(adj, stem)
    flat, lens = toks[:], [len(s) for s in seqs]
    e_sh, s_sh = [], []
    for _ in range(SHUF):
        rng.shuffle(flat); sh, i = [], 0
        for L in lens:
            sh.append(flat[i:i + L]); i += L
        e, s_ = g3_shares(near_pairs(sh), stem); e_sh.append(e); s_sh.append(s_)
    out.update({"ENDZ_adj": e_adj, "ENDZ_shuf": float(np.mean(e_sh)), "ENDZ": e_adj / float(np.mean(e_sh)),
                "SAMESTEM_adj": s_adj, "SAMESTEM_shuf": float(np.mean(s_sh)), "SAMESTEM": s_adj / float(np.mean(s_sh))})
    if lines_known:
        out["top_edits"] = Counter("%s>%s" % edit_info(a, b)[1] for a, b in adj).most_common(12)
        out["top_endings"] = suf.most_common(15)
    return out


def main():
    lines, cur, dev_words, locked = E.voynich_lines()
    assert len(dev_words) == N
    clean = [[w for w in l if w] for l in lines]
    sets = {"Voynich DEV": [l for l in clean if l],
            "Voynich A": [l for l, c in zip(clean, cur) if l and c == "A"],
            "Voynich B": [l for l, c in zip(clean, cur) if l and c == "B"]}
    W = windows()
    for name, bid in REFS.items():
        s = W[bid][0]
        sets[name] = [tokens(bid)[s:s + N]]
    res = {}
    for name, seqs in sets.items():
        res[name] = profile(seqs, random.Random(SEED), name.startswith("Voynich"))
        r = res[name]
        print(f"{name:12s} " + " ".join(f"{k} {r[k]:.3g}" for k in
              ["tokens", "NSUF95", "ENDS_PER_STEM", "I_EXCESS", "DBL_RHO", "DBL_SUFFIXED", "ENDZ", "SAMESTEM"])
              + (f" DBL_LINE_FIRST {r['DBL_LINE_FIRST']:.3g}" if "DBL_LINE_FIRST" in r else ""), flush=True)
    for name in ("Voynich DEV",):
        print("top doubled", res[name]["top_doubled"]); print("top edits", res[name]["top_edits"])
        print("top endings", res[name]["top_endings"])
    OUT.write_text(json.dumps({"experiment": "E037", "seg": SEG, "seed": SEED, "results": res,
                               "locked_test_excluded": locked}, indent=1, default=str))


if __name__ == "__main__":
    main()
