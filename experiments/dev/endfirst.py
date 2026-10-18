"""Probe 8 (compound idea, stage 1): decode the ENDINGS alone. Synthetic cipher: each Latin word = stem + ending
(latseg.seg); stems and endings each replaced by secret codes. The missing ending ('') stays visible.
Signals over the ending key m (code ending -> Latin ending, injective):
  uni : sum n_a log p(m(a))                         (ending frequencies)
  seq : sum C[a,b] log P(m(b) | m(a))              (adjacent-word ending bigrams: agreement, syntax)
  par : sum Cp[a,b] log Q(m(a), m(b))              (pairs of endings seen on the SAME stem = paradigms, Kober)
Latin reference stats from the Latin Library; paradigm pairs counted in 24k-word chunks to match the sample size."""
import sys, time, random, math
import numpy as np
from collections import Counter, defaultdict
import latseg
from latseg import seg, words_of

def ref_stats(ref, E, chunk=24000, n_chunks=300):
    K = len(E); ix = {e: i for i, e in enumerate(E)}
    ends = np.array([ix[seg(w)[1]] for w in ref])
    uni = np.bincount(ends, minlength=K) + 0.5
    big = np.zeros((K, K)); np.add.at(big, (ends[:-1], ends[1:]), 1); big += 0.1
    Lseq = np.log(big / big.sum(1, keepdims=True))
    par = np.zeros((K, K)); rng = np.random.default_rng(0)
    for st in rng.integers(0, len(ref) - chunk, n_chunks):
        P = defaultdict(set)
        for w in ref[st:st + chunk]:
            s, e = seg(w)
            if e: P[s].add(ix[e])
        for es in P.values():
            es = list(es)
            for a in es:
                for b in es:
                    if a != b: par[a, b] += 1
    par += 0.1
    return np.log(uni / uni.sum()), Lseq, np.log(par / par.sum())

def score(m, n, C, Cp, Luni, Lseq, Lpar, lam):
    return float(n @ Luni[m] + (C * Lseq[np.ix_(m, m)]).sum() + lam * (Cp * Lpar[np.ix_(m, m)]).sum())

def anneal(m0, free, K, args, iters, rng, t0, t1=0.02):
    m = m0.copy(); cur = score(m, *args); best, bm = cur, m.copy()
    ratio = (t1 / t0) ** (1 / iters); T = t0
    used = np.zeros(K, bool); used[m] = True
    for it in range(iters):
        i = free[rng.integers(len(free))]; m2 = m.copy()
        if rng.random() < 0.6:
            j = free[rng.integers(len(free))]
            if i == j: T *= ratio; continue
            m2[i], m2[j] = m[j], m[i]
        else:
            L = int(rng.integers(1, K))
            if used[L]: T *= ratio; continue
            m2[i] = L
        new = score(m2, *args); d = new - cur
        if d >= 0 or rng.random() < math.exp(max(-700, d / T)):
            if m2[i] != m[i] and not used[m2[i]]: used[m[i]] = False; used[m2[i]] = True
            m, cur = m2, new
            if cur > best: best, bm = cur, m.copy()
        T *= ratio
    return bm, best

if __name__ == "__main__":
    lam, iters, restarts, n_plain = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    ref = latseg.latlib()
    E = [""] + [e for e in latseg.END]; K = len(E); ix = {e: i for i, e in enumerate(E)}
    t = time.time(); Luni, Lseq, Lpar = ref_stats(ref, E); print(f"ref stats {time.time()-t:.0f}s", flush=True)
    plain = words_of("la", "tune")[:n_plain]
    sp = [seg(w) for w in plain]
    r0 = random.Random(88001)
    perm = list(range(1, K)); r0.shuffle(perm); code_of = {0: 0, **{i: perm[i - 1] for i in range(1, K)}}  # secret
    truth = {c: l for l, c in code_of.items()}
    ce = np.array([code_of[ix[e]] for _, e in sp])
    n = np.bincount(ce, minlength=K).astype(float)
    C = np.zeros((K, K)); np.add.at(C, (ce[:-1], ce[1:]), 1)
    P = defaultdict(set)
    for (s, _), c in zip(sp, ce):
        if c: P[s].add(c)          # stems are coded too, but only their identity matters here
    Cp = np.zeros((K, K))
    for es in P.values():
        for a in es:
            for b in es:
                if a != b: Cp[a, b] += 1
    args = (n, C, Cp, Luni, Lseq, Lpar, lam)
    mt = np.array([truth[c] for c in range(K)])
    present = n > 0; tok = n.copy(); tok[0] = 0
    acc = lambda m: float(((m == mt) * tok).sum() / tok.sum())
    # init: frequency rank matching
    order_c = [c for c in np.argsort(-n) if c != 0]; order_l = [l for l in np.argsort(-Luni) if l != 0]
    m0 = np.zeros(K, int)
    for c, l in zip(order_c, order_l): m0[c] = l
    free = np.array([c for c in range(1, K)])
    print(f"lam {lam} n {n_plain}: codes used {int(present.sum())}; true {score(mt,*args):.0f}; init {score(m0,*args):.0f} acc {acc(m0):.3f}", flush=True)
    keys = []
    for r in range(restarts):
        t = time.time(); m, b = anneal(m0, free, K, args, iters, np.random.default_rng(r), t0=50.0)
        keys.append(m); print(f"  r{r}: score {b:.0f} acc {acc(m):.3f} ({time.time()-t:.0f}s)", flush=True)
    best = max(keys, key=lambda m: score(m, *args))
    agree = np.mean([((k == best) * tok).sum() / tok.sum() for k in keys])
    print(f"best acc {acc(best):.3f}; mean token agreement with best {agree:.3f}")
    print("top decoded:", [(E[best[c]], E[mt[c]]) for c in order_c[:25]])
