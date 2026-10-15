"""Character n-gram models on the default event stream (see stream.py).

* `Unigram`: add-one unigram over the 28 predicted symbols.
* `KneserNey`: interpolated modified Kneser-Ney (Chen & Goodman 1998), orders 1..6,
  three discounts per order (D1, D2, D3+) estimated from count-of-counts, continuation
  counts for lower orders (raw counts for n-grams that start with the BOS pad, as in KenLM),
  final interpolation with the uniform distribution over the fixed 28-symbol vocabulary,
  so no event ever has zero probability.
* `VarietyMixKN`: Currier-variety conditioning by linear interpolation of a variety-specific
  KN model with the pooled KN model (lambda tuned on an inner validation split).

All models expose `dist(history, line)` (a length-V probability vector), `line_bits(line)`,
`score(lines)`, `sample_lines(conds, seed)`, and `save(path) -> sha256`.
"""
from __future__ import annotations

import hashlib
import math
import pickle
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from vcl.models.stream import BOS_ID, LE_ID, V, Line, decode_events, encode_line


def score_bits(model, lines: list[Line]) -> dict:
    """Shared scorer: total bits over all events; bits/glyph and bits/word per protocol section 2."""
    bits = 0.0
    words = glyphs = 0
    for ln in lines:
        bits += float(np.sum(model.line_bits(ln)))
        words += ln.n_words
        glyphs += ln.n_glyphs
    events = words + glyphs
    return {"bits": bits, "events": events, "words": words, "glyphs": glyphs,
            "bits_per_glyph": bits / events, "bits_per_word": bits / words}


class _Base:
    order = 1

    def line_bits(self, line: Line) -> np.ndarray:
        ids = encode_line(line)
        hist = [BOS_ID] * max(self.order - 1, 0)
        out = np.empty(len(ids))
        for j, w in enumerate(ids):
            out[j] = -math.log2(self.dist(hist, line)[w])
            hist.append(w)
        return out

    def score(self, lines):
        return score_bits(self, lines)

    def sample_lines(self, conds, seed: int = 0, max_events: int = 200) -> list[list[str]]:
        """conds: list of (currier, para_start). Returns sampled word lists (ancestral sampling)."""
        rng = np.random.default_rng(seed)
        out = []
        for currier, para in conds:
            stub = Line("S", "S", 0, currier, para, [])
            hist = [BOS_ID] * max(self.order - 1, 0)
            ids = []
            for _ in range(max_events):
                w = int(rng.choice(V, p=self.dist(hist, stub)))
                ids.append(w)
                hist.append(w)
                if w == LE_ID:
                    break
            out.append(decode_events(ids))
        return out

    def save(self, path) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(self, protocol=4))
        return hashlib.sha256(path.read_bytes()).hexdigest()


class Unigram(_Base):
    name = "unigram"

    def fit(self, lines):
        c = np.ones(V)
        for ln in lines:
            for w in encode_line(ln):
                c[w] += 1
        self.p = c / c.sum()
        return self

    def dist(self, hist, line=None):
        return self.p


class KneserNey(_Base):
    def __init__(self, order: int = 5):
        assert 1 <= order <= 8
        self.order = order
        self.name = f"kn{order}"
        self._cache = {}

    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if k != "_cache"}

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._cache = {}

    def _grams(self, lines):
        n = self.order
        for ln in lines:
            padded = [BOS_ID] * (n - 1) + encode_line(ln)
            for i in range(n - 1, len(padded)):
                yield tuple(padded[i - n + 1:i + 1])

    def fit(self, lines):
        return self._fit_grams(self._grams(lines), self.order)

    def _fit_grams(self, grams, n):
        """grams: iterable of length-n tuples (context..., target); context symbols may be any ids."""
        self._n = n
        raw = [None] + [Counter() for _ in range(n)]
        for g in grams:
            for k in range(1, n + 1):
                raw[k][g[n - k:]] += 1
        adj = [None] * (n + 1)
        adj[n] = raw[n]
        for k in range(n - 1, 0, -1):
            cont = Counter()
            for g in raw[k + 1]:
                cont[g[1:]] += 1           # number of distinct left extensions
            adj[k] = Counter({g: (c if g[0] == BOS_ID else cont[g]) for g, c in raw[k].items()})
        self.discounts = {}
        self.tables = {}
        for k in range(1, n + 1):
            coc = Counter(c for c in adj[k].values() if c <= 4)
            n1, n2, n3, n4 = (coc.get(i, 0) for i in (1, 2, 3, 4))
            if n1 and n2:
                y = n1 / (n1 + 2 * n2)
                d1 = 1 - 2 * y * n2 / n1
                d2 = 2 - 3 * y * n3 / n2 if n2 else 1.0
                d3 = 3 - 4 * y * n4 / n3 if n3 else 1.5
            else:
                d1, d2, d3 = 0.5, 1.0, 1.5
            d = (0.0, min(max(d1, 0.05), 1.0), min(max(d2, 0.05), 2.0), min(max(d3, 0.05), 3.0))
            self.discounts[k] = d
            byctx = defaultdict(lambda: np.zeros(V))
            for g, c in adj[k].items():
                byctx[g[:-1]][g[-1]] = c
            tab = {}
            darr = np.array(d)
            for h, cnt in byctx.items():
                tot = cnt.sum()
                disc = np.minimum(darr[np.minimum(cnt, 3).astype(int)], cnt)
                tab[h] = ((cnt - disc) / tot, float(disc.sum() / tot))
            self.tables[k] = tab
        self._cache = {}
        return self

    def dist(self, hist, line=None):
        n = self.order
        return self._dist_ctx(tuple(hist[len(hist) - (n - 1):]) if n > 1 else ())

    def _dist_ctx(self, ctx):
        n = len(ctx) + 1
        p = self._cache.get(ctx)
        if p is not None:
            return p
        p = np.full(V, 1.0 / V)
        for k in range(1, n + 1):
            h = ctx[len(ctx) - (k - 1):] if k > 1 else ()
            e = self.tables[k].get(h)
            if e is None:
                continue
            p = e[0] + e[1] * p
        self._cache[ctx] = p
        return p


class VarietyMixKN(_Base):
    """P(w|h, v) = lam * KN_v(w|h) + (1 - lam) * KN_pooled(w|h); variety '?' uses the pooled model."""

    def __init__(self, order: int = 5, lam: float = 0.5):
        self.order = order
        self.lam = lam
        self.name = f"kn{order}+variety"

    def fit(self, lines, val_lines=None, grid=(0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0)):
        self.pooled = KneserNey(self.order).fit(lines)
        self.by_var = {v: KneserNey(self.order).fit([l for l in lines if l.currier == v]) for v in ("A", "B")}
        if val_lines:
            best = None
            for lam in grid:
                self.lam = lam
                b = self.score(val_lines)["bits"]
                if best is None or b < best[0]:
                    best = (b, lam)
            self.lam = best[1]
        return self

    def dist(self, hist, line):
        p = self.pooled.dist(hist)
        m = self.by_var.get(line.currier)
        if m is None or self.lam == 0.0:
            return p
        return self.lam * m.dist(hist) + (1 - self.lam) * p


COND_BASE = 64     # ids >= COND_BASE are conditioning symbols (never predicted)


class ConditionedKN(KneserNey):
    """KN char model whose context is (last order-1 stream symbols) + one conditioning symbol
    c = (final glyph of the previous word in the line, or line-start; is the current word line-final).
    The conditioning symbol sits nearest the target, so back-off drops old characters first and
    the condition last. This mirrors the external R2 'M2 conditioned' description (previous
    unit's final glyph + line-final position); their exact implementation is not available.
    NB: the line-final flag is side information about layout (it makes '$' vs '_' predictable)."""

    def __init__(self, order: int = 5):
        super().__init__(order)
        self.name = f"kn{order}+prevfinal+linefinal"

    @staticmethod
    def _conds(ln):
        out = []
        for i, w in enumerate(ln.words):
            g = 26 if i == 0 else ord(ln.words[i - 1][-1]) - 97
            c = COND_BASE + 2 * g + int(i == ln.n_words - 1)
            out += [c] * (len(w) + 1)
        return out

    def _events(self, ln):
        n = self.order
        ids = encode_line(ln)
        padded = [BOS_ID] * (n - 1) + ids
        for j, (w, c) in enumerate(zip(ids, self._conds(ln))):
            yield tuple(padded[j:j + n - 1]) + (c,), w

    def fit(self, lines):
        return self._fit_grams((ctx + (w,) for ln in lines for ctx, w in self._events(ln)), self.order + 1)

    def line_bits(self, line):
        return np.array([-math.log2(self._dist_ctx(ctx)[w]) for ctx, w in self._events(line)])

    def sample_lines(self, *a, **k):
        raise NotImplementedError("line-final flag requires the line length in advance; not used as a generator")
