"""Probe 12: compound attack end-to-end at VOYNICH'S ENDING PROFILE (E026: ~28 ending classes, partly marked).
Plaintext Latin -> stem + ending class, class = last 2 letters of the Latin ending (an abbreviated ending system,
35 classes, 22 cover 95%). Codes in 20 EVA glyphs; ending glyphs drawn from mix(own 6, all 20; alpha), stems from
mix(other 14, all 20; alpha). alpha=0 fully marked, 1 unmarked. Pipeline: learned split -> stage 1 (classes) ->
stage 2 (stems). Reports split acc, features, class acc, stem acc, whole-word acc, restart agreement, pair-cover."""
import sys, time, random, math, pickle, os
import numpy as np
from collections import Counter, defaultdict
from scipy.optimize import linear_sum_assignment
sys.path.insert(0, "/Users/arhampartapjain/voynich-ai-cryptolinguist/src")
import latseg
from latseg import seg, words_of
from wordsub_proto import WordLM, NgramTable, DeltaScorer
import endfirst as EF
import ctxassign as CA
from vcl.solvers.segment import segment_types, ending_features

EVA = list("ydnlrmacehikopqstfgx")
cls = lambda e: e[-2:]

def ref_class():
    p = latseg.X + "latlib_sc_lm.pkl"
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    out = [(s, cls(e)) for s, e in map(seg, pickle.load(open(latseg.X + "latlib_words_lm.pkl", "rb")))]
    pickle.dump(out, open(p, "wb")); return out

def ref_stats_c(rsp, E, chunk=24000, n_chunks=300):
    K = len(E); ix = {e: i for i, e in enumerate(E)}
    ends = np.array([ix[e] for _, e in rsp])
    uni = np.bincount(ends, minlength=K) + 0.5
    big = np.zeros((K, K)); np.add.at(big, (ends[:-1], ends[1:]), 1); big += 0.1
    par = np.zeros((K, K)); rng = np.random.default_rng(0)
    for st in rng.integers(0, len(rsp) - chunk, n_chunks):
        P = defaultdict(set)
        for s, e in rsp[st:st + chunk]:
            if e: P[s].add(ix[e])
        for es in P.values():
            for a in es:
                for b in es:
                    if a != b: par[a, b] += 1
    par += 0.1
    return np.log(uni / uni.sum()), np.log(big / big.sum(1, keepdims=True)), np.log(par / par.sum())

def codes(items, lo, hi, rng, taken, own, alpha):
    out = {}
    for it in items:
        while True:
            c = "".join(rng.choice(EVA) if rng.random() < alpha else rng.choice(own) for _ in range(rng.randint(lo, hi)))
            if c not in taken: taken.add(c); out[it] = c; break
    return out

def make_cipher(sp, alpha, seed, stem_shuffle=False):
    rng = random.Random(seed); taken = set()
    if stem_shuffle:                     # meaningless control: classes kept in order, stems re-paired at random
        st = [s for s, _ in sp]; rng.shuffle(st); sp = [(s, e) for s, (_, e) in zip(st, sp)]
    ec = codes(sorted({e for _, e in sp if e}), 1, 3, rng, taken, EVA[:6], alpha); ec[""] = ""
    sc = codes(sorted({s for s, _ in sp}), 2, 5, rng, taken, EVA[6:], alpha)
    return [sc[s] + ec[e] for s, e in sp], [len(sc[s]) for s, _ in sp], sp

def stage1(sufs, stems, E, ref, restarts, iters=200000):
    Luni, Lseq, Lpar = ref; KE = len(E)
    top = [f for f, _ in Counter(f for f in sufs if f).most_common(KE - 1)]
    cid = {f: i + 1 for i, f in enumerate(top)}; cid[""] = 0
    ce = np.array([cid.get(f, 0) for f in sufs]); n = np.bincount(ce, minlength=KE).astype(float)
    C = np.zeros((KE, KE)); np.add.at(C, (ce[:-1], ce[1:]), 1)
    P = defaultdict(set)
    for s, c in zip(stems, ce):
        if c: P[s].add(c)
    Cp = np.zeros((KE, KE))
    for es in P.values():
        for a in es:
            for b in es:
                if a != b: Cp[a, b] += 1
    args = (n, C, Cp, Luni, Lseq, Lpar, 1.0)
    oc = [c for c in np.argsort(-n) if c != 0]; ol = [l for l in np.argsort(-Luni) if l != 0]
    m0 = np.zeros(KE, int)
    for c, l in zip(oc, ol): m0[c] = l
    keys = [EF.anneal(m0, np.arange(1, KE), KE, args, iters, np.random.default_rng(r), 50.0) for r in range(restarts)]
    b, m = max(keys, key=lambda x: x[1])[::-1]
    ag = float(np.mean([np.mean(k[ce] == m[ce]) for k, _ in keys]))
    return [E[m[c]] for c in ce], ag

def anneal_u(sc, U, cand, cand_sym, m0, S, K, iters, rng, t0, wu, t1=0.05, p_swap=0.3):
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

def stage2(stems, dec_end, E, lm, pe, restarts, wu=1.0, iters=2000000, rounds=6):
    ix = {e: i for i, e in enumerate(E)}; KE = len(E); N = len(stems); K = lm.UNK
    cnt = Counter(stems); top = [c for c, k in cnt.most_common() if k >= 2]
    sid = {c: k + 1 for k, c in enumerate(top)}; S = len(top) + 1
    seq = np.array([sid.get(c, S) for c in stems]); tab = NgramTable(seq, order=2)
    sc = DeltaScorer(tab, lm, seq, S, kl_weight=0.0)
    nse = np.zeros((S + 1, KE))
    for c, e in zip(stems, dec_end): nse[sid.get(c, S), ix[e]] += 1
    mu = N * pe[1:K]
    with np.errstate(all="ignore"):
        U = np.zeros((S + 1, K - 1)); U[1:S] = nse[1:S] @ np.log(mu).T - mu.sum(1)[None, :]
    kc = 40; cand = np.zeros((S + 1, kc), int); cand[1:S] = np.argsort(-U[1:S], axis=1)[:, :kc]
    pos_of = {}
    for i in range(1, S):
        for L in cand[i, :10]: pos_of.setdefault(int(L) + 1, []).append(i)
    cand_sym = [[]] + [sorted({j for L in cand[i, :10] for j in pos_of.get(int(L) + 1, []) if j != i}) for i in range(1, S)] + [[]]
    r_, c_ = linear_sum_assignment(-U[1:S]); m0 = np.zeros(S + 1, int); m0[1 + r_] = c_ + 1; m0[S] = lm.UNK
    tot = lambda m: sc.reset(m) + wu * U[np.arange(1, S), m[1:S] - 1].sum()
    keys = []
    for r in range(restarts):
        rng = np.random.default_rng(1000 + r)
        m, cur = anneal_u(sc, U, cand, cand_sym, m0, S, K, iters, rng, t0=max(1.0, 0.01 * N), wu=wu)
        for it in range(rounds):
            m2 = CA.ctx_round(m, seq, S, K, lm, U, wu)
            m2, b2 = anneal_u(sc, U, cand, cand_sym, m2, S, K, iters // 2, rng, t0=2.0, wu=wu)
            if b2 > cur: m, cur = m2, b2
        keys.append((cur, m))
    cur, best = max(keys, key=lambda x: x[0])
    tokw = np.array([0] + [cnt[c] for c in top], float)
    ag = float(np.mean([((k == best)[1:S] * tokw[1:S]).sum() / tokw[1:S].sum() for _, k in keys]))
    fq = tokw >= 20
    agf = float(np.mean([((k == best)[1:S] * (tokw * fq)[1:S]).sum() / (tokw * fq)[1:S].sum() for _, k in keys]))
    dec = [lm.alphabet[best[sid[c]]] if c in sid else "?" for c in stems]
    return dec, (ag, agf), cur / N

if __name__ == "__main__":
    alpha, n_plain, r1, r2, mode = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    t = time.time(); rsp = ref_class()
    E = [""] + sorted({e for _, e in rsp if e}); KE = len(E); ix = {e: i for i, e in enumerate(E)}
    ref = ref_stats_c(rsp, E); lm = WordLM([s for s, _ in rsp], 6000); K = lm.UNK
    pe = np.zeros((lm.A, KE))
    for s, e in rsp: pe[lm.idx.get(s, lm.UNK), ix[e]] += 1
    pe[lm.UNK] /= max(1, sum(1 for s in set(s for s, _ in rsp) if s not in lm.idx)); pe = (pe + 0.01) / len(rsp)
    pairs = Counter(rsp)
    print(f"ref ready {time.time()-t:.0f}s; {KE-1} classes", flush=True)
    group = sys.argv[7] if len(sys.argv) > 7 else "calib"
    if seed == 1: plain = words_of("la", "tune")[:n_plain]
    else:
        H = pickle.load(open(latseg.X + "latlib_hold.pkl", "rb"))[group]; fs = sorted(H)
        plain = H[fs[(seed - 2) % len(fs)]][2000:2000 + n_plain]; print("plaintext", fs[(seed - 2) % len(fs)], len(plain), flush=True); sp = [(s, cls(e)) for s, e in map(seg, plain)]
    if mode in ("rugg_rep", "self_citation_rep"):
        sys.path.insert(0, "/Users/arhampartapjain/voynich-ai-cryptolinguist/experiments")
        import e011_twin_search as EE
        from vcl.synthetic import edge_twins as X, rep_twins as R, twins as T
        lines, _, dev_words, _ = EE.voynich_lines()
        p = R.random_params(mode, random.Random(seed))
        g = R.generate(mode, p, seed, T.chunk_pools(dev_words), n_plain, X.coupling_matrix(lines), R.null_pool(dev_words))
        cip = [w for l in g["lines"] for w in l if w][:n_plain]; tb = [-1] * len(cip); sp = [("#", "#")] * len(cip)
    else:
        cip, tb, sp = make_cipher(sp, alpha, seed, stem_shuffle=(mode == "shuf"))
    t = time.time(); split = segment_types(Counter(cip), max_suf=4, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, seed=seed, smooth=0.01)
    pb = [split[w] for w in cip]; f = ending_features(cip, split)
    print(f"alpha {alpha} mode {mode}: split acc {np.mean([a == b for a, b in zip(pb, tb)]):.3f} "
          f"feats { {k: round(v, 3) for k, v in f.items()} } ({time.time()-t:.0f}s)", flush=True)
    sufs = [w[b:] for w, b in zip(cip, pb)]; stems = [w[:b] for w, b in zip(cip, pb)]
    t = time.time(); dec_e, ag1 = stage1(sufs, stems, E, ref, r1)
    print(f"stage 1: class acc {np.mean([d == e for d, (_, e) in zip(dec_e, sp)]):.3f} agreement {ag1:.3f} ({time.time()-t:.0f}s)", flush=True)
    t = time.time(); dec_s, ag2, sc_ = stage2(stems, dec_e, E, lm, pe, r2)
    sacc = np.mean([d == s for d, (s, _) in zip(dec_s, sp)]); wacc = np.mean([d == s and de == e for d, de, (s, e) in zip(dec_s, dec_e, sp)])
    pc = np.mean([pairs[(d, de)] >= 5 for d, de in zip(dec_s, dec_e) if d != "?"])
    print(f"stage 2: stem acc {sacc:.3f} whole-word {wacc:.3f} agreement {ag2[0]:.3f} freq-agreement {ag2[1]:.3f} score/tok {sc_:.3f} pair-cover {pc:.3f} ({time.time()-t:.0f}s)", flush=True)
    perm = np.random.default_rng(7).permutation(len(stems))
    _, _, sc_null = stage2([stems[i] for i in perm], [dec_e[i] for i in perm], E, lm, pe, 1)
    print(f"self-null: shuffled-order score/tok {sc_null:.3f}; gap {sc_ - sc_null:.3f}", flush=True)
    import json
    open("cmp_calib.jsonl", "a").write(json.dumps(dict(mode=mode, seed=seed, alpha=alpha, split_acc=float(np.mean([a == b for a, b in zip(pb, tb)])),
        **f, class_acc=float(np.mean([d == e for d, (_, e) in zip(dec_e, sp)])), ag1=ag1, stem_acc=float(sacc), word_acc=float(wacc),
        ag=ag2[0], agf=ag2[1], score=sc_, null=sc_null, gap=sc_ - sc_null, pair_cover=float(pc))) + "\n")
    print("decoded:", " ".join(f"{d}-{e}" for d, e in zip(dec_s[:30], dec_e[:30])))
    print("truth:  ", " ".join(f"{s}-{e}" for s, e in sp[:30]))
