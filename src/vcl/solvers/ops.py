"""Composable decipherment operations for a planner (e.g. an LLM agent) to try mechanisms outside the
classifier's label set.

All stream ops take and return a list of cipher symbols (the PublicTask.symbols format: strings, with " " as the
written word boundary) so they can be chained freely; solver ops take a symbol list and return a plain dict
that is JSON-serialisable (text, language, gap, per-char log-prob, key/info), so an agent can log and compare.

Stream transforms
  reverse_words(s)                     reverse symbol order inside every word (undo right-to-left word writing)
  reverse_stream(s)                    reverse the whole stream
  drop_symbols(s, drop)                delete a set of symbols (e.g. suspected nulls)
  remove_boundaries(s)                 delete written word boundaries
  merge_symbol_ngrams(s, k)            re-tokenise each word into consecutive k-symbol chunks treated as single units
                                       (verbose / syllabic writing where a letter is spelled by k glyphs)
  merge_pairs(s, pairs)                treat specific adjacent symbol pairs as one unit (greedy, left to right)
  split_symbols(s, mapping)            expand a symbol into a sequence of new symbols (e.g. a code-glyph into letters)
  untranspose(s, ncols, order)         undo a columnar transposition (boundaries are dropped)
  null_candidates(s, k)                the k most null-like symbols (never word-initial, unstructured predecessors)
  symbol_stats(s)                      ciphertext statistics (features.features) as a dict

Solvers (run on any transformed stream)
  run_mono / run_homophonic / run_nulls / run_vigenere / run_columnar(s, lang=None, library=None, ...)
      lang=None -> searches the library (3-stage search used by api.solve); otherwise solves under that language.
  best_language(s, family, library)    cheap language ranking (no solving)
  score_text(text, lang)               decode quality of any candidate plaintext: per-char log-prob, gap to the
                                       language's typical cross-entropy, and dictionary-word rate.
  classify(s)                          encoding-family probabilities incl. open-set 'unknown'.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from .features import features as _features
from .lm import Library, get_lm

BOUNDARY = " "


# ------------------------------------------------------------------ stream transforms
def _words(symbols: list[str]) -> list[list[str]]:
    out, cur = [], []
    for s in symbols:
        if s == BOUNDARY:
            out.append(cur); cur = []
        else:
            cur.append(s)
    out.append(cur)
    return out


def _join(words: list[list[str]]) -> list[str]:
    out = []
    for i, w in enumerate(words):
        if i:
            out.append(BOUNDARY)
        out.extend(w)
    return out


def reverse_words(symbols: list[str]) -> list[str]:
    """Reverse the symbol order inside every word, keeping word order and boundaries."""
    return _join([w[::-1] for w in _words(symbols)])


def reverse_stream(symbols: list[str]) -> list[str]:
    """Reverse the entire symbol stream."""
    return list(symbols[::-1])


def drop_symbols(symbols: list[str], drop) -> list[str]:
    """Delete every occurrence of the given symbols (boundaries are never dropped unless listed)."""
    drop = set(drop)
    return [s for s in symbols if s not in drop]


def remove_boundaries(symbols: list[str]) -> list[str]:
    """Delete written word boundaries (for streams whose spaces are unreliable or absent)."""
    return [s for s in symbols if s != BOUNDARY]


def merge_symbol_ngrams(symbols: list[str], k: int, offset: int = 0) -> list[str]:
    """Re-tokenise each word into consecutive k-symbol chunks (after skipping `offset` symbols, which form their own
    chunk); each chunk becomes one new symbol named by joining its glyphs with '+'. Use for verbose ciphers or
    syllabic scripts where several glyphs spell one plaintext unit."""
    out_words = []
    for w in _words(symbols):
        chunks = []
        if offset and w:
            chunks.append("+".join(w[:offset])); w = w[offset:]
        chunks += ["+".join(w[i:i + k]) for i in range(0, len(w), k)]
        out_words.append([c for c in chunks if c])
    return _join(out_words)


def merge_pairs(symbols: list[str], pairs) -> list[str]:
    """Greedily (left to right) merge listed adjacent symbol pairs (a, b) into a single symbol 'a+b'."""
    pairs = {tuple(p) for p in pairs}
    out, i = [], 0
    while i < len(symbols):
        if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) in pairs:
            out.append(symbols[i] + "+" + symbols[i + 1]); i += 2
        else:
            out.append(symbols[i]); i += 1
    return out


def split_symbols(symbols: list[str], mapping: dict) -> list[str]:
    """Replace a symbol by a sequence of symbols (mapping: symbol -> list of symbols)."""
    out = []
    for s in symbols:
        out.extend(mapping.get(s, [s]))
    return out


def untranspose(symbols: list[str], ncols: int, order: list[int]) -> list[str]:
    """Undo a columnar transposition with `ncols` columns read out in `order` (boundaries are removed first)."""
    from .columnar import untranspose_index
    letters = remove_boundaries(symbols)
    idx = untranspose_index(len(letters), order)
    return [letters[i] for i in idx]


def null_candidates(symbols: list[str], k: int = 6) -> list[str]:
    """The k most null-like symbols (never word-initial first, then by predecessor-distribution KL)."""
    from .substitution import encode_symbols, null_order
    seq, names = encode_symbols(symbols)
    return [names[i] for i in null_order(seq, len(names) - 1)[:k]]


def symbol_stats(symbols: list[str]) -> dict:
    """Ciphertext statistics (IoC, entropies, periodic IoC, word-length stats, positional stats...)."""
    return _features(symbols)


def symbol_counts(symbols: list[str], top: int = 30) -> list[tuple[str, int]]:
    return Counter(s for s in symbols if s != BOUNDARY).most_common(top)


# ------------------------------------------------------------------ solvers
def _res(r) -> dict:
    from .api import _jsonable
    return {"family": r.solver, "lang": r.lang, "text": r.text, "per_char": float(r.per_char), "gap": float(r.gap),
            "key": _jsonable(r.key), "info": _jsonable(r.info)}


def _run_family(fam: str, symbols: list[str], lang: str | None, library: Library | None, budget=None,
                **kw) -> dict:
    from .api import Budget, _run, _variant, solve_family, solve_nulls_family
    from .substitution import encode_symbols
    seq, names = encode_symbols(symbols)
    S = len(names) - 1
    if lang is not None:
        r = _run(fam, "full", seq, S, get_lm(lang, _variant(fam)), {}, kw.get("scale", 1.0), kw.get("seed", 0))
        return _res(r)
    library = library or Library.full()
    budget = budget or Budget()
    if fam == "nulls":
        rs = solve_nulls_family(seq, S, library, budget, {}, seed=kw.get("seed", 0))
    else:
        rs = solve_family(fam, seq, S, library, budget, {}, seed=kw.get("seed", 0))
    out = _res(rs[0])
    out["alternatives"] = [(r.lang, float(r.gap)) for r in rs[1:6]]
    return out


def run_mono(symbols, lang=None, library=None, **kw) -> dict:
    """Monoalphabetic substitution solve (boundaries kept as word breaks)."""
    return _run_family("mono", symbols, lang, library, **kw)


def run_homophonic(symbols, lang=None, library=None, **kw) -> dict:
    """Many-to-one substitution solve (more cipher symbols than letters)."""
    return _run_family("homophonic", symbols, lang, library, **kw)


def run_nulls(symbols, lang=None, library=None, **kw) -> dict:
    """Monoalphabetic with null symbols; chooses how many null-like symbols to delete."""
    return _run_family("nulls", symbols, lang, library, **kw)


def run_vigenere(symbols, lang=None, library=None, **kw) -> dict:
    """Periodic shift cipher over an unknown glyph alphabet (period estimated by periodic IoC)."""
    return _run_family("vigenere", symbols, lang, library, **kw)


def run_columnar(symbols, lang=None, library=None, **kw) -> dict:
    """Columnar transposition + substitution on the boundary-free letter stream (includes the identity order,
    so this is also the solver for any boundary-free monoalphabetic stream)."""
    return _run_family("columnar", remove_boundaries(symbols), lang, library, **kw)


def best_language(symbols: list[str], family: str = "mono", library: Library | None = None, top: int = 10):
    """Cheap language ranking (no solving) from ciphertext statistics."""
    from .langrank import language_distances
    from .substitution import encode_symbols
    library = library or Library.full()
    seq, names = encode_symbols(symbols)
    var = "nospace" if family == "columnar" else "space"
    d = language_distances(seq, len(names) - 1, [library.lm(l, var) for l in library], family)
    return sorted(d.items(), key=lambda kv: kv[1])[:top]


def score_text(text: str, lang: str, nospace: bool = False) -> dict:
    """Decode quality of `text` under language `lang`: mean log-prob per char, gap to the language's typical
    cross-entropy (lower is better; ~0-0.5 for real text, >1 for garbage), and dictionary-word rate."""
    lm = get_lm(lang, "nospace" if nospace else "space")
    pc = lm.score_text(text)
    n = len(text)
    return {"lang": lang, "per_char": pc, "gap": -pc - lm.typical_H(n),
            "lexicon_rate": None if nospace else lm.lexicon_rate(text)}


def classify(symbols: list[str]) -> dict:
    """Encoding-family probabilities (train families + 'unknown')."""
    from .classifier import load_classifier
    return load_classifier().predict(symbols)
