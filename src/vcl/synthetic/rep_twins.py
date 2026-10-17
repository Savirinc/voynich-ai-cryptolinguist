"""Repetition mechanisms (E014) layered on the E013 edge-aware twins.

  * nulls: with probability p_null before each word, insert a one-glyph filler word drawn from the Voynich DEV
    one-glyph words that are NOT Naibbe unigram glyphs ('s', 'l', 'r', 'o', 'd', ... -- 'y' excluded), so a decoder
    can drop them (decode returns '?' for them; tested).
  * ditto: with probability p_rep a word is written twice (the second copy is a null by convention).
  * memory (Naibbe only): when a plaintext unit was enciphered within the last `mem_window` units, its previous spelling
    is reused with probability p_reuse instead of a fresh table draw (still exactly decodable).

Meaningless families get nulls and ditto; memory has no analogue there (their words carry no units).
"""
from __future__ import annotations

import random
from collections import Counter

from vcl.synthetic import edge_twins as X
from vcl.synthetic import naibbe_exact as NX
from vcl.synthetic import twins as T

REP_BOUNDS = dict(p_null=(0.0, 0.08), p_rep=(0.0, 0.03), p_reuse=(0.0, 0.9), mem_window=(1, 60))
REP_OFF = dict(p_null=0.0, p_rep=0.0, p_reuse=0.0, mem_window=1)
FAMILIES = ["naibbe_rep", "rugg_rep", "self_citation_rep"]
EDGE_FAMILY = {"naibbe_rep": "naibbe_edge", "rugg_rep": "rugg_edge", "self_citation_rep": "self_citation_edge"}
IS_LANGUAGE = {"naibbe_rep": True, "rugg_rep": False, "self_citation_rep": False}


def null_pool(dev_words) -> dict:
    uni = {g for (s, _, _), g in NX.load_tables().items() if s == "unigram"}
    c = Counter(w for w in dev_words if len(w) == 1 and w not in uni)
    return dict(c)


def naibbe_tokens(plain, C, beta, k, seed, p_reuse=0.0, mem_window=1):
    """E013 sandhi encoder plus spelling memory. beta=0, k=1, p_reuse=0 equals naibbe_exact.encode_tokens."""
    key = NX.key({}, 0, plain)
    tab, uni = key["tables"], key["unigrams"]
    rng = random.Random(seed)
    text = "".join(c for c in NX.clean(plain) if c in key["letters"])
    grams = NX._respace(text, rng)
    deck, di = [], 0

    def draw():
        nonlocal deck, di
        if di >= len(deck):
            deck = [t for t, n in NX.CARD_WEIGHTS.items() for _ in range(n)]
            rng.shuffle(deck); di = 0
        di += 1
        return deck[di - 1]

    def one(g):
        if len(g) == 1:
            return tab[("unigram", draw(), g)]
        while True:
            w = tab[("prefix", draw(), g[0])] + tab[("suffix", draw(), g[1])]
            if w not in uni:
                return w

    words, prev, last = [], None, {}
    for i, g in enumerate(grams):
        if p_reuse > 0 and g in last and i - last[g][0] <= mem_window and rng.random() < p_reuse:
            w = last[g][1]
        else:
            w = X._pick([one(g) for _ in range(max(1, k))], prev, C, beta, rng)
        words.append(w); prev = w; last[g] = (i, w)
    return words, grams


def add_nulls_ditto(words, nulls: dict, p_null, p_rep, rng):
    if p_null == 0 and p_rep == 0:
        return list(words)
    ks, ws = list(nulls), list(nulls.values())
    out = []
    for w in words:
        if p_null and rng.random() < p_null:
            out.append(rng.choices(ks, ws)[0])
        out.append(w)
        if p_rep and rng.random() < p_rep:
            out.append(w)
    return out


def bounds(family):
    b = {**X.bounds(EDGE_FAMILY[family]), **REP_BOUNDS}
    if family != "naibbe_rep":
        b = {k: v for k, v in b.items() if k not in ("p_reuse", "mem_window")}
    return b


def defaults(family):
    d = {**X.defaults(EDGE_FAMILY[family]), **REP_OFF}
    return {k: v for k, v in d.items() if k in bounds(family)}


def _clip(family, params):
    out = {}
    for k_, (lo, hi) in bounds(family).items():
        v = min(hi, max(lo, params.get(k_, defaults(family)[k_])))
        out[k_] = int(round(v)) if isinstance(lo, int) and isinstance(hi, int) else float(v)
    return out


def random_params(family, rng):
    return _clip(family, {k_: (rng.randint(lo, hi) if isinstance(lo, int) and isinstance(hi, int)
                               else rng.uniform(lo, hi)) for k_, (lo, hi) in bounds(family).items()})


def perturb_params(family, params, rng, scale=0.15, n_changes=2):
    q = dict(params)
    for k_ in rng.sample(list(bounds(family)), min(n_changes, len(bounds(family)))):
        lo, hi = bounds(family)[k_]
        if isinstance(lo, int) and isinstance(hi, int):
            s = max(1, int(round((hi - lo) * scale))); q[k_] += rng.randint(-s, s)
        else:
            q[k_] += rng.gauss(0, (hi - lo) * scale)
    return _clip(family, q)


def generate(family, params, seed, pools, n_words, C, nulls, plain=None, width_mean=49.7, width_sd=9.0):
    p = {**defaults(family), **params}
    rng = random.Random(seed ^ 0x5E9)
    if family == "naibbe_rep":
        words, _ = naibbe_tokens(plain, C, p["beta"], p["k"], seed, p["p_reuse"], p["mem_window"])
        words = add_nulls_ditto(words[:n_words], nulls, p["p_null"], p["p_rep"], rng)
        words = X.respace(words, C, p["p_split"], p["p_merge"], p["beta_s"], rng)
        lines = T.wrap_lines(words, rng, width_mean, width_sd)
    elif family == "rugg_rep":
        base = {k_: p[k_] for k_ in T.FAMILIES["rugg_grille"].bounds}
        words, _ = X.rugg_sandhi(n_words, base, seed, pools, C, p["beta"], p["k"])
        words = add_nulls_ditto(words, nulls, p["p_null"], p["p_rep"], rng)
        words = X.respace(words, C, p["p_split"], p["p_merge"], p["beta_s"], rng)
        lines = T.wrap_lines(words, rng, width_mean, width_sd)
    else:
        base = {k_: p[k_] for k_ in T.FAMILIES["self_citation"].bounds}
        lines, _ = X.self_citation_sandhi(n_words, base, seed, pools, C, p["beta"], p["k"], width_mean, width_sd)
        lines = [X.respace(add_nulls_ditto(l, nulls, p["p_null"], p["p_rep"], rng), C, p["p_split"], p["p_merge"],
                           p["beta_s"], rng) for l in lines]
    lines = X.line_end_m(lines, p["p_m"], rng)
    return {"lines": lines, "is_language": IS_LANGUAGE[family]}
