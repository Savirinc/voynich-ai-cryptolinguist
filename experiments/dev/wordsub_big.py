"""Probe 5: injective word-substitution attack with a word-bigram LM trained on the Latin Library (13M words,
held-out overlap removed). Plaintext: la tune text."""
import sys, json, time, random
sys.path.insert(0, "/private/tmp/claude-501/-Users-arhampartapjain/88643098-eceb-4bf4-97b5-9edd541be4ec/scratchpad")
import numpy as np
from collections import Counter
from wordsub_proto import WordLM, words_of, NgramTable, DeltaScorer, NX
from wordsub_inj import anneal_inj
from wordsub_rank import anneal_rank
X = "/private/tmp/claude-501/-Users-arhampartapjain/88643098-eceb-4bf4-97b5-9edd541be4ec/scratchpad/ext/"
V, n_plain, TOP, restarts = map(int, sys.argv[1:5])
ref = []
for f in json.load(open(X + "latlib_keep.json")):
    ref += [w for w in (NX.clean(x) for x in open(X + "lat_text_latin_library/" + f, errors="ignore").read().split()) if w]
t = time.time(); lm = WordLM(ref, V); print(f"LM {len(ref)} words V {V} built {time.time()-t:.0f}s", flush=True)
plain = words_of("la", "tune")[:n_plain]
rng0 = random.Random(77001)
types = list(dict.fromkeys(plain)); code = {w: k for k, w in enumerate(rng0.sample(types, len(types)))}
cip = [code[w] for w in plain]; cnt = Counter(cip)
top = [c for c, k in cnt.most_common() if k >= 2]; SCORE_TOP = TOP; sid = {c: k + 1 for k, c in enumerate(top)}; S = len(top) + 1
seq = np.array([sid.get(c, S) for c in cip]); tab = NgramTable(seq, order=2)
sc = DeltaScorer(tab, lm, seq, S, kl_weight=0.0)
truth = {sid[c]: w for w, c in code.items() if c in sid}; tokw = np.array([cnt[c] if k < SCORE_TOP else 0 for k, c in enumerate(top)])
order_let = [i for i in np.argsort(-lm.unigram) if i not in (0, lm.UNK)]
m0 = np.zeros(S + 1, dtype=np.int64); m0[1:S] = order_let[:S - 1]; m0[S] = lm.UNK
mt = m0.copy()
for s in range(1, S):
    w = lm.idx.get(truth[s]); mt[s] = w if w is not None else lm.UNK
acc = lambda m: np.dot(np.array([lm.alphabet[m[s]] == truth[s] for s in range(1, S)]), tokw) / tokw.sum()
inv = sum(tokw[s - 1] for s in range(1, S) if truth[s] in lm.idx) / tokw.sum()
print(f"symbols {S-1} (count>=2, {sum(cnt[c] for c in top)/len(cip):.2f} of tokens); plain {n_plain} TOP {TOP}: in-vocab {inv:.3f} true-key {sc.reset(mt)/tab.n_events:.3f} init acc {acc(m0):.3f}", flush=True)
for r in range(restarts):
    t = time.time()
    m, best = anneal_inj(sc, m0, S, lm.UNK, 3000000, np.random.default_rng(r), t0=max(1.0, 0.03 * len(seq)))
    print(f"  r{r}: found {best/tab.n_events:.3f} acc {acc(m):.3f} ({time.time()-t:.0f}s)", flush=True)
if len(sys.argv) > 5:
    import warnings; warnings.filterwarnings("ignore")
    from wordsub_icm import ICM
    icm = ICM(tab, lm, seq, S)
    rank_words = np.array(order_let)
    for r in range(int(sys.argv[5])):
        t = time.time()
        m, best = anneal_rank(sc, m0, S, lm.UNK, rank_words, 3000000, np.random.default_rng(10 + r), t0=max(1.0, 0.01 * len(seq)), f=1.5)
        a1 = acc(m)
        m2, bs = icm.solve(m, np.random.default_rng(r), tab, lm, n_ils=5)
        print(f"  r{r}: SA bigram {best/tab.n_events:.3f} acc {a1:.3f} -> +ICM bigram {tab.score(m2, lm)/tab.n_events:.3f} acc {acc(m2):.3f} ({time.time()-t:.0f}s)", flush=True)
