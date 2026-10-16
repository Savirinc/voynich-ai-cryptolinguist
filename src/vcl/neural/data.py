"""Self-generated known-answer tasks for training and tuning the neural decipherer.

Leakage controls (same rules as solver v1, experiments/e003_tune.py):
  * plaintext only from books whose PUBLIC role (data/derived/benchmark_v1/book_roles.json) is 'ref' or 'tune' and
    whose language family is a TRAIN family (germanic, romance, slavic);
  * only TRAIN encodings (mono, homophonic, vigenere, columnar, nulls) from vcl.synthetic.encoders;
  * abstention is trained on pure-noise streams from vcl.synthetic.encoders.one_time_pad (a generic
    'no information' stream; recorded in the report). No decoy generator (vcl.synthetic.decoys) is used anywhere;
  * nothing under data/derived/benchmark_v1/secret/ is read.

Book split inside the allowed pool: SFT and GRPO train on 'ref'-role books; confidence calibration, aggregation
choices and the pre-test dev comparison use 'tune'-role books (so the calibration set has unseen source documents,
like the test splits).
"""
from __future__ import annotations

import json
import random
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np

from vcl.synthetic.corpora import load_books
from vcl.synthetic.encoders import ENCODERS, decode

from .representation import (BOUNDARY, IN_PAD, N_FEAT, NULL_CHAR, TRAIN_FAMILIES, WINDOW, OutVocab, hint_inputs,
                             rank_encode, window_bounds, window_inputs)

ROOT = Path(__file__).resolve().parents[3]
TRAIN_LANG_FAMILIES = ("germanic", "romance", "slavic")
ALLOWED_ROLES = ("ref", "tune")


@lru_cache(maxsize=4)
def books_for(role: str) -> tuple:
    """Books with the given public role, TRAIN language families only."""
    assert role in ALLOWED_ROLES, role
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    out = tuple(b for b in load_books()
                if roles[b["id"]]["role"] == role and roles[b["id"]]["family"] in TRAIN_LANG_FAMILIES)
    assert out and all(b["family"] in TRAIN_LANG_FAMILIES for b in out)
    return out


def train_char_counts() -> Counter:
    c: Counter = Counter()
    for role in ALLOWED_ROLES:
        for b in books_for(role):
            c.update(b["text"])
    return c


def sample_plaintext(text: str, length: int, rng: random.Random) -> str:
    start = rng.randrange(0, max(1, len(text) - length - 50))
    sp = text.find(" ", start)
    chunk = text[sp + 1: sp + 1 + length]
    return chunk[: chunk.rfind(" ")] if " " in chunk else chunk


def gen_task(rng: random.Random, role: str, family: str | None = None, length: int | None = None,
             p_noise: float = 0.1, lengths=(300, 1000, 3000)) -> dict:
    """One known-answer task. family='noise' -> one_time_pad stream (correct answer: abstain)."""
    books = books_for(role)
    langs = sorted({b["lang"] for b in books})
    lang = rng.choice(langs)
    book = rng.choice([b for b in books if b["lang"] == lang])
    if family is None:
        family = "noise" if rng.random() < p_noise else rng.choice(TRAIN_FAMILIES)
    length = length or rng.choice(lengths)
    plain = sample_plaintext(book["text"], length, rng)
    if family == "noise":
        syms, key, _, _ = ENCODERS["one_time_pad"](plain, rng)
        return {"family": "noise", "symbols": syms, "plain": None, "recov": None, "key": None, "lang": lang,
                "length": len(plain)}
    syms, key, _, recov = ENCODERS[family](plain, rng)
    return {"family": family, "symbols": syms, "plain": plain, "recov": recov, "key": key, "lang": lang,
            "length": len(plain)}


def window_target_raw(task: dict, a: int, b: int) -> str | None:
    """ALIGNED target for cipher window [a, b): exactly one character per cipher symbol (' ' for a boundary,
    NULL_CHAR for a null symbol). None => abstain (noise)."""
    fam, syms, key = task["family"], task["symbols"], task["key"]
    if fam == "noise":
        return None
    w = syms[a:b]
    if fam in ("mono", "homophonic"):
        raw = decode(fam, w, key)                     # stateless 1:1 decoders: exact on any slice
    elif fam == "nulls":
        inv = {g: c for c, g in key["key"].items()}
        raw = "".join(" " if s == BOUNDARY else inv.get(s, NULL_CHAR) for s in w)
    elif fam == "vigenere":
        plain = task["plain"]
        assert len(plain) == len(syms)
        raw = plain[a:b]                              # 1:1 aligned, spaces <-> boundaries
    elif fam == "columnar":
        # only the substitution layer is recoverable from a window: letters in CIPHER order
        inv = {g: c for c, g in key["glyph"].items()}
        raw = "".join(inv[s] for s in w)
    else:
        raise ValueError(fam)
    assert len(raw) == len(w)
    return raw


def window_target(task: dict, a: int, b: int) -> str | None:
    """Plaintext the window decodes to (nulls deleted); None => abstain. Used for rewards and dev scoring."""
    raw = window_target_raw(task, a, b)
    return None if raw is None else raw.replace(NULL_CHAR, "")


def target_ids(task: dict, raw: str | None, vocab: OutVocab) -> list[int]:
    """[family token] + one id per cipher symbol (noise: just '<fam:noise>')."""
    fam_tok = vocab.fam_ids[task["family"]]
    if raw is None:
        return [fam_tok]
    return [fam_tok] + vocab.encode_text(raw)


def task_windows(task: dict, vocab: OutVocab | None = None, window: int = WINDOW) -> list[dict]:
    """All windows of a task as model examples (prompt ids/features, aligned hints, and if vocab is given, targets)."""
    enc = rank_encode(task["symbols"])
    out = []
    for a, b in window_bounds(len(task["symbols"]), window):
        ids, ft = window_inputs(enc, a, b, window)
        hid, hft = hint_inputs(enc, a, b)
        ex = {"ids": ids, "feats": ft, "hint_ids": hid, "hint_feats": hft, "a": a, "b": b}
        if vocab is not None:
            raw = window_target_raw(task, a, b)
            ex["target_text"] = None if raw is None else raw.replace(NULL_CHAR, "")
            ex["target"] = target_ids(task, raw, vocab)
            ex["family"] = task["family"]
        out.append(ex)
    return out


def example_stream(seed: int, role: str, vocab: OutVocab, p_noise: float = 0.1, max_windows_per_task: int = 3,
                   lengths=(150, 300, 600, 1000, 2000, 3000)):
    """Infinite generator of window examples from fresh random tasks (at most `max_windows_per_task` per task
    so long tasks do not dominate)."""
    rng = random.Random(seed)
    while True:
        task = gen_task(rng, role, p_noise=p_noise, lengths=lengths)
        wins = task_windows(task, vocab)
        rng.shuffle(wins)
        for w in wins[:max_windows_per_task]:
            yield w


def pad_hints(examples: list[dict], T: int) -> tuple[np.ndarray, np.ndarray]:
    """Hints for answer input positions 0..T-1 (position t carries cipher symbol t; beyond the window: PAD)."""
    hid = np.full((len(examples), T), IN_PAD, np.int32)
    hft = np.zeros((len(examples), T, N_FEAT), np.float32)
    for i, e in enumerate(examples):
        n = min(T, len(e["hint_ids"]))
        hid[i, :n] = e["hint_ids"][:n]
        hft[i, :n] = e["hint_feats"][:n]
    return hid, hft


def pad_batch(examples: list[dict], pad_out: int):
    """Stack prompts, teacher-forcing targets and hints.
    Returns ids [B,P], feats [B,P,F], out [B,T], mask [B,T], hint_ids [B,T-1], hint_feats [B,T-1,F]
    (answer input position t = out[:, t] embedding + hint of cipher symbol t, predicting out[:, t+1])."""
    ids = np.stack([e["ids"] for e in examples])
    lf = np.stack([e["feats"] for e in examples])
    T = max(2, max(len(e["target"]) for e in examples))
    out = np.full((len(examples), T), pad_out, np.int32)
    mask = np.zeros((len(examples), T), np.float32)
    for i, e in enumerate(examples):
        out[i, : len(e["target"])] = e["target"]
        mask[i, : len(e["target"])] = 1.0
    hid, hft = pad_hints(examples, T - 1)
    return ids, lf, out, mask, hid, hft


__all__ = ["books_for", "gen_task", "task_windows", "example_stream", "pad_batch", "pad_hints", "window_target",
           "window_target_raw", "BOUNDARY"]
