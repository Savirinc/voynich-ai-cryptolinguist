"""Shared search engine: n-gram tables over a symbol stream + simulated annealing over symbol->letter maps.

Conventions
  * A symbol stream is an int array; id 0 is the word boundary (written space) and always maps to LM index 0.
    Cipher symbols are ids 1..S.
  * A key is an int array `m` of length S+1 with m[0] == 0 and m[i] in 1..K (LM letter indices).
  * Score of a key = sum over the stream's (padded) order-4 n-grams of log P under the LM. Because the stream
    is fixed, unique n-grams and their counts are precomputed once, so each evaluation is a vectorised gather.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .lm import ORDER, CharLM


class NgramTable:
    def __init__(self, seq: np.ndarray, pad: bool = True, order: int = ORDER):
        seq = np.asarray(seq, dtype=np.int64)
        if pad:
            seq = np.concatenate([np.zeros(order - 1, dtype=np.int64), seq])
        self.n_events = max(1, len(seq) - order + 1 if not pad else len(seq) - (order - 1))
        base = int(seq.max()) + 1 if len(seq) else 1
        n = len(seq)
        if n < order:
            seq = np.concatenate([seq, np.zeros(order - n, dtype=np.int64)])
            n = order
        g = np.zeros(n - order + 1, dtype=np.int64)
        for k in range(order):
            g = g * base + seq[k:n - order + 1 + k]
        u, cnt = np.unique(g, return_counts=True)
        cols = []
        for k in range(order):
            cols.append(u % base); u = u // base
        self.cols = cols[::-1]                      # c0..c3 arrays of symbol ids
        self.counts = cnt.astype(np.float64)
        self.order = order

    def score(self, m: np.ndarray, lm: CharLM) -> float:
        A = lm.A
        f = m[self.cols[0]]
        for c in self.cols[1:]:
            f = f * A + m[c]
        return float(np.dot(lm.flat[f].astype(np.float64), self.counts))

    def per_char(self, m, lm) -> float:
        return self.score(m, lm) / self.n_events


@dataclass
class SAResult:
    m: np.ndarray
    score: float
    per_char: float


def anneal(table: NgramTable, lm: CharLM, m0: np.ndarray, propose, iters: int, rng: np.random.Generator,
           t0: float = 1.0, t1: float = 0.02, extra=None) -> SAResult:
    """Simulated annealing on total log-prob (minus `extra(m)`, an optional penalty in nats).
    `propose(m, rng) -> m_new` must return a fresh array. Temperature decays geometrically from t0 to t1."""
    f = (lambda mm: table.score(mm, lm) - extra(mm)) if extra is not None else (lambda mm: table.score(mm, lm))
    m = m0.copy()
    cur = f(m)
    best_m, best = m.copy(), cur
    if iters <= 0:
        return SAResult(best_m, best, best / table.n_events)
    ratio = (t1 / t0) ** (1.0 / iters)
    T = t0
    rand = rng.random(iters)
    for it in range(iters):
        cand = propose(m, rng)
        s = f(cand)
        d = s - cur
        if d >= 0 or rand[it] < math.exp(d / T):
            m, cur = cand, s
            if cur > best:
                best, best_m = cur, m.copy()
        T *= ratio
    return SAResult(best_m, best, best / table.n_events)


def hill_climb_swaps(table: NgramTable, lm: CharLM, m: np.ndarray, free_letters: bool = True,
                     max_passes: int = 6) -> SAResult:
    """Deterministic polish: try every pairwise swap of assignments (and, for injective keys, every move of a
    symbol to an unused letter); accept improvements; repeat until no gain."""
    m = m.copy()
    S = len(m) - 1
    K = lm.A - 1
    cur = table.score(m, lm)
    for _ in range(max_passes):
        improved = False
        for i in range(1, S + 1):
            for j in range(i + 1, S + 1):
                if m[i] == m[j]:
                    continue
                c = m.copy(); c[i], c[j] = m[j], m[i]
                s = table.score(c, lm)
                if s > cur + 1e-6:
                    m, cur, improved = c, s, True
            if free_letters:
                used = set(m[1:].tolist())
                for L in range(1, K + 1):
                    if L in used:
                        continue
                    c = m.copy(); c[i] = L
                    s = table.score(c, lm)
                    if s > cur + 1e-6:
                        m, cur, improved = c, s, True
                        used = set(m[1:].tolist())
        if not improved:
            break
    return SAResult(m, cur, cur / table.n_events)


def freq_init(seq: np.ndarray, S: int, lm: CharLM, injective: bool = True) -> np.ndarray:
    """Initial key: cipher symbols ranked by frequency -> LM letters ranked by unigram probability."""
    cnt = np.bincount(seq, minlength=S + 1)[1:S + 1]
    order_sym = np.argsort(-cnt, kind="stable") + 1
    order_let = np.argsort(-lm.unigram[1:], kind="stable") + 1
    m = np.zeros(S + 1, dtype=np.int64)
    if injective and S <= len(order_let):
        m[order_sym] = order_let[:S]
    else:
        # many-to-one: assign proportionally to letter frequency (greedy fill)
        p = lm.unigram[order_let]; p = p / p.sum()
        tot = cnt.sum()
        acc = np.zeros(len(order_let))
        for s in order_sym:
            k = int(np.argmax(p * tot - acc))
            m[s] = order_let[k]; acc[k] += cnt[s - 1]
    return m


def unigram_penalty(seq: np.ndarray, S: int, lm: CharLM, weight: float = 1.0):
    """Penalty factory: weight * N * KL(decoded letter distribution || LM letter distribution).

    Many-to-one keys can collapse a text onto a few letters whose repetitions the n-gram LM likes ('nanana...');
    natural text must also match the language's letter frequencies, which this term enforces."""
    sym_counts = np.bincount(seq, minlength=S + 1)[1:].astype(float)
    N = sym_counts.sum()
    logp = np.log(np.maximum(lm.unigram, 1e-6))
    A = lm.A

    def pen(m: np.ndarray) -> float:
        q = np.bincount(m[1:], weights=sym_counts, minlength=A) / max(N, 1.0)
        nz = q > 0
        return weight * N * float((q[nz] * (np.log(q[nz]) - logp[nz])).sum())
    return pen


def unigram_kl(text: str, lm: CharLM) -> float:
    """KL(decoded letter distribution || LM letter distribution), nats; ~0.02-0.1 for real text."""
    ids = [lm.idx[c] for c in text if c != " " and c in lm.idx]
    if not ids:
        return 5.0
    q = np.bincount(ids, minlength=lm.A) / len(ids)
    nz = q > 0
    return float((q[nz] * (np.log(q[nz]) - np.log(np.maximum(lm.unigram[nz], 1e-6)))).sum())
