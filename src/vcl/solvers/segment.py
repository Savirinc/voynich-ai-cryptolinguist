"""Unsupervised stem + suffix segmentation of word types (Stage B; dev probes in experiments/dev/seg_*.py).

Model (Goldwater-style): each word type = stem + suffix (suffix may be ''). Stems and suffixes are drawn from two
Dirichlet-multinomial lexicons (concentrations a_s, a_f) whose base distributions P0 are LEARNED per class: a glyph
unigram and a length distribution for stems, and separate ones for suffixes, re-estimated after every sweep from
the current lexicons. Annealed Gibbs sampling over each type's split point, starting from 'no type is split'.
Validated on synthetic stem+ending codes: split 99.5% correct when endings use their own glyphs (dev, 2026-10-19).
"""
from __future__ import annotations

import math
import random
from collections import Counter


def segment_types(types, max_suf=3, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, seed=0,
                  smooth=0.01) -> dict:
    """-> {type: split index b} (stem = w[:b], suffix = w[b:])."""
    rng = random.Random(seed)
    types = list(types)
    glyphs = sorted({g for w in types for g in w})

    def fit(lex):
        gc = Counter(g for x in lex for g in x); tot = sum(gc.values()) + smooth * len(glyphs)
        q = {g: math.log((gc[g] + smooth) / tot) for g in glyphs}
        lc = Counter(len(x) for x in lex); lt = sum(lc.values()) + smooth * 16
        ql = {L: math.log((lc[L] + smooth) / lt) for L in range(0, 16)}
        return lambda x: ql.get(len(x), -30.0) + sum(q[g] for g in x)

    split, st, sf = {}, Counter(), Counter()
    for w in types:
        split[w] = len(w); st[w] += 1; sf[""] += 1
    order = list(types)
    for sw in range(sweeps):
        P0s, P0f = fit([x for x in st if st[x] > 0]), fit([x for x in sf if sf[x] > 0])
        T = t0 * (t1 / t0) ** (sw / max(1, sweeps - 1))
        rng.shuffle(order)
        for w in order:
            b = split[w]; st[w[:b]] -= 1; sf[w[b:]] -= 1
            opts, lps = [], []
            for k in range(0, max_suf + 1):
                if len(w) - k < min_stem and k > 0:
                    break
                s, f = w[:len(w) - k], w[len(w) - k:]
                lp = math.log(st[s] + a_s * math.exp(P0s(s))) + math.log(sf[f] + a_f * math.exp(P0f(f)))
                opts.append(len(w) - k); lps.append(lp / T)
            mx = max(lps); ps = [math.exp(x - mx) for x in lps]; r = rng.random() * sum(ps)
            for o, p in zip(opts, ps):
                r -= p
                if r <= 0:
                    b = o; break
            split[w] = b; st[w[:b]] += 1; sf[w[b:]] += 1
    return split


def ending_features(tokens, split) -> dict:
    """Summary of a segmentation. SPLIT: share of tokens with a non-empty suffix. NSUF95: number of suffix types
    covering 95% of suffixed tokens. DIST: total-variation distance between the glyph distributions of the suffix
    lexicon and the stem lexicon (unique entries). PAR: share of word types whose stem occurs with >= 2 suffixes."""
    suf = [w[split[w]:] for w in tokens]
    sc = Counter(f for f in suf if f)
    n_s = sum(sc.values())
    acc, nsuf = 0, 0
    for _, c in sc.most_common():
        if acc >= 0.95 * n_s:
            break
        acc += c; nsuf += 1
    stems = {w[:b] for w, b in split.items()}; sufs = {w[b:] for w, b in split.items() if b < len(w)}
    gs, gf = Counter(g for x in stems for g in x), Counter(g for x in sufs for g in x)
    ts, tf = sum(gs.values()) or 1, sum(gf.values()) or 1
    dist = 0.5 * sum(abs(gs[g] / ts - gf[g] / tf) for g in set(gs) | set(gf)) if sufs else 0.0
    forms = Counter()
    seen = {}
    for w, b in split.items():
        seen.setdefault(w[:b], set()).add(w[b:])
    par = sum(len(seen[w[:b]]) >= 2 for w, b in split.items()) / max(1, len(split))
    return {"SPLIT": n_s / max(1, len(tokens)), "NSUF95": float(nsuf), "DIST": float(dist), "PAR": float(par)}
