"""Probe 9 (compound idea, stage 2): with endings decoded (stage 1), decode the STEMS.
Symbol = code stem (count >= 2; rarer -> one fixed UNK symbol). Candidates = top-V Latin Library stems.
Score = stem-bigram KN LM (DeltaScorer) + wu * unary U[s, L], where U is the Poisson log-likelihood of the stem's
decoded ending counts n_se under the Latin stem's expected counts mu_Le = N * p(L, e)  (frequency + paradigm).
Init = linear assignment on U (Hungarian). SA proposals: a symbol's top-k candidates by U, or swaps."""
import sys, time, random, math
import numpy as np
from collections import Counter, defaultdict
from scipy.optimize import linear_sum_assignment
import latseg
from latseg import seg, words_of
from wordsub_proto import WordLM, NgramTable, DeltaScorer
import endfirst as EF

def anneal_u(sc, U, cand, m0, S, K, iters, rng, t0, wu, t1=0.05, p_swap=0.3):
    cur = sc.reset(m0) + wu * U[np.arange(1, S), m0[1:S] - 1].sum(); best, bm = cur, sc.m.copy()
    used = np.zeros(K + 1, bool); used[sc.m[1:S]] = True
    ratio = (t1 / t0) ** (1 / iters); T = t0; k = cand.shape[1]
    for it in range(iters):
        i = int(rng.integers(1, S))
        if rng.random() < p_swap:
            j = int(cand_sym[i][rng.integers(len(cand_sym[i]))]) if cand_sym[i] else int(rng.integers(1, S))
            if i == j: T *= ratio; continue
            idx, vals = np.array([i, j]), np.array([sc.m[j], sc.m[i]])
        else:
            L = int(cand[i, rng.integers(k)]) + 1
            if used[L] or L == sc.m[i]: T *= ratio; continue
            idx, vals = np.array([i]), np.array([L])
        d, st = sc.propose(idx, vals)
        d += wu * float(U[idx, vals - 1].sum() - U[idx, sc.m[idx] - 1].sum())
        if d >= 0 or rng.random() < math.exp(max(-700, d / T)):
            if len(idx) == 1: used[sc.m[i]] = False; used[vals[0]] = True
            sc.accept(st); cur += d
            if cur > best: best, bm = cur, sc.m.copy()
        T *= ratio
    return bm, best

if __name__ == "__main__":
    V, iters, restarts, n_plain, wu, oracle_end = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    ref = latseg.latlib()
    E = [""] + list(latseg.END); KE = len(E); ix = {e: i for i, e in enumerate(E)}
    rsp = [seg(w) for w in ref]
    t = time.time(); lm = WordLM([s for s, _ in rsp], V); print(f"stem LM V {V} {time.time()-t:.0f}s", flush=True)
    K = lm.UNK                      # LM stems are 1..K-1, UNK = K
    # p(L, e) over LM stems + a generic 'rare stem' row for UNK
    pe = np.zeros((lm.A, KE))
    for s, e in rsp: pe[lm.idx.get(s, lm.UNK), ix[e]] += 1
    nrare = sum(1 for s, c in Counter(s for s, _ in rsp).items() if s not in lm.idx)
    pe[lm.UNK] /= max(nrare, 1)
    pe = (pe + 0.01) / len(rsp)
    plain = words_of("la", "tune")[:n_plain]; sp = [seg(w) for w in plain]; N = len(sp)
    r0 = random.Random(99001)
    stems = list(dict.fromkeys(s for s, _ in sp)); scode = {s: k for k, s in enumerate(r0.sample(stems, len(stems)))}
    # ending key: oracle (truth) or decoded by stage 1 on this same cipher
    if oracle_end:
        dec_end = [e for _, e in sp]
    else:
        Luni, Lseq, Lpar = EF.ref_stats(ref, E)
        perm = list(range(1, KE)); random.Random(88001).shuffle(perm); code_of = {0: 0, **{i: perm[i - 1] for i in range(1, KE)}}
        ce = np.array([code_of[ix[e]] for _, e in sp]); n = np.bincount(ce, minlength=KE).astype(float)
        C = np.zeros((KE, KE)); np.add.at(C, (ce[:-1], ce[1:]), 1)
        Pp = defaultdict(set)
        for (s, _), c in zip(sp, ce):
            if c: Pp[scode[s]].add(c)
        Cp = np.zeros((KE, KE))
        for es in Pp.values():
            for a in es:
                for b in es:
                    if a != b: Cp[a, b] += 1
        args = (n, C, Cp, Luni, Lseq, Lpar, 1.0)
        oc = [c for c in np.argsort(-n) if c != 0]; ol = [l for l in np.argsort(-Luni) if l != 0]
        m0e = np.zeros(KE, int)
        for c, l in zip(oc, ol): m0e[c] = l
        keys = [EF.anneal(m0e, np.arange(1, KE), KE, args, 200000, np.random.default_rng(r), 50.0)[0] for r in range(2)]
        ke = max(keys, key=lambda m: EF.score(m, *args))
        dec_end = [E[ke[c]] for c in ce]
        print(f"stage 1 ending token acc {np.mean([a == e for a, (_, e) in zip(dec_end, sp)]):.3f}", flush=True)
    cs = [scode[s] for s, _ in sp]; cnt = Counter(cs)
    top = [c for c, k in cnt.most_common() if k >= 2]; sid = {c: k + 1 for k, c in enumerate(top)}; S = len(top) + 1
    seq = np.array([sid.get(c, S) for c in cs]); tab = NgramTable(seq, order=2)
    sc = DeltaScorer(tab, lm, seq, S, kl_weight=0.0)
    nse = np.zeros((S + 1, KE))
    for c, e in zip(cs, dec_end): nse[sid.get(c, S), ix[e]] += 1
    mu = N * pe[1:K]                                             # (K-1, KE) for LM stems 1..K-1
    with np.errstate(all="ignore"): U = np.zeros((S + 1, K - 1)); U[1:S] = nse[1:S] @ np.log(mu).T - mu.sum(1)[None, :]
    print("U finite:", bool(np.isfinite(U).all()), flush=True)
    inv = {c: s for s, c in scode.items()}
    truth = np.array([0] + [lm.idx.get(inv[c], lm.UNK) for c in top])
    tokw = np.array([0] + [cnt[c] for c in top], float)
    acc = lambda m: float(((m[1:S] == truth[1:S]) * tokw[1:S]).sum() / tokw[1:S].sum())
    full = lambda m: float(np.mean([(seq[t] < S and m[seq[t]] == truth[seq[t]] and truth[seq[t]] != lm.UNK) and dec_end[t] == sp[t][1] for t in range(N)]))
    cov = tokw[1:S].sum() / N; inv_share = ((truth[1:S] != lm.UNK) * tokw[1:S]).sum() / tokw[1:S].sum()
    mt = np.zeros(S + 1, int); mt[1:S] = truth[1:S]; mt[S] = lm.UNK
    tot = lambda m: sc.reset(m) + wu * U[np.arange(1, S), np.minimum(m[1:S], K - 1) - 1].sum()
    # Hungarian init on U (pad with -inf-ish for injectivity)
    r_, c_ = linear_sum_assignment(-U[1:S]); m0 = np.zeros(S + 1, int); m0[1 + r_] = c_ + 1; m0[S] = lm.UNK
    print(f"symbols {S-1} cover {cov:.2f} of tokens; true stem in LM vocab {inv_share:.3f}; "
          f"true-key total {tot(mt) if (mt[1:S] < K).all() else float('nan'):.0f}; Hungarian init acc {acc(m0):.3f} full-word {full(m0):.3f} total {tot(m0):.0f}", flush=True)
    kc = 40; cand = np.zeros((S + 1, kc), int); cand[1:S] = np.argsort(-U[1:S], axis=1)[:, :kc]
    pos_of = {}
    for i in range(1, S):
        for L in cand[i, :10]: pos_of.setdefault(int(L) + 1, []).append(i)
    cand_sym = [[]] + [sorted({j for L in cand[i, :10] for j in pos_of.get(int(L) + 1, []) if j != i}) for i in range(1, S)] + [[]]
    keys = []
    for r in range(restarts):
        t = time.time(); m, b = anneal_u(sc, U, cand, m0, S, K, iters, np.random.default_rng(r), t0=max(1.0, 0.01 * N), wu=wu)
        keys.append((b, m)); print(f"  r{r}: total {b:.0f} stem acc {acc(m):.3f} full-word {full(m):.3f} ({time.time()-t:.0f}s)", flush=True)
    b, best = max(keys, key=lambda x: x[0])
    ag = np.mean([((k == best)[1:S] * tokw[1:S]).sum() / tokw[1:S].sum() for _, k in keys])
    print(f"bigram-only: true {sc.reset(mt)/tab.n_events:.3f} found {sc.reset(best)/tab.n_events:.3f}")
    print(f"best: stem acc {acc(best):.3f} full-word token acc {full(best):.3f}; agreement {ag:.3f}")
    dec = [(lm.alphabet[best[seq[t]]] if seq[t] < S else "?") + "-" + dec_end[t] for t in range(60)]
    print("decoded:", " ".join(dec)); print("truth:  ", " ".join(s + "-" + e for s, e in sp[:60]))
    import ctxassign as CA
    tot2 = lambda m: sc.reset(m) + wu * U[np.arange(1, S), m[1:S] - 1].sum()
    for start_name, m in (("Hungarian init", m0),):
        cur = tot2(m); print(f"ctx-assign from {start_name}: total {cur:.0f} acc {acc(m):.3f}", flush=True)
        for it in range(12):
            m2 = CA.ctx_round(m, seq, S, K, lm, U, wu)
            m2, b2 = anneal_u(sc, U, cand, m2, S, K, 1000000, np.random.default_rng(100 + it), t0=2.0, wu=wu)
            if b2 > cur: m, cur = m2, b2
            print(f"   round {it}: total {b2:.0f} acc {acc(m2):.3f}  (kept {cur:.0f} acc {acc(m):.3f})", flush=True)
    ok = (m[1:S] == truth[1:S]); f = tokw[1:S]
    for lo, hi in ((100, 10**9), (20, 100), (5, 20), (3, 5), (2, 3)):
        sel = (f >= lo) & (f < hi)
        print(f"  stems seen {lo}-{hi if hi < 10**9 else 'max'} times: {sel.sum()} stems, {f[sel].sum()/N:.2f} of tokens, accuracy {ok[sel].mean():.3f}")
    print("final full-word token acc", full(m))
