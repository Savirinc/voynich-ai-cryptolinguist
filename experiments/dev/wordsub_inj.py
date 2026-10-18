"""Probe 2: INJECTIVE word substitution (codebook, one code per word). Moves: swap two symbols' words, or move a
symbol to an unused LM word. Compares true-key score with found."""
import sys, math, time
sys.path.insert(0, "/private/tmp/claude-501/-Users-arhampartapjain/88643098-eceb-4bf4-97b5-9edd541be4ec/scratchpad")
import numpy as np, random
from collections import Counter
from wordsub_proto import WordLM, words_of, NgramTable, DeltaScorer

def anneal_inj(sc, m0, S, K, iters, rng, t0, t1=0.05, p_swap=0.5):
    cur = sc.reset(m0); best, bm = cur, sc.m.copy()
    used = np.zeros(K + 1, dtype=bool); used[sc.m[1:S]] = True
    ratio = (t1 / t0) ** (1 / iters); T = t0
    for it in range(iters):
        i = int(rng.integers(1, S))
        if rng.random() < p_swap:
            j = int(rng.integers(1, S))
            if i == j: T *= ratio; continue
            idx, vals = np.array([i, j]), np.array([sc.m[j], sc.m[i]])
        else:
            L = int(rng.integers(1, K))       # K = UNK index; words 1..K-1
            if used[L]: T *= ratio; continue
            idx, vals = np.array([i]), np.array([L])
        d, st = sc.propose(idx, vals)
        if d >= 0 or rng.random() < math.exp(d / T):
            if len(idx) == 1:
                used[sc.m[i]] = False; used[vals[0]] = True
            sc.accept(st); cur += d
            if cur > best: best, bm = cur, sc.m.copy()
        T *= ratio
    return bm, best

if __name__ == "__main__":
    V, TOP, iters, restarts, n_plain = map(int, sys.argv[1:6])
    tune = words_of("la", "tune")
    plain = tune[:n_plain]
    lm = WordLM(words_of("la", "ref") + (tune[n_plain:] if len(sys.argv) > 6 else []), V)
    print("LM words", len(words_of("la","ref")) + (len(tune)-n_plain if len(sys.argv) > 6 else 0), "tune total", len(tune))
    rng0 = random.Random(77001)
    types = list(dict.fromkeys(plain)); code = {w: k for k, w in enumerate(rng0.sample(types, len(types)))}
    cip = [code[w] for w in plain]; cnt = Counter(cip)
    top = [c for c, _ in cnt.most_common(TOP)]
    sid = {c: k + 1 for k, c in enumerate(top)}; S = TOP + 1
    seq = np.array([sid.get(c, S) for c in cip])
    tab = NgramTable(seq, order=2)
    sc = DeltaScorer(tab, lm, seq, S, kl_weight=0.0)
    truth = {sid[c]: w for w, c in code.items() if c in sid}
    tokw = np.array([cnt[c] for c in top])
    order_let = [i for i in np.argsort(-lm.unigram) if i not in (0, lm.UNK)]
    m0 = np.zeros(S + 1, dtype=np.int64); m0[1:S] = order_let[:TOP]; m0[S] = lm.UNK
    mt = m0.copy(); usedw = set()
    for s in range(1, S):
        w = lm.idx.get(truth[s]); mt[s] = w if w is not None else lm.UNK
    def acc(m): ok = np.array([lm.alphabet[m[s]] == truth[s] for s in range(1, S)]); return np.dot(ok, tokw) / tokw.sum()
    print(f"V {V} TOP {TOP} n {n_plain}: in-vocab share of top tokens {sum(tokw[s-1] for s in range(1,S) if truth[s] in lm.idx)/tokw.sum():.3f}; "
          f"true-key score/ev {sc.reset(mt)/tab.n_events:.3f}; init acc {acc(m0):.3f} score {sc.reset(m0)/tab.n_events:.3f}", flush=True)
    for r in range(restarts):
        t = time.time()
        m, best = anneal_inj(sc, m0, S, lm.UNK, iters, np.random.default_rng(r), t0=max(1.0, 0.03 * len(seq)))
        print(f"  r{r}: acc {acc(m):.3f} score/ev {best/tab.n_events:.3f} ({time.time()-t:.0f}s)", flush=True)
