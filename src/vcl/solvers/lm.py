"""Per-language character n-gram language models for the decipherment solvers.

Leakage rules (eval/PROTOCOL_v1.md section 3 + solver brief):
  * Models are built ONLY from Gutenberg books whose role in data/derived/benchmark_v1/book_roles.json
    (a public file) is 'ref'. 'tune' and 'test' books are never read here.
  * Nothing under data/derived/benchmark_v1/secret/ is read.

Model: dense interpolated Kneser-Ney character model of order 4 (discount 0.75) over a per-language
alphabet = space (index 0) + the most frequent letters covering 99.9% of letter mass (capped at
MAX_LETTERS). Word boundaries are modelled: the space symbol is index 0 and the start of a text is
padded with spaces. A second variant ('nospace') is trained on the same text with spaces deleted, for
mechanisms that destroy written word boundaries (e.g. columnar transposition).

Each model stores its typical per-character cross-entropy H (nats) measured on a 5% held-out tail of the
reference text, so decodes in different languages can be compared by the *gap* xent(decode) - H.

Libraries (regimes):
  * R1 'full'    : every language that has at least one ref book.
  * R2 'unknown' : TRAIN language families only (germanic, romance, slavic) - i.e. every held-out family
                   is absent, which is the honest 'language not in library' condition for test_lang /
                   test_both. `Library.excluding(family)` gives the single-family-excluded variant.

Models are cached as .npy (memory-mapped, so worker processes share pages) under data/derived/lm_cache/.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
ROLES = ROOT / "data/derived/benchmark_v1/book_roles.json"
CACHE = ROOT / "data/derived/lm_cache"
ORDER = 4
DISCOUNT = 0.75
MAX_LETTERS = 55
COVER = 0.999
LM_VERSION = "lm-v1-kn4"
TRAIN_FAMILIES = ("germanic", "romance", "slavic")


def _roles() -> dict:
    return json.loads(ROLES.read_text())


def language_families() -> dict[str, str]:
    """lang -> language family, from the public book_roles.json."""
    return {v["lang"]: v["family"] for v in _roles().values()}


def ref_languages() -> list[str]:
    return sorted({v["lang"] for v in _roles().values() if v["role"] == "ref"})


def _ref_text(lang: str) -> str:
    from vcl.synthetic.corpora import load_books  # allowed import (plaintext corpora, provenance-checked)
    roles = _roles()
    texts = [b["text"] for b in load_books() if b["lang"] == lang and roles.get(b["id"], {}).get("role") == "ref"]
    if not texts:
        raise ValueError(f"no ref books for {lang}")
    return " ".join(texts)


def _kn_dense(seq: np.ndarray, A: int, order: int = ORDER, D: float = DISCOUNT) -> np.ndarray:
    """Interpolated Kneser-Ney log-probabilities as a dense array of shape (A,)*order (float32).

    logp[h1..h_{n-1}, w] = log P(w | h). Lower orders use continuation counts; final interpolation with
    the uniform distribution, so nothing is zero.
    """
    seq = seq.astype(np.int64)
    n = len(seq)
    grams = np.zeros(n - order + 1, dtype=np.int64)
    for k in range(order):
        grams = grams * A + seq[k:n - order + 1 + k]
    counts = np.bincount(grams, minlength=A ** order).astype(np.float64).reshape((A,) * order)

    # continuation counts for orders < order: N1+(. w_2..w_k)
    cont = {order: counts}
    for k in range(order - 1, 0, -1):
        cont[k] = (cont[k + 1] > 0).sum(axis=0).astype(np.float64)
    # P1: continuation unigram mixed with uniform
    c1 = cont[1]
    p = (np.maximum(c1 - D, 0) + (D * (c1 > 0).sum() + 1.0) / A) / (c1.sum() + 1.0)
    p = p / p.sum()
    for k in range(2, order + 1):
        ck = cont[k]                                   # shape (A,)*k
        tot = ck.sum(axis=-1, keepdims=True)           # history totals
        types = (ck > 0).sum(axis=-1, keepdims=True)
        lower = np.broadcast_to(p[None, ...], ck.shape)  # P(w | shorter history), broadcast over first axis
        with np.errstate(divide="ignore", invalid="ignore"):
            hi = np.where(tot > 0, np.maximum(ck - D, 0) / np.maximum(tot, 1e-12), 0.0)
            lam = np.where(tot > 0, D * types / np.maximum(tot, 1e-12), 1.0)
        p = hi + lam * lower
    return np.log(p).astype(np.float32)


class CharLM:
    """A cached char n-gram LM for one language and variant ('space' | 'nospace')."""

    def __init__(self, lang: str, variant: str = "space"):
        self.lang, self.variant = lang, variant
        meta_path = CACHE / f"{lang}_{variant}.json"
        if not meta_path.exists() or json.loads(meta_path.read_text()).get("version") != LM_VERSION:
            build(lang, variant)
        meta = json.loads(meta_path.read_text())
        self.family = meta["family"]
        self.alphabet: list[str] = meta["alphabet"]      # index 0 = ' '
        self.idx = {c: i for i, c in enumerate(self.alphabet)}
        self.A = len(self.alphabet)
        self.H = meta["H"]                               # typical xent, nats/char (held-out tail)
        self.H_by_len = meta["H_by_len"]                 # typical xent of windows of given length
        self.unigram = np.array(meta["unigram"])         # letter probs, index-aligned with alphabet
        self.wordlen = np.array(meta["wordlen"])         # P(word length = 1..20)
        self.expected_types = meta["expected_types"]     # {N: expected distinct letters in N letters}
        self.logp = np.load(CACHE / f"{lang}_{variant}.npy", mmap_mode="r")
        self._flat = None
        self._vocab = None

    @property
    def flat(self) -> np.ndarray:
        if self._flat is None:
            self._flat = np.asarray(self.logp).reshape(-1)
        return self._flat

    @property
    def vocab(self) -> dict[str, int]:
        """Word -> count over the ref text (top 60k words)."""
        if self._vocab is None:
            self._vocab = json.loads((CACHE / f"{self.lang}_vocab.json").read_text())
        return self._vocab

    def encode(self, text: str) -> np.ndarray:
        return np.array([self.idx.get(c, -1) for c in text], dtype=np.int64)

    def score_text(self, text: str) -> float:
        """Mean log-prob (nats/char) of `text` (chars outside the alphabet are skipped)."""
        if self.variant == "nospace":
            text = text.replace(" ", "")
        ids = self.encode(text)
        ids = ids[ids >= 0]
        if len(ids) == 0:
            return -math.inf
        pad = np.zeros(ORDER - 1, dtype=np.int64)
        s = np.concatenate([pad, ids]) if self.variant == "space" else np.concatenate([ids[:1].repeat(ORDER - 1), ids])
        g = np.zeros(len(s) - ORDER + 1, dtype=np.int64)
        for k in range(ORDER):
            g = g * self.A + s[k:len(s) - ORDER + 1 + k]
        lp = self.flat[g]
        if self.variant == "nospace":
            lp = lp[ORDER - 1:] if len(lp) > ORDER else lp
        return float(lp.mean())

    def typical_H(self, n_chars: int) -> float:
        keys = sorted(int(k) for k in self.H_by_len)
        k = min(keys, key=lambda x: abs(math.log(x) - math.log(max(n_chars, 1))))
        return self.H_by_len[str(k)]

    def lexicon_rate(self, text: str, min_len: int = 3) -> float:
        """Fraction of decoded word tokens (length >= min_len) found in the reference vocabulary."""
        toks = [w for w in text.split(" ") if len(w) >= min_len]
        if not toks:
            return 0.0
        v = self.vocab
        return sum(w in v for w in toks) / len(toks)


def build(lang: str, variant: str = "space") -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    fam = language_families()[lang]
    text = _ref_text(lang)
    letters = Counter(c for c in text if c != " ")
    tot = sum(letters.values())
    alpha, cum = [], 0
    for c, v in letters.most_common():
        if cum / tot >= COVER or len(alpha) >= MAX_LETTERS:
            break
        alpha.append(c); cum += v
    alphabet = [" "] + alpha
    idx = {c: i for i, c in enumerate(alphabet)}
    # drop out-of-alphabet chars (rare) and collapse spaces
    clean = "".join(c for c in text if c in idx)
    clean = " ".join(clean.split())
    if variant == "nospace":
        body = clean.replace(" ", "")
    else:
        body = clean
    ids = np.array([idx[c] for c in body], dtype=np.int64)
    cut = int(len(ids) * 0.95)
    A = len(alphabet)
    pad = np.zeros(ORDER - 1, dtype=np.int64)
    logp = _kn_dense(np.concatenate([pad, ids[:cut]]), A)
    np.save(CACHE / f"{lang}_{variant}.npy", logp)
    flat = logp.reshape(-1)
    held = ids[cut:]
    g = np.zeros(len(held) - ORDER + 1, dtype=np.int64)
    for k in range(ORDER):
        g = g * A + held[k:len(held) - ORDER + 1 + k]
    lp = flat[g]
    H = float(-lp.mean())
    H_by_len = {}
    for L in (100, 300, 1000, 3000):
        if len(lp) > L:
            H_by_len[str(L)] = float(-np.mean([lp[i:i + L].mean() for i in range(0, len(lp) - L, max(1, L // 2))]))
        else:
            H_by_len[str(L)] = H
    uni = np.zeros(A)
    for c, v in letters.items():
        if c in idx:
            uni[idx[c]] = v
    uni /= uni.sum()
    words = clean.split(" ")
    wl = np.bincount(np.minimum([len(w) for w in words], 20), minlength=21)[1:21].astype(float)
    wl /= wl.sum()
    exp_types = {str(N): float(np.sum(1 - (1 - uni[1:]) ** N)) for N in (25, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000)}
    meta = {"version": LM_VERSION, "lang": lang, "family": fam, "variant": variant, "alphabet": alphabet,
            "order": ORDER, "discount": DISCOUNT, "H": H, "H_by_len": H_by_len, "unigram": uni.tolist(),
            "wordlen": wl.tolist(), "expected_types": exp_types, "train_chars": int(cut)}
    (CACHE / f"{lang}_{variant}.json").write_text(json.dumps(meta, ensure_ascii=False))
    if variant == "space":
        vc = Counter(words)
        (CACHE / f"{lang}_vocab.json").write_text(json.dumps(dict(vc.most_common(60000)), ensure_ascii=False))


@lru_cache(maxsize=None)
def get_lm(lang: str, variant: str = "space") -> CharLM:
    return CharLM(lang, variant)


class Library:
    """A set of candidate languages available to the solver."""

    def __init__(self, langs: list[str], name: str):
        self.langs = sorted(langs)
        self.name = name

    @classmethod
    def full(cls) -> "Library":
        """R1: every language with ref books."""
        return cls(ref_languages(), "R1_full")

    @classmethod
    def train_families_only(cls) -> "Library":
        """R2: only TRAIN language families; every held-out family is absent from the library."""
        fams = language_families()
        return cls([l for l in ref_languages() if fams[l] in TRAIN_FAMILIES], "R2_train_families_only")

    @classmethod
    def excluding(cls, family: str) -> "Library":
        fams = language_families()
        return cls([l for l in ref_languages() if fams[l] != family], f"R2_minus_{family}")

    def lm(self, lang: str, variant: str = "space") -> CharLM:
        return get_lm(lang, variant)

    def __iter__(self):
        return iter(self.langs)


def build_all(variants=("space", "nospace")) -> None:
    for lang in ref_languages():
        for v in variants:
            meta = CACHE / f"{lang}_{v}.json"
            if not meta.exists() or json.loads(meta.read_text()).get("version") != LM_VERSION:
                build(lang, v)
                print("built", lang, v, flush=True)


if __name__ == "__main__":
    build_all()
