"""Bayesian stem+suffix segmentation over word TYPES (Goldwater-style Dirichlet-multinomial with a base
distribution that charges for new lexicon entries). P(stem s) = (n_s + a_s P0(s)) / (N + a_s), P0 = geometric
length * uniform glyph; same for suffixes (suffix '' allowed). Annealed Gibbs sampling over each type's split."""
import math, random
from collections import Counter

def gibbs_segment(types, n_glyph, max_suf=3, min_stem=2, a_s=1.0, a_f=1.0, p_stop=0.3, sweeps=60, t0=3.0, t1=1.0, seed=0):
    rng = random.Random(seed)
    lg = math.log(1.0 / n_glyph)
    def lp0(x): return len(x) * (lg + math.log(1 - p_stop)) + math.log(p_stop)
    split = {}
    st, sf = Counter(), Counter()
    for w in types:                       # random init
        ks = [k for k in range(0, max_suf + 1) if len(w) - k >= min_stem]
        b = len(w) - rng.choice(ks); split[w] = b; st[w[:b]] += 1; sf[w[b:]] += 1
    N = len(types)
    order = list(types)
    for sw in range(sweeps):
        T = t0 * (t1 / t0) ** (sw / max(1, sweeps - 1))
        rng.shuffle(order)
        for w in order:
            b = split[w]; st[w[:b]] -= 1; sf[w[b:]] -= 1
            opts, lps = [], []
            for k in range(0, max_suf + 1):
                if len(w) - k < min_stem: break
                s, f = w[:len(w) - k], w[len(w) - k:]
                lp = math.log(st[s] + a_s * math.exp(lp0(s))) + math.log(sf[f] + a_f * math.exp(lp0(f)))
                opts.append(len(w) - k); lps.append(lp / T)
            mx = max(lps); ps = [math.exp(x - mx) for x in lps]; r = rng.random() * sum(ps)
            for o, p in zip(opts, ps):
                r -= p
                if r <= 0: b = o; break
            split[w] = b; st[w[:b]] += 1; sf[w[b:]] += 1
    return split


def gibbs_segment2(types, max_suf=3, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, seed=0, smooth=0.5,
                   init="random"):
    """As gibbs_segment, but the base distributions P0 are LEARNED per class: P0_stem(x) and P0_suf(x) use separate
    glyph unigrams and length distributions, re-estimated after every sweep from the current stem and suffix lexicons.
    A suffix written in glyphs that suffixes rarely use is then expensive (lets the model find 'ending glyphs')."""
    rng = random.Random(seed)
    glyphs = sorted({g for w in types for g in w})
    def fit(lex):
        gc = Counter(g for x in lex for g in x); tot = sum(gc.values()) + smooth * len(glyphs)
        q = {g: math.log((gc[g] + smooth) / tot) for g in glyphs}
        lc = Counter(len(x) for x in lex); lt = sum(lc.values()) + smooth * 8
        ql = {L: math.log((lc[L] + smooth) / lt) for L in range(0, 8)}
        return lambda x: ql.get(len(x), -30.0) + sum(q[g] for g in x)
    split, st, sf = {}, Counter(), Counter()
    for w in types:
        ks = [k for k in range(0, max_suf + 1) if len(w) - k >= min_stem]
        b = len(w) - (rng.choice(ks) if init == "random" else 0); split[w] = b; st[w[:b]] += 1; sf[w[b:]] += 1
    order = list(types)
    for sw in range(sweeps):
        P0s, P0f = fit([x for x in st if st[x] > 0]), fit([x for x in sf if sf[x] > 0])
        T = t0 * (t1 / t0) ** (sw / max(1, sweeps - 1))
        rng.shuffle(order)
        for w in order:
            b = split[w]; st[w[:b]] -= 1; sf[w[b:]] -= 1
            opts, lps = [], []
            for k in range(0, max_suf + 1):
                if len(w) - k < min_stem: break
                s, f = w[:len(w) - k], w[len(w) - k:]
                lp = math.log(st[s] + a_s * math.exp(P0s(s))) + math.log(sf[f] + a_f * math.exp(P0f(f)))
                opts.append(len(w) - k); lps.append(lp / T)
            mx = max(lps); ps = [math.exp(x - mx) for x in lps]; r = rng.random() * sum(ps)
            for o, p in zip(opts, ps):
                r -= p
                if r <= 0: b = o; break
            split[w] = b; st[w[:b]] += 1; sf[w[b:]] += 1
    return split
