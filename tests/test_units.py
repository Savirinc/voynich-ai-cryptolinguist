"""Fast tests for vcl.corpus.units: collapse/slot rules, BPE determinism and round-trip of tokenisation."""
import random

from vcl.corpus import units as U

WORDS = ("qokeedy chedy daiin qokaiin shedy otedy chol chor okaiin qokedy ol dar cheol shol qokeey okeey "
         "ckhy cthy cphy cfhy saiin chckhy qotchy daiiin teeedy").split() * 3


def test_collapse_rules():
    assert U.collapsed_units("qokeedy") == ["q", "o", "k", "ee", "d", "y"]
    assert U.collapsed_units("chckhy") == ["ch", "ckh", "y"]
    assert U.collapsed_units("daiin") == ["d", "a", "iin"]
    assert U.collapsed_units("dain") == ["d", "a", "in"]
    assert U.collapsed_units("daiiin") == ["d", "a", "i", "iin"]        # greedy longest match from the left
    assert U.collapsed_units("teeedy") == ["t", "ee", "e", "d", "y"]
    assert U.collapsed_units("cthshcphcfh") == ["cth", "sh", "cph", "cfh"]
    assert set(U.COMPOSITES) == {"cth", "ckh", "cph", "cfh", "ch", "sh", "iin", "in", "ee"}


def test_slot_alphabet():
    assert len(U.SLOT_ALPHABET) == 26
    assert U.slot_units("daiiin") == ["d", "a", "iii", "n"]
    assert U.slot_units("teeedy") == ["t", "eee", "d", "y"]
    assert U.slot_units("qokeeeedy") == ["q", "o", "k", "eee", "e", "d", "y"]
    assert U.slot_units("cthgx") == ["cth", "g", "x"]                    # out-of-alphabet glyphs kept singly


def test_fixed_round_trip():
    for w in WORDS + ["", "x", "chhh", "cccc"]:
        for f in U.FIXED.values():
            assert "".join(f(w)) == w


def test_bpe_determinism_and_round_trip():
    a = U.learn_bpe(WORDS, 30)
    b = U.learn_bpe(list(reversed(WORDS)), 30)
    assert a.merges == b.merges and a.alphabet == b.alphabet         # order of input does not matter
    seen = {}
    U.learn_bpe(WORDS, 30, checkpoints=[30], on_checkpoint=lambda k, m: seen.update(m))
    for w in set(WORDS):
        units = a.apply(w)
        assert "".join(units) == w
        assert units == seen[w]                                      # apply() reproduces the training segmentation
    assert "".join(a.apply("qokchedaiin")) == "qokchedaiin"             # unseen word round-trips
    assert len(a.for_vocab(len(a.alphabet) + 5).merges) == 5
    assert a.for_vocab(3).merges == []


def test_bpe_lines_and_crossing():
    lines = [["qokeedy", "chedy", "daiin"], ["ol", "chedy", "qokeedy"]] * 5
    bpe = U.learn_bpe_lines(lines, 40)
    segs = U.segment_lines_erased(bpe, lines)
    for s, l in zip(segs, lines):
        assert "".join(s) == "".join(l)
    cr = U.crossing_rates(segs, lines, [["", ".", ","], ["", ",", "."]] * 5)
    assert 0.0 <= cr["all_positions"] <= 1.0 and cr["n_all_separators"] == 20
    # no merges -> nothing crossed
    cr0 = U.crossing_rates(U.segment_lines_erased(bpe.truncated(0), lines), lines)
    assert cr0["all_positions"] == 0.0


def test_bpe_random_words_round_trip():
    rng = random.Random(0)
    ws = ["".join(rng.choice("okeychdai") for _ in range(rng.randint(1, 8))) for _ in range(300)]
    b = U.learn_bpe(ws, 60)
    assert all("".join(b.apply(w)) == w for w in ws)
