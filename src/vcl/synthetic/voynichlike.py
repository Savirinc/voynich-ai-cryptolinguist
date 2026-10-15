"""Parametric mechanisms aimed at Voynich-like statistics (Milestone 3 curriculum extension).

Linguistic: `positional_verbose` encodes real plaintext; every letter becomes a 1-3 glyph code chosen from a
small inventory, with separate code tables for word-initial, medial and final positions (positional
allography + verbosity, both proposed for Voynichese in the literature). Exactly decodable given the key.
Nonlinguistic: `slot_grammar` emits words from prefix/core/suffix slots with Zipfian choices and no
underlying text (a probabilistic cousin of the Rugg grille).
Both are parameterised so their fingerprints can be fitted to a target, to test identifiability.
"""
from __future__ import annotations

import random

from .encoders import GLYPHS, _alphabet
from .schema import BOUNDARY


def positional_verbose(plain: str, rng: random.Random, n_glyphs: int = 18, p_two: float = 0.5, p_three: float = 0.1,
                       shared: float = 0.5, **_):
    inv = rng.sample(GLYPHS, n_glyphs)
    # positional sub-inventories overlap by `shared`, which controls how rigid glyph positions are
    k = max(4, int(n_glyphs * (1 - shared) / 2))
    init_pool = inv[:n_glyphs - k]
    final_pool = inv[k:]
    mid_pool = inv
    alpha = _alphabet(plain)

    def table(pool):
        used, t = set(), {}
        for c in alpha:
            for _ in range(200):
                r = rng.random()
                L = 3 if r < p_three else (2 if r < p_three + p_two else 1)
                code = tuple(rng.choice(pool) for _ in range(L))
                if code not in used:
                    used.add(code); t[c] = code; break
            else:
                t[c] = tuple(rng.choice(pool) for _ in range(4))
        return t
    tabs = {"i": table(init_pool), "m": table(mid_pool), "f": table(final_pool)}
    out = []
    for wi, w in enumerate(plain.split(" ")):
        if wi:
            out.append(BOUNDARY)
        for j, c in enumerate(w):
            pos = "i" if j == 0 else ("f" if j == len(w) - 1 else "m")
            out.extend(tabs[pos][c])
    key = {p: {c: "".join(v) for c, v in t.items()} for p, t in tabs.items()}
    return out, key, "equivalence_class", plain


def slot_grammar(n_symbols: int, rng: random.Random, n_glyphs: int = 20, n_prefix: int = 12, n_core: int = 25,
                 n_suffix: int = 15, zipf: float = 1.0, p_empty: float = 0.3, **_):
    inv = rng.sample(GLYPHS, n_glyphs)
    third = max(3, n_glyphs // 3)
    pools = [inv[:2 * third], inv, inv[third:]]

    def fragments(n, pool, lo, hi):
        return [[rng.choice(pool) for _ in range(rng.randint(lo, hi))] for _ in range(n)]
    slots = [fragments(n_prefix, pools[0], 1, 2), fragments(n_core, pools[1], 1, 3), fragments(n_suffix, pools[2], 1, 3)]
    weights = [[1 / (r + 1) ** zipf for r in range(len(s))] for s in slots]
    out = []
    while len(out) < n_symbols:
        w = []
        for si, (s, wt) in enumerate(zip(slots, weights)):
            if si != 1 and rng.random() < p_empty:
                continue
            w += rng.choices(s, weights=wt)[0]
        if out:
            out.append(BOUNDARY)
        out.extend(w)
    return out[:n_symbols], {"slots": len(slots)}
