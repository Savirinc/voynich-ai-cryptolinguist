"""Default event stream for Voynich structure models (PROTOCOL_v1 sections 1-2).

Default stream: prose tokens only, clean tokens only ([a-z]+, no '?'), first alternative
reading, uncertain spaces (',') treated as word boundaries. Each manuscript line is one
sequence. Unclean tokens are dropped from the line (280 of 35,069 prose tokens corpus-wide).

Events of a line with words w1..wk:

    ^  w1 _ w2 _ ... _ wk $

'^' (BOS) is context only and is never predicted. Every word is followed by exactly one
end symbol: '_' (word end) or, for the line-final word, '$' (word end + line end). So

    n_events = n_glyphs + n_words
    bits/glyph = total bits / n_events      (EVA glyph incl. its word-end symbol)
    bits/word  = total bits / n_words       (sum of glyph bits over word + end symbol)

and every model is scored on exactly the same events. The predicted vocabulary is fixed to
EVA a-z plus '_' and '$' (28 symbols); there are no OOV exclusions.

Leakage control: `dev_lines` / `dev_fold_split` never return LOCKED_TEST leaves. The only
way to obtain locked lines is `locked_test_lines(..., confirm_final_scoring=True)`, which
must only be called by the single final scoring function in experiments/e002.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from functools import lru_cache

from vcl.corpus.ivtff import parse
from vcl.corpus.splits import dev_folds, locked_test_leaves

LETTERS = "abcdefghijklmnopqrstuvwxyz"
WORD_END = "_"
LINE_END = "$"
BOS = "^"
SYMBOLS = list(LETTERS) + [WORD_END, LINE_END]   # predicted vocabulary
V = len(SYMBOLS)                                 # 28
SYM2ID = {s: i for i, s in enumerate(SYMBOLS)}
BOS_ID = V                                       # context-only id (not predicted)
WE_ID, LE_ID = SYM2ID[WORD_END], SYM2ID[LINE_END]
VARIETIES = ("A", "B", "?")


@dataclass
class Line:
    leaf: str
    folio: str
    line_no: int
    currier: str          # 'A' | 'B' | '?'
    para_start: bool
    words: list[str] = field(default_factory=list)

    @property
    def n_glyphs(self) -> int:
        return sum(len(w) for w in self.words)

    @property
    def n_words(self) -> int:
        return len(self.words)


def encode_words(words: list[str]) -> list[int]:
    """Predicted event ids for one line (without BOS)."""
    out = []
    for i, w in enumerate(words):
        out.extend(SYM2ID[c] for c in w)
        out.append(LE_ID if i == len(words) - 1 else WE_ID)
    return out


def encode_line(line: Line) -> list[int]:
    return encode_words(line.words)


def decode_events(ids: list[int]) -> list[str]:
    """Inverse of encode_words; stops at the first '$'."""
    words, cur = [], ""
    for i in ids:
        if i in (WE_ID, LE_ID):
            if cur:
                words.append(cur)
            cur = ""
            if i == LE_ID:
                break
        elif i < len(LETTERS):
            cur += LETTERS[i]
    if cur:
        words.append(cur)
    return words


@lru_cache(maxsize=1)
def _tokens():
    return tuple(parse()[1])


def _build_lines(tokens, keep_leaf, merge_uncertain: bool = False) -> list[Line]:
    lines: dict[tuple, Line] = {}
    for t in tokens:
        if t.mode != "prose" or not keep_leaf(t.leaf):
            continue
        key = (t.folio, t.line_no)
        ln = lines.get(key)
        if ln is None:
            ln = lines[key] = Line(t.leaf, t.folio, t.line_no, t.currier if t.currier in VARIETIES else "?",
                                   t.para_start)
        if not t.is_clean:
            ln.words.append(None)   # placeholder: blocks a later uncertain-space merge
            continue
        if merge_uncertain and t.space_before == "," and ln.words and ln.words[-1] is not None:
            ln.words[-1] += t.eva
        else:
            ln.words.append(t.eva)
    out = []
    for ln in lines.values():
        ln.words = [w for w in ln.words if w is not None]
        if ln.words:
            out.append(ln)
    return out


def locked_set(tokens=None) -> set[str]:
    return set(locked_test_leaves(_tokens() if tokens is None else tokens))


def dev_lines(tokens=None, merge_uncertain: bool = False) -> list[Line]:
    """All DEV (non-locked) prose lines."""
    tokens = _tokens() if tokens is None else tokens
    locked = locked_set(tokens)
    return _build_lines(tokens, lambda leaf: leaf not in locked, merge_uncertain)


def fold_map(tokens=None) -> dict[str, int]:
    return dev_folds(_tokens() if tokens is None else tokens)


def dev_fold_split(fold: int, tokens=None, merge_uncertain: bool = False) -> tuple[list[Line], list[Line]]:
    """(train, test) lines for one of the 5 leaf-grouped DEV folds."""
    tokens = _tokens() if tokens is None else tokens
    folds = fold_map(tokens)
    lines = dev_lines(tokens, merge_uncertain)
    return ([ln for ln in lines if folds[ln.leaf] != fold], [ln for ln in lines if folds[ln.leaf] == fold])


def inner_split(lines: list[Line], frac: float = 0.1, salt: str = "vcl-e002-inner") -> tuple[list[Line], list[Line]]:
    """Carve an inner validation set from *training* leaves only (salted leaf hash)."""
    leaves = sorted({ln.leaf for ln in lines}, key=lambda l: hashlib.sha256(f"{salt}:{l}".encode()).hexdigest())
    k = max(1, round(frac * len(leaves)))
    val = set(leaves[:k])
    return [ln for ln in lines if ln.leaf not in val], [ln for ln in lines if ln.leaf in val]


def locked_test_lines(tokens=None, *, confirm_final_scoring: bool = False) -> list[Line]:
    """LOCKED_TEST prose lines. Only the single final scoring function may call this."""
    if not confirm_final_scoring:
        raise PermissionError("LOCKED_TEST lines are reserved for the one-time final scoring of a frozen model")
    tokens = _tokens() if tokens is None else tokens
    locked = locked_set(tokens)
    return _build_lines(tokens, lambda leaf: leaf in locked)


def stream_stats(lines: list[Line]) -> dict:
    return {"lines": len(lines), "words": sum(l.n_words for l in lines), "glyphs": sum(l.n_glyphs for l in lines),
            "events": sum(l.n_words + l.n_glyphs for l in lines), "leaves": len({l.leaf for l in lines})}
