"""Final round, family F (syllable notation), dev probe. Known answers only, no Voynich.
Generator: plaintext words -> syllables (E019 syllables()); each syllable type -> a code = 1-2 Voynich units
(E024 S3 units + single EVA letters), prefix-free as EVA strings, frequent syllables get shorter codes; a word is
written as the concatenation of its syllable codes (word boundaries kept).
Attack: (1) learn the code inventory: type-level Gibbs segmentation of words into chunks (Dirichlet-process
unigram lexicon, learned glyph/length base distribution, annealed); (2) solve chunk -> syllable with a syllable
bigram KN LM (word boundary '#' as a token) by simulated annealing over an injective key, frequency-window
proposals, R restarts. Reports: segmentation accuracy, syllable token accuracy, whole-word accuracy, restart
agreement, long-word lexical coverage of decoded words."""
import sys, time, random, math, pickle, os, json
import numpy as np
from collections import Counter
sys.path[:0] = ["/Users/arhampartapjain/voynich-ai-cryptolinguist/src", "/Users/arhampartapjain/voynich-ai-cryptolinguist/experiments"]
from e019_unit_burstiness import syllables
import latseg
from wordsub_proto import WordLM, NgramTable, DeltaScorer

UNITS = ["cth", "ckh", "cph", "cfh", "ch", "sh", "iiin", "iin", "in", "iiir", "iir", "ir", "eee", "ee", "qo", "dy"] + list("ydnlrmaokestpfg")

def make_table(syl_counts, rng, homo=0):
    codes, taken = {}, []
    def ok(c): return all(not c.startswith(t) and not t.startswith(c) for t in taken)
    for s, _ in syl_counts.most_common():
        k = 1 + (homo if homo and syl_counts[s] > 200 else 0)
        codes[s] = []
        for _ in range(k):
            for tries in range(100000):
                L = 1 if (len(taken) < 6 and rng.random() < 0.5) else (2 if rng.random() < 0.85 else 3)
                c = "".join(rng.choice(UNITS) for _ in range(L))
                if ok(c): taken.append(c); codes[s].append(c); break
    return codes

def encrypt(words, codes, rng):
    out, truth = [], []
    for w in words:
        sy = syllables(w); cs = [rng.choice(codes[s]) for s in sy]
        out.append("".join(cs)); truth.append((sy, [len(c) for c in cs]))
    return out, truth

def seg_gibbs(types, alpha=1.0, sweeps=60, t0=2.0, t1=0.05, seed=0, smooth=0.01, maxlen=8):
    rng = random.Random(seed); glyphs = sorted({g for w in types for g in w})
    bnd = {w: [False] * (len(w) - 1) for w in types}           # boundary after position i
    def chunks(w):
        out, s = [], 0
        for i, b in enumerate(bnd[w]):
            if b: out.append(w[s:i + 1]); s = i + 1
        out.append(w[s:]); return out
    lex = Counter(c for w in types for c in chunks(w)); N = sum(lex.values())
    for sw in range(sweeps):
        gc = Counter(); lc = Counter()
        for c, n in lex.items():
            if n > 0:
                for g in c: gc[g] += 1
                lc[len(c)] += 1
        tg = sum(gc.values()) + smooth * len(glyphs); tl = sum(lc.values()) + smooth * 16
        lq = {g: math.log((gc[g] + smooth) / tg) for g in glyphs}; ll = {L: math.log((lc[L] + smooth) / tl) for L in range(1, 17)}
        P0 = lambda c: math.exp(ll.get(len(c), -30) + sum(lq[g] for g in c)) if len(c) <= maxlen else 0.0
        T = t0 * (t1 / t0) ** (sw / max(1, sweeps - 1))
        order = list(types); rng.shuffle(order)
        for w in order:
            for i in range(len(w) - 1):
                # locate the chunk(s) around boundary i
                b = bnd[w]; l = i
                while l > 0 and not b[l - 1]: l -= 1
                r = i + 1
                while r < len(w) - 1 and not b[r]: r += 1
                left, right, whole = w[l:i + 1], w[i + 1:r + 1], w[l:r + 1]
                if b[i]: lex[left] -= 1; lex[right] -= 1; N -= 2
                else: lex[whole] -= 1; N -= 1
                p_m = (lex[whole] + alpha * P0(whole)) / (N + alpha)
                p_s = (lex[left] + alpha * P0(left)) / (N + alpha) * (lex[right] + alpha * P0(right) + (left == right)) / (N + 1 + alpha)
                a, c_ = math.log(max(p_s, 1e-300)) / T, math.log(max(p_m, 1e-300)) / T
                ps = 1 / (1 + math.exp(max(-700, min(700, c_ - a))))
                if rng.random() < ps: b[i] = True; lex[left] += 1; lex[right] += 1; N += 2
                else: b[i] = False; lex[whole] += 1; N += 1
    return {w: chunks(w) for w in types}

def syl_lm(V):
    p = latseg.X + f"syl_lm_tokens.pkl"
    if os.path.exists(p): toks = pickle.load(open(p, "rb"))
    else:
        toks = []
        for w in pickle.load(open(latseg.X + "latlib_words_lm.pkl", "rb")):
            toks += syllables(w); toks.append("#")
        pickle.dump(toks, open(p, "wb"))
    return WordLM(toks, V)

def solve(cw_chunks, lm, restarts, iters, seed=0, kl=0.0, window=60):
    cnt = Counter(c for cs in cw_chunks for c in cs)
    top = [c for c, k in cnt.most_common() if k >= 2][:lm.A - 4]
    sid = {c: k + 1 for k, c in enumerate(top)}; UNK = len(top) + 1; B = len(top) + 2; S = B
    seq = []
    for cs in cw_chunks:
        seq += [sid.get(c, UNK) for c in cs]; seq.append(B)
    seq = np.array(seq); tab = NgramTable(seq, order=2)
    sc = DeltaScorer(tab, lm, seq, S, kl_weight=kl)
    hb = lm.idx["#"]
    lmf = lm.unigram.copy(); lmf[[0, hb, lm.UNK]] = 0
    order_l = [int(i) for i in np.argsort(-lmf) if lmf[i] > 0]
    rank_of_l = {l: r for r, l in enumerate(order_l)}
    m0 = np.zeros(S + 1, dtype=np.int64); m0[UNK] = lm.UNK; m0[B] = hb
    for r, c in enumerate(top): m0[sid[c]] = order_l[r]
    free = np.arange(1, UNK)
    rng_master = np.random.default_rng(seed); keys = []
    for rr in range(restarts):
        rng = np.random.default_rng(rng_master.integers(1 << 30))
        m = m0.copy()
        for _ in range(len(free) // 2 * (rr > 0)):            # restarts start from a perturbed frequency init
            i, j = rng.choice(free, 2)
            if abs(i - j) < window: m[i], m[j] = m[j], m[i]
        cur = sc.reset(m); best, bm = cur, m.copy()
        owner = {int(m[i]): int(i) for i in free}
        T0, T1 = max(1.0, 0.002 * len(seq)), 0.05; ratio = (T1 / T0) ** (1 / iters); T = T0
        for it in range(iters):
            i = int(free[rng.integers(len(free))])
            r = rank_of_l[int(sc.m[i])] + int(rng.integers(-window, window + 1))
            if r < 0 or r >= len(order_l): T *= ratio; continue
            L = order_l[r]
            if L == sc.m[i]: T *= ratio; continue
            j = owner.get(L)
            if j is not None: idx, vals = np.array([i, j]), np.array([L, sc.m[i]])
            else: idx, vals = np.array([i]), np.array([L])
            d, st = sc.propose(idx, vals)
            if d >= 0 or rng.random() < math.exp(max(-700, d / T)):
                old = int(sc.m[i]); sc.accept(st); cur += d
                if j is not None: owner[L] = i; owner[old] = j
                else: owner.pop(old, None); owner[L] = i
                if cur > best: best, bm = cur, sc.m.copy()
            T *= ratio
        keys.append((best, bm))
    keys.sort(key=lambda x: -x[0])
    bm = keys[0][1]; tokw = np.bincount(seq, minlength=S + 1).astype(float); tokw[[0, UNK, B]] = 0
    ag = max([float(((k == bm) * tokw).sum() / tokw.sum()) for _, k in keys[1:]] or [0.0])
    dec = [[lm.alphabet[bm[sid[c]]] if c in sid else "?" for c in cs] for cs in cw_chunks]
    return dec, ag, keys[0][0] / tab.n_events

if __name__ == "__main__":
    n_words, restarts, iters, mode, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
    seg_mode = sys.argv[6] if len(sys.argv) > 6 else "learn"
    t = time.time(); lm = syl_lm(2000); print(f"syllable LM: {lm.A} symbols ({time.time()-t:.0f}s)", flush=True)
    vocab = {w for w in pickle.load(open(latseg.X + "latlib_words_lm.pkl", "rb"))[:4000000] if len(w) >= 7}
    H = pickle.load(open(latseg.X + "latlib_hold.pkl", "rb"))["calib"]; fs = sorted(H)
    words = H[fs[seed % len(fs)]][2000:2000 + n_words]
    rng = random.Random(seed)
    if mode == "shufchar":
        L = list("".join(words)); rng.shuffle(L); it_ = iter(L); words = ["".join(next(it_) for _ in w) for w in words]
    codes = make_table(Counter(s for w in words for s in syllables(w)), rng)
    cw, truth = encrypt(words, codes, rng)
    print(f"{fs[seed % len(fs)]} mode {mode}: {len(cw)} words, {len(set(cw))} types, mean len {np.mean([len(w) for w in cw]):.2f}; e.g. {' '.join(cw[:8])}", flush=True)
    t = time.time()
    if seg_mode == "oracle":
        tc = {}
        for w, (sy, ls) in zip(cw, truth):
            out, p = [], 0
            for L in ls: out.append(w[p:p + L]); p += L
            tc[w] = out
        seg = tc
    else:
        seg = seg_gibbs(list(Counter(cw)), seed=seed)
    chunks = [seg[w] for w in cw]
    sacc = np.mean([[len(c) for c in seg[w]] == ls for w, (_, ls) in zip(cw, truth)])
    print(f"segmentation ({seg_mode}) word-exact {sacc:.3f}; chunk types {len(set(c for cs in chunks for c in cs))} (true {len(codes)}) ({time.time()-t:.0f}s)", flush=True)
    t = time.time(); dec, ag, sc_ = solve(chunks, lm, restarts, iters, seed=seed)
    tokacc = np.mean([a == b for d, (sy, _) in zip(dec, truth) if len(d) == len(sy) for a, b in zip(d, sy)])
    wacc = np.mean([d == sy for d, (sy, _) in zip(dec, truth)])
    dw = ["".join(d) for d in dec]; lc = np.mean([w in vocab for w in dw if len(w) >= 7 and "?" not in w])
    print(f"solve: syllable acc {tokacc:.3f} word acc {wacc:.3f} agreement {ag:.3f} score/ev {sc_:.3f} long-word-in-dict {lc:.3f} ({time.time()-t:.0f}s)", flush=True)
    print("decoded:", " ".join(dw[:25])); print("truth:  ", " ".join(words[:25]))
