"""Cheap candidate-language ranking from ciphertext statistics (stage A of the language search).

Signals (each a distance, lower = more similar), combined with fixed, untuned unit weights:
  * word-length distribution: Jensen-Shannon divergence between cipher word lengths and the LM's (needs
    boundaries; skipped for boundary-free streams or the nulls family, whose words are inflated by nulls);
  * sorted unigram profile: L1 distance between the cipher's rank-frequency curve and the language's (valid
    for any one-to-one substitution: mono, columnar, nulls after removal; skipped for homophonic / vigenere);
  * alphabet size: |observed glyph types - expected distinct letters in a sample of this size| / 10
    (skipped for homophonic, whose inventory is inflated).
"""
from __future__ import annotations

import numpy as np

from .lm import CharLM


def _js(p, q) -> float:
    p = np.asarray(p, float) + 1e-9; q = np.asarray(q, float) + 1e-9
    p /= p.sum(); q /= q.sum()
    m = (p + q) / 2
    return float(0.5 * (p * np.log(p / m)).sum() + 0.5 * (q * np.log(q / m)).sum())


def _expected_types(lm: CharLM, n: int) -> float:
    keys = sorted(int(k) for k in lm.expected_types)
    xs = np.log(keys); ys = [lm.expected_types[str(k)] for k in keys]
    return float(np.interp(np.log(max(n, 1)), xs, ys))


def language_distances(seq: np.ndarray, S: int, lms: list[CharLM], family: str) -> dict[str, float]:
    if family == "nulls":
        # strip the estimated nulls first, then rank as a monoalphabetic stream
        from .substitution import likely_nulls, relabel, remove_symbols
        seq, S = relabel(remove_symbols(seq, set(likely_nulls(seq, S))))
        family = "mono"
    letters = seq[seq > 0]
    n = len(letters)
    cnt = np.sort(np.bincount(letters, minlength=S + 1)[1:])[::-1].astype(float)
    prof = cnt / max(1, cnt.sum())
    has_b = (seq == 0).any()
    wl = None
    if has_b and family not in ("nulls", "columnar"):
        b = np.nonzero(np.concatenate([[0], seq, [0]]) == 0)[0]
        lens = np.diff(b) - 1
        lens = lens[lens > 0]
        wl = np.bincount(np.minimum(lens, 20), minlength=21)[1:21].astype(float)
    out = {}
    for lm in lms:
        d = 0.0
        if wl is not None:
            d += 5 * _js(wl, lm.wordlen)
        if family not in ("homophonic", "vigenere"):
            lp = np.sort(lm.unigram[1:])[::-1]
            L = max(len(prof), len(lp))
            a = np.zeros(L); a[:len(prof)] = prof
            c = np.zeros(L); c[:len(lp)] = lp
            d += float(np.abs(a - c).sum())
        if family != "homophonic":
            d += abs(S - _expected_types(lm, n)) / 10
        out[lm.lang] = d
    return out
