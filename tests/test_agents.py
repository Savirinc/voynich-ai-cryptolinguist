import json
import random

from vcl.agents.cryptolinguist import agent_solve, describe
from vcl.agents.ops import apply_pipeline
from vcl.agents.llm import extract_json
from vcl.synthetic.encoders import ENCODERS
from vcl.synthetic.schema import PublicTask, Prediction, BOUNDARY

PLAIN = "the scribe wrote every word backwards so that the casual reader would see only nonsense " * 6


def _oracle_solver(key):
    """Test double: decodes with a known mono key and is confident only if the result looks like PLAIN."""
    inv = {g: c for c, g in key.items()}

    def solve(task, **_):
        if any(s not in inv and s != BOUNDARY for s in task.symbols):
            return Prediction(task.task_id, 0.5)
        txt = "".join(" " if s == BOUNDARY else inv[s] for s in task.symbols)
        ok = "the scribe" in txt
        return Prediction(task.task_id, 0.9, family="mono", plaintext=txt if ok else None,
                          confidence=0.95 if ok else 0.1, abstain=not ok)
    return solve


def test_reverse_words_pipeline_recovers_original_order():
    syms, key, _, _ = ENCODERS["reversed_words"](PLAIN.strip(), random.Random(0))
    out, post = apply_pipeline(syms, [{"op": "reverse_words"}])
    inv = {g: c for c, g in key.items()}
    assert post("".join(" " if s == BOUNDARY else inv[s] for s in out)) == PLAIN.strip()


def test_exhaustive_mode_finds_reversal_and_baseline_abstains():
    syms, key, _, _ = ENCODERS["reversed_words"](PLAIN.strip(), random.Random(1))
    task = PublicTask("t", syms, "test_enc")
    pred, trace = agent_solve(task, _oracle_solver(key), mode="exhaustive")
    assert trace["baseline"]["abstain"] and not pred.abstain and pred.plaintext == PLAIN.strip()


def test_llm_mode_with_scripted_llm_and_bad_ops_are_recorded():
    syms, key, _, _ = ENCODERS["reversed_words"](PLAIN.strip(), random.Random(2))
    reply = json.dumps({"assessment": "x", "pipelines": [
        {"hypothesis": "bogus", "prediction": "-", "steps": [{"op": "not_an_op"}]},
        {"hypothesis": "mirror", "prediction": "solver confident", "steps": [{"op": "reverse_words"}]}]})
    pred, trace = agent_solve(PublicTask("t", syms, "test_enc"), _oracle_solver(key), llm=lambda *a, **k: reply)
    assert pred.plaintext == PLAIN.strip()
    assert any("error" in r for r in trace["rounds"][0]["results"])


def test_describe_hides_raw_glyphs():
    syms, _, _, _ = ENCODERS["mono"](PLAIN, random.Random(3))
    text, idmap = describe(syms)
    assert all(g not in text for g in set(syms) - {BOUNDARY})


def test_extract_json_takes_last_object():
    assert extract_json('blah {"a": 1} then {"b": {"c": 2}}') == {"b": {"c": 2}}


def test_drop_symbols_accepts_int_and_g_ids():
    from vcl.agents.cryptolinguist import run_pipeline
    syms, key, _, _ = ENCODERS["mono"](PLAIN.strip(), random.Random(5))
    _, idmap = describe(syms)
    seen = {}

    def spy(task, **_):
        seen["n"] = len(task.symbols); return Prediction(task.task_id, 0.5)
    run_pipeline(PublicTask("t", syms, "x"), [{"op": "drop_symbols", "args": {"drop": [0, "g1"]}}], idmap, spy)
    top2 = {idmap["g0"], idmap["g1"]}
    assert seen["n"] == sum(s not in top2 for s in syms)
