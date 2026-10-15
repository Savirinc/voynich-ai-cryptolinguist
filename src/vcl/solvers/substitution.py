"""Substitution-family solvers: monoalphabetic, homophonic (many-to-one) and null-padded monoalphabetic.

All work on an int symbol stream (0 = word boundary, 1..S = cipher symbols; see engine.py) and a CharLM.
Each returns a SolveResult with the decoded text, its per-character log-prob and the key.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import numpy as np

from .engine import NgramTable, SAResult, anneal, freq_init, hill_climb_swaps, unigram_penalty
from .lm import CharLM

BOUNDARY = " "
T0_FACTOR = 0.03       # initial SA temperature per symbol (nats); swept on self-generated tune-book tasks only


@dataclass
class SolveResult:
    solver: str
    lang: str
    text: str
    per_char: float                 # mean log-prob (nats) per scored event under lm
    gap: float                      # xent(decode) - typical xent of the LM (lower is better)
    key: dict = field(default_factory=dict)
    info: dict = field(default_factory=dict)


def encode_symbols(symbols: list[str]) -> tuple[np.ndarray, list[str]]:
    """Map a list of cipher symbols to ids (BOUNDARY -> 0, others 1..S by first appearance)."""
    inv: dict[str, int] = {}
    ids = np.empty(len(symbols), dtype=np.int64)
    names = [BOUNDARY]
    for i, s in enumerate(symbols):
        if s == BOUNDARY:
            ids[i] = 0
        else:
            j = inv.get(s)
            if j is None:
                j = inv[s] = len(names); names.append(s)
            ids[i] = j
    return ids, names


def decode_map(seq: np.ndarray, m: np.ndarray, lm: CharLM) -> str:
    alpha = np.array(lm.alphabet)
    return "".join(alpha[m[seq]])


def _gap(per_char: float, lm: CharLM, n: int) -> float:
    return -per_char - lm.typical_H(n)


def _propose_injective(K: int):
    def prop(m, rng):
        c = m.copy()
        S = len(m) - 1
        i = rng.integers(1, S + 1)
        L = rng.integers(1, K + 1)
        if L == c[i]:
            return c
        j = np.nonzero(c[1:] == L)[0]
        if len(j):
            c[j[0] + 1] = c[i]
        c[i] = L
        return c
    return prop


def _propose_free(K: int, p_letters: np.ndarray):
    cum = np.cumsum(p_letters)

    def prop(m, rng):
        c = m.copy()
        S = len(m) - 1
        if rng.random() < 0.3:
            i, j = rng.integers(1, S + 1, size=2)
            c[i], c[j] = c[j], c[i]
        else:
            i = rng.integers(1, S + 1)
            c[i] = 1 + int(np.searchsorted(cum, rng.random() * cum[-1]))
        return c
    return prop


def solve_mono(seq: np.ndarray, S: int, lm: CharLM, iters: int = 20000, restarts: int = 6, seed: int = 0,
               polish: bool = True) -> SolveResult:
    """Monoalphabetic substitution: SA over injective symbol->letter keys, then a swap hill-climb polish.
    If the cipher has more symbol types than the LM has letters, falls back to a many-to-one key."""
    K = lm.A - 1
    if S > K:
        return solve_homophonic(seq, S, lm, iters=iters, restarts=restarts, seed=seed)
    tab = NgramTable(seq)
    rng = np.random.default_rng(seed)
    best = None
    n = len(seq)
    t0 = max(1.0, T0_FACTOR * n)
    for r in range(restarts):
        m0 = freq_init(seq, S, lm)
        if r:  # perturb
            for _ in range(r * 3):
                m0 = _propose_injective(K)(m0, rng)
        res = anneal(tab, lm, m0, _propose_injective(K), iters, rng, t0=t0, t1=0.05)
        if best is None or res.score > best.score:
            best = res
    if polish:
        best = hill_climb_swaps(tab, lm, best.m, free_letters=True, max_passes=3)
    text = decode_map(seq, best.m, lm)
    return SolveResult("mono", lm.lang, text, best.per_char, _gap(best.per_char, lm, n),
                       key={"map": best.m.tolist()})


def solve_homophonic(seq: np.ndarray, S: int, lm: CharLM, iters: int = 15000, restarts: int = 3,
                     seed: int = 0) -> SolveResult:
    """Homophonic substitution: many-to-one SA (each cipher symbol -> any letter)."""
    K = lm.A - 1
    tab = NgramTable(seq)
    rng = np.random.default_rng(seed)
    n = len(seq)
    t0 = max(1.0, T0_FACTOR * n)
    p = lm.unigram[1:] ** 0.5
    prop = _propose_free(K, p / p.sum())
    pen = unigram_penalty(seq, S, lm)
    best = None
    for r in range(restarts):
        m0 = freq_init(seq, S, lm, injective=False)
        if r:
            for _ in range(r * 4):
                m0 = prop(m0, rng)
        res = anneal(tab, lm, m0, prop, iters, rng, t0=t0, t1=0.05, extra=pen)
        if best is None or res.score > best.score:
            best = res
    best = SAResult(best.m, tab.score(best.m, lm), tab.score(best.m, lm) / tab.n_events)
    text = decode_map(seq, best.m, lm)
    return SolveResult("homophonic", lm.lang, text, best.per_char, _gap(best.per_char, lm, n),
                       key={"map": best.m.tolist()})


def null_candidates(seq: np.ndarray, S: int) -> list[int]:
    """Rank cipher symbols by how null-like they are.

    Nulls in the train 'nulls' mechanism are inserted *after* a letter, so a null is (almost) never word-initial
    and its predecessor distribution is close to the overall letter distribution (it attaches to any letter).
    Score = word-initial rate (lower = more null-like) + KL(predecessor dist || unigram)."""
    cnt = np.bincount(seq, minlength=S + 1).astype(float)
    letters = cnt[1:].sum()
    uni = (cnt[1:] + 0.5) / (letters + 0.5 * S)
    prev = np.concatenate([[0], seq[:-1]])
    out = []
    for s in range(1, S + 1):
        pos = np.nonzero(seq == s)[0]
        if len(pos) < 3:
            continue
        init = np.mean(prev[pos] == 0)
        pd = np.bincount(prev[pos], minlength=S + 1)[1:].astype(float) + 0.5
        pd /= pd.sum()
        kl = float(np.sum(pd * np.log(pd / uni)))
        out.append((init * 5 + kl, s))
    out.sort()
    return [s for _, s in out]


def null_order(seq: np.ndarray, S: int) -> list[int]:
    """Null candidates, most null-like first: symbols that are never word-initial (likely_nulls with a 1% frequency
    floor) ordered by predecessor-KL, followed by all other symbols in null_candidates order."""
    ranked = null_candidates(seq, S)
    ln = set(likely_nulls(seq, S, min_freq=0.01))
    return [c for c in ranked if c in ln] + [c for c in ranked if c not in ln]


def remove_symbols(seq: np.ndarray, drop: set[int]) -> np.ndarray:
    keep = ~np.isin(seq, list(drop))
    return seq[keep]


def relabel(seq: np.ndarray) -> tuple[np.ndarray, int]:
    """Compact symbol ids to 1..S' (boundary stays 0)."""
    u = np.unique(seq[seq > 0])
    lut = np.zeros(int(seq.max()) + 1 if len(seq) else 1, dtype=np.int64)
    lut[u] = np.arange(1, len(u) + 1)
    return lut[seq], len(u)


def likely_nulls(seq: np.ndarray, S: int, max_init: float = 0.01, min_freq: float = 0.02) -> list[int]:
    """Language-independent null guess: frequent symbols (>= min_freq of letters) that are (almost) never
    word-initial, ordered by frequency."""
    prev = np.concatenate([[0], seq[:-1]])
    n = max(1, int((seq > 0).sum()))
    out = []
    for s in range(1, S + 1):
        pos = np.nonzero(seq == s)[0]
        if len(pos) >= 3 and np.mean(prev[pos] == 0) < max_init and len(pos) / n >= min_freq:
            out.append((-len(pos), s))
    return [s for _, s in sorted(out)]


def estimate_n_nulls(seq: np.ndarray, S: int) -> int:
    return max(1, len(likely_nulls(seq, S)))


def solve_nulls(seq: np.ndarray, S: int, lm: CharLM, iters: int = 4000, restarts: int = 2, seed: int = 0,
                max_nulls: int = 6, ks=None) -> SolveResult:
    """Null-padded monoalphabetic: rank null candidates, try removing the top-k (k in `ks`, default 1..max_nulls),
    solve mono on each reduced stream, keep the best LM gap."""
    cands = null_order(seq, S)
    K = lm.A - 1
    best = None
    for k in (ks or range(1, max_nulls + 1)):
        drop = set(cands[:k])
        red = remove_symbols(seq, drop)
        red, S2 = relabel(red)
        if S2 > K or len(red) < 20:
            continue
        r = solve_mono(red, S2, lm, iters=iters, restarts=restarts, seed=seed + k, polish=False)
        if best is None or r.gap < best.gap:
            best = r
            best.info = {"nulls_removed": k}
    if best is None:
        best = solve_mono(seq, S, lm, iters=iters, restarts=restarts, seed=seed)
        best.info = {"nulls_removed": 0}
    best.solver = "nulls"
    return best
