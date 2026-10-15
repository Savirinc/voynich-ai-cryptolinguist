"""Relabelling-invariant cipher representation and windowing.

Cipher glyphs are arbitrary Unicode code points (or 'S017'-style names), so their identity carries no information.
Following Aldarrab & May (2021, "Can Sequence-to-Sequence Models Crack Substitution Ciphers?"), every task is
re-encoded by *frequency rank* computed over the WHOLE task:

    id(symbol) = rank of the symbol's count among all non-boundary symbols (0 = most frequent),
                 ties broken by first occurrence position (so the result never depends on glyph identity),
    ranks >= N_RANK-1 share one 'rare' bucket id.

The word boundary gets its own id. Each position additionally carries the (relabelling-invariant) log relative
frequency of its symbol, so the model sees absolute frequencies (e.g. the flattened profile of a homophonic cipher),
not only their order. Any permutation/renaming of the glyph inventory gives an identical encoding.

Long tasks are split into k = ceil(n / WINDOW) contiguous windows of (nearly) equal length; frequency ranks are
always computed on the full task so all windows share one consistent relabelling, which lets per-window outputs be
aggregated into one global key (see predict.py).
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

import numpy as np

BOUNDARY = " "
N_RANK = 120                 # rank ids 0..118, 119 = rare bucket
RANK_RARE = N_RANK - 1
WINDOW = 320                 # cipher symbols per window (a 300-char plaintext task fits in one window)

# input-side special ids (appended after the rank ids)
IN_BOUNDARY = N_RANK         # written word boundary
IN_PAD = N_RANK + 1          # left padding (all prompts in a batch have the same length)
IN_SEP = N_RANK + 2          # end of cipher, start of answer
N_IN = N_RANK + 3

# output-side specials (indices into the restricted output vocabulary, after the characters)
OUT_SPECIALS = ["<eos>", "<abstain>", "<unk>", "<fam:mono>", "<fam:homophonic>", "<fam:vigenere>",
                "<fam:columnar>", "<fam:nulls>", "<fam:noise>"]
TRAIN_FAMILIES = ["mono", "homophonic", "vigenere", "columnar", "nulls"]
FAMILY_TOKENS = {f: f"<fam:{f}>" for f in TRAIN_FAMILIES + ["noise"]}


@dataclass
class Encoded:
    ids: np.ndarray        # int32 [n] rank ids / IN_BOUNDARY
    logf: np.ndarray       # float32 [n] log relative frequency of the symbol (0 for boundary)
    n_letters: int
    n_types: int


def rank_encode(symbols: list[str]) -> Encoded:
    """Frequency-rank encoding of a whole task (relabelling-invariant)."""
    counts: Counter = Counter()
    first: dict[str, int] = {}
    for i, s in enumerate(symbols):
        if s == BOUNDARY:
            continue
        counts[s] += 1
        first.setdefault(s, i)
    order = sorted(counts, key=lambda s: (-counts[s], first[s]))
    rank = {s: min(r, RANK_RARE) for r, s in enumerate(order)}
    n = max(1, sum(counts.values()))
    ids = np.empty(len(symbols), dtype=np.int32)
    logf = np.zeros(len(symbols), dtype=np.float32)
    for i, s in enumerate(symbols):
        if s == BOUNDARY:
            ids[i] = IN_BOUNDARY
        else:
            ids[i] = rank[s]
            logf[i] = math.log(counts[s] / n)
    return Encoded(ids, logf, n_letters=sum(counts.values()), n_types=len(counts))


def window_bounds(n: int, window: int = WINDOW) -> list[tuple[int, int]]:
    """k = ceil(n / window) contiguous, nearly equal windows covering [0, n)."""
    if n <= 0:
        return [(0, 0)]
    k = max(1, math.ceil(n / window))
    edges = [round(i * n / k) for i in range(k + 1)]
    return [(edges[i], edges[i + 1]) for i in range(k)]


def window_inputs(enc: Encoded, a: int, b: int, window: int = WINDOW) -> tuple[np.ndarray, np.ndarray]:
    """Left-padded prompt for window [a, b): PAD* + cipher ids + SEP (length window + 1)."""
    ids = enc.ids[a:b]
    pad = window - len(ids)
    if pad < 0:
        raise ValueError("window too long")
    full = np.concatenate([np.full(pad, IN_PAD, np.int32), ids, np.array([IN_SEP], np.int32)])
    lf = np.concatenate([np.zeros(pad, np.float32), enc.logf[a:b], np.zeros(1, np.float32)])
    return full, lf


class OutVocab:
    """Restricted output vocabulary: plaintext characters (mapped to single Qwen token ids) + specials."""

    def __init__(self, chars: list[str], token_ids: list[int]):
        assert len(chars) == len(token_ids)
        self.chars = list(chars)
        self.token_ids = list(token_ids)
        self.items = self.chars + OUT_SPECIALS
        self.index = {c: i for i, c in enumerate(self.items)}
        self.n_chars = len(self.chars)
        self.eos = self.index["<eos>"]
        self.abstain = self.index["<abstain>"]
        self.unk = self.index["<unk>"]
        self.fam_ids = {f: self.index[t] for f, t in FAMILY_TOKENS.items()}
        self.id_fam = {v: k for k, v in self.fam_ids.items()}

    def __len__(self):
        return len(self.items)

    def encode_text(self, text: str) -> list[int]:
        return [self.index.get(c, self.unk) if c != "<" else self.unk for c in text]

    def decode(self, ids) -> str:
        return "".join(self.items[i] if i < self.n_chars else ("?" if i == self.unk else "") for i in ids)

    def to_json(self) -> dict:
        return {"chars": self.chars, "token_ids": self.token_ids}

    @classmethod
    def from_json(cls, d: dict) -> "OutVocab":
        return cls(d["chars"], d["token_ids"])


def build_out_vocab(char_counts: Counter, tokenizer, min_count: int = 20) -> OutVocab:
    """Keep characters seen >= min_count times in TRAIN-family tune/ref text that are a single Qwen token."""
    chars, toks = [], []
    for c, n in char_counts.most_common():
        if n < min_count or c == "<":
            continue
        t = tokenizer.encode(c, add_special_tokens=False) if hasattr(tokenizer, "encode") else None
        if t is not None and len(t) == 1:
            chars.append(c); toks.append(int(t[0]))
    return OutVocab(chars, toks)
