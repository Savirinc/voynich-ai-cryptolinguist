"""Columnar transposition (+ unknown monoalphabetic glyph substitution) solver.

Mechanism assumed (train family 'columnar'): spaces are dropped, letters are written row-wise into a grid of
`ncols` columns, read out column by column in a secret column order, then each letter is written with a glyph.

Approach
  1. For each column count c (default 2..10) search the column order that maximises a substitution-invariant
     statistic of the un-transposed stream: plug-in mutual information between consecutive symbols (natural
     text has strongly dependent neighbours; a wrong order gives ~independent neighbours).
     c <= 7: exhaustive; c >= 8: simulated annealing over permutations.
  2. The best few (c, order) candidates are un-transposed and solved as monoalphabetic ciphers under the
     'nospace' LM variant; the decode with the best LM score wins.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

from .lm import CharLM
from .substitution import SolveResult, solve_mono, _gap


def untranspose_index(N: int, order: list[int] | np.ndarray) -> np.ndarray:
    """Index array idx such that plaintext = cipher[idx] for a columnar transposition with this column order."""
    c = len(order)
    nrows, extra = divmod(N, c)
    lens = np.array([nrows + (1 if k < extra else 0) for k in range(c)])
    start = np.zeros(c, dtype=np.int64)
    p = 0
    for k in order:
        start[k] = p; p += lens[k]
    t = np.arange(N)
    return start[t % c] + t // c


def transpose_index(N: int, order) -> np.ndarray:
    """Inverse of untranspose_index: cipher = plaintext[idx]."""
    u = untranspose_index(N, order)
    inv = np.empty(N, dtype=np.int64); inv[u] = np.arange(N)
    return inv


def bigram_mi(x: np.ndarray, S: int) -> float:
    pair = x[:-1] * (S + 1) + x[1:]
    c = np.bincount(pair, minlength=(S + 1) ** 2).astype(float)
    c = c[c > 0]
    n = len(x) - 1
    uni = np.bincount(x, minlength=S + 1).astype(float)
    hu = uni[uni > 0] / len(x)
    return float((c / n * np.log(c / n)).sum() - 2 * (hu * np.log(hu)).sum())


def search_orders(seq: np.ndarray, S: int, cols=range(2, 11), sa_iters: int = 15000, keep: int = 3,
                  sa_restarts: int = 4,
                  seed: int = 0) -> list[tuple[float, int, list[int]]]:
    """Return the top (mi, ncols, order) candidates across column counts."""
    rng = np.random.default_rng(seed)
    N = len(seq)
    out = []
    for c in cols:
        if c >= N // 2:
            continue
        cand = []
        if c <= 7:
            for perm in itertools.permutations(range(c)):
                cand.append((bigram_mi(seq[untranspose_index(N, perm)], S), list(perm)))
            cand.sort(key=lambda x: -x[0])
            cand = cand[:keep]
        else:
            for _ in range(sa_restarts):
                order = [int(x) for x in rng.permutation(c)]
                cur = bigram_mi(seq[untranspose_index(N, order)], S)
                best = (cur, list(order))
                T, t1 = 0.05, 0.0005
                ratio = (t1 / T) ** (1 / sa_iters)
                for _ in range(sa_iters):
                    o2 = list(order)
                    i, j = rng.integers(0, c, size=2)
                    if rng.random() < 0.5:
                        o2[i], o2[j] = o2[j], o2[i]
                    else:
                        g = o2.pop(i); o2.insert(j, g)
                    v = bigram_mi(seq[untranspose_index(N, o2)], S)
                    if v >= cur or rng.random() < math.exp((v - cur) / T):
                        order, cur = o2, v
                        if cur > best[0]:
                            best = (cur, list(order))
                    T *= ratio
                cand.append(best)
        for mi, o in cand:
            out.append((mi, c, o))
    out.sort(key=lambda x: -x[0])
    return out[:keep * 2]


def _stream_score(ids: np.ndarray, lm: CharLM) -> float:
    A = lm.A
    f = ids[:-3] * A ** 3 + ids[1:-2] * A ** 2 + ids[2:-1] * A + ids[3:]
    return float(lm.flat[f].astype(np.float64).sum())


def refine_order(letters: np.ndarray, m: np.ndarray, order: list[int], lm: CharLM, passes: int = 4) -> list[int]:
    """Hill-climb the column order (swaps + single-column moves) under the LM with the substitution key fixed."""
    N = len(letters)
    mapped = m[letters]
    cur = _stream_score(mapped[untranspose_index(N, order)], lm)
    c = len(order)
    for _ in range(passes):
        improved = False
        for i in range(c):
            for j in range(c):
                if i == j:
                    continue
                o2 = list(order)
                if i < j:
                    o2[i], o2[j] = o2[j], o2[i]
                else:
                    g = o2.pop(i); o2.insert(j, g)
                v = _stream_score(mapped[untranspose_index(N, o2)], lm)
                if v > cur + 1e-6:
                    order, cur, improved = o2, v, True
        if not improved:
            break
    return order


def solve_columnar(seq: np.ndarray, S: int, lm_nospace: CharLM, n_candidates: int = 3, mono_iters: int = 20000,
                   mono_restarts: int = 6, seed: int = 0, cands=None) -> SolveResult:
    letters = seq[seq > 0]
    N = len(letters)
    if cands is None:
        cands = search_orders(letters, S, seed=seed)
    best = None
    for mi, c, order in cands[:n_candidates]:
        plain_ids = letters[untranspose_index(N, order)]
        r = solve_mono(plain_ids, S, lm_nospace, iters=mono_iters, restarts=mono_restarts, seed=seed)
        for _ in range(2):   # alternate: order under LM with key fixed, then re-solve the key
            m = np.array(r.key["map"])
            o2 = refine_order(letters, m, list(order), lm_nospace)
            if o2 == list(order):
                break
            order = o2
            r2 = solve_mono(letters[untranspose_index(N, order)], S, lm_nospace, iters=mono_iters // 2,
                            restarts=1, seed=seed + 1)
            if r2.per_char > r.per_char:
                r = r2
        r.info = {"ncols": c, "order": [int(x) for x in order], "mi": mi}
        if best is None or r.per_char > best.per_char:
            best = r
    best.solver = "columnar"
    best.text = best.text.replace(" ", "")
    best.gap = _gap(best.per_char, lm_nospace, N)
    return best
