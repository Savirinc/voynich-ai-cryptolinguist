"""Stage B feasibility probe (DEV keys only): word-substitution cipher of ~24k Latin words, attacked with a word
bigram KN LM (la ref books) via the E017 delta-scored SA. Measures token accuracy on frequent types."""
import sys, json, math, random, time
from collections import Counter
sys.path.insert(0, "/Users/arhampartapjain/voynich-ai-cryptolinguist/src"); sys.path.insert(0, "/Users/arhampartapjain/voynich-ai-cryptolinguist/experiments")
import numpy as np
import e011_twin_search as E
from vcl.synthetic import naibbe_exact as NX
from vcl.synthetic.corpora import load_books
from vcl.solvers.engine import NgramTable
from vcl.solvers.fast_anneal import DeltaScorer
from vcl.solvers.lm import _kn_dense

ROOT = "/Users/arhampartapjain/voynich-ai-cryptolinguist"
roles = json.load(open(ROOT + "/data/derived/benchmark_v1/book_roles.json"))
def words_of(lang, role):
    out = []
    for b in load_books():
        if b["lang"] == lang and roles.get(b["id"], {}).get("role") == role:
            out += [w for w in (NX.clean(x) for x in b["text"][2000:].split()) if w]
    return out
class WordLM:
    def __init__(self, ref, V):
        top = [w for w, _ in Counter(ref).most_common(V)]
        self.alphabet = ["<b>"] + top + ["<unk>"]
        self.idx = {w: i for i, w in enumerate(self.alphabet)}
        self.A = len(self.alphabet); self.UNK = self.A - 1
        ids = np.array([self.idx.get(w, self.UNK) for w in ref])
        self.logp = _kn_dense(np.concatenate([[0], ids]), self.A, order=2)
        self.flat = self.logp.reshape(-1)
        c = np.bincount(ids, minlength=self.A).astype(float); c[0] = 1
        self.unigram = c / c.sum()
def anneal(sc, m0, free, cand_p, iters, rng, t0, t1=0.05):
    cur = sc.reset(m0); best, bm = cur, sc.m.copy()
    ratio = (t1 / t0) ** (1 / iters); T = t0
    cum = np.cumsum(cand_p)
    for it in range(iters):
        if rng.random() < 0.3:
            i, j = free[rng.integers(len(free))], free[rng.integers(len(free))]
            if sc.m[i] == sc.m[j]: T *= ratio; continue
            idx, vals = np.array([i, j]), np.array([sc.m[j], sc.m[i]])
        else:
            i = free[rng.integers(len(free))]
            L = 1 + int(np.searchsorted(cum, rng.random() * cum[-1]))
            if L == sc.m[i]: T *= ratio; continue
            idx, vals = np.array([i]), np.array([L])
        d, st = sc.propose(idx, vals)
        if d >= 0 or rng.random() < math.exp(d / T):
            sc.accept(st); cur += d
            if cur > best: best, bm = cur, sc.m.copy()
        T *= ratio
    return bm, best
if __name__ == "__main__":
    V, TOP, iters, restarts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    lm = WordLM(words_of("la", "ref"), V)
    plain = words_of("la", "tune")[:24000]
    rng0 = random.Random(77001)
    types = list(dict.fromkeys(plain)); code = {w: k for k, w in enumerate(rng0.sample(types, len(types)))}
    cip = [code[w] for w in plain]
    cnt = Counter(cip)
    top = [c for c, _ in cnt.most_common(TOP)]
    sid = {c: k + 1 for k, c in enumerate(top)}; S = TOP + 1   # symbol S = all rare cipher types
    seq = np.array([sid.get(c, S) for c in cip])
    tab = NgramTable(seq, order=2)
    sc = DeltaScorer(tab, lm, seq, S, kl_weight=1.0)
    # init: frequency rank matching
    order_let = [i for i in np.argsort(-lm.unigram) if i not in (0, lm.UNK)]
    m0 = np.zeros(S + 1, dtype=np.int64); m0[1:S] = order_let[:TOP]; m0[S] = lm.UNK
    free = np.arange(1, S)
    p = lm.unigram.copy(); p[0] = 0; p[lm.UNK] = 0; p = p[1:] ** 0.5; p /= p.sum()
    truth = {sid[c]: w for w, c in code.items() if c in sid}
    tokw = np.array([cnt[c] for c in top])
    for r in range(restarts):
        rng = np.random.default_rng(r); t = time.time()
        m, best = anneal(sc, m0, free, p, iters, rng, t0=max(1.0, 0.03 * len(seq)))
        ok = np.array([lm.alphabet[m[s]] == truth[s] for s in range(1, S)])
        covered = sum(cnt[c] for c in top) / len(cip)
        print(f"V {V} TOP {TOP} it {iters} r{r}: token acc on top types {np.dot(ok, tokw) / tokw.sum():.3f} "
              f"(types {ok.mean():.3f}; top covers {covered:.2f} of tokens) score/ev {best / tab.n_events:.3f} ({time.time() - t:.0f}s)", flush=True)
    m_init_ok = np.array([lm.alphabet[m0[s]] == truth[s] for s in range(1, S)])
    print("init acc", np.dot(m_init_ok, tokw) / tokw.sum())
    mt = m0.copy()
    for s in range(1, S):
        mt[s] = lm.idx.get(truth[s], lm.UNK)
    print("true-key score/ev", sc.reset(mt) / tab.n_events, "| true words outside LM vocab:", sum(lm.idx.get(truth[s]) is None for s in range(1, S)))
    # start from truth and anneal at low temperature: does the truth stay?
    rng = np.random.default_rng(9)
    m, best = anneal(sc, mt, free, p, 300000, rng, t0=1.0)
    ok = np.array([lm.alphabet[m[s]] == truth[s] for s in range(1, S)])
    print("from truth, after 300k cold SA: token acc", np.dot(ok, tokw) / tokw.sum(), "score/ev", best / tab.n_events)
