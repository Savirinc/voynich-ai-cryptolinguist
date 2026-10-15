"""Frozen solver entry point: `solve(task, library, budget) -> Prediction`.

Pipeline (all decisions use only the PublicTask ciphertext; no secrets are read anywhere in vcl.solvers):
  1. Too-short guard: fewer than MIN_LETTERS cipher letters -> abstain as non-identifiable. MIN_LETTERS is a prior
     (roughly twice the unicity distance of a simple substitution over ~25 letters), not tuned on any test split.
  2. Encoding-family classifier (closed set of TRAIN encodings + open-set 'unknown').
  3. For each plausible family (boundary-free streams -> columnar, which includes the identity order):
       stage A: rank library languages by cheap statistics (langrank),
       stage B: quick low-budget solve for the top `quick_langs` languages, ranked by LM gap,
       stage C: full solve for the best `full_langs` languages.
     If the open-set detector says 'unknown', generic substitution solvers (mono, homophonic) are run as well.
  4. Pick the decode with the lowest gap = xent(decode | its LM) - typical xent of that LM.
  5. Confidence = calibrated P(char acc >= 0.9) from a logistic model over decode-quality features, fitted ONLY on
     self-generated TRAIN-family x TRAIN-encoding tasks from 'tune'-role books (experiments/e003_tune.py).
     Abstain when confidence < the calibrated operating threshold.
"""
from __future__ import annotations

import math
import pickle
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from vcl.synthetic.schema import PublicTask, Prediction

from .classifier import load_classifier, ART
from .columnar import bigram_mi, search_orders, solve_columnar
from .langrank import language_distances
from .engine import unigram_kl
from .lm import Library, CharLM
from .substitution import (SolveResult, encode_symbols, estimate_n_nulls, null_order, relabel, remove_symbols,
                           solve_homophonic, solve_mono, solve_nulls)
from .vigenere import solve_vigenere

MIN_LETTERS = 60
SOLVER_VERSION = "solver-v1"
FAMILIES = ["mono", "homophonic", "vigenere", "columnar", "nulls"]


@dataclass
class Budget:
    quick_langs: int = 14       # languages given a quick solve (stage B)
    full_langs: int = 2         # languages given a full solve (stage C)
    scale: float = 1.0          # multiplies all iteration counts
    max_families: int = 2       # max encoding families tried (plus generic fallbacks when 'unknown')
    family_min_prob: float = 0.15


def _it(x, scale):
    return max(200, int(x * scale))


def _run(fam: str, stage: str, seq, S, lm: CharLM, ctx: dict, scale: float, seed: int) -> SolveResult:
    q = stage == "quick"
    if fam == "mono":
        return solve_mono(seq, S, lm, iters=_it(10000 if q else 20000, scale), restarts=2 if q else 6, seed=seed,
                          polish=not q)
    if fam == "homophonic":
        return solve_homophonic(seq, S, lm, iters=_it(10000 if q else 30000, scale), restarts=2 if q else 4, seed=seed)
    if fam == "nulls":
        if q:
            k = ctx.setdefault("n_nulls", estimate_n_nulls(seq, S))
            return solve_nulls(seq, S, lm, iters=_it(4000, scale), restarts=1, seed=seed, ks=[k])
        return solve_nulls(seq, S, lm, iters=_it(8000, scale), restarts=3, seed=seed)
    if fam == "vigenere":
        if q:
            return solve_vigenere(seq, S, lm, iters=_it(2000, scale), restarts=1, beam=8, n_periods=1, seed=seed)
        return solve_vigenere(seq, S, lm, iters=_it(30000, scale), restarts=5, beam=30, n_periods=2, seed=seed)
    if fam == "columnar":
        if "orders" not in ctx:
            letters = seq[seq > 0]
            cands = search_orders(letters, S, seed=seed, sa_iters=_it(8000, scale), sa_restarts=3)
            # identity (no transposition) is always a candidate, ranked by the same statistic
            cands = sorted(cands + [(bigram_mi(letters, S), 1, [0])], key=lambda x: -x[0])
            ctx["orders"] = cands
        if q:
            return solve_columnar(seq, S, lm, n_candidates=1, mono_iters=_it(10000, scale), mono_restarts=2, seed=seed,
                                  cands=ctx["orders"])
        return solve_columnar(seq, S, lm, n_candidates=3, mono_iters=_it(20000, scale), mono_restarts=6, seed=seed,
                              cands=ctx["orders"])
    raise ValueError(fam)


def _variant(fam: str) -> str:
    return "nospace" if fam == "columnar" else "space"


def _adjust(r: SolveResult, lm: CharLM) -> SolveResult:
    """gap := LM gap + KL(decoded letter distribution || language letter distribution). The KL term rejects
    degenerate many-to-one decodes ('nanana...') that a char n-gram LM alone scores well."""
    if "gap_lm" not in r.info:
        kl = unigram_kl(r.text, lm)
        r.info = {**r.info, "gap_lm": float(r.gap), "unigram_kl": kl}
        r.gap = float(r.gap + kl)
    return r


def solve_family(fam: str, seq, S, library: Library, budget: Budget, ctx: dict, seed: int = 0,
                 log: list | None = None) -> list[SolveResult]:
    """Run the 3-stage language search for one encoding family; returns full-stage results, best (lowest gap) first."""
    lms = [library.lm(l, _variant(fam)) for l in library]
    dist = language_distances(seq, S, lms, fam)
    ranked = sorted(lms, key=lambda m: dist[m.lang])[: budget.quick_langs]
    quick = []
    for lm in ranked:
        quick.append(_run(fam, "quick", seq, S, lm, ctx, budget.scale, seed))
    for r in quick:
        _adjust(r, library.lm(r.lang, _variant(fam)))
    quick.sort(key=lambda r: r.gap)
    full = []
    for r in quick[: budget.full_langs]:
        lm = library.lm(r.lang, _variant(fam))
        full.append(_adjust(_run(fam, "full", seq, S, lm, ctx, budget.scale, seed + 1), lm))
    # keep quick results for languages not fully solved (for margins)
    done = {r.lang for r in full}
    rest = [r for r in quick if r.lang not in done]
    out = sorted(full, key=lambda r: r.gap) + rest
    for r in out:   # label by the family that was run (solve_mono may fall back to a many-to-one engine)
        if r.solver != fam:
            r.info = {**r.info, "engine": r.solver}
            r.solver = fam
    if log is not None:
        log.append({"family": fam, "quick": [(r.lang, round(r.gap, 4)) for r in quick],
                    "full": [(r.lang, round(r.gap, 4)) for r in full]})
    return out


def solve_nulls_family(seq, S, library: Library, budget: Budget, ctx: dict, seed: int = 0, max_nulls: int = 6,
                       log: list | None = None) -> list[SolveResult]:
    """Nulls: choose how many of the most null-like symbols to delete (k = 0..max_nulls) by quick mono solves in the
    3 best stage-A languages, then run the full mono language search on the reduced stream."""
    order = null_order(seq, S)
    lms = [library.lm(l) for l in library]
    trial = []
    for k in range(0, max_nulls + 1):
        red, S2 = relabel(remove_symbols(seq, set(order[:k])))
        if (red > 0).sum() < 20:
            break
        dist = language_distances(red, S2, lms, "mono")
        best_k = None
        for lm in sorted(lms, key=lambda m: dist[m.lang])[:3]:
            if S2 > lm.A - 1:
                continue
            r = solve_mono(red, S2, lm, iters=_it(6000, budget.scale), restarts=1, seed=seed, polish=False)
            if best_k is None or r.gap < best_k:
                best_k = r.gap
        if best_k is not None:
            trial.append((best_k, k))
    if not trial:
        return solve_family("homophonic", seq, S, library, budget, ctx, seed, log)
    _, k = min(trial)
    red, S2 = relabel(remove_symbols(seq, set(order[:k])))
    out = solve_family("mono", red, S2, library, budget, {}, seed, log)
    for r in out:
        r.solver = "nulls"
        r.info = {**r.info, "nulls_removed": k}
    if log is not None:
        log.append({"nulls_k_trials": [(kk, round(g, 4)) for g, kk in trial], "k": k})
    return out


def _lexicon(text: str, lm: CharLM, fam: str) -> float:
    if fam == "columnar":
        return -1.0
    return lm.lexicon_rate(text)


_CAL = None


def load_calibrator(path: Path = ART / "calibrator.pkl"):
    global _CAL
    if _CAL is None and path.exists():
        with open(path, "rb") as f:
            _CAL = pickle.load(f)
    return _CAL


def confidence_features(best: SolveResult, results: list[SolveResult], clf_out: dict, n_letters: int, S: int,
                        library: Library) -> dict:
    fam = best.solver
    lm = library.lm(best.lang, _variant(fam))
    lex = _lexicon(best.text, lm, fam)
    others = [r.gap for r in results if r.lang != best.lang]
    margin = min(min(others) - best.gap, 2.0) if others else 2.0
    return {
        "gap": float(best.gap), "lex": float(lex), "has_lex": float(lex >= 0), "log_n": math.log(n_letters),
        "margin": float(margin), "p_family": float(clf_out["closed_probs"].get(fam, 0.0)),
        "p_unknown": float(clf_out["p_unknown"]), "types_per_sqrt_n": S / math.sqrt(n_letters),
        **{f"fam_{f}": float(fam == f) for f in FAMILIES},
    }


def heuristic_confidence(cf: dict) -> float:
    """Fallback used only before a calibrator exists (i.e. while generating calibration data)."""
    z = -4.0 * cf["gap"] + (4.0 * cf["lex"] if cf["has_lex"] else 0.0) + 0.5 * cf["log_n"] - 3.0
    return float(1 / (1 + math.exp(-z)))


def solve(task: PublicTask, library: Library | None = None, budget: Budget | None = None, seed: int = 0,
          force_answer: bool = False) -> Prediction:
    """Solve one task. `force_answer=True` (calibration only) returns the best decode even below threshold."""
    t0 = time.time()
    library = library or Library.full()
    budget = budget or Budget()
    log: list = [{"solver_version": SOLVER_VERSION, "library": library.name}]
    seq, names = encode_symbols(task.symbols)
    S = len(names) - 1
    n_letters = int((seq > 0).sum())
    clf = load_classifier()
    if n_letters < 2:
        return Prediction(task.task_id, 0.0, family="unknown", abstain=True, identifiability="non_identifiable",
                          log=log + ["empty"])
    co = clf.predict(task.symbols)
    fam_probs = co["family_probs"]
    pred_family = max(fam_probs, key=fam_probs.get)
    log.append({"family_probs": {k: round(v, 4) for k, v in fam_probs.items()}, "ood_distance": round(co["ood_distance"], 3)})
    if n_letters < MIN_LETTERS:
        log.append(f"abstain: only {n_letters} letters < MIN_LETTERS={MIN_LETTERS}")
        return Prediction(task.task_id, is_language_prob=0.5 * co["typicality"], family=pred_family,
                          family_probs=fam_probs, language=None, plaintext=None, confidence=0.0, abstain=True,
                          identifiability="non_identifiable", log=log)

    has_boundary = bool((seq == 0).any())
    closed = co["closed_probs"]
    if not has_boundary:
        fams = ["columnar"]
    else:
        cand = sorted((f for f in FAMILIES if f != "columnar"), key=lambda f: -closed.get(f, 0.0))
        fams = [f for f in cand if closed.get(f, 0.0) >= budget.family_min_prob][: budget.max_families] or cand[:1]
        if co["p_unknown"] > 0.5:
            for g in ("mono", "homophonic"):
                if g not in fams:
                    fams.append(g)
    ctx: dict = {}
    by_fam: dict[str, list[SolveResult]] = {}
    for f in fams:
        if f == "vigenere" and S > max(library.lm(l).A - 1 for l in library):
            continue
        if f == "nulls":
            by_fam[f] = solve_nulls_family(seq, S, library, budget, ctx, seed=seed, log=log)
        else:
            by_fam[f] = solve_family(f, seq, S, library, budget, ctx, seed=seed, log=log)
    if not by_fam:   # e.g. vigenere skipped because the inventory exceeds every LM alphabet
        by_fam["homophonic"] = solve_family("homophonic", seq, S, library, budget, ctx, seed=seed, log=log)
    best = min((rs[0] for rs in by_fam.values()), key=lambda r: r.gap)
    # prefer the classifier's top family when it is nearly as good (avoids e.g. homophonic overfitting mono)
    top = fams[0]
    if top in by_fam and by_fam[top][0] is not best and by_fam[top][0].gap <= best.gap + 0.05 \
            and closed.get(top, 0) >= 0.6:
        best = by_fam[top][0]
    cf = confidence_features(best, by_fam[best.solver], co, n_letters, S, library)
    cal = load_calibrator()
    if cal is not None:
        x = np.array([[cf[k] for k in cal["features"]]])
        conf = float(cal["model"].predict_proba(x)[0, 1])
        thr = cal["threshold"]
    else:
        conf, thr = heuristic_confidence(cf), 0.5
    abstain = conf < thr and not force_answer
    is_lang = float(max(conf, 0.5 * co["typicality"]))
    log.append({"chosen": {"family": best.solver, "lang": best.lang, "gap": round(best.gap, 4), "info": _jsonable(best.info)},
                "conf_features": cf, "confidence": conf, "threshold": thr, "seconds": round(time.time() - t0, 2)})
    if pred_family == "unknown":
        fam_out = "unknown"
    else:
        fam_out = pred_family
    return Prediction(task.task_id, is_language_prob=is_lang, family=fam_out, family_probs=fam_probs,
                      language=best.lang, plaintext=None if abstain else best.text, confidence=conf,
                      abstain=abstain, identifiability="unique" if not abstain else
                      ("equivalence_class" if is_lang >= 0.5 else "non_identifiable"), log=log)


def _jsonable(d):
    if isinstance(d, dict):
        return {k: _jsonable(v) for k, v in d.items()}
    if isinstance(d, (list, tuple)):
        return [_jsonable(v) for v in d]
    if isinstance(d, (np.integer,)):
        return int(d)
    if isinstance(d, (np.floating,)):
        return float(d)
    if isinstance(d, float) and math.isnan(d):
        return None
    return d
