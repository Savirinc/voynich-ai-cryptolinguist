"""Ciphertext-only statistics used by the encoding-family classifier, the open-set detector and language ranking.

Everything here is computed from the symbol stream alone (what a real decipherer sees).
"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np

BOUNDARY = " "
MAX_P = 12
FEATURE_NAMES: list[str] = []


def _entropy(counts) -> float:
    c = np.asarray([v for v in counts if v > 0], dtype=float)
    if c.sum() == 0:
        return 0.0
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def _ioc(seq) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    c = np.array(list(Counter(seq).values()), dtype=float)
    return float((c * (c - 1)).sum() / (n * (n - 1)))


def word_list(symbols: list[str]) -> list[list[str]]:
    words, cur = [], []
    for s in symbols:
        if s == BOUNDARY:
            if cur:
                words.append(cur); cur = []
        else:
            cur.append(s)
    if cur:
        words.append(cur)
    return words


def features(symbols: list[str]) -> dict[str, float]:
    letters = [s for s in symbols if s != BOUNDARY]
    n = max(1, len(letters))
    cnt = Counter(letters)
    types = len(cnt)
    f: dict[str, float] = {}
    f["log_n"] = math.log(n)
    f["types"] = types
    f["log_types"] = math.log(max(types, 1))
    f["types_per_sqrt_n"] = types / math.sqrt(n)
    f["boundary_rate"] = (len(symbols) - len(letters)) / max(1, len(symbols))
    f["has_boundary"] = float(f["boundary_rate"] > 0)
    f["ioc"] = _ioc(letters)
    f["ioc_x_types"] = f["ioc"] * types                 # ~1 for flat, ~1.7+ for natural-language letters
    h1 = _entropy(cnt.values())
    f["h1"] = h1
    f["h1_norm"] = h1 / math.log2(types) if types > 1 else 0.0
    big = Counter(zip(letters, letters[1:]))
    h2 = _entropy(big.values())
    f["h_cond"] = h2 - h1
    f["mi_bigram"] = 2 * h1 - h2
    f["double_rate"] = sum(v for (a, b), v in big.items() if a == b) / max(1, n - 1)
    freqs = np.array(sorted(cnt.values(), reverse=True), dtype=float) / n
    for k in range(5):
        f[f"top{k + 1}"] = float(freqs[k]) if k < len(freqs) else 0.0
    f["hapax_types"] = sum(1 for v in cnt.values() if v == 1) / max(1, types)
    f["rare_types"] = sum(1 for v in cnt.values() if v / n < 0.005) / max(1, types)
    # periodic IoC
    pi = []
    for p in range(1, MAX_P + 1):
        pi.append(np.mean([_ioc(letters[j::p]) for j in range(p)]) if n >= 2 * p else 0.0)
    pi = np.array(pi)
    base = pi[0] if pi[0] > 0 else 1e-9
    f["pioc_max_ratio"] = float(pi[1:].max() / base) if n > 4 else 1.0
    f["pioc_best_p"] = float(np.argmax(pi) + 1)
    f["pioc_max_x_types"] = float(pi.max() * types)
    # words
    words = word_list(symbols)
    wl = np.array([len(w) for w in words]) if words else np.array([n])
    f["n_words_log"] = math.log(max(1, len(words)))
    f["wl_mean"] = float(wl.mean())
    f["wl_std"] = float(wl.std())
    f["wl_1"] = float(np.mean(wl == 1))
    f["wl_long"] = float(np.mean(wl >= 10))
    wc = Counter(tuple(w) for w in words)
    f["word_ttr"] = len(wc) / max(1, len(words))
    f["word_top_share"] = (wc.most_common(1)[0][1] / len(words)) if words else 0.0
    # positional: symbols that (almost) never start a word although frequent (null indicator)
    init = Counter(w[0] for w in words)
    fin = Counter(w[-1] for w in words)
    freq_types = [s for s, v in cnt.items() if v / n >= 0.01]
    never_init = [s for s in freq_types if init.get(s, 0) / cnt[s] < 0.01]
    f["never_init_types"] = float(len(never_init)) if words and f["has_boundary"] else 0.0
    f["never_init_mass"] = (sum(cnt[s] for s in never_init) / n) if words and f["has_boundary"] else 0.0
    f["init_entropy"] = _entropy(init.values()) if words else 0.0
    f["final_entropy"] = _entropy(fin.values()) if words else 0.0
    return f


def feature_vector(symbols: list[str]) -> tuple[np.ndarray, list[str]]:
    f = features(symbols)
    names = sorted(f)
    return np.array([f[k] for k in names], dtype=float), names
