"""Faster search for many-to-one (homophonic) keys (E017).

  * DeltaScorer: the score of a key is a sum over unique 4-gram rows; changing one or two symbols only changes the
    rows that contain them, so each proposal is re-scored on ~1% of the rows (about 10x faster than
    NgramTable.score on Voynich-sized streams). The unigram-KL penalty (engine.unigram_penalty) is updated
    incrementally too. Results are identical to the full score (tested).
  * anneal_delta: the engine.anneal schedule (geometric t0 -> t1, 30% swaps / 70% re-assignments with letters drawn
    from p_letters) on top of DeltaScorer.
  * cipher_alphabet_lm: the same Kneser-Ney model as lm.build, trained on the same ref books (never tune/test), but
    on text passed through a cleaning function first (e.g. Greshko's clean_line, which maps j->i, k->c, w->uu and
    strips accents), so the LM alphabet equals the cipher's plaintext alphabet.
"""
from __future__ import annotations

import json
import math
from collections import Counter

import numpy as np

from .engine import NgramTable
from .lm import CACHE, ORDER, CharLM, _kn_dense, _ref_text, language_families


class DeltaScorer:
    def __init__(self, table: NgramTable, lm: CharLM, seq: np.ndarray, S: int, kl_weight: float = 1.0):
        self.cols = np.stack(table.cols)
        self.counts = table.counts
        self.flat = lm.flat
        self.A = lm.A
        R = self.cols.shape[1]
        hit = np.zeros((S + 1, R), dtype=bool)
        for k in range(self.cols.shape[0]):
            hit[self.cols[k], np.arange(R)] = True
        self.rows_of = [np.nonzero(hit[s])[0] for s in range(S + 1)]
        self.sym_counts = np.bincount(seq, minlength=S + 1).astype(float)
        self.sym_counts[0] = 0.0
        self.N = max(self.sym_counts.sum(), 1.0)
        self.logp = np.log(np.maximum(lm.unigram, 1e-6))
        self.w = kl_weight

    def _contrib(self, m, rows):
        c = self.cols[:, rows]
        f = m[c[0]]
        for k in range(1, c.shape[0]):
            f = f * self.A + m[c[k]]
        return self.flat[f].astype(np.float64) * self.counts[rows]

    def reset(self, m):
        self.m = m.copy()
        self.c = self._contrib(self.m, np.arange(self.cols.shape[1]))
        self.lp = float(self.c.sum())
        self.mass = np.bincount(self.m, weights=self.sym_counts, minlength=self.A)
        return self.total()

    def _pen_letters(self, mass, letters):
        q = mass[letters] / self.N
        nz = q > 0
        return self.w * self.N * float((q[nz] * (np.log(q[nz]) - self.logp[letters][nz])).sum())

    def penalty(self):
        return self._pen_letters(self.mass, np.arange(self.A))

    def total(self):
        return self.lp - self.penalty()

    def propose(self, idx, vals):
        """Score delta (total, penalty included) of setting m[idx] = vals; returns (delta, state for accept)."""
        rows = self.rows_of[idx[0]] if len(idx) == 1 else np.union1d(self.rows_of[idx[0]], self.rows_of[idx[1]])
        old = self.m[idx].copy()
        self.m[idx] = vals
        newc = self._contrib(self.m, rows)
        self.m[idx] = old
        d_lp = float(newc.sum() - self.c[rows].sum())
        letters = np.unique(np.concatenate([old, vals]))
        mass2 = self.mass[letters].copy()
        for s, a, b in zip(idx, old, vals):
            mass2[np.searchsorted(letters, a)] -= self.sym_counts[s]
            mass2[np.searchsorted(letters, b)] += self.sym_counts[s]
        full2 = self.mass.copy(); full2[letters] = mass2
        d_pen = self._pen_letters(full2, letters) - self._pen_letters(self.mass, letters)
        return d_lp - d_pen, (idx, vals, rows, newc, letters, mass2, d_lp)

    def accept(self, st):
        idx, vals, rows, newc, letters, mass2, d_lp = st
        self.m[idx] = vals
        self.c[rows] = newc
        self.lp += d_lp
        self.mass[letters] = mass2


def anneal_delta(sc: DeltaScorer, m0, p_letters, iters, rng, t0, t1=0.05, p_swap=0.3):
    """Returns (best key, best total score). Same schedule and moves as engine.anneal + substitution._propose_free."""
    S = len(m0) - 1
    cum = np.cumsum(p_letters)
    cur = sc.reset(m0)
    best, best_m = cur, sc.m.copy()
    ratio = (t1 / t0) ** (1.0 / max(iters, 1))
    T = t0
    rand = rng.random(iters)
    kinds = rng.random(iters)
    for it in range(iters):
        if kinds[it] < p_swap:
            i, j = rng.integers(1, S + 1, size=2)
            if i == j or sc.m[i] == sc.m[j]:
                T *= ratio; continue
            idx, vals = np.array([i, j]), np.array([sc.m[j], sc.m[i]])
        else:
            i = int(rng.integers(1, S + 1))
            L = 1 + int(np.searchsorted(cum, rng.random() * cum[-1]))
            if L == sc.m[i]:
                T *= ratio; continue
            idx, vals = np.array([i]), np.array([L])
        d, st = sc.propose(idx, vals)
        if d >= 0 or rand[it] < math.exp(d / T):
            sc.accept(st); cur += d
            if cur > best:
                best, best_m = cur, sc.m.copy()
        T *= ratio
    return best_m, best


class _MetaLM(CharLM):
    def __init__(self, name):  # noqa: D401 - bypass CharLM's build-on-miss for custom variants
        meta = json.loads((CACHE / f"{name}.json").read_text())
        self.lang, self.variant, self.family = meta["lang"], meta["variant"], meta["family"]
        self.alphabet = meta["alphabet"]; self.idx = {c: i for i, c in enumerate(self.alphabet)}
        self.A = len(self.alphabet); self.H = meta["H"]; self.H_by_len = meta["H_by_len"]
        self.unigram = np.array(meta["unigram"]); self.wordlen = None; self.expected_types = {}
        self.logp = np.load(CACHE / f"{name}.npy", mmap_mode="r"); self._flat = None; self._vocab = None


_CLM = {}


def _build_nospace(name: str, body: str, lang: str, family: str) -> None:
    letters = Counter(body)
    alphabet = [" "] + [c for c, _ in letters.most_common()]
    idx = {c: i for i, c in enumerate(alphabet)}
    ids = np.array([idx[c] for c in body], dtype=np.int64)
    cut = int(len(ids) * 0.95)
    A = len(alphabet)
    logp = _kn_dense(np.concatenate([np.zeros(ORDER - 1, dtype=np.int64), ids[:cut]]), A)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(CACHE / f"{name}.npy", logp)
    flat = logp.reshape(-1)
    held = ids[cut:]
    g = np.zeros(len(held) - ORDER + 1, dtype=np.int64)
    for k in range(ORDER):
        g = g * A + held[k:len(held) - ORDER + 1 + k]
    lp = flat[g]
    H_by_len = {str(L): float(-np.mean([lp[i:i + L].mean() for i in range(0, len(lp) - L, max(1, L // 2))]))
                for L in (100, 300, 1000, 3000)}
    uni = np.zeros(A)
    for c, v in letters.items():
        uni[idx[c]] = v
    uni /= uni.sum()
    meta = {"version": "clm-v1", "lang": lang, "family": family, "variant": name.split("_", 1)[-1],
            "alphabet": alphabet, "H": float(-lp.mean()), "H_by_len": H_by_len, "unigram": uni.tolist(),
            "train_chars": cut}
    (CACHE / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False))


def cipher_alphabet_lm(lang: str, clean, tag: str = "naibbe") -> CharLM:
    """No-space KN-4 LM over clean(ref text). Cached as data/derived/lm_cache/{lang}_{tag}_nospace.*"""
    name = f"{lang}_{tag}_nospace"
    if name in _CLM:
        return _CLM[name]
    if not (CACHE / f"{name}.json").exists():
        _build_nospace(name, clean(_ref_text(lang)), lang, language_families()[lang])
    _CLM[name] = _MetaLM(name)
    return _CLM[name]


def lm_from_text(text: str, name: str, clean=None) -> CharLM:
    """No-space KN-4 letter LM from ANY text you supply (e.g. a medieval Latin or Old Italian corpus), usable
    wherever the solvers take a CharLM. `clean` defaults to the Naibbe plaintext alphabet (naibbe_exact.clean).
    Cached as data/derived/lm_cache/custom_{name}_nospace.*; delete those files to rebuild."""
    if clean is None:
        from vcl.synthetic.naibbe_exact import clean
    key = f"custom_{name}_nospace"
    if key not in _CLM:
        if not (CACHE / f"{key}.json").exists():
            _build_nospace(key, clean(text), name, "custom")
        _CLM[key] = _MetaLM(key)
    return _CLM[key]
