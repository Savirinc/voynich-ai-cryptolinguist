"""Edge-aware twin mechanisms (E013): word-boundary coupling, respacing and line-end abbreviation.

Three switchable mechanisms layered on existing twin families (vcl.synthetic.twins, naibbe_exact):

  * sandhi (context-dependent variant choice): for each output word, K equivalent candidates are drawn and one is
    chosen with probability proportional to exp(beta * C[last glyph of previous word, first glyph of candidate]).
    For the Naibbe cipher the candidates are alternative table draws for the SAME plaintext unit, so the text stays
    exactly decodable by `naibbe_exact.decode`. For meaningless generators the candidates are alternative draws of
    the generator itself.
  * respacing (spaces are not unit boundaries): words of >= 4 glyphs are split with probability p_split at an
    internal position chosen with weight exp(beta_s * C[left, right]); adjacent words are merged with probability
    p_merge, preferring poorly-coupled joins (weight exp(-beta_s * C)).
  * line-end abbreviation: a line-final word ending in 'iin'/'in' is rewritten with final 'm' with probability p_m
    (the reading m = iin is Bowern & Lindemann 2021's candidate; it keeps the text decodable).

C is a single glyph-coupling matrix estimated from Voynich DEV prose (LOCKED_TEST never read): pointwise log ratio
log P(first = b | last = a) / P(first = b), shrunk toward independence (alpha = 20). It is TARGET-DERIVED: matching edge coupling is
therefore partly by construction, and E013 scores these mechanisms on the remaining, independent features.
"""
from __future__ import annotations

import math
import random
from collections import Counter

from vcl.synthetic import naibbe_exact as NX
from vcl.synthetic import twins as T

EDGE_BOUNDS = dict(beta=(0.0, 4.0), k=(1, 8), p_split=(0.0, 0.3), p_merge=(0.0, 0.15), beta_s=(0.0, 4.0),
                   p_m=(0.0, 1.0))
EDGE_OFF = dict(beta=0.0, k=1, p_split=0.0, p_merge=0.0, beta_s=0.0, p_m=0.0)


def coupling_matrix(lines, alpha: float = 20.0, min_count: int = 50, clip: float = 3.0) -> dict:
    """{(a, b): log ratio} from lines of EVA words (None breaks adjacency). P(b | a) is shrunk toward P(b) with
    alpha pseudo-observations; glyphs seen < min_count times at that edge get 0 (unknown pairs), values are
    clipped to +-clip, so rare glyphs cannot dominate."""
    pairs = Counter()
    for l in lines:
        for x, y in zip(l, l[1:]):
            if x and y:
                pairs[(x[-1], y[0])] += 1
    n = sum(pairs.values())
    pf, na = Counter(), Counter()
    for (a, b), v in pairs.items():
        pf[b] += v; na[a] += v
    lr = lambda a, b: math.log(((pairs[(a, b)] + alpha * pf[b] / n) / (na[a] + alpha)) / (pf[b] / n))
    return {(a, b): max(-clip, min(clip, lr(a, b)))
            for a in na if na[a] >= min_count for b in pf if pf[b] >= min_count}


def _c(C, a, b):
    return C.get((a, b), 0.0)


def _pick(cands, prev, C, beta, rng):
    if prev is None or beta == 0 or len(cands) == 1:
        return cands[0]
    w = [math.exp(beta * _c(C, prev[-1], c[0])) for c in cands]
    return rng.choices(cands, w)[0]


# ------------------------------------------------------------------------------------------------ naibbe + sandhi
def naibbe_sandhi_tokens(plain: str, C: dict, beta: float, k: int, seed: int) -> tuple[list[str], list[str]]:
    """Naibbe (published tables) with context-dependent homophone choice; returns (words, plaintext grams)."""
    key = NX.key({}, 0, plain)
    tab, uni = key["tables"], key["unigrams"]
    rng = random.Random(seed)
    text = "".join(c for c in NX.clean(plain) if c in key["letters"])
    grams = NX._respace(text, rng)
    deck, di = [], 0

    def draw():
        nonlocal deck, di
        if di >= len(deck):
            deck = [t for t, n in NX.CARD_WEIGHTS.items() for _ in range(n)]
            rng.shuffle(deck); di = 0
        di += 1
        return deck[di - 1]

    def one(g):
        if len(g) == 1:
            return tab[("unigram", draw(), g)]
        while True:
            w = tab[("prefix", draw(), g[0])] + tab[("suffix", draw(), g[1])]
            if w not in uni:
                return w

    words, prev = [], None
    for g in grams:
        w = _pick([one(g) for _ in range(max(1, k))], prev, C, beta, rng)
        words.append(w); prev = w
    return words, grams


# ------------------------------------------------------------------------------------------------ meaningless + sandhi
def rugg_sandhi(n_words, params, seed, pools, C, beta, k):
    """Rugg grille stream; each output word is chosen among the next k unused grille outputs (scribe skips ahead)."""
    stream, key = T.rugg_generate(n_words * max(1, k) + k, params, seed, pools)
    rng = random.Random(seed ^ 0xB0B)
    out, buf, it, prev = [], [], iter(stream), None
    while len(out) < n_words:
        while len(buf) < max(1, k):
            try:
                buf.append(next(it))
            except StopIteration:
                break
        if not buf:
            break
        w = _pick(buf, prev, C, beta, rng)
        buf.remove(w); out.append(w); prev = w
    return out, key


def self_citation_sandhi(n_words, params, seed, pools, C, beta, k, width_mean=49.7, width_sd=9.0):
    """Timm & Schinner self-citation with k candidate (source, mutation) draws per word, chosen by edge coupling."""
    p = {**T.SELF_DEFAULTS, **params}
    rng = random.Random(seed)
    smp = T.ChunkSampler(pools, p["tau"], p["p_single"], p["p_mid_final"])
    seeds = [smp.sample("W", rng) for _ in range(int(p["n_seed_words"]))]
    lines, cur, prev, recent, n, width = [], [], [], list(seeds), 0, max(8, rng.gauss(width_mean, width_sd))
    W = int(p["window"])

    def cand():
        r = rng.random()
        if r < p["p_fresh"]:
            src = smp.sample("W", rng)
        elif prev and r < p["p_fresh"] + p["p_prev_line"]:
            j = min(len(prev) - 1, max(0, len(cur) + rng.choice([-1, 0, 0, 1])))
            src = prev[j]
        else:
            src = rng.choice(recent[-W:])
        w = src
        if rng.random() < p["p_mutate"]:
            m = 1 + (int(rng.expovariate(1 / p["extra_mutations"])) if p["extra_mutations"] > 0 else 0)
            for _ in range(min(m, 6)):
                w = T._mutate(w, rng, smp, recent[-W:])
        return w or src

    while n < n_words:
        w = _pick([cand() for _ in range(max(1, k))], cur[-1] if cur else None, C, beta, rng)
        add = len(w) + (1 if cur else 0)
        if cur and sum(len(x) for x in cur) + len(cur) - 1 + add > width:
            lines.append(cur); prev, cur = cur, []
            width = max(8, rng.gauss(width_mean, width_sd))
        cur.append(w); recent.append(w); n += 1
        if len(recent) > 4 * W:
            recent = recent[-2 * W:]
    if cur:
        lines.append(cur)
    return lines, {"seed_words": seeds}


# ------------------------------------------------------------------------------------------------ respacing, line end
def respace(words: list[str], C: dict, p_split: float, p_merge: float, beta_s: float, rng) -> list[str]:
    if p_split == 0 and p_merge == 0:
        return list(words)
    out = []
    for w in words:
        if len(w) >= 4 and rng.random() < p_split:
            pos = list(range(2, len(w) - 1))          # keep >= 2 glyphs on each side
            if pos:
                j = rng.choices(pos, [math.exp(beta_s * _c(C, w[i - 1], w[i])) for i in pos])[0]
                out += [w[:j], w[j:]]
                continue
        out.append(w)
    if p_merge == 0:
        return out
    res = []
    for w in out:
        if res and rng.random() < p_merge * min(1.0, math.exp(-beta_s * _c(C, res[-1][-1], w[0]))):
            res[-1] += w
        else:
            res.append(w)
    return res


def line_end_m(lines, p_m: float, rng):
    if p_m == 0:
        return lines
    out = []
    for l in lines:
        l = list(l)
        if l and l[-1] and rng.random() < p_m:
            w = l[-1]
            if w.endswith("iin"):
                l[-1] = w[:-3] + "m"
            elif w.endswith("in"):
                l[-1] = w[:-2] + "m"
        out.append(l)
    return out


# ------------------------------------------------------------------------------------------------ families
BASES = {"naibbe_edge": "naibbe_exact", "rugg_edge": "rugg_grille", "self_citation_edge": "self_citation"}
IS_LANGUAGE = {"naibbe_edge": True, "rugg_edge": False, "self_citation_edge": False}


def bounds(family: str) -> dict:
    return {**T.FAMILIES[BASES[family]].bounds, **EDGE_BOUNDS}


def defaults(family: str) -> dict:
    return {**T.FAMILIES[BASES[family]].defaults, **EDGE_OFF}


def _clip(family, params):
    out = {}
    for k_, (lo, hi) in bounds(family).items():
        v = min(hi, max(lo, params.get(k_, defaults(family)[k_])))
        out[k_] = int(round(v)) if isinstance(lo, int) and isinstance(hi, int) else float(v)
    return out


def random_params(family, rng):
    return _clip(family, {k_: (rng.randint(lo, hi) if isinstance(lo, int) and isinstance(hi, int)
                               else rng.uniform(lo, hi)) for k_, (lo, hi) in bounds(family).items()})


def perturb_params(family, params, rng, scale=0.15, n_changes=2):
    q = dict(params)
    for k_ in rng.sample(list(bounds(family)), min(n_changes, len(bounds(family)))):
        lo, hi = bounds(family)[k_]
        if isinstance(lo, int) and isinstance(hi, int):
            q[k_] += rng.randint(-max(1, int(round((hi - lo) * scale))), max(1, int(round((hi - lo) * scale))))
        else:
            q[k_] += rng.gauss(0, (hi - lo) * scale)
    return _clip(family, q)


def generate(family, params, seed, pools, n_words, C, plain=None, width_mean=49.7, width_sd=9.0):
    """Returns {'lines', 'is_language', 'words_before_respacing'}."""
    p = {**defaults(family), **params}
    rng = random.Random(seed ^ 0xED6E)
    if family == "naibbe_edge":
        words, _ = naibbe_sandhi_tokens(plain, C, p["beta"], p["k"], seed)
        words = words[:n_words]
        raw = list(words)
        words = respace(words, C, p["p_split"], p["p_merge"], p["beta_s"], rng)
        lines = T.wrap_lines(words, rng, width_mean, width_sd)
    elif family == "rugg_edge":
        base = {k_: p[k_] for k_ in T.FAMILIES["rugg_grille"].bounds}
        words, _ = rugg_sandhi(n_words, base, seed, pools, C, p["beta"], p["k"])
        raw = list(words)
        words = respace(words, C, p["p_split"], p["p_merge"], p["beta_s"], rng)
        lines = T.wrap_lines(words, rng, width_mean, width_sd)
    else:
        base = {k_: p[k_] for k_ in T.FAMILIES["self_citation"].bounds}
        lines, _ = self_citation_sandhi(n_words, base, seed, pools, C, p["beta"], p["k"], width_mean, width_sd)
        raw = [w for l in lines for w in l]
        lines = [respace(l, C, p["p_split"], p["p_merge"], p["beta_s"], rng) for l in lines]
    lines = line_end_m(lines, p["p_m"], rng)
    return {"lines": lines, "is_language": IS_LANGUAGE[family], "words_before_respacing": raw}

