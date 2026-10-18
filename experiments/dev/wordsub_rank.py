"""Probe 6: rank-local proposals. Symbol i (cipher frequency rank r_i) proposes LM words with rank in
[r_i/f, r_i*f] (log window) with prob p_local; swaps pair symbols of similar rank."""
import sys, math, time
import numpy as np

def anneal_rank(sc, m0, S, K, rank_words, iters, rng, t0, t1=0.05, p_swap=0.4, f=2.0):
    """rank_words: LM word indices ordered by LM frequency (no boundary/UNK). Symbols 1..S-1 ordered by cipher freq."""
    cur = sc.reset(m0); best, bm = cur, sc.m.copy()
    used = np.zeros(K + 1, dtype=bool); used[sc.m[1:S]] = True
    nW = len(rank_words)
    ratio = (t1 / t0) ** (1 / iters); T = t0
    U = rng.random(iters); R2 = rng.random(iters); R3 = rng.random(iters)
    for it in range(iters):
        i = int(rng.integers(1, S))
        lo, hi = max(0, int(i / f) - 1), min(nW, int(i * f) + 2)
        if R2[it] < p_swap:
            lo_s, hi_s = max(1, int(i / f)), min(S, int(i * f) + 2)
            j = int(rng.integers(lo_s, hi_s))
            if i == j or sc.m[i] == sc.m[j]: T *= ratio; continue
            idx, vals = np.array([i, j]), np.array([sc.m[j], sc.m[i]])
        else:
            L = int(rank_words[int(lo + R3[it] * (hi - lo))])
            if used[L]: T *= ratio; continue
            idx, vals = np.array([i]), np.array([L])
        d, st = sc.propose(idx, vals)
        if d >= 0 or U[it] < math.exp(max(-700, d / T)):
            if len(idx) == 1:
                used[sc.m[i]] = False; used[vals[0]] = True
            sc.accept(st); cur += d
            if cur > best: best, bm = cur, sc.m.copy()
        T *= ratio
    return bm, best
