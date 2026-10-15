"""System C: a pretrained reasoning model as hypothesis generator + experiment planner.

Loop per task (all inputs public):
  1. Baseline: the calibrated solver runs on the raw ciphertext.
  2. The LLM sees ciphertext statistics, a glyph-id rendering, and the baseline outcome, and proposes
     up to K pipelines of mechanism hypotheses (ops.py), each with a falsifiable prediction.
  3. Each pipeline is executed: transform -> calibrated solver -> post-map. Results go back to the LLM,
     which may propose one refinement round.
  4. Selection is verifier-guided and does NOT trust the LLM: the candidate with the highest calibrated
     solver confidence wins; if no candidate is non-abstaining, the agent abstains.
The LLM never writes plaintext. Controls with the same pipeline budget: `random` (uniformly sampled
pipelines) and `exhaustive` (every default pipeline), isolating the planner's contribution.
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter

from vcl.synthetic.schema import BOUNDARY, PublicTask, Prediction
from vcl.agents.ops import OPS, OP_DOCS, apply_pipeline
from vcl.agents.llm import extract_json

SYSTEM = """You are a cryptanalyst-paleographer working on a known-answer benchmark of unknown writing systems.
You receive statistics about a ciphertext written in abstract glyph ids (g0 = most frequent glyph, '|' = written space).
The underlying text may be natural language in an unknown language, encoded by an unknown mechanism, or may be
meaningless (a decoy). A calibrated substitution/transposition solver does the actual decoding; your job is to
propose hypotheses about the WRITING MECHANISM as pipelines of preprocessing ops that make the stream solvable,
each with a falsifiable prediction. Never guess plaintext. Prefer few, informative pipelines. Reply with JSON only."""

DEFAULT_PIPELINES = [[{"op": "reverse_words"}], [{"op": "reverse_all"}], [{"op": "remove_boundaries"}],
                     [{"op": "merge_pairs", "args": {"n_merges": 8}}], [{"op": "merge_pairs", "args": {"n_merges": 20}}],
                     [{"op": "chunk", "args": {"k": 2}}], [{"op": "chunk", "args": {"k": 3}}]]


def _entropy(c: Counter) -> float:
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values()) if n else 0.0


def describe(symbols: list[str]) -> tuple[str, dict]:
    """Public statistics + glyph-id rendering. Returns (text for the LLM, id map)."""
    glyphs = [s for s in symbols if s != BOUNDARY]
    freq = Counter(glyphs)
    ids = {g: f"g{i}" for i, (g, _) in enumerate(freq.most_common())}
    words = "".join("|" if s == BOUNDARY else "\x00" for s in symbols).split("|")
    wl = Counter(len(w) for w in words if w)
    pairs = Counter(zip(glyphs, glyphs[1:]))
    h1 = _entropy(freq)
    h2 = _entropy(pairs) - h1 if pairs else 0.0
    ioc = sum(v * (v - 1) for v in freq.values()) / max(1, len(glyphs) * (len(glyphs) - 1))
    per_ioc = []
    for p in range(1, 11):
        cols = [Counter(glyphs[i::p]) for i in range(p)]
        per_ioc.append(round(sum(sum(v * (v - 1) for v in c.values()) / max(1, sum(c.values()) * (sum(c.values()) - 1))
                                 for c in cols) / p, 4))
    pos = Counter(); tot = Counter()
    wsyms, cur = [], []
    for s in symbols + [BOUNDARY]:
        if s == BOUNDARY:
            if cur:
                wsyms.append(cur)
            cur = []
        else:
            cur.append(s)
    for w in wsyms:
        for j, g in enumerate(w):
            tot[g] += 1
            if j == 0:
                pos[(g, "initial")] += 1
            if j == len(w) - 1:
                pos[(g, "final")] += 1
    positional = [f"{ids[g]}:{pos[(g,'initial')]/tot[g]:.2f}/{pos[(g,'final')]/tot[g]:.2f}"
                  for g, _ in freq.most_common(15)]
    wfreq = Counter(" ".join(ids[g] for g in w) for w in wsyms)
    render = " ".join("|" if s == BOUNDARY else ids[s] for s in symbols[:160])
    stats = {
        "glyph_tokens": len(glyphs), "glyph_types": len(freq), "written_spaces": symbols.count(BOUNDARY),
        "words": len(wsyms), "word_length_hist": dict(sorted(wl.items())[:15]),
        "unique_word_share": round(len(wfreq) / max(1, len(wsyms)), 3),
        "h1_bits": round(h1, 3), "h2_cond_bits": round(h2, 3), "ioc": round(ioc, 4),
        "periodic_ioc_p1_to_10": per_ioc,
        "top_glyph_freq": [f"{ids[g]}:{v}" for g, v in freq.most_common(20)],
        "share_initial/final_for_top15": positional,
        "top_words": [f"[{w}]x{v}" for w, v in wfreq.most_common(10)],
    }
    text = json.dumps(stats) + "\nFIRST 160 SYMBOLS: " + render
    return text, {v: k for k, v in ids.items()}


def _summ(pred: Prediction) -> dict:
    return {"abstain": pred.abstain, "confidence": round(pred.confidence, 3), "family_guess": pred.family,
            "language_guess": pred.language, "is_language_prob": round(pred.is_language_prob, 3),
            "decode_preview": (pred.plaintext or "")[:160] if pred.plaintext else None}


def run_pipeline(task: PublicTask, pipeline, idmap, solve, **kw) -> Prediction:
    pipe = []
    for step in pipeline:
        step = dict(step)
        if step.get("op") == "drop_symbols":
            step["args"] = {"drop": [idmap[g] for g in (step.get("args") or {}).get("drop", []) if g in idmap]}
        if step.get("op") not in OPS:
            raise ValueError(f"unknown op {step.get('op')}")
        pipe.append(step)
    syms, post = apply_pipeline(list(task.symbols), pipe)
    if len([s for s in syms if s != BOUNDARY]) < 20:
        raise ValueError("pipeline destroyed the stream")
    p = solve(PublicTask(task.task_id, syms, task.split), **kw)
    if p.plaintext is not None:
        p.plaintext = post(p.plaintext)
    p.log = (p.log or []) + [{"pipeline": pipeline}]
    return p


def select(cands: list[tuple[list, Prediction]]) -> tuple[list, Prediction]:
    """Verifier-guided: highest calibrated confidence among non-abstaining candidates, else the baseline abstention."""
    live = [c for c in cands if not c[1].abstain and c[1].plaintext is not None]
    if not live:
        return cands[0]
    return max(live, key=lambda c: c[1].confidence)


def agent_solve(task: PublicTask, solve, llm=None, mode: str = "llm", k: int = 3, refine: bool = True,
                seed: int = 0, **solve_kw) -> tuple[Prediction, dict]:
    """mode: 'llm' | 'random' | 'exhaustive' | 'none'. Returns final Prediction and a trace."""
    base = solve(task, **solve_kw)
    cands = [([], base)]
    trace = {"task_id": task.task_id, "mode": mode, "baseline": _summ(base), "rounds": []}
    desc, idmap = describe(task.symbols)
    rng = random.Random(seed)

    def execute(pipelines, label):
        res = []
        for pl in pipelines[:k if mode != "exhaustive" else len(pipelines)]:
            try:
                p = run_pipeline(task, pl, idmap, solve, **solve_kw)
                cands.append((pl, p)); res.append({"pipeline": pl, "result": _summ(p)})
            except Exception as ex:  # noqa: BLE001 - invalid hypothesis is recorded, not fatal
                res.append({"pipeline": pl, "error": str(ex)[:200]})
        trace["rounds"].append({"label": label, "results": res})
        return res

    if mode == "exhaustive":
        execute(DEFAULT_PIPELINES, "exhaustive")
    elif mode == "random":
        execute([rng.choice(DEFAULT_PIPELINES) for _ in range(k * (2 if refine else 1))], "random")
    elif mode == "llm":
        ops_doc = "\n".join(f"- {k_}: {v}" for k_, v in OP_DOCS.items())
        prompt = (f"CIPHERTEXT STATISTICS:\n{desc}\n\nBASELINE SOLVER ON RAW STREAM: {json.dumps(_summ(base))}\n\n"
                  f"AVAILABLE OPS (compose into pipelines, applied before the solver):\n{ops_doc}\n\n"
                  f"Propose up to {k} pipelines. JSON: {{\"assessment\": str, \"is_language_guess\": float, "
                  f"\"pipelines\": [{{\"hypothesis\": str, \"prediction\": str, \"steps\": [{{\"op\": str, \"args\": {{}}}}]}}]}}. "
                  f"If the baseline already looks solved (high confidence, readable), or the text looks like a decoy, "
                  f"you may return an empty pipelines list.")
        out = extract_json(llm(SYSTEM, prompt, role="propose")) or {}
        trace["llm_round1"] = out
        res = execute([p.get("steps", []) for p in out.get("pipelines", []) if p.get("steps")], "llm_round1")
        best = select(cands)[1]
        if refine and res and (best.abstain or best.confidence < 0.8):
            prompt2 = (prompt + f"\n\nRESULTS OF YOUR PIPELINES: {json.dumps(res)}\n\nRevise: propose up to {k} new "
                       f"pipelines that test what these results suggest, or an empty list to stop. Same JSON format.")
            out2 = extract_json(llm(SYSTEM, prompt2, role="refine")) or {}
            trace["llm_round2"] = out2
            execute([p.get("steps", []) for p in out2.get("pipelines", []) if p.get("steps")], "llm_round2")
    pl, final = select(cands)
    trace["selected_pipeline"] = pl
    trace["final"] = _summ(final)
    final.log = (final.log or []) + [{"agent_mode": mode, "selected_pipeline": pl, "n_candidates": len(cands)}]
    return final, trace
