"""Fast tests for the classical solvers (src/vcl/solvers). Plaintext comes from 'ref'-role books only."""
import json
import random
from pathlib import Path

import numpy as np
import pytest

from vcl.solvers import ops
from vcl.solvers.lm import ROLES, get_lm
from vcl.solvers.substitution import encode_symbols, solve_mono
from vcl.solvers.vigenere import estimate_periods
from vcl.synthetic.encoders import ENCODERS
from vcl.synthetic.schema import PublicTask

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/derived/solver_v1"


def _ref_plain(lang="en", n=1000, seed=0):
    from vcl.synthetic.corpora import load_books
    roles = json.loads(ROLES.read_text())
    book = next(b for b in load_books() if b["lang"] == lang and roles[b["id"]]["role"] == "ref")
    rng = random.Random(seed)
    start = rng.randrange(0, len(book["text"]) - n - 100)
    start = book["text"].find(" ", start) + 1
    chunk = book["text"][start:start + n]
    return chunk[: chunk.rfind(" ")]


def _acc(a, b):
    return np.mean([x == y for x, y in zip(a, b)]) if len(a) == len(b) else 0.0


def test_mono_recovers_english():
    plain = _ref_plain("en", 1000, seed=1)
    syms, key, _, _ = ENCODERS["mono"](plain, random.Random(5))
    seq, names = encode_symbols(syms)
    r = solve_mono(seq, len(names) - 1, get_lm("en"), iters=8000, restarts=3, seed=0)
    assert _acc(r.text, plain) >= 0.95


@pytest.mark.parametrize("period", [3, 5, 7])
def test_vigenere_period_detection(period):
    plain = _ref_plain("en", 2000, seed=period)
    syms, key, _, _ = ENCODERS["vigenere"](plain, random.Random(period), period=period)
    seq, _ = encode_symbols(syms)
    assert estimate_periods(seq)[0] == period


def test_ops_roundtrips():
    s = list("ab cd e")
    assert ops.reverse_words(ops.reverse_words(s)) == s
    assert ops.reverse_words(s) == list("ba dc e")
    assert ops.remove_boundaries(s) == list("abcde")
    assert ops.drop_symbols(s, {"a", "e"}) == list("b cd ")
    assert ops.merge_symbol_ngrams(list("abcd ef"), 2) == ["a+b", "c+d", " ", "e+f"]
    from vcl.solvers.columnar import untranspose_index, transpose_index
    order = [2, 0, 3, 1]
    x = np.arange(23)
    assert (x[transpose_index(23, order)][untranspose_index(23, order)] == x).all()
    # agrees with the benchmark encoder's columnar transposition
    plain = "thequickbrownfoxjumpsoverthelazydog"
    syms, key, _, letters = ENCODERS["columnar"](plain, random.Random(3), ncols=5)
    inv = {g: c for c, g in key["glyph"].items()}
    assert "".join(inv[s] for s in ops.untranspose(syms, 5, key["order"])) == letters


needs_artifacts = pytest.mark.skipif(not (ART / "calibrator.pkl").exists() or not (ART / "family_classifier.pkl").exists(),
                                     reason="run experiments/e003_tune.py first")


@needs_artifacts
def test_abstains_on_one_time_pad():
    from vcl.solvers.api import solve, Budget
    from vcl.solvers.lm import Library
    plain = _ref_plain("en", 400, seed=7)
    syms, _, _, _ = ENCODERS["one_time_pad"](plain, random.Random(7))
    p = solve(PublicTask("otp", syms, "unit"), Library.train_families_only(), Budget(quick_langs=4, scale=0.3))
    assert p.abstain and p.plaintext is None


@needs_artifacts
def test_abstains_on_autocopy_and_short():
    from vcl.solvers.api import solve, Budget
    from vcl.solvers.lm import Library
    from vcl.synthetic.decoys import autocopy
    syms, _ = autocopy(500, random.Random(11))
    p = solve(PublicTask("auto", syms, "unit"), Library.train_families_only(), Budget(quick_langs=4, scale=0.3))
    assert p.abstain and p.plaintext is None
    short, _, _, _ = ENCODERS["mono"](_ref_plain("en", 24, seed=2), random.Random(2))
    p = solve(PublicTask("short", short, "unit"), Library.full())
    assert p.abstain and p.identifiability == "non_identifiable"
