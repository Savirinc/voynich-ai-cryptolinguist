"""Inference for the neural decipherer: windowed generation, key/consistency aggregation, calibrated abstention,
self-null check, and wrapping into vcl.synthetic.schema.Prediction.

Pipeline per task (uses only the PublicTask ciphertext):
  1. Too-short guard (same prior as solver v1): < MIN_LETTERS cipher letters -> abstain as non-identifiable.
  2. Rank-encode the whole task, split into windows (representation.py), greedy-decode every window (batched across
     tasks). Step 0 of each window is a family token; '<fam:noise>' means "no information" (abstain on that window).
  3. Aggregation. The decoder emits exactly one token (character / space / <null>) per cipher symbol.
     'concat': concatenate window outputs (nulls deleted). 'vote': for each glyph take the majority output token over
     ALL its positions in the task (one global key; enforces cross-window consistency) and re-decode the stream. Which aggregation is used for each predicted family is
     chosen on self-generated 'tune'-role dev tasks (choose_aggregation), never on test results.
  4. Confidence = logistic P(char acc >= 0.9) over decode-quality features (mean token logprob, worst window, noise
     probability, key-vote agreement, length...), fitted on the dev tasks only; abstain below the operating threshold
     (smallest threshold whose out-of-fold selective solved rate >= 0.95, as in solver v1).
  5. Self-null (as solver v2): decode one order-2 Markov resample of the task's own ciphertext; abstain unless the real
     confidence beats the resample's by `margin` (5th percentile of gaps of correct dev answers). No decoy generator
     is used anywhere.
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import numpy as np

from vcl.synthetic.schema import BOUNDARY, Prediction, PublicTask

from .data import pad_hints
from .representation import NULL_CHAR, TRAIN_FAMILIES, WINDOW, hint_inputs, rank_encode, window_bounds, window_inputs
from .reward import is_degenerate

MIN_LETTERS = 60
CONF_FEATURES = ["mean_lp", "min_win_lp", "p_noise", "p_fam", "aligned", "vote_agree", "log_n", "degenerate",
                 "frac_noise_windows"]


@dataclass
class TaskDecode:
    task_id: str
    n_letters: int
    windows: list = field(default_factory=list)     # per window: dict(text, fam_probs, mean_lp, a, b, abstained)
    fam_probs: dict = field(default_factory=dict)
    texts: dict = field(default_factory=dict)        # aggregation -> plaintext
    feats: dict = field(default_factory=dict)


def _letters(symbols) -> int:
    return sum(1 for s in symbols if s != BOUNDARY)


def decode_tasks(model, tasks: list[PublicTask], batch: int = 48, temperature: float = 0.0, seed: int = 0,
                 progress=None) -> list[TaskDecode]:
    """Greedy (or sampled) decoding of every window of every task, batched across tasks."""
    from .model import generate
    vocab = model.vocab
    jobs, encs, out = [], {}, []
    for ti, t in enumerate(tasks):
        td = TaskDecode(t.task_id, _letters(t.symbols))
        out.append(td)
        if td.n_letters < MIN_LETTERS:
            continue
        enc = rank_encode(list(t.symbols))
        encs[ti] = enc
        for a, b in window_bounds(len(t.symbols)):
            ids, ft = window_inputs(enc, a, b)
            hid, hft = hint_inputs(enc, a, b)
            jobs.append((ti, a, b, ids, ft, hid, hft))
    for i in range(0, len(jobs), batch):
        chunk = jobs[i:i + batch]
        ids = np.stack([j[3] for j in chunk]); ft = np.stack([j[4] for j in chunk])
        n_steps = np.array([j[2] - j[1] for j in chunk])
        hid, hft = pad_hints([{"hint_ids": j[5], "hint_feats": j[6]} for j in chunk], int(n_steps.max()))
        toks, lps, fam_p, fam_names = generate(model, ids, ft, hid, hft, n_steps, temperature=temperature,
                                               seed=seed + i)
        for k, (ti, a, b, *_) in enumerate(chunk):
            seq = toks[k]
            abst = seq[0] == vocab.fam_ids["noise"]
            n = max(1, len(seq) - 1)
            out[ti].windows.append({"a": a, "b": b, "raw": None if abst else vocab.decode_raw(seq[1:]),
                                    "fam_probs": dict(zip(fam_names, map(float, fam_p[k]))),
                                    "mean_lp": float(lps[k, 1:len(seq)].sum() / n) if len(seq) > 1 else 0.0,
                                    "abstained": bool(abst)})
        if progress:
            progress(min(i + batch, len(jobs)), len(jobs))
    for ti, td in enumerate(out):
        if ti in encs:
            _aggregate(td, tasks[ti], encs[ti])
    return out


def _aggregate(td: TaskDecode, task: PublicTask, enc):
    W = sorted(td.windows, key=lambda w: w["a"])
    td.windows = W
    fp = defaultdict(float)
    for w in W:
        for f, p in w["fam_probs"].items():
            fp[f] += p / len(W)
    td.fam_probs = dict(fp)
    answered = [w for w in W if not w["abstained"]]
    td.texts["concat"] = "".join(w["raw"] for w in answered).replace(NULL_CHAR, "") if answered else None
    aligned = bool(answered) and all(len(w["raw"]) == w["b"] - w["a"] for w in answered)
    agree = 0.0
    if aligned:
        votes = defaultdict(Counter)
        for w in answered:
            for s, c in zip(task.symbols[w["a"]:w["b"]], w["raw"]):
                if s != BOUNDARY:
                    votes[s][c] += 1
        key = {s: c.most_common(1)[0][0] for s, c in votes.items()}
        tot = sum(sum(c.values()) for c in votes.values())
        agree = sum(c.most_common(1)[0][1] for c in votes.values()) / max(1, tot)
        td.texts["vote"] = "".join(" " if s == BOUNDARY else key.get(s, "?") for s in task.symbols).replace(
            NULL_CHAR, "")
    else:
        td.texts["vote"] = td.texts["concat"]
    lps = [w["mean_lp"] for w in answered]
    fam_lang = {f: p for f, p in fp.items() if f != "noise"}
    td.feats = {
        "mean_lp": float(np.mean(lps)) if lps else -10.0,
        "min_win_lp": float(min(lps)) if lps else -10.0,
        "p_noise": float(fp.get("noise", 0.0)),
        "p_fam": float(max(fam_lang.values())) if fam_lang else 0.0,
        "aligned": float(aligned), "vote_agree": float(agree),
        "log_n": math.log(max(2, td.n_letters)),
        "degenerate": float(bool(td.texts["concat"]) and is_degenerate(td.texts["concat"])),
        "frac_noise_windows": 1.0 - len(answered) / max(1, len(W)),
    }


def predicted_family(td: TaskDecode) -> str:
    if not td.fam_probs:
        return "unknown"
    lang = {f: p for f, p in td.fam_probs.items() if f != "noise"}
    if td.fam_probs.get("noise", 0.0) > 0.5 or not lang:
        return "noise"
    return max(lang, key=lang.get)


def final_text(td: TaskDecode, agg_by_family: dict) -> str | None:
    fam = predicted_family(td)
    return td.texts.get(agg_by_family.get(fam, "concat"))


def feature_row(td: TaskDecode) -> list[float]:
    return [td.feats.get(k, 0.0) for k in CONF_FEATURES]


@dataclass
class Calibrator:
    model: object
    threshold: float
    margin: float
    agg_by_family: dict
    info: dict = field(default_factory=dict)

    def confidence(self, td: TaskDecode) -> float:
        if self.model is None or not td.feats or predicted_family(td) == "noise":
            return 0.0
        return float(self.model.predict_proba(np.array([feature_row(td)]))[0, 1])


def fit_calibrator(rows_feats: np.ndarray, solved: np.ndarray, target_precision: float = 0.95):
    """Logistic P(solved | features) and the operating threshold from 5-fold out-of-fold predictions."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
    if solved.sum() < 5 or (1 - solved).sum() < 5:
        return None, 1.01, None          # too few solved (or unsolved) dev tasks: never answer
    oof = cross_val_predict(model, rows_feats, solved, cv=5, method="predict_proba")[:, 1]
    thr = 1.01
    for t in np.linspace(0.3, 0.99, 70):
        m = oof >= t
        if m.sum() >= 5 and solved[m].mean() >= target_precision:
            thr = float(t); break
    model.fit(rows_feats, solved)
    return model, thr, oof


def to_prediction(task: PublicTask, td: TaskDecode, cal: Calibrator | None, null_conf: float | None = None,
                  extra_log: dict | None = None) -> Prediction:
    log = [{"neural": True, "fam_probs": {k: round(v, 4) for k, v in td.fam_probs.items()}, "feats": td.feats}]
    if extra_log:
        log.append(extra_log)
    if td.n_letters < MIN_LETTERS:
        return Prediction(task.task_id, 0.5, family="unknown", abstain=True, identifiability="non_identifiable",
                          log=log + [f"abstain: {td.n_letters} letters < MIN_LETTERS"])
    fam = predicted_family(td)
    fam_probs = dict(td.fam_probs)
    if fam == "noise":
        return Prediction(task.task_id, float(1 - td.fam_probs.get("noise", 1.0)), family="unknown",
                          family_probs=fam_probs, abstain=True, identifiability="non_identifiable",
                          log=log + ["abstain: noise family"])
    text = final_text(td, cal.agg_by_family if cal else {})
    conf = cal.confidence(td) if cal else 0.0
    if cal is not None and cal.threshold < 0:      # forced-answer diagnostic mode
        return Prediction(task.task_id, 0.5, family=fam, family_probs=fam_probs, plaintext=text, confidence=conf,
                          abstain=text is None, identifiability="unique", log=log + ["forced answer (diagnostic)"])
    thr = cal.threshold if cal else 1.01
    abstain = text is None or conf < thr
    if not abstain and null_conf is not None and cal is not None and conf - null_conf < cal.margin:
        abstain = True
        log.append({"abstain_reason": "self-null indistinguishable", "null_conf": null_conf, "margin": cal.margin})
    log.append({"confidence": conf, "threshold": thr, "null_conf": null_conf})
    return Prediction(task.task_id, is_language_prob=float(max(conf, 1 - td.fam_probs.get("noise", 0.0)) * 0.999),
                      family=fam, family_probs=fam_probs, language=None, plaintext=None if abstain else text,
                      confidence=conf, abstain=abstain,
                      identifiability="unique" if not abstain else "equivalence_class", log=log)


def self_null_tasks(tasks: list[PublicTask], seed: int = 0) -> list[PublicTask]:
    """One order-2 Markov resample of each task's own ciphertext (solver v2's self-null)."""
    from vcl.solvers.selfnull import markov_resample
    rng = random.Random(seed)
    return [PublicTask(f"{t.task_id}#null0", markov_resample(list(t.symbols), rng), t.split) for t in tasks]


def predict_tasks(model, tasks: list[PublicTask], cal: Calibrator, batch: int = 48, self_null: bool = True,
                  progress=None) -> tuple[list[Prediction], list[TaskDecode]]:
    """Full prediction for a list of tasks (decode, calibrate, self-null check for would-be answers)."""
    decs = decode_tasks(model, tasks, batch=batch, progress=progress)
    preds = [to_prediction(t, d, cal) for t, d in zip(tasks, decs)]
    if self_null:
        idx = [i for i, p in enumerate(preds) if not p.abstain]
        if idx:
            nd = decode_tasks(model, self_null_tasks([tasks[i] for i in idx]), batch=batch)
            for i, d in zip(idx, nd):
                preds[i] = to_prediction(tasks[i], decs[i], cal, null_conf=cal.confidence(d))
    return preds, decs


__all__ = ["decode_tasks", "predict_tasks", "to_prediction", "fit_calibrator", "Calibrator", "predicted_family",
           "final_text", "self_null_tasks", "MIN_LETTERS", "TRAIN_FAMILIES", "WINDOW"]
