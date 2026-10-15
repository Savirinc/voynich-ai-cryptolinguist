"""Symbol-stream transformations an agent can compose before handing a stream to the solver.

Each op is (pre, post): `pre` rewrites the ciphertext symbol list; `post` maps a plaintext decoded
from the transformed stream to the reported plaintext. All current ops undo a writing transformation in
`pre`, so their `post` is the identity; the hook exists for future ops (e.g. re-inserting dropped units). Ops encode *hypotheses about the
writing mechanism* ("words are written backwards", "glyph pairs are single units", "these glyphs
are nulls") and never use plaintext knowledge. They operate on public symbols only.
"""
from __future__ import annotations

from collections import Counter

from vcl.synthetic.schema import BOUNDARY


def _words(symbols):
    w, out = [], []
    for s in symbols:
        if s == BOUNDARY:
            out.append(w); w = []
        else:
            w.append(s)
    out.append(w)
    return out


def _join(words):
    out = []
    for i, w in enumerate(words):
        if i:
            out.append(BOUNDARY)
        out.extend(w)
    return out


def reverse_words(symbols, **_):
    return _join([w[::-1] for w in _words(symbols)]), lambda p: p


def reverse_all(symbols, **_):
    return symbols[::-1], lambda p: p


def remove_boundaries(symbols, **_):
    return [s for s in symbols if s != BOUNDARY], lambda p: p


def drop_symbols(symbols, drop=(), **_):
    drop = set(drop)
    return [s for s in symbols if s not in drop], lambda p: p


def merge_pairs(symbols, n_merges=10, **_):
    """BPE-style: repeatedly fuse the most frequent within-word adjacent pair into one unit
    (hypothesis: one plaintext letter is written with several glyphs, a 'verbose' cipher)."""
    words = _words(symbols)
    for _ in range(int(n_merges)):
        c = Counter((a, b) for w in words for a, b in zip(w, w[1:]))
        if not c:
            break
        (a, b), n = c.most_common(1)[0]
        if n < 3:
            break
        new = []
        for w in words:
            out, i = [], 0
            while i < len(w):
                if i + 1 < len(w) and w[i] == a and w[i + 1] == b:
                    out.append(a + b); i += 2
                else:
                    out.append(w[i]); i += 1
            new.append(out)
        words = new
    return _join(words), lambda p: p


def chunk(symbols, k=2, **_):
    """Every k consecutive glyphs inside a word form one unit (fixed-length polygraphic hypothesis)."""
    k = int(k)
    return _join([["".join(w[i:i + k]) for i in range(0, len(w), k)] for w in _words(symbols)]), lambda p: p


OPS = {f.__name__: f for f in [reverse_words, reverse_all, remove_boundaries, drop_symbols, merge_pairs, chunk]}

OP_DOCS = {
    "reverse_words": "reverse glyph order inside every word (script direction / mirrored words)",
    "reverse_all": "reverse the entire stream",
    "remove_boundaries": "delete all word-space symbols (spaces may be unreliable or fake)",
    "drop_symbols": "delete listed glyph ids, args {\"drop\": [ids]} (null-glyph hypothesis)",
    "merge_pairs": "fuse the most frequent within-word glyph pairs into single units n times, args {\"n_merges\": int} "
                   "(several glyphs per letter / verbose cipher)",
    "chunk": "treat every k glyphs inside a word as one unit, args {\"k\": int} (fixed-length polygraphic code)",
}


def apply_pipeline(symbols, pipeline):
    """pipeline: list of {"op": name, "args": {...}}. Returns transformed symbols and a composed post-map."""
    posts = []
    for step in pipeline:
        fn = OPS[step["op"]]
        symbols, post = fn(symbols, **(step.get("args") or {}))
        posts.append(post)

    def post_all(p):
        for f in reversed(posts):
            p = f(p)
        return p
    return symbols, post_all
