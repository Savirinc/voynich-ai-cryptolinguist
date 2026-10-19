"""Probe 11 (compound idea, step 1): the split is NOT given. Cipher words = code stem + code ending written together
(glyph strings, no separator). Infer the split by unsupervised stem+suffix segmentation (hard-EM, Morfessor-like
MDL cost), then run stage 1 (endfirst) on the inferred endings.
Codes: stems = random strings of 2-5 glyphs; endings = random strings of 1-3 glyphs ('' stays empty); alphabet of
20 glyphs; injective."""
import sys, time, random, math
import numpy as np
from collections import Counter, defaultdict
import latseg
from latseg import seg, words_of
import endfirst as EF

GL = list("abcdefghiklmnopqrsty")

def make_codes(items, lo, hi, rng, taken, gl=GL):
    out = {}
    for it in items:
        while True:
            c = "".join(rng.choice(gl) for _ in range(rng.randint(lo, hi)))
            if c not in taken: taken.add(c); out[it] = c; break
    return out

def segment(types_cnt, max_suf=3, iters=8, alpha=1.0, cost=None):
    """Hard-EM over word TYPES: w = stem + suffix (suffix may be ''). Score log P(stem) + log P(suffix) with
    P from type counts (+alpha), plus an MDL cost per glyph for a stem/suffix not yet in the lexicon."""
    types = list(types_cnt)
    split = {w: len(w) for w in types}                       # init: no suffix
    # init suffix counts: every ending of length 1..max_suf counted once per type (gives frequent endings mass)
    for it in range(iters):
        st, sf = Counter(), Counter()
        if it == 0:
            for w in types:
                st[w] += 1
                for k in range(1, max_suf + 1):
                    if len(w) - k >= 2: sf[w[-k:]] += 1; st[w[:-k]] += 1
        else:
            for w in types:
                b = split[w]; st[w[:b]] += 1; sf[w[b:]] += 1
        Nst, Nsf = sum(st.values()), sum(sf.values())
        Vst, Vsf = len(st) + 1, len(sf) + 1
        changed = 0
        for w in types:
            best, bb = -1e18, len(w)
            for k in range(0, max_suf + 1):
                if len(w) - k < 2: break
                s, f = w[:len(w) - k], w[len(w) - k:]
                lp = math.log((st[s] + alpha) / (Nst + alpha * Vst)) + math.log((sf[f] + alpha) / (Nsf + alpha * Vsf))
                if cost:
                    if st[s] == 0: lp -= cost * len(s)
                    if sf[f] == 0: lp -= cost * len(f)
                if lp > best: best, bb = lp, len(w) - k
            if bb != split[w]: changed += 1; split[w] = bb
        if changed == 0: break
    return split

if __name__ == "__main__":
    n_plain, cost, max_suf = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    mode = sys.argv[4] if len(sys.argv) > 4 else "random"   # random | marked (endings use their own 6 glyphs)
    ref = latseg.latlib()
    E = [""] + list(latseg.END); KE = len(E); ix = {e: i for i, e in enumerate(E)}
    plain = words_of("la", "tune")[:n_plain]; sp = [seg(w) for w in plain]
    rng = random.Random(11011); taken = set()
    EG, SG = (GL[:6], GL[6:]) if mode == "marked" else (GL, GL)
    ecode = make_codes(sorted({e for _, e in sp if e}), 1, 3, rng, taken, EG); ecode[""] = ""
    scode = make_codes(sorted({s for s, _ in sp}), 2, 5, rng, taken, SG)
    cipher = [scode[s] + ecode[e] for s, e in sp]
    true_b = [len(scode[s]) for s, _ in sp]
    print(f"{len(cipher)} cipher words, {len(set(cipher))} types; e.g. {' '.join(cipher[:10])}", flush=True)
    import seg_gibbs; t = time.time(); split = seg_gibbs.gibbs_segment2(list(Counter(cipher)), max_suf=max_suf, a_s=1.0, a_f=cost, init="none", smooth=0.01)
    pb = [split[w] for w in cipher]
    print(f"segmentation {time.time()-t:.0f}s: split-point token accuracy {np.mean([a == b for a, b in zip(pb, true_b)]):.3f}", flush=True)
    # stage 1 on inferred endings: code ids by inferred suffix string (top KE-1 by frequency; others -> '')
    sufs = [w[b:] for w, b in zip(cipher, pb)]; stems_inf = [w[:b] for w, b in zip(cipher, pb)]
    top = [f for f, _ in Counter(f for f in sufs if f).most_common(KE - 1)]
    cid = {f: i + 1 for i, f in enumerate(top)}; cid[""] = 0
    ce = np.array([cid.get(f, 0) for f in sufs])
    print(f"inferred suffix types {len(set(sufs))}, used as codes {len(top)}", flush=True)
    Luni, Lseq, Lpar = EF.ref_stats(ref, E)
    n = np.bincount(ce, minlength=KE).astype(float)
    C = np.zeros((KE, KE)); np.add.at(C, (ce[:-1], ce[1:]), 1)
    P = defaultdict(set)
    for s, c in zip(stems_inf, ce):
        if c: P[s].add(c)
    Cp = np.zeros((KE, KE))
    for es in P.values():
        for a in es:
            for b in es:
                if a != b: Cp[a, b] += 1
    args = (n, C, Cp, Luni, Lseq, Lpar, 1.0)
    oc = [c for c in np.argsort(-n) if c != 0]; ol = [l for l in np.argsort(-Luni) if l != 0]
    m0 = np.zeros(KE, int); rest = [l for l in range(1, KE) if l not in ol[:len(oc)]]
    for c, l in zip(oc, ol): m0[c] = l
    keys = []
    for r in range(4):
        m, b = EF.anneal(m0, np.arange(1, KE), KE, args, 200000, np.random.default_rng(r), 50.0); keys.append((b, m))
        dec = [E[m[c]] for c in ce]
        print(f"  r{r}: score {b:.0f} ending token acc {np.mean([d == e for d, (_, e) in zip(dec, sp)]):.3f}", flush=True)
    b, m = max(keys, key=lambda x: x[0])
    dec = [E[m[c]] for c in ce]
    ag = np.mean([np.mean(k[ce] == m[ce]) for _, k in keys])
    print(f"best: ending token acc {np.mean([d == e for d, (_, e) in zip(dec, sp)]):.3f}; whole-word split+ending right "
          f"{np.mean([d == e and a == bb for d, (_, e), a, bb in zip(dec, sp, pb, true_b)]):.3f}; agreement {ag:.3f}")
