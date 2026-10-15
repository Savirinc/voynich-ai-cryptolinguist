"""Blind evaluator: the only module that loads SecretAnswer files.

Per task: character accuracy (1 - normalised edit distance vs the *recoverable* plaintext),
word accuracy, solved flag (char acc >= 0.90, the Gate 1 threshold), family identification,
language identification, abstention correctness and calibration inputs.
Tables are reported per split, never pooled across holdout axes.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from vcl.synthetic.encoders import comparable
from vcl.synthetic.schema import SecretAnswer, Prediction, load_jsonl

SOLVED = 0.90


def levenshtein(a: str, b: str) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    bb = np.frombuffer(b.encode("utf-32-le"), dtype=np.uint32)
    ar = np.arange(len(b) + 1)
    prev = ar.copy()
    aa = np.frombuffer(a.encode("utf-32-le"), dtype=np.uint32)
    for i, ch in enumerate(aa, 1):
        cur = np.empty_like(prev)
        cur[0] = i
        cur[1:] = np.minimum(prev[1:] + 1, prev[:-1] + (bb != ch))
        cur = np.minimum.accumulate(cur - ar) + ar   # insertions within the row
        prev = cur
    return int(prev[-1])


def char_acc(pred: str | None, gold: str | None) -> float:
    if pred is None or gold is None:
        return 0.0
    return max(0.0, 1 - levenshtein(pred, gold) / max(1, len(gold)))


def word_acc(pred: str | None, gold: str | None) -> float:
    if pred is None or gold is None:
        return 0.0
    p, g = pred.split(" "), gold.split(" ")
    return sum(x == y for x, y in zip(p, g)) / max(1, len(g))


def score_task(sec: SecretAnswer, pred: Prediction) -> dict:
    gold = comparable(sec.family, sec.recoverable_plaintext)
    out = comparable(sec.family, pred.plaintext) if not pred.abstain else None
    should_abstain = (not sec.is_language) or sec.identifiability == "non_identifiable"
    ca = char_acc(out, gold) if gold is not None else 0.0
    row = {
        "task_id": sec.task_id, "family": sec.family, "language": sec.language,
        "language_family": sec.language_family, "is_language": sec.is_language,
        "identifiability": sec.identifiability, "length": sec.difficulty.get("plaintext_chars"),
        "abstained": pred.abstain, "should_abstain": should_abstain,
        "char_acc": ca, "word_acc": word_acc(out, gold) if gold else 0.0,
        "solved": bool(ca >= SOLVED and not should_abstain),
        "family_correct": pred.family == sec.family if sec.is_language else None,
        "language_correct": pred.language == sec.language if sec.is_language else None,
        "is_language_prob": pred.is_language_prob, "confidence": pred.confidence,
        "false_discovery": bool(should_abstain and not pred.abstain),
    }
    return row


def ece(conf, correct, bins=10):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    if len(conf) == 0:
        return float("nan")
    idx = np.minimum((conf * bins).astype(int), bins - 1)
    e = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            e += m.mean() * abs(conf[m].mean() - correct[m].mean())
    return float(e)


def summarise(rows: list[dict]) -> dict:
    lang = [r for r in rows if not r["should_abstain"]]
    null = [r for r in rows if r["should_abstain"]]
    answered = [r for r in lang if not r["abstained"]]
    s = {"n": len(rows), "n_language_tasks": len(lang), "n_null_tasks": len(null)}
    if lang:
        s.update({
            "mean_char_acc": float(np.mean([r["char_acc"] for r in lang])),
            "solved_rate": float(np.mean([r["solved"] for r in lang])),
            "mean_word_acc": float(np.mean([r["word_acc"] for r in lang])),
            "family_id_acc": float(np.mean([bool(r["family_correct"]) for r in lang])),
            "language_id_acc": float(np.mean([bool(r["language_correct"]) for r in lang])),
            "abstention_rate": float(np.mean([r["abstained"] for r in lang])),
            "selective_solved_rate": float(np.mean([r["solved"] for r in answered])) if answered else None,
            "ece": ece([r["confidence"] for r in lang], [r["solved"] for r in lang]),
        })
    if null:
        s["null_false_discovery_rate"] = float(np.mean([r["false_discovery"] for r in null]))
    by_fam = defaultdict(list)
    for r in lang:
        by_fam[r["family"]].append(r)
    s["by_family"] = {f: {"n": len(v), "solved_rate": float(np.mean([r["solved"] for r in v])),
                          "mean_char_acc": float(np.mean([r["char_acc"] for r in v]))} for f, v in sorted(by_fam.items())}
    by_lf = defaultdict(list)
    for r in lang:
        by_lf[r["language_family"]].append(r)
    s["by_language_family"] = {f: {"n": len(v), "solved_rate": float(np.mean([r["solved"] for r in v]))}
                               for f, v in sorted(by_lf.items())}
    if null:
        by_null = defaultdict(list)
        for r in null:
            by_null[r["family"]].append(r)
        s["null_by_kind"] = {k: {"n": len(v), "fdr": float(np.mean([r["false_discovery"] for r in v]))}
                             for k, v in sorted(by_null.items())}
    return s


def evaluate(bench_dir: Path, split: str, preds: list[Prediction]) -> tuple[list[dict], dict]:
    secrets = {s.task_id: s for s in load_jsonl(bench_dir / "secret" / f"{split}.jsonl", SecretAnswer)}
    pmap = {p.task_id: p for p in preds}
    rows = [score_task(sec, pmap.get(tid, Prediction(tid, 0.5))) for tid, sec in secrets.items()]
    return rows, summarise(rows)


def write_report(path: Path, summaries: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summaries, indent=1))
