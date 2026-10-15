"""Solver v2 abstention: a self-null test that order-2 statistics cannot fool.

Motivation (E003, Gate 3 FAIL): order-2 Markov resamples of real ciphertext decode to locally fluent text and
the v1 calibrator accepts them. A careful decipherer asks: "would my solver be just as happy with a stream that
has only this text's order-2 statistics?" We therefore solve K order-2 resamples of the ciphertext itself and
abstain unless the real stream beats every resample by a margin.

The margin is set ONLY from real (tune-family, tune-book) ciphers: the smallest margin that keeps >= 95% of the
correct v1 answers. No decoy of any kind is used to set it.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict

from vcl.synthetic.schema import PublicTask, Prediction


def markov_resample(symbols: list[str], rng: random.Random, order: int = 2) -> list[str]:
    trans = defaultdict(Counter)
    for i in range(order, len(symbols)):
        trans[tuple(symbols[i - order:i])][symbols[i]] += 1
    out = list(symbols[:order])
    while len(out) < len(symbols):
        c = trans.get(tuple(out[-order:]))
        if not c:
            out.extend(symbols[:order]); continue
        out.append(rng.choices(list(c), weights=list(c.values()))[0])
    return out[: len(symbols)]


def self_null_gap(task: PublicTask, pred: Prediction, solve, k: int = 2, seed: int = 0, **kw) -> tuple[float, list]:
    """confidence(real) - max confidence(order-2 resamples). Large gap = structure beyond order 2."""
    rng = random.Random(seed)
    nulls = []
    for j in range(k):
        p = solve(PublicTask(f"{task.task_id}#null{j}", markov_resample(list(task.symbols), rng), task.split), **kw)
        nulls.append(0.0 if p.abstain else float(p.confidence))
    return float(pred.confidence) - max(nulls), nulls


def solve_v2(task: PublicTask, solve, margin: float, k: int = 2, seed: int = 0, **kw) -> Prediction:
    pred = solve(task, **kw)
    if pred.abstain or pred.plaintext is None:
        return pred
    gap, nulls = self_null_gap(task, pred, solve, k=k, seed=seed, **kw)
    pred.log = (pred.log or []) + [{"self_null_conf": nulls, "gap": round(gap, 4), "margin": margin}]
    if gap < margin:
        pred.abstain, pred.plaintext = True, None
        pred.log.append({"abstain_reason": "self-null indistinguishable (order-2 resample decodes as well)"})
    return pred
