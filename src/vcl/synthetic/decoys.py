"""Nonlinguistic decoy generators, matched to real ciphertext statistics where possible.

The correct output for every decoy is "no underlying language" (abstain). They include the
two best-known mechanical hypotheses for Voynichese, so a solver that 'deciphers' them has
a false-discovery problem:
  * autocopy  - Timm & Schinner (2020) self-citation: copy an earlier word and mutate it.
  * grille    - Rugg (2004)-style table + grille: prefix/midfix/suffix columns combined.
  * markov    - order-2 symbol Markov chain fitted to a REAL ciphertext and resampled
                (matches local glyph statistics, destroys lexical/syntactic structure).
  * zipf_bag  - i.i.d. words from a Zipfian lexicon of random glyph spellings (word unigram only).
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict

from .encoders import GLYPHS
from .schema import BOUNDARY


def _word_from(rng, inv, lo=2, hi=8):
    return [rng.choice(inv) for _ in range(rng.randint(lo, hi))]


def autocopy(n_symbols, rng, **_):
    inv = rng.sample(GLYPHS, rng.randint(18, 26))
    words = [_word_from(rng, inv) for _ in range(12)]
    out_words = []
    while sum(len(w) + 1 for w in out_words) < n_symbols:
        src = list(rng.choice((out_words or words)[-40:]))
        for _ in range(rng.choice([0, 1, 1, 2])):
            op = rng.random()
            i = rng.randrange(len(src))
            if op < .5:
                src[i] = rng.choice(inv)
            elif op < .75 and len(src) < 10:
                src.insert(i, rng.choice(inv))
            elif len(src) > 2:
                src.pop(i)
        out_words.append(src)
    return _join(out_words), {"inventory": inv}


def grille(n_symbols, rng, **_):
    inv = rng.sample(GLYPHS, rng.randint(18, 26))
    cols = [[_word_from(rng, inv, 1, 3) for _ in range(rng.randint(6, 14))] for _ in range(3)]
    for c in cols:
        c.append([])  # empty cell allowed
    out_words = []
    while sum(len(w) + 1 for w in out_words) < n_symbols:
        w = sum((rng.choice(c) for c in cols), [])
        if w:
            out_words.append(w)
    return _join(out_words), {"inventory": inv}


def markov(n_symbols, rng, source_symbols=None, order=2, **_):
    seq = source_symbols
    trans = defaultdict(Counter)
    for i in range(order, len(seq)):
        trans[tuple(seq[i - order:i])][seq[i]] += 1
    state = tuple(seq[:order]); out = list(state)
    while len(out) < n_symbols:
        c = trans.get(state)
        if not c:
            state = tuple(seq[:order]); continue
        nxt = rng.choices(list(c), weights=list(c.values()))[0]
        out.append(nxt); state = tuple(out[-order:])
    return out, {"order": order}


def zipf_bag(n_symbols, rng, **_):
    inv = rng.sample(GLYPHS, rng.randint(18, 26))
    lex = [_word_from(rng, inv) for _ in range(600)]
    w = [1 / (r + 1) for r in range(len(lex))]
    out_words = []
    while sum(len(x) + 1 for x in out_words) < n_symbols:
        out_words.append(rng.choices(lex, weights=w)[0])
    return _join(out_words), {"lexicon_size": len(lex)}


def _join(words):
    out = []
    for i, w in enumerate(words):
        if i:
            out.append(BOUNDARY)
        out.extend(w)
    return out


DECOYS = {f.__name__: f for f in [autocopy, grille, markov, zipf_bag]}
