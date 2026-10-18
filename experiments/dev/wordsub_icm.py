"""Probe 7: best-response (ICM) sweeps for an injective word key under a bigram LM, plus a Poisson frequency prior,
with iterated local search (perturb + re-sweep)."""
import math, time
import numpy as np
from scipy.special import gammaln

class ICM:
    def __init__(self, tab, lm, seq, S, prior_w=1.0):
        c0, c1 = tab.cols[0], tab.cols[1]; cnt = tab.counts
        self.out = [[] for _ in range(S + 1)]; self.inn = [[] for _ in range(S + 1)]
        for a, b, c in zip(c0, c1, cnt):
            self.out[a].append((b, c)); self.inn[b].append((a, c))
        self.out = [(np.array([x for x, _ in o], dtype=np.int64), np.array([c for _, c in o])) for o in self.out]
        self.inn = [(np.array([x for x, _ in o], dtype=np.int64), np.array([c for _, c in o])) for o in self.inn]
        self.LP = np.asarray(lm.logp, dtype=np.float32)
        self.S, self.A, self.UNK = S, lm.A, lm.UNK
        n = len(seq); sc = np.bincount(seq, minlength=S + 1).astype(float)
        lam = np.maximum(lm.unigram * n, 1e-3)
        self.prior = prior_w * (sc[:, None] * np.log(lam)[None, :] - lam[None, :] - gammaln(sc + 1)[:, None])  # S+1 x A
        self.prior[:, 0] = -1e9; self.prior[:, self.UNK] = -1e9
    def vec(self, m, i):
        js, cj = self.out[i]; ks, ck = self.inn[i]
        v = self.prior[i].astype(np.float64).copy()
        if len(js):
            selfm = js == i
            v += self.LP[:, m[js[~selfm]]] @ cj[~selfm]
            if selfm.any(): v += np.diag(self.LP) * cj[selfm].sum()
        if len(ks):
            selfm = ks == i
            v += self.LP[m[ks[~selfm]], :].T @ ck[~selfm]
        return v
    def total(self, m, tab, lm):
        return tab.score(m, lm) + sum(self.prior[i, m[i]] for i in range(1, self.S))
    def sweep(self, m, rng):
        owner = -np.ones(self.A, dtype=np.int64); owner[m[1:self.S]] = np.arange(1, self.S)
        changed = 0
        for i in rng.permutation(np.arange(1, self.S)):
            v = self.vec(m, i)
            cur = v[m[i]]
            free = owner < 0
            free[0] = free[self.UNK] = False
            L = int(np.argmax(np.where(free, v, -np.inf)))
            if v[L] > cur + 1e-9:
                owner[m[i]] = -1; m[i] = L; owner[L] = i; changed += 1
        return changed
    def solve(self, m0, rng, tab, lm, n_ils=30, frac=0.05, max_sweeps=30):
        m = m0.copy()
        for _ in range(max_sweeps):
            if self.sweep(m, rng) == 0: break
        best, bs = m.copy(), self.total(m, tab, lm)
        for k in range(n_ils):
            m = best.copy()
            idx = rng.choice(np.arange(1, self.S), size=max(1, int(frac * (self.S - 1))), replace=False)
            perm = rng.permutation(idx); m[idx] = best[perm]           # shuffle assignments among chosen symbols
            for _ in range(max_sweeps):
                if self.sweep(m, rng) == 0: break
            s = self.total(m, tab, lm)
            if s > bs: best, bs = m.copy(), s
        return best, bs
