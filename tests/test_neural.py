"""Fast tests for the neural decipherer (no model weights are loaded)."""
import random

import numpy as np
import pytest

from vcl.eval.score import char_acc as eval_char_acc
from vcl.neural import data
from vcl.neural.predict import Calibrator, TaskDecode, _aggregate, predicted_family, to_prediction
from vcl.neural.representation import (IN_BOUNDARY, N_FEAT, rank_encode, window_bounds, window_inputs)
from vcl.neural.reward import char_acc, is_degenerate, window_reward
from vcl.synthetic.encoders import ENCODERS, GLYPHS, decode
from vcl.synthetic.schema import BOUNDARY, PublicTask

PLAIN = ("the old scribe wrote every word with great care so that the reader would find the meaning hidden "
         "in plain sight and the cipher would keep its secret for many years ") * 4


def test_rank_encoding_is_relabelling_invariant():
    syms, _, _, _ = ENCODERS["homophonic"](PLAIN.strip(), random.Random(0))
    inv = sorted(set(syms) - {BOUNDARY})
    perm = dict(zip(inv, random.Random(1).sample([g for g in GLYPHS if g not in inv], len(inv))))
    renamed = [s if s == BOUNDARY else perm[s] for s in syms]
    a, b = rank_encode(syms), rank_encode(renamed)
    assert np.array_equal(a.ids, b.ids) and np.allclose(a.feats, b.feats)
    assert a.feats.shape == (len(syms), N_FEAT)
    assert (a.ids[[i for i, s in enumerate(syms) if s == BOUNDARY]] == IN_BOUNDARY).all()


def test_two_mono_keys_give_identical_encoding():
    s1, _, _, _ = ENCODERS["mono"](PLAIN.strip(), random.Random(2))
    s2, _, _, _ = ENCODERS["mono"](PLAIN.strip(), random.Random(3))
    assert s1 != s2
    assert np.array_equal(rank_encode(s1).ids, rank_encode(s2).ids)


def test_windows_cover_and_pad():
    for n in [1, 255, 256, 257, 1000, 3737]:
        wb = window_bounds(n)
        assert wb[0][0] == 0 and wb[-1][1] == n and all(b - a <= 256 for a, b in wb)
        assert all(x[1] == y[0] for x, y in zip(wb, wb[1:]))
    enc = rank_encode(list("abcab ca"))
    ids, ft = window_inputs(enc, 0, 8)
    assert ids.shape == (257,) and ft.shape == (257, N_FEAT)


@pytest.mark.parametrize("fam", ["mono", "homophonic", "vigenere", "nulls"])
def test_window_targets_concatenate_to_plaintext(fam):
    plain = PLAIN.strip()
    syms, key, _, recov = ENCODERS[fam](plain, random.Random(4))
    task = {"family": fam, "symbols": syms, "key": key, "plain": plain, "recov": recov}
    txt = "".join(data.window_target(task, a, b) for a, b in window_bounds(len(syms)))
    assert txt == recov == decode(fam, syms, key)


@pytest.mark.parametrize("fam", ["mono", "homophonic", "vigenere", "nulls", "columnar"])
def test_raw_targets_are_one_token_per_symbol(fam):
    plain = PLAIN.strip()
    syms, key, _, recov = ENCODERS[fam](plain, random.Random(8))
    task = {"family": fam, "symbols": syms, "key": key, "plain": plain, "recov": recov}
    for a, b in window_bounds(len(syms)):
        raw = data.window_target_raw(task, a, b)
        assert len(raw) == b - a
        assert all((c == " ") == (s == BOUNDARY) for c, s in zip(raw, syms[a:b]))


def test_noise_target_is_abstain_and_test_role_rejected():
    assert data.window_target({"family": "noise", "symbols": [], "key": None}, 0, 0) is None
    with pytest.raises(AssertionError):
        data.books_for("test")


def test_reward_char_acc_matches_evaluator():
    rng = random.Random(5)
    for _ in range(50):
        a = "".join(rng.choice("abc d") for _ in range(rng.randint(0, 30)))
        b = "".join(rng.choice("abc d") for _ in range(rng.randint(1, 30)))
        assert abs(char_acc(a, b) - eval_char_acc(a, b)) < 1e-12


def test_reward_sanity():
    gold = "the cat sat on the mat"
    assert window_reward(gold, "mono", gold, "mono") > window_reward("xxq zzv", "mono", gold, "mono")
    assert window_reward(None, "noise", None, "noise") > window_reward("abc", "mono", None, "noise")
    assert window_reward(None, "mono", gold, "mono") > window_reward("qqqqqqqqqqqqqqqqqqqqqq", "mono", gold, "mono")
    assert is_degenerate("aaaaaaaaaa") and not is_degenerate(gold)


class _FakeLR:
    def __init__(self, p):
        self.p = p

    def predict_proba(self, x):
        return np.array([[1 - self.p, self.p]])


def _td(task, texts, fam="mono", p_noise=0.0):
    td = TaskDecode(task.task_id, sum(s != BOUNDARY for s in task.symbols))
    for (a, b), t in zip(window_bounds(len(task.symbols)), texts):
        td.windows.append({"a": a, "b": b, "raw": t, "abstained": t is None, "mean_lp": -0.1,
                           "fam_probs": {fam: 1 - p_noise, "noise": p_noise}})
    _aggregate(td, task, rank_encode(list(task.symbols)))
    return td


def test_predict_wraps_abstention_and_answers():
    plain = PLAIN.strip()
    syms, key, _, _ = ENCODERS["mono"](plain, random.Random(6))
    task = PublicTask("t1", syms, "x")
    wins = [plain[a:b] for a, b in window_bounds(len(syms))]
    hi = Calibrator(_FakeLR(0.99), threshold=0.5, margin=0.1, agg_by_family={"mono": "vote"})
    lo = Calibrator(_FakeLR(0.10), threshold=0.5, margin=0.1, agg_by_family={"mono": "vote"})
    p = to_prediction(task, _td(task, wins), hi)
    assert not p.abstain and p.plaintext == plain and p.family == "mono"
    assert to_prediction(task, _td(task, wins), lo).abstain                     # below threshold
    assert to_prediction(task, _td(task, wins), hi, null_conf=0.95).abstain     # self-null too close
    noisy = to_prediction(task, _td(task, [None] * len(wins), fam="mono", p_noise=0.9), hi)
    assert noisy.abstain and noisy.plaintext is None and predicted_family(_td(task, [None] * len(wins), p_noise=0.9)) == "noise"
    short = PublicTask("t2", syms[:30], "x")
    assert to_prediction(short, TaskDecode("t2", 25), hi).abstain


def test_key_vote_repairs_inconsistent_window():
    plain = PLAIN.strip()
    syms, _, _, _ = ENCODERS["mono"](plain, random.Random(7))
    task = PublicTask("t3", syms, "x")
    wb = window_bounds(len(syms))
    wins = [plain[a:b] for a, b in wb]
    wins[0] = wins[0].replace("e", "o")         # one window gets a letter wrong; the other windows outvote it
    td = _td(task, wins)
    assert td.texts["vote"] == plain and td.texts["concat"] != plain and td.feats["aligned"] == 1.0
