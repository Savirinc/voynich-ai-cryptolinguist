"""Known-answer task schema.

The split between PublicTask (what a decipherer sees) and SecretAnswer (what only the
evaluator sees) is the core leakage control: solvers and agents import only PublicTask;
src/vcl/eval is the only package that loads secrets.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

BOUNDARY = " "  # word-boundary symbol in symbol streams

IDENTIFIABILITY = ("unique", "equivalence_class", "non_identifiable")


@dataclass
class PublicTask:
    task_id: str
    symbols: list[str]                 # ciphertext as a list of symbols; BOUNDARY marks a written space
    split: str                         # tune | test_in | test_lang | test_enc | test_both | test_null
    note: str = ""                     # only information a real decipherer would have

    def text(self, sep: str = "") -> str:
        return sep.join(self.symbols)


@dataclass
class SecretAnswer:
    task_id: str
    is_language: bool
    plaintext: str | None              # normalised plaintext (None for nonlinguistic decoys)
    family: str                        # encoding family or decoy generator
    key: dict | list | None
    language: str | None
    language_family: str | None
    source_id: str | None              # Gutenberg id
    source_url: str | None
    seed: int
    difficulty: dict = field(default_factory=dict)
    identifiability: str = "unique"
    recoverable_plaintext: str | None = None   # what an ideal solver could recover (e.g. consonants for abjad)


@dataclass
class Prediction:
    task_id: str
    is_language_prob: float            # P(underlying source is natural language)
    family: str | None = None          # guessed encoding family
    family_probs: dict = field(default_factory=dict)
    language: str | None = None
    plaintext: str | None = None       # None => abstain on plaintext
    confidence: float = 0.0            # P(plaintext is correct), used for calibration
    abstain: bool = True
    identifiability: str | None = None
    log: list = field(default_factory=list)


def save_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        for r in rows:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


def load_jsonl(path: Path, cls):
    with open(path, encoding="utf8") as f:
        return [cls(**json.loads(line)) for line in f]
