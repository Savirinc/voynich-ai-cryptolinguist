"""Probe 3: does the true key win when the word LM is trained on more text? English: plaintext = 12k words of one
book; LM = the other books (all roles), truncated to M words."""
import sys, math, time, random, json
sys.path.insert(0, "/private/tmp/claude-501/-Users-arhampartapjain/88643098-eceb-4bf4-97b5-9edd541be4ec/scratchpad")
import numpy as np
from collections import Counter
from wordsub_proto import WordLM, NgramTable, DeltaScorer, NX, load_books
from wordsub_inj import anneal_inj
lang, M = sys.argv[1], int(sys.argv[2])
books = [b for b in load_books() if b["lang"] == lang]
ws = [[w for w in (NX.clean(x) for x in b["text"][2000:].split()) if w] for b in books]
print(lang, "books", len(ws), "words", [len(w) for w in ws])
plain = ws[0][:12000]
ref = [w for b in ws[1:] for w in b][:M]
lm = WordLM(ref, 5000)
cnt0 = None
rng0 = random.Random(77001)
types = list(dict.fromkeys(plain)); code = {w: k for k, w in enumerate(rng0.sample(types, len(types)))}
cip = [code[w] for w in plain]; cnt = Counter(cip); TOP = 300
top = [c for c, _ in cnt.most_common(TOP)]; sid = {c: k + 1 for k, c in enumerate(top)}; S = TOP + 1
seq = np.array([sid.get(c, S) for c in cip]); tab = NgramTable(seq, order=2)
sc = DeltaScorer(tab, lm, seq, S, kl_weight=0.0)
truth = {sid[c]: w for w, c in code.items() if c in sid}; tokw = np.array([cnt[c] for c in top])
order_let = [i for i in np.argsort(-lm.unigram) if i not in (0, lm.UNK)]
m0 = np.zeros(S + 1, dtype=np.int64); m0[1:S] = order_let[:TOP]; m0[S] = lm.UNK
mt = m0.copy()
for s in range(1, S):
    w = lm.idx.get(truth[s]); mt[s] = w if w is not None else lm.UNK
acc = lambda m: np.dot(np.array([lm.alphabet[m[s]] == truth[s] for s in range(1, S)]), tokw) / tokw.sum()
print(f"LM {len(ref)} words: true-key {sc.reset(mt)/tab.n_events:.3f}", flush=True)
m, best = anneal_inj(sc, m0, S, lm.UNK, 2000000, np.random.default_rng(0), t0=max(1.0, 0.03 * len(seq)))
print(f"  found {best/tab.n_events:.3f} acc {acc(m):.3f}", flush=True)
