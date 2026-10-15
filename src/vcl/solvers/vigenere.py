"""Periodic polyalphabetic (Vigenere-type over an unknown glyph alphabet) solver.

Mechanism assumed (train family 'vigenere'): plaintext letters (spaces kept and not counted) are shifted by a
periodic key s_j over the sample's sorted letter alphabet (size n), then written with an unknown glyph per letter.
So decode(glyph g at letter-position t) = alpha[(P[g] - s[t mod p]) mod n], where P: glyph -> Z_n is unknown.

Approach
  1. Period estimation: mean index of coincidence of the letter-only stream split into p columns, p = 1..12.
  2. The stream becomes an 'augmented' symbol stream (glyph, column) -> id, i.e. a structured homophonic cipher.
  3. Initialisation: beam search over the shift vector with the glyph order profiled out exactly by a Hungarian
     assignment against the LM unigram distribution (shift_beam).
  4. Simulated annealing over (P, shifts, alphabet choice) scored by the char LM, then coordinate-ascent polish;
     the alphabet is initialised to the n most frequent LM letters in code-point order and can swap letters in/out.
"""
from __future__ import annotations

import math

import numpy as np

from .engine import NgramTable
from .lm import CharLM
from .substitution import SolveResult, decode_map, _gap


def ioc(x: np.ndarray) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    c = np.bincount(x).astype(float)
    return float((c * (c - 1)).sum() / (n * (n - 1)))


def periodic_ioc(seq: np.ndarray, max_p: int = 12) -> dict[int, float]:
    """Mean IoC of the letter stream (boundaries removed) split into p interleaved columns."""
    letters = seq[seq > 0]
    return {p: float(np.mean([ioc(letters[j::p]) for j in range(p)])) for p in range(1, max_p + 1)}


def estimate_periods(seq: np.ndarray, max_p: int = 12, k: int = 3) -> list[int]:
    """Candidate periods, best first: smallest p whose periodic IoC is within 8% of the max, then others."""
    pi = periodic_ioc(seq, max_p)
    mx = max(pi.values())
    first = min(p for p, v in pi.items() if v >= 0.92 * mx)
    rest = sorted((p for p in pi if p != first), key=lambda p: -pi[p])
    return [first] + rest[:k - 1]


def shift_beam(seq_letters: np.ndarray, col: np.ndarray, n: int, p: int, logu: np.ndarray, beam: int = 12,
               refine_rounds: int = 3, top: int = 3):
    """Exact profile over the glyph order: for a shift vector s, the best glyph order P is a linear assignment
    (Hungarian) on W[g, pos] = sum_j C[j,g] log u[(pos - s_j) mod n]. Search s by beam search over columns
    (s_0 = 0 fixes the rotation symmetry), then coordinate ascent over each s_j. Returns up to `top` distinct
    (score, P, s) candidates, best first."""
    from scipy.optimize import linear_sum_assignment
    C = np.zeros((p, n))
    np.add.at(C, (col, seq_letters), 1.0)
    idx = (np.arange(n)[:, None] - np.arange(n)[None, :]) % n
    LU = logu[idx]                                                # [pos, shift]

    def solve(W):
        r, c = linear_sum_assignment(-W)
        return float(W[r, c].sum()), c                          # c[g] = position of glyph g

    states = [(0.0, [0], np.outer(C[0], LU[:, 0]))]               # W[g,pos] partial
    for j in range(1, p):
        cand = []
        for _, sv, W in states:
            for v in range(n):
                W2 = W + np.outer(C[j], LU[:, v])
                sc, _ = solve(W2)
                cand.append((sc, sv + [v], W2))
        cand.sort(key=lambda x: -x[0])
        states = cand[:beam]
    results = []
    for sc, sv, W in states[:max(top, 3)]:
        s_ = np.array(sv)
        cur, P = solve(sum(np.outer(C[j], LU[:, s_[j]]) for j in range(p)))
        for _ in range(refine_rounds):
            improved = False
            for j in range(1, p):
                base = sum(np.outer(C[i], LU[:, s_[i]]) for i in range(p) if i != j)
                for v in range(n):
                    if v == s_[j]:
                        continue
                    sc2, P2 = solve(base + np.outer(C[j], LU[:, v]))
                    if sc2 > cur + 1e-9:
                        cur, P, improved = sc2, P2, True
                        s_ = s_.copy(); s_[j] = v
            if not improved:
                break
        results.append((cur, np.asarray(P, dtype=np.int64), s_))
    results.sort(key=lambda x: -x[0])
    out, seen = [], set()
    for r in results:
        k = tuple(r[2])
        if k not in seen:
            seen.add(k); out.append(r)
    return out[:top]


def _polish(tab, lm, make_map, rb, n, p, n_alpha, rounds: int = 6):
    """Coordinate ascent: exhaustive shift per column, then all pairwise swaps of glyph positions."""
    cur, P, s, alpha, sel, out = rb
    P, s = P.copy(), s.copy()
    for _ in range(rounds):
        improved = False
        for j in range(p):
            for v in range(n_alpha):
                if v == s[j]:
                    continue
                s2 = s.copy(); s2[j] = v
                sc = tab.score(make_map(P, s2, alpha), lm)
                if sc > cur + 1e-6:
                    cur, s, improved = sc, s2, True
        for a in range(n):
            for b in range(a + 1, n):
                P2 = P.copy(); P2[a], P2[b] = P[b], P[a]
                sc = tab.score(make_map(P2, s, alpha), lm)
                if sc > cur + 1e-6:
                    cur, P, improved = sc, P2, True
        if not improved:
            break
    return (cur, P, s, alpha, sel, out)


def solve_vigenere(seq: np.ndarray, S: int, lm: CharLM, period: int | None = None, iters: int = 20000,
                   restarts: int = 3, seed: int = 0, beam: int = 12, n_periods: int = 1) -> SolveResult:
    """Solve a periodic shift cipher over an unknown glyph alphabet (see module docstring)."""
    periods = [period] if period else estimate_periods(seq, k=n_periods)
    best = None
    for p in periods[:n_periods] if not period else periods:
        r = _solve_period(seq, S, lm, p, iters, restarts, seed, beam)
        # BIC-style penalty: each shift is a free parameter worth log(n) nats; longer periods can always
        # emulate shorter ones, so without it multiples of the true period win by overfitting.
        r.info["penalised"] = r.per_char - p * math.log(max(S, 2)) / max(1, len(seq))
        if best is None or r.info["penalised"] > best.info["penalised"]:
            best = r
    return best


def _solve_period(seq, S, lm, p, iters, restarts, seed, beam) -> SolveResult:
    rng = np.random.default_rng(seed)
    n = S
    K = lm.A - 1
    is_letter = seq > 0
    col = np.zeros(len(seq), dtype=np.int64)
    col[is_letter] = np.arange(is_letter.sum()) % p
    glyph = seq - 1                                       # 0..n-1 for letters
    aug = np.where(is_letter, 1 + col * n + glyph, 0)
    tab = NgramTable(aug)
    g_of = np.concatenate([[0], np.tile(np.arange(n), p)])      # augmented id -> glyph
    c_of = np.concatenate([[0], np.repeat(np.arange(p), n)])    # augmented id -> column
    by_freq = list(np.argsort(-lm.unigram[1:]) + 1)             # LM letter ids by frequency
    n_alpha = min(n, K)

    def make_map(P, s, alpha):
        m = alpha[(P[g_of] - s[c_of]) % n_alpha]
        m[0] = 0
        return m

    def sorted_alpha(sel):
        return np.array(sorted(sel, key=lambda i: lm.alphabet[i]), dtype=np.int64)

    best = None
    n_ev = tab.n_events
    t0 = max(0.5, 0.002 * len(seq))
    sel0 = by_freq[:n_alpha]
    alpha0 = sorted_alpha(sel0)
    inits = []
    if n == n_alpha:
        u = lm.unigram[alpha0] + 1e-4
        inits = [(P, s_) for _, P, s_ in shift_beam(glyph[is_letter], col[is_letter], n, p, np.log(u / u.sum()),
                                                     beam=beam, top=restarts)]
    while len(inits) < restarts:
        inits.append((rng.permutation(n) % n_alpha, rng.integers(0, n_alpha, size=p)))
    for r in range(restarts):
        sel, out = list(sel0), list(by_freq[n_alpha:])
        alpha = alpha0.copy()
        P, s = inits[r]
        cur = tab.score(make_map(P, s, alpha), lm)
        T = t0
        ratio = (0.05 / t0) ** (1.0 / max(1, iters))
        rb = (cur, P.copy(), s.copy(), alpha.copy(), list(sel), list(out))
        rnd = rng.random(max(1, iters))
        for it in range(iters):
            u = rng.random()
            P2, s2, alpha2, sel2, out2 = P, s, alpha, sel, out
            if u < 0.55:
                a, b = rng.integers(0, n, size=2)
                P2 = P.copy(); P2[a], P2[b] = P[b], P[a]
            elif u < 0.95:
                j = rng.integers(0, p)
                s2 = s.copy(); s2[j] = (s[j] + (rng.integers(1, n_alpha))) % n_alpha
            elif out:
                i, o = rng.integers(0, len(sel)), rng.integers(0, len(out))
                sel2, out2 = list(sel), list(out)
                sel2[i], out2[o] = out[o], sel[i]
                alpha2 = sorted_alpha(sel2)
            else:
                continue
            sc = tab.score(make_map(P2, s2, alpha2), lm)
            d = sc - cur
            if d >= 0 or rnd[it] < math.exp(d / T):
                P, s, alpha, sel, out, cur = P2, s2, alpha2, sel2, out2, sc
                if cur > rb[0]:
                    rb = (cur, P.copy(), s.copy(), alpha.copy(), list(sel), list(out))
            T *= ratio
        rb = _polish(tab, lm, make_map, rb, n, p, n_alpha)
        if best is None or rb[0] > best[0]:
            best = rb
    sc, P, s, alpha, _, _ = best
    text = decode_map(aug, make_map(P, s, alpha), lm)
    pc = sc / n_ev
    return SolveResult("vigenere", lm.lang, text, pc, _gap(pc, lm, len(seq)),
                       key={"period": p, "shifts": s.tolist()}, info={"period": p})
