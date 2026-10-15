"""Encoding families: the 'encrypt other languages' half of the system.

Each encoder turns a normalised plaintext (letters + single spaces) into a symbol stream
over an abstract glyph inventory (Runic + Glagolitic code points, so no cipher symbol is a
plaintext letter). Each returns (symbols, key, identifiability, recoverable_plaintext), and
each has an exact decoder used ONLY by the evaluator's round-trip verifier.

Families are grouped so that whole mechanisms can be held out (see configs/benchmark_v1.yaml).
"""
from __future__ import annotations

import random
import re
from collections import Counter

from .schema import BOUNDARY

GLYPHS = [chr(c) for c in range(0x16A0, 0x16F1)] + [chr(c) for c in range(0x2C00, 0x2C5F)]
VOWELS = set("aeiouyàáâãäåæèéêëìíîïòóôõöøùúûüýÿœαεηιουωаеёиоуыэюяאוי") | set("ాిీుూెేైొోౌ")


def _alphabet(plain: str) -> list[str]:
    return sorted({c for c in plain if c != " "})


def _glyphs(rng: random.Random, n: int) -> list[str]:
    if n > len(GLYPHS):
        raise ValueError("glyph inventory too small")
    return rng.sample(GLYPHS, n)


def _stream(plain: str, f) -> list[str]:
    out = []
    for ch in plain:
        out.extend([BOUNDARY] if ch == " " else f(ch))
    return out


# ---------------------------------------------------------------- train families
def mono(plain, rng, **_):
    alpha = _alphabet(plain)
    key = dict(zip(alpha, _glyphs(rng, len(alpha))))
    return _stream(plain, lambda c: [key[c]]), key, "unique", plain


def homophonic(plain, rng, max_homophones=4, **_):
    alpha = _alphabet(plain)
    freq = Counter(c for c in plain if c != " ")
    total = sum(freq.values())
    n_h = {c: max(1, min(max_homophones, round(freq[c] / total * len(alpha) * 1.8))) for c in alpha}
    pool = iter(_glyphs(rng, sum(n_h.values())))
    key = {c: [next(pool) for _ in range(n_h[c])] for c in alpha}
    return _stream(plain, lambda c: [rng.choice(key[c])]), key, "unique", plain


def vigenere(plain, rng, period=None, **_):
    alpha = _alphabet(plain)
    period = period or rng.randint(3, 8)
    glyph = dict(zip(alpha, _glyphs(rng, len(alpha))))
    shifts = [rng.randrange(len(alpha)) for _ in range(period)]
    idx, pos = {c: i for i, c in enumerate(alpha)}, [0]

    def enc(c):
        s = shifts[pos[0] % period]; pos[0] += 1
        return [glyph[alpha[(idx[c] + s) % len(alpha)]]]
    return _stream(plain, enc), {"glyph": glyph, "shifts": shifts, "alphabet": alpha}, "unique", plain


def columnar(plain, rng, ncols=None, **_):
    """Columnar transposition of the letter stream (spaces dropped), then a glyph relabelling."""
    letters = plain.replace(" ", "")
    ncols = ncols or rng.randint(4, 9)
    order = list(range(ncols)); rng.shuffle(order)
    rows = [letters[i:i + ncols] for i in range(0, len(letters), ncols)]
    trans = "".join("".join(r[c] for r in rows if c < len(r)) for c in order)
    alpha = _alphabet(letters)
    glyph = dict(zip(alpha, _glyphs(rng, len(alpha))))
    return [glyph[c] for c in trans], {"order": order, "glyph": glyph}, "unique", letters


def nulls(plain, rng, rate=None, n_nulls=None, **_):
    rate = rate if rate is not None else rng.uniform(0.1, 0.3)
    alpha = _alphabet(plain)
    gl = _glyphs(rng, len(alpha) + (n_nulls or rng.randint(2, 5)))
    key, null_set = dict(zip(alpha, gl)), gl[len(alpha):]
    return (_stream(plain, lambda c: [key[c]] + ([rng.choice(null_set)] if rng.random() < rate else [])),
            {"key": key, "nulls": null_set, "rate": rate}, "unique", plain)


# ---------------------------------------------------------------- held-out families
def verbose(plain, rng, **_):
    """Each letter -> fixed sequence of 1-3 glyphs from a small inventory (Voynich-relevant 'verbose cipher')."""
    alpha = _alphabet(plain)
    inv = _glyphs(rng, rng.randint(8, 12))
    codes, used = {}, set()
    for c in sorted(alpha, key=lambda c: -plain.count(c)):
        while True:
            L = rng.choice([1, 2, 2, 3]) if len(used) >= len(inv) else rng.choice([1, 2])
            code = tuple(rng.choice(inv) for _ in range(L))
            if code not in used:
                used.add(code); codes[c] = code; break
    # ambiguity (non-prefix-free codes) makes the exact parse an equivalence class in general
    return _stream(plain, lambda c: list(codes[c])), {c: "".join(v) for c, v in codes.items()}, "equivalence_class", plain


def abjad(plain, rng, **_):
    """Vowel letters dropped, consonants substituted. Only consonantal skeleton recoverable."""
    cons = re.sub(r" +", " ", "".join(c for c in plain if c not in VOWELS)).strip()
    syms, key, _, _ = mono(cons, rng)
    return syms, key, "equivalence_class", cons


def syllabary(plain, rng, **_):
    """Split words into (C*)V(C?) chunks; each distinct chunk gets one glyph (large inventory, like Linear B)."""
    chunks_by_word = [re.findall(r"[^" + "".join(VOWELS) + r"]*[" + "".join(VOWELS) + r"]+|[^" + "".join(VOWELS) + r"]+$", w)
                      for w in plain.split(" ")]
    types = sorted({c for ws in chunks_by_word for c in ws}, key=lambda c: -plain.count(c))
    glyph_names = [f"S{i:03d}" for i in range(len(types))]
    rng.shuffle(glyph_names)
    key = dict(zip(types, glyph_names))
    out = []
    for i, ws in enumerate(chunks_by_word):
        if i:
            out.append(BOUNDARY)
        out.extend(key[c] for c in ws)
    return out, key, "unique", plain


def autokey(plain, rng, **_):
    """Context-dependent substitution: glyph depends on current and previous plaintext letter."""
    alpha = _alphabet(plain)
    glyph = dict(zip(alpha, _glyphs(rng, len(alpha))))
    idx = {c: i for i, c in enumerate(alpha)}
    primer = rng.choice(alpha)
    prev = [primer]

    def enc(c):
        s = idx[prev[0]]; prev[0] = c
        return [glyph[alpha[(idx[c] + s) % len(alpha)]]]
    return _stream(plain, enc), {"glyph": glyph, "primer": primer, "alphabet": alpha}, "unique", plain


def boundary_noise(plain, rng, p_drop=0.3, p_insert=0.08, **_):
    """Monoalphabetic, but written spaces are unreliable (dropped and spuriously inserted)."""
    syms, key, _, _ = mono(plain, rng)
    out = []
    for s in syms:
        if s == BOUNDARY and rng.random() < p_drop:
            continue
        out.append(s)
        if s != BOUNDARY and rng.random() < p_insert:
            out.append(BOUNDARY)
    return out, key, "unique", plain


def reversed_words(plain, rng, **_):
    """Monoalphabetic with every word written right-to-left."""
    syms, key, _, _ = mono(" ".join(w[::-1] for w in plain.split(" ")), rng)
    return syms, key, "unique", plain


def nomenclator(plain, rng, n_codewords=40, **_):
    """Frequent words -> single code glyph; remaining words spelled with a monoalphabetic key."""
    words = plain.split(" ")
    top = [w for w, _ in Counter(words).most_common(n_codewords)]
    alpha = _alphabet(plain)
    gl = _glyphs(rng, len(alpha) + len(top))
    key = dict(zip(alpha, gl))
    code = {w: gl[len(alpha) + i] for i, w in enumerate(top)}
    out = []
    for i, w in enumerate(words):
        if i:
            out.append(BOUNDARY)
        out.extend([code[w]] if w in code else [key[c] for c in w])
    return out, {"letters": key, "codewords": code}, "unique", plain


# ---------------------------------------------------------------- non-identifiable
def one_time_pad(plain, rng, **_):
    """Fresh random substitution per character: the ciphertext carries no information about the plaintext."""
    alpha = _alphabet(plain)
    gl = _glyphs(rng, len(alpha))
    return _stream(plain, lambda c: [rng.choice(gl)]), None, "non_identifiable", None


ENCODERS = {f.__name__: f for f in [mono, homophonic, vigenere, columnar, nulls, verbose, abjad, syllabary,
                                    autokey, boundary_noise, reversed_words, nomenclator, one_time_pad]}


# ---------------------------------------------------------------- exact decoders (evaluator only)
def decode(family: str, symbols: list[str], key) -> str | None:
    if family in ("mono", "boundary_noise", "abjad"):
        inv = {g: c for c, g in key.items()}
        return "".join(" " if s == BOUNDARY else inv[s] for s in symbols)
    if family == "reversed_words":
        inv = {g: c for c, g in key.items()}
        return " ".join(w[::-1] for w in "".join(" " if s == BOUNDARY else inv[s] for s in symbols).split(" "))
    if family == "homophonic":
        inv = {g: c for c, gs in key.items() for g in gs}
        return "".join(" " if s == BOUNDARY else inv[s] for s in symbols)
    if family == "nulls":
        inv = {g: c for c, g in key["key"].items()}
        return "".join(" " if s == BOUNDARY else inv.get(s, "") for s in symbols)
    if family == "vigenere":
        alpha, inv = key["alphabet"], {g: c for c, g in key["glyph"].items()}
        idx, out, pos = {c: i for i, c in enumerate(alpha)}, [], 0
        for s in symbols:
            if s == BOUNDARY:
                out.append(" "); continue
            out.append(alpha[(idx[inv[s]] - key["shifts"][pos % len(key["shifts"])]) % len(alpha)]); pos += 1
        return "".join(out)
    if family == "autokey":
        alpha, inv = key["alphabet"], {g: c for c, g in key["glyph"].items()}
        idx, out, prev = {c: i for i, c in enumerate(alpha)}, [], key["primer"]
        for s in symbols:
            if s == BOUNDARY:
                out.append(" "); continue
            c = alpha[(idx[inv[s]] - idx[prev]) % len(alpha)]; out.append(c); prev = c
        return "".join(out)
    if family == "columnar":
        inv = {g: c for c, g in key["glyph"].items()}
        letters, order, n = [inv[s] for s in symbols], key["order"], len(symbols)
        ncols = len(order)
        nrows, extra = divmod(n, ncols)
        lens = {c: nrows + (1 if c < extra else 0) for c in range(ncols)}
        cols, p = {}, 0
        for c in order:
            cols[c] = letters[p:p + lens[c]]; p += lens[c]
        return "".join(cols[c][r] for r in range(nrows + 1) for c in range(ncols) if r < lens[c])
    if family == "syllabary":
        inv = {g: c for c, g in key.items()}
        return "".join(" " if s == BOUNDARY else inv[s] for s in symbols)
    if family == "nomenclator":
        inv = {g: c for c, g in key["letters"].items()} | {g: w for w, g in key["codewords"].items()}
        return "".join(" " if s == BOUNDARY else inv[s] for s in symbols)
    if family == "verbose":
        # greedy parse is not guaranteed; verifier checks re-encoding instead
        return None
    return None


SPACE_UNRELIABLE = {"boundary_noise", "columnar"}


def comparable(family: str, text: str | None) -> str | None:
    """Canonical form used by verifiers: drop spaces for families whose written spaces carry no information."""
    if text is None:
        return None
    return text.replace(" ", "") if family in SPACE_UNRELIABLE else text
