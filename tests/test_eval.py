from vcl.eval.score import score_task, summarise, char_acc
from vcl.eval.gates import gate5_semantic, gate3_nonsense, gate2_ood_transfer
from vcl.synthetic.schema import SecretAnswer, Prediction


def _sec(**kw):
    base = dict(task_id="t", is_language=True, plaintext="abc def", family="mono", key={}, language="en",
                language_family="germanic", source_id="1", source_url="u", seed=0, identifiability="unique",
                recoverable_plaintext="abc def")
    return SecretAnswer(**(base | kw))


def test_perfect_prediction_is_solved():
    r = score_task(_sec(), Prediction("t", 1.0, family="mono", language="en", plaintext="abc def", abstain=False))
    assert r["solved"] and r["char_acc"] == 1.0 and not r["false_discovery"]


def test_abstention_on_decoy_is_correct_and_answer_is_false_discovery():
    dec = _sec(is_language=False, plaintext=None, recoverable_plaintext=None, family="autocopy",
               identifiability="non_identifiable")
    assert not score_task(dec, Prediction("t", 0.1))["false_discovery"]
    assert score_task(dec, Prediction("t", 0.9, plaintext="xyz", abstain=False))["false_discovery"]


def test_space_insensitive_family():
    s = _sec(family="columnar", recoverable_plaintext="abcdef")
    assert score_task(s, Prediction("t", 1, plaintext="abc def", abstain=False))["char_acc"] == 1.0


def test_char_acc_bounds():
    assert char_acc("", "abc") == 0.0 and char_acc(None, "abc") == 0.0


def test_gate5_defaults_to_no_decipherment():
    g = gate5_semantic()
    assert g["status"] == "FAIL" and g["verdict"] == "no decipherment"


def test_gate3_and_gate2():
    assert gate3_nonsense({"null_false_discovery_rate": 0.2})["status"] == "FAIL"
    s = summarise([score_task(_sec(), Prediction("t", 1, plaintext="abc def", abstain=False))])
    assert gate2_ood_transfer(s, s, "test")["status"] in ("PASS", "FAIL")
