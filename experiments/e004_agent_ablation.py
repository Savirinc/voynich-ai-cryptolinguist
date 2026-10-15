"""E004: does the pretrained-LLM planner add anything over the solver and over blind search?

Conditions (identical solver, library and budget per candidate):
  none        - calibrated solver on the raw stream (System C absent)
  random      - 2k uniformly sampled default pipelines (same max pipelines as llm)
  llm         - Claude proposes <= k pipelines, one refinement round (<= 2k pipelines)
  exhaustive  - all 7 default pipelines (upper bound of the op library without planning)
Fixed stratified subset of public tasks (seeded); predictions are produced from PublicTask only;
secrets are loaded only afterwards for scoring. This is a search-policy benchmark, NOT RL training.

Run: .venv/bin/python experiments/e004_agent_ablation.py [--model sonnet] [--workers 5]
"""
import argparse, json, random, sys, time, zlib
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.synthetic.schema import PublicTask, SecretAnswer, load_jsonl  # noqa: E402

BENCH = ROOT / "data/derived/benchmark_v1"
PLAN = {"test_in": 3, "test_enc": 4, "test_both": 4, "test_null": 3}   # tasks per family/kind
MODES = ["none", "random", "llm", "exhaustive"]


def pick_subset(seed=4004):
    """Stratify by family using the secret family label ONLY to choose which public tasks to include
    (selection, not solving); the agent sees nothing but the PublicTask."""
    rng = random.Random(seed)
    chosen = []
    for split, per in PLAN.items():
        pubs = {p.task_id: p for p in load_jsonl(BENCH / "public" / f"{split}.jsonl", PublicTask)}
        by = defaultdict(list)
        for s in load_jsonl(BENCH / "secret" / f"{split}.jsonl", SecretAnswer):
            by[s.family].append(s.task_id)
        for fam in sorted(by):
            ids = sorted(by[fam]); rng.shuffle(ids)
            chosen += [pubs[i] for i in ids[:per]]
    return chosen


_STATE = {}


def _init(model, calls_per_worker, run):
    from vcl.solvers.api import solve
    from vcl.solvers.lm import Library
    from vcl.agents.llm import ClaudeCLI
    import os
    _STATE["solve"] = solve
    _STATE["lib"] = Library.full()
    _STATE["llm"] = ClaudeCLI(model=model, run_name=f"{run}_w{os.getpid()}", max_calls=calls_per_worker)


def _work(args):
    task, mode = args
    from vcl.agents.cryptolinguist import agent_solve
    from vcl.agents.llm import BudgetExceeded
    t0 = time.time()
    try:
        pred, trace = agent_solve(task, _STATE["solve"], llm=_STATE["llm"], mode=mode, k=3,
                                  seed=zlib.crc32(task.task_id.encode()), library=_STATE["lib"])
    except BudgetExceeded as ex:
        pred, trace = agent_solve(task, _STATE["solve"], mode="none", library=_STATE["lib"])
        trace["budget_exceeded"] = str(ex)
    trace["secs"] = round(time.time() - t0, 1)
    trace["llm_calls_so_far"] = _STATE["llm"].calls
    trace["llm_cost_so_far"] = round(_STATE["llm"].cost, 4)
    return mode, asdict(pred), trace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--max-llm-calls", type=int, default=200)
    ap.add_argument("--modes", default=",".join(MODES))
    ap.add_argument("--limit", type=int, default=0, help="debug: only first N tasks")
    a = ap.parse_args()
    run = time.strftime("e004_%Y%m%d_%H%M%S")
    tasks = pick_subset()
    if a.limit:
        tasks = tasks[:a.limit]
    modes = a.modes.split(",")
    jobs = [(t, m) for t in tasks for m in modes]
    out_rows = ROOT / f"experiments/results/{run}_traces.jsonl"
    preds = defaultdict(dict)
    with ProcessPoolExecutor(a.workers, initializer=_init,
                             initargs=(a.model, a.max_llm_calls // a.workers, run)) as ex, open(out_rows, "w") as f:
        for mode, pred, trace in ex.map(_work, jobs):
            preds[mode][pred["task_id"]] = pred
            f.write(json.dumps(trace) + "\n"); f.flush()
            print(mode, pred["task_id"], "abstain" if pred["abstain"] else f"conf={pred['confidence']:.2f}",
                  trace["secs"], "s", flush=True)

    # ---- scoring (secrets loaded only now)
    from vcl.eval.score import score_task, summarise
    from vcl.synthetic.schema import Prediction
    secrets = {}
    for split in PLAN:
        for s in load_jsonl(BENCH / "secret" / f"{split}.jsonl", SecretAnswer):
            secrets[s.task_id] = s
    res = {"run": run, "model": a.model, "n_tasks": len(tasks), "command": " ".join(sys.argv), "by_mode": {}}
    for mode in modes:
        res["by_mode"][mode] = {}
        for split in PLAN:
            rows = [score_task(secrets[t.task_id], Prediction(**preds[mode][t.task_id]))
                    for t in tasks if t.split == split and t.task_id in preds[mode]]
            res["by_mode"][mode][split] = summarise(rows)
    (ROOT / f"experiments/results/{run}.json").write_text(json.dumps(res, indent=1))
    for mode in modes:
        print(mode, {sp: (round(v.get("solved_rate", 0), 3), v.get("null_false_discovery_rate"))
                     for sp, v in res["by_mode"][mode].items()})


if __name__ == "__main__":
    main()
