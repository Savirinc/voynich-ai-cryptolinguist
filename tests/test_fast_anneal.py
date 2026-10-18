import numpy as np

from vcl.solvers.engine import NgramTable, freq_init, unigram_penalty
from vcl.solvers.fast_anneal import DeltaScorer, anneal_delta
from vcl.solvers.lm import get_lm


def _setup():
    lm = get_lm("it", "nospace")
    rng = np.random.default_rng(0)
    S = 40
    seq = rng.integers(1, S + 1, size=3000)
    return lm, seq, S, NgramTable(seq)


def test_delta_matches_full_score():
    lm, seq, S, tab = _setup()
    pen = unigram_penalty(seq, S, lm)
    sc = DeltaScorer(tab, lm, seq, S)
    m = freq_init(seq, S, lm, injective=False)
    cur = sc.reset(m)
    assert abs(cur - (tab.score(m, lm) - pen(m))) < 1e-6 * abs(cur)
    rng = np.random.default_rng(1)
    for _ in range(300):
        if rng.random() < 0.5:
            i, j = rng.integers(1, S + 1, size=2)
            if i == j:
                continue
            idx, vals = np.array([i, j]), np.array([sc.m[j], sc.m[i]])
        else:
            idx, vals = np.array([rng.integers(1, S + 1)]), np.array([rng.integers(1, lm.A)])
        d, st = sc.propose(idx, vals)
        m2 = sc.m.copy(); m2[idx] = vals
        assert abs(d - ((tab.score(m2, lm) - pen(m2)) - cur)) < 1e-6 * abs(cur)
        sc.accept(st); cur += d
    assert abs(sc.total() - cur) < 1e-6 * abs(cur)


def test_anneal_delta_returns_consistent_best():
    lm, seq, S, tab = _setup()
    pen = unigram_penalty(seq, S, lm)
    sc = DeltaScorer(tab, lm, seq, S)
    p = lm.unigram[1:] ** 0.5
    m, best = anneal_delta(sc, freq_init(seq, S, lm, injective=False), p / p.sum(), 3000,
                           np.random.default_rng(2), t0=50.0)
    assert abs(best - (tab.score(m, lm) - pen(m))) < 1e-6 * abs(best)
