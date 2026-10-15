"""Verifiable reward for GRPO, using our OWN copy of the scoring logic (not vcl.eval, which loads secrets).

char_acc here re-implements vcl.eval.score.char_acc (1 - Levenshtein / len(gold), floored at 0) so that RL rewards
are computed only from self-generated known answers. tests/test_neural.py checks it agrees with vcl.eval.score on
random strings.

Window reward r(output | window):
  language window, answered     r = char_acc - 0.25 * [char_acc < 0.3]        (penalise confident wrong answers)
  language window, abstained    r = 0
  noise window, abstained       r = 1
  noise window, answered        r = -0.5
  degenerate output             r -= 0.5   (longest single-char run >= 8, or one character > 50% of the output,
                                            or fewer than 4 distinct characters in >= 40 characters)
  family token correct          r += 0.1
"""
from __future__ import annotations

import numpy as np


def levenshtein(a: str, b: str) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    bb = np.frombuffer(b.encode("utf-32-le"), dtype=np.uint32)
    ar = np.arange(len(b) + 1)
    prev = ar.copy()
    for i, ch in enumerate(np.frombuffer(a.encode("utf-32-le"), dtype=np.uint32), 1):
        cur = np.empty_like(prev)
        cur[0] = i
        cur[1:] = np.minimum(prev[1:] + 1, prev[:-1] + (bb != ch))
        cur = np.minimum.accumulate(cur - ar) + ar
        prev = cur
    return int(prev[-1])


def char_acc(pred: str | None, gold: str | None) -> float:
    if pred is None or gold is None:
        return 0.0
    return max(0.0, 1 - levenshtein(pred, gold) / max(1, len(gold)))


def is_degenerate(text: str) -> bool:
    if not text:
        return False
    run, best = 1, 1
    for x, y in zip(text, text[1:]):
        run = run + 1 if x == y else 1
        best = max(best, run)
    if best >= 8:
        return True
    letters = text.replace(" ", "")
    if len(letters) >= 20:
        top = max(letters.count(c) for c in set(letters))
        if top / len(letters) > 0.5:
            return True
    if len(text) >= 40 and len(set(text)) < 4:
        return True
    return False


def window_reward(pred_text: str | None, pred_family: str | None, gold_text: str | None, gold_family: str) -> float:
    """pred_text None = abstained; gold_text None = noise window (correct answer: abstain)."""
    if gold_text is None:
        r = 1.0 if pred_text is None else -0.5
    elif pred_text is None:
        r = 0.0
    else:
        ca = char_acc(pred_text, gold_text)
        r = ca - (0.25 if ca < 0.3 else 0.0)
    if pred_text is not None and is_degenerate(pred_text):
        r -= 0.5
    if pred_family == gold_family:
        r += 0.1
    return float(r)
