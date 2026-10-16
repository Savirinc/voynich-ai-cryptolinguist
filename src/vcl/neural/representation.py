"""Relabelling-invariant cipher representation and windowing.

Cipher glyphs are arbitrary Unicode code points (or 'S017'-style names), so their identity carries no information.
Following Aldarrab & May (2021, "Can Sequence-to-Sequence Models Crack Substitution Ciphers?"), every task is
re-encoded by *frequency rank* computed over the WHOLE task:

    id(symbol) = rank of the symbol's count among all non-boundary symbols (0 = most frequent),
                 ties broken by first occurrence position (so the result never depends on glyph identity),
    ranks >= N_RANK-1 share one 'rare' bucket id.

The word boundary gets its own id. In addition every position carries a vector of N_FEAT relabelling-invariant
*symbol-profile* features of its symbol, computed over the whole task (log frequency, word-initial / word-final /
single-letter-word / doubling rates, left/right neighbour entropies and variety) plus a few task-global features
(length, inventory size, presence of written boundaries, mean word length). These let a window "see" global
statistics such as the flattened profile of a homophonic cipher or the vowel-like behaviour of a symbol, which a
256-symbol window alone cannot estimate. Any permutation/renaming of the glyph inventory gives an identical encoding
(tested in tests/test_neural.py).

Long tasks are split into k = ceil(n / WINDOW) contiguous windows of (nearly) equal length; ranks and features are
always computed on the full task so all windows share one consistent relabelling, which lets per-window outputs be
aggregated into one global key (see predict.py).
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass

import numpy as np

BOUNDARY = " "
N_RANK = 120                 # rank ids 0..118, 119 = rare bucket
RANK_RARE = N_RANK - 1
WINDOW = 256                 # cipher symbols per window

# input-side special ids (appended after the rank ids)
IN_BOUNDARY = N_RANK         # written word boundary
IN_PAD = N_RANK + 1          # left padding (all prompts in a batch have the same length)
IN_SEP = N_RANK + 2          # end of cipher, start of answer
N_IN = N_RANK + 3

FEATURES = ["logf", "rank_frac", "p_initial", "p_final", "p_single", "p_double", "h_right", "h_left",
            "v_right", "v_left", "g_log_n", "g_types", "g_has_boundary", "g_mean_wordlen", "is_boundary"]
N_FEAT = len(FEATURES)

# output-side specials (indices into the restricted output vocabulary, after the characters)
OUT_SPECIALS = ["<eos>", "<abstain>", "<unk>", "<null>", "<fam:mono>", "<fam:homophonic>", "<fam:vigenere>",
                "<fam:columnar>", "<fam:nulls>", "<fam:noise>"]
TRAIN_FAMILIES = ["mono", "homophonic", "vigenere", "columnar", "nulls"]
FAMILY_TOKENS = {f: f"<fam:{f}>" for f in TRAIN_FAMILIES + ["noise"]}


@dataclass
class Encoded:
    ids: np.ndarray        # int32 [n] rank ids / IN_BOUNDARY
    feats: np.ndarray      # float32 [n, N_FEAT] relabelling-invariant symbol-profile features
    n_letters: int
    n_types: int
    rank_of: dict          # glyph -> rank id (used only to map a predicted key back onto the glyph stream)


def _entropy(c: Counter) -> float:
    n = sum(c.values())
    return -sum(v / n * math.log(v / n) for v in c.values()) if n else 0.0


def rank_encode(symbols: list[str]) -> Encoded:
    """Frequency-rank encoding + symbol-profile features of a whole task (relabelling-invariant)."""
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
    T = max(1, len(counts))
    has_b = any(s == BOUNDARY for s in symbols)
    init, fin, single, double = Counter(), Counter(), Counter(), Counter()
    right, left = defaultdict(Counter), defaultdict(Counter)
    L = len(symbols)
    for i, s in enumerate(symbols):
        if s == BOUNDARY:
            continue
        prv = symbols[i - 1] if i > 0 else BOUNDARY
        nxt = symbols[i + 1] if i + 1 < L else BOUNDARY
        if has_b:
            if prv == BOUNDARY:
                init[s] += 1
            if nxt == BOUNDARY:
                fin[s] += 1
            if prv == BOUNDARY and nxt == BOUNDARY:
                single[s] += 1
        if nxt == s:
            double[s] += 1
        if nxt != BOUNDARY:
            right[s][nxt] += 1
        if prv != BOUNDARY:
            left[s][prv] += 1
    words = [w for w in "".join("\x00" if s == BOUNDARY else "x" for s in symbols).split("\x00") if w]
    mean_wl = (sum(map(len, words)) / len(words)) if (has_b and words) else 0.0
    logT = math.log(T + 1)
    glob = [math.log(n) / 8.0, T / 100.0, float(has_b), mean_wl / 10.0]
    prof = {}
    for s, c in counts.items():
        prof[s] = [math.log(c / n) / 5.0, rank[s] / max(1, T - 1) if T > 1 else 0.0,
                   init[s] / c, fin[s] / c, single[s] / c, double[s] / c,
                   _entropy(right[s]) / logT, _entropy(left[s]) / logT,
                   math.log(len(right[s]) + 1) / logT, math.log(len(left[s]) + 1) / logT] + glob + [0.0]
    bvec = [0.0] * 10 + glob + [1.0]
    ids = np.empty(L, dtype=np.int32)
    feats = np.empty((L, N_FEAT), dtype=np.float32)
    for i, s in enumerate(symbols):
        if s == BOUNDARY:
            ids[i] = IN_BOUNDARY
            feats[i] = bvec
        else:
            ids[i] = rank[s]
            feats[i] = prof[s]
    return Encoded(ids, feats, n_letters=sum(counts.values()), n_types=len(counts), rank_of=rank)


def window_bounds(n: int, window: int = WINDOW) -> list[tuple[int, int]]:
    """k = ceil(n / window) contiguous, nearly equal windows covering [0, n)."""
    if n <= 0:
        return [(0, 0)]
    k = max(1, math.ceil(n / window))
    edges = [round(i * n / k) for i in range(k + 1)]
    return [(edges[i], edges[i + 1]) for i in range(k)]


def window_inputs(enc: Encoded, a: int, b: int, window: int = WINDOW) -> tuple[np.ndarray, np.ndarray]:
    """RIGHT-padded prompt for window [a, b): cipher ids + PAD* + SEP (length window + 1), and its features.

    Right padding puts cipher symbol t at position t and its answer step at position window + 1 + t, a constant
    relative (RoPE) distance for every window length, which makes the input->output alignment easy to learn."""
    ids = enc.ids[a:b]
    pad = window - len(ids)
    if pad < 0:
        raise ValueError("window too long")
    full = np.concatenate([ids, np.full(pad, IN_PAD, np.int32), np.array([IN_SEP], np.int32)])
    ft = np.concatenate([enc.feats[a:b], np.zeros((pad, N_FEAT), np.float32), np.zeros((1, N_FEAT), np.float32)])
    return full, ft


NULL_CHAR = "\x00"      # in aligned target strings: 'this cipher symbol is a null (delete it)'


def hint_inputs(enc: Encoded, a: int, b: int) -> tuple[np.ndarray, np.ndarray]:
    """Aligned hint for the answer steps: answer step t (which predicts the plaintext of cipher symbol t) also
    receives the embedding of cipher symbol t. Makes the decoder a tagger with autoregressive LM context; the
    hypothesis class is therefore 1 output token (character, space or <null>) per cipher symbol."""
    return enc.ids[a:b].copy(), enc.feats[a:b].copy()


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
        self.null = self.index["<null>"]
        self.fam_ids = {f: self.index[t] for f, t in FAMILY_TOKENS.items()}
        self.id_fam = {v: k for k, v in self.fam_ids.items()}

    def __len__(self):
        return len(self.items)

    def encode_text(self, text: str) -> list[int]:
        return [self.null if c == NULL_CHAR else (self.index.get(c, self.unk) if c != "<" else self.unk)
                for c in text]

    def decode_raw(self, ids) -> str:
        """Aligned string: one character per id (<null> -> NULL_CHAR, <unk> -> '?', other specials dropped)."""
        return "".join(self.items[i] if i < self.n_chars else
                       (NULL_CHAR if i == self.null else "?" if i == self.unk else "") for i in ids)

    def decode(self, ids) -> str:
        return self.decode_raw(ids).replace(NULL_CHAR, "")

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
