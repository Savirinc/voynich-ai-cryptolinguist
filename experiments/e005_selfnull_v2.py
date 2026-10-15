"""E005: solver v2 = v1 + self-null abstention (src/vcl/solvers/selfnull.py). A NEW VERSION created after E003's
Gate 3 failure was seen; v1 results stay reported as they are (experiments/FAILURES.md).

Stage 1 (tune only): generate real tune-family ciphers from tune-role books (e003_tune.gen_task), solve with v1,
  keep the correct answers, set margin = 5th percentile of their self-null gaps (95% retention). No decoys used.
Stage 2 (frozen): run v2 on test_null, test_in and test_lang (R1), score, apply Gates 1-3.

Run: .venv/bin/python experiments/e005_selfnull_v2.py [--n-cal 120] [--workers 10]
"""
import argparse, importlib.util, json, random, sys, time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.synthetic.schema import PublicTask, load_jsonl  # noqa: E402

spec = importlib.util.spec_from_file_location("e003_tune", ROOT / "experiments/e003_tune.py")
e003_tune = importlib.util.module_from_spec(spec); spec.loader.exec_module(e003_tune)
BENCH = ROOT / "data/derived/benchmark_v1"
OUT = ROOT / "experiments/results"
_S = {}


def _init():
    from vcl.solvers.api import solve
    from vcl.solvers.lm import Library
    _S["solve"], _S["lib"] = solve, Library.full()


def _cal(t):
    from vcl.solvers.selfnull import self_null_gap
    from vcl.eval.score import char_acc
    task = PublicTask(t["id"], t["symbols"], "selftune")
    p = _S["solve"](task, library=_S["lib"])
    if p.abstain or p.plaintext is None:
        return None
    ok = char_acc(p.plaintext.replace(" ", "") if t["family"] == "columnar" else p.plaintext,
                  t["plain"].replace(" ", "") if t["family"] == "columnar" else t["plain"]) >= 0.9
    gap, nulls = self_null_gap(task, p, _S["solve"], library=_S["lib"])
    return {"id": t["id"], "family": t["family"], "correct": ok, "gap": gap, "conf": p.confidence, "nulls": nulls}


def _run(args):
    from vcl.solvers.selfnull import solve_v2
    task, margin = args
    return asdict(solve_v2(task, _S["solve"], margin, library=_S["lib"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-cal", type=int, default=120)
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    t0 = time.time()
    rng = random.Random(5005)
    tasks = [e003_tune.gen_task(i, rng.randrange(2**31), [300, 1000, 3000]) for i in range(a.n_cal)]
    with ProcessPoolExecutor(a.workers, initializer=_init) as ex:
        cal = [r for r in ex.map(_cal, tasks) if r]
        gaps = sorted(r["gap"] for r in cal if r["correct"])
        margin = gaps[int(0.05 * len(gaps))] if gaps else 0.0
        print(f"calibration: {len(cal)} answered, {len(gaps)} correct, margin={margin:.4f}", flush=True)
        from vcl.eval.score import evaluate
        from vcl.eval.gates import gate1_positive_control, gate2_ood_transfer, gate3_nonsense
        from vcl.synthetic.schema import Prediction
        res = {"margin": margin, "calibration": {"answered": len(cal), "correct": len(gaps),
                                                 "wrong_answered_gaps": sorted(r["gap"] for r in cal if not r["correct"])},
               "splits": {}, "command": " ".join(sys.argv)}
        for split in ["test_null", "test_in", "test_lang"]:
            pubs = load_jsonl(BENCH / "public" / f"{split}.jsonl", PublicTask)
            preds = [Prediction(**d) for d in ex.map(_run, [(p, margin) for p in pubs])]
            rows, summ = evaluate(BENCH, split, preds)
            res["splits"][split] = summ
            print(split, {k: summ.get(k) for k in ["solved_rate", "mean_char_acc", "abstention_rate",
                                                    "null_false_discovery_rate"]}, flush=True)
    s = res["splits"]
    res["gates"] = {
        "gate1": gate1_positive_control(s["test_in"], ["mono", "homophonic", "vigenere", "columnar", "nulls"]),
        "gate2_test_lang_R1": gate2_ood_transfer(s["test_in"], s["test_lang"], "test_lang_R1"),
        "gate3": gate3_nonsense(s["test_null"]),
    }
    res["wall_s"] = round(time.time() - t0)
    (OUT / "e005.json").write_text(json.dumps(res, indent=1))
    from vcl.eval.ledger import append
    append([dict(experiment="E005", model="solver_v2_selfnull", checkpoint_sha256=f"margin={margin:.4f}",
                 split=split, metric=metric, value=summ[metric], command=res["command"],
                 notes="v2 created after seeing E003 Gate3 failure; margin set on tune ciphers only")
            for split, summ in s.items()
            for metric in ["solved_rate", "mean_char_acc", "abstention_rate", "null_false_discovery_rate"]
            if summ.get(metric) is not None])
    print(json.dumps(res["gates"], indent=1, default=str))


if __name__ == "__main__":
    main()
