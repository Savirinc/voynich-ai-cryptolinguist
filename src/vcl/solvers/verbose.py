"""Attack on the Naibbe-class verbose homophonic cipher (E016), given the glyph-string INVENTORY but not the key.

Hypothesis class (E013-E015 working model): each word is a unigram glyph string (1 letter) or prefix + suffix
(2 letters); the strings come from the published Naibbe inventory (Greshko 2025), but WHICH letter each string
stands for is unknown. The attack:
  1. parse every word with the inventory (unigram, else the first prefix+suffix split; unparseable words dropped);
  2. treat each (role, string) component as a cipher symbol of a homophonic substitution, without word boundaries;
  3. many-to-one simulated annealing under a 4-gram no-space character LM with the unigram-KL penalty
     (vcl.solvers.engine), `restarts` independent restarts, best total score kept.
Also: secret-key generation and a labelled encoder for known-answer tests.
"""
from __future__ import annotations

import random
from collections import defaultdict

import numpy as np

from vcl.solvers.engine import NgramTable, anneal, freq_init, unigram_penalty
from vcl.solvers.lm import CharLM
from vcl.solvers.substitution import T0_FACTOR, _propose_free
from vcl.synthetic import edge_twins as X
from vcl.synthetic import naibbe_exact as NX


def inventory() -> dict[str, set]:
    tab = NX.load_tables()
    return {r: {g for (s, _, _), g in tab.items() if s == r} for r in ("unigram", "prefix", "suffix")}


def random_key(seed: int) -> dict:
    """Secret key: the published glyph strings, letters permuted independently within each (state, table)."""
    tab = NX.load_tables()
    letters = sorted({l for (_, _, l) in tab})
    rng = random.Random(seed)
    key = {}
    for st in ("unigram", "prefix", "suffix"):
        for t in NX.TABLES:
            perm = letters[:]; rng.shuffle(perm)
            for a, b in zip(letters, perm):
                key[(st, t, a)] = tab[(st, t, b)]
    return key


def encode_labelled(text: str, key: dict, C: dict, nulls: dict, seed: int, beta=2.0, k=6, p_null=0.02, p_rep=0.01,
                    p_merge=0.04, p_m=0.5, width=(49.7, 9.0)):
    """E014-style encryption of cleaned `text` with a secret key. Returns (lines, labels): labels[i][j] is the
    plaintext letters carried by word j of line i ('' for nulls and ditto copies; merged words concatenate)."""
    rng = random.Random(seed)
    uni = {g for (s, _, _), g in key.items() if s == "unigram"}
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
            return key[("unigram", draw(), g)]
        while True:
            w = key[("prefix", draw(), g[0])] + key[("suffix", draw(), g[1])]
            if w not in uni:
                return w

    ks, ws = list(nulls), list(nulls.values())
    words, labels, prev = [], [], None
    for g in grams:
        if rng.random() < p_null:
            words.append(rng.choices(ks, ws)[0]); labels.append("")
        w = X._pick([one(g) for _ in range(k)], prev, C, beta, rng)
        words.append(w); labels.append(g); prev = w
        if rng.random() < p_rep:
            words.append(w); labels.append("")
    mw, ml = [], []
    for w, l in zip(words, labels):
        if mw and rng.random() < p_merge * min(1.0, np.exp(-2.0 * C.get((mw[-1][-1], w[0]), 0.0))):
            mw[-1] += w; ml[-1] += l
        else:
            mw.append(w); ml.append(l)
    lines, labs, cur, cl, n, target = [], [], [], [], 0, max(8, rng.gauss(*width))
    for w, l in zip(mw, ml):
        if cur and n + len(w) + 1 > target:
            lines.append(cur); labs.append(cl); cur, cl, n, target = [], [], 0, max(8, rng.gauss(*width))
        cur.append(w); cl.append(l); n += len(w) + (1 if n else 0)
    if cur:
        lines.append(cur); labs.append(cl)
    out = []
    for l in lines:
        l = list(l)
        if rng.random() < p_m and l[-1].endswith("iin"):
            l[-1] = l[-1][:-3] + "m"
        out.append(l)
    return out, labs


def parse_word(w: str, inv: dict):
    if w in inv["unigram"]:
        return [("U", w)]
    for i in range(1, len(w)):
        if w[:i] in inv["prefix"] and w[i:] in inv["suffix"]:
            return [("P", w[:i]), ("S", w[i:])]
    return None


def components(words: list[str], inv: dict | None = None):
    """-> (int symbol stream 1..S, owner word index per component, symbol names, n unparsed words)."""
    inv = inv or inventory()
    ids, seq, owner, bad = {}, [], [], 0
    for i, w in enumerate(words):
        p = parse_word(w, inv) if w else None
        if p is None:
            bad += 1; continue
        for c in p:
            seq.append(ids.setdefault(c, len(ids) + 1)); owner.append(i)
    names = [None] + sorted(ids, key=ids.get)
    return np.array(seq, dtype=np.int64), owner, names, bad


def attack(words: list[str], lm: CharLM, iters: int = 600_000, restarts: int = 4, seed: int = 0) -> dict:
    seq, owner, names, bad = components(words)
    S = len(names) - 1
    K = lm.A - 1
    tab = NgramTable(seq)
    p = lm.unigram[1:] ** 0.5
    prop = _propose_free(K, p / p.sum())
    pen = unigram_penalty(seq, S, lm)
    rng = np.random.default_rng(seed)
    runs, best = [], None
    for r in range(restarts):
        m0 = freq_init(seq, S, lm, injective=False)
        for _ in range(r * 4):
            m0 = prop(m0, rng)
        res = anneal(tab, lm, m0, prop, iters, rng, t0=max(1.0, T0_FACTOR * len(seq)), t1=0.05, extra=pen)
        pc = tab.score(res.m, lm) / tab.n_events
        runs.append(round(pc, 4))
        if best is None or pc > best[0]:
            best = (pc, res.m)
    alpha = np.array(lm.alphabet)
    dec = alpha[best[1][seq]]
    per_word = defaultdict(str)
    for o, c in zip(owner, dec):
        per_word[o] += c
    return {"lang": lm.lang, "per_char": best[0], "gap": -best[0] - lm.typical_H(len(seq)), "restart_per_char": runs,
            "n_components": len(seq), "n_symbols": S, "n_unparsed": bad,
            "decoded_words": [per_word.get(i, "") for i in range(len(words))],
            "key": {f"{names[s][0]}:{names[s][1]}": lm.alphabet[int(best[1][s])] for s in range(1, S + 1)}}


def char_accuracy(decoded_words: list[str], labels: list[str]) -> float:
    tot = sum(len(l) for l in labels)
    ok = sum(sum(a == b for a, b in zip(d, l)) for d, l in zip(decoded_words, labels) if l)
    return ok / tot if tot else 0.0


def attack_portfolio(words: list[str], lm: CharLM, iters: int = 100_000, restarts: int = 128, seed: int = 0,
                     agree_min: float = 0.9) -> dict:
    """E017 attack: many SHORT independent restarts with the delta scorer (vcl.solvers.fast_anneal).

    Development on non-test keys showed success is a rare early-basin event: 100k-iteration restarts succeed more
    often than 2M-iteration ones, so the budget goes into restarts. Confidence signal: `agreement` = the largest
    fraction of components decoded identically by the best restart and any OTHER restart (independent restarts
    that reach the same plaintext). `n_agree` = restarts whose decode agrees with the best one on >= agree_min."""
    from vcl.solvers.fast_anneal import DeltaScorer, anneal_delta
    seq, owner, names, bad = components(words)
    S = len(names) - 1
    tab = NgramTable(seq)
    sc = DeltaScorer(tab, lm, seq, S)
    p = lm.unigram[1:] ** 0.5
    p = p / p.sum()
    rng = np.random.default_rng(seed)
    m0 = freq_init(seq, S, lm, injective=False)
    t0 = max(1.0, T0_FACTOR * len(seq))
    runs = []
    for _ in range(restarts):
        m, s = anneal_delta(sc, m0, p, iters, rng, t0=t0)
        runs.append((s, m))
    runs.sort(key=lambda x: -x[0])
    best_s, best_m = runs[0]
    dec_best = best_m[seq]
    agrees = [float(np.mean(m[seq] == dec_best)) for _, m in runs[1:]]
    alpha = np.array(lm.alphabet)
    per_word = defaultdict(str)
    for o, c in zip(owner, alpha[dec_best]):
        per_word[o] += c
    lp = tab.score(best_m, lm) / tab.n_events
    return {"lang": lm.lang, "per_char": lp, "gap": -lp - lm.typical_H(len(seq)),
            "objective_per_char": best_s / tab.n_events,
            "restart_objective": [round(s / tab.n_events, 4) for s, _ in runs],
            "agreement": max(agrees) if agrees else 0.0, "agreements_sorted": sorted((round(a, 3) for a in agrees),
                                                                                     reverse=True)[:20], "n_agree": int(sum(a >= agree_min for a in agrees)),
            "n_components": len(seq), "n_symbols": S, "n_unparsed": bad,
            "decoded_words": [per_word.get(i, "") for i in range(len(words))],
            "key": {f"{names[s][0]}:{names[s][1]}": lm.alphabet[int(best_m[s])] for s in range(1, S + 1)}}


def lexical_coverage(text: str, vocab, min_len: int = 4, max_len: int = 14) -> float:
    """Fraction of letters in a no-space `text` covered by dictionary words (length min_len..max_len) under the
    best segmentation (dynamic programming; uncovered letters allowed). `vocab` is a set of cleaned words."""
    n = len(text)
    cov = [0] * (n + 1)
    for i in range(1, n + 1):
        best = cov[i - 1]
        for L in range(min_len, min(max_len, i) + 1):
            if text[i - L:i] in vocab and cov[i - L] + L > best:
                best = cov[i - L] + L
        cov[i] = best
    return cov[n] / n if n else 0.0
