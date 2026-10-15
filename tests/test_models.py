import math

import numpy as np
import pytest
import torch

from vcl.models import content_free as cf
from vcl.models.ngram import KneserNey, Unigram, VarietyMixKN
from vcl.models.stream import (BOS_ID, LE_ID, V, WE_ID, Line, decode_events, dev_fold_split, dev_lines,
                               encode_line, encode_words, fold_map, inner_split, locked_set, locked_test_lines)
from vcl.models.transformer import CharTransformer, TConfig, TransformerLM

TOY = [Line("1", "f1r", i, "A" if i % 2 else "B", i == 0, ws) for i, ws in enumerate(
    [["qokeedy", "chedy", "daiin"], ["otedy", "qokaiin", "shol"], ["chol", "daiin", "qokedy", "dar"],
     ["okaly", "chey"], ["qotedy", "otam"]])]


def test_encoding_roundtrip_and_counts():
    ids = encode_words(["qo", "dy"])
    assert ids[-1] == LE_ID and ids.count(WE_ID) == 1 and len(ids) == 4 + 2
    assert decode_events(ids) == ["qo", "dy"]
    assert V == 28 and BOS_ID == V


@pytest.mark.parametrize("n", [1, 2, 3, 6])
def test_kn_sums_to_one(n):
    m = KneserNey(n).fit(TOY)
    for hist in ([BOS_ID] * 6, [BOS_ID] * 3 + encode_words(["qok"])[:3], encode_words(["zzzzzz"])[:6]):
        p = m.dist(list(hist))
        assert p.shape == (V,) and np.all(p > 0) and abs(p.sum() - 1) < 1e-9


def test_variety_mix_and_unigram_sum_to_one():
    m = VarietyMixKN(3).fit(TOY, val_lines=TOY[:2])
    assert abs(m.dist([BOS_ID] * 2, TOY[0]).sum() - 1) < 1e-9
    assert abs(Unigram().fit(TOY).dist([]).sum() - 1) < 1e-12


def test_bits_per_word_consistent():
    m = KneserNey(3).fit(TOY)
    ln = TOY[2]
    bits = m.line_bits(ln)
    assert len(bits) == ln.n_glyphs + ln.n_words
    r = m.score([ln])
    assert math.isclose(r["bits"], bits.sum())
    # bits/word = sum over each word's glyphs + its end symbol
    per_word, i = [], 0
    for w in ln.words:
        per_word.append(bits[i:i + len(w) + 1].sum()); i += len(w) + 1
    assert math.isclose(sum(per_word) / ln.n_words, r["bits_per_word"])
    assert math.isclose(r["bits_per_glyph"] * r["events"], r["bits_per_word"] * r["words"])


def test_transformer_forward_shape_and_scoring():
    for cond in (False, True):
        c = TConfig(d_model=32, n_layers=1, n_heads=2, d_ff=64, cond=cond, max_len=64)
        net = CharTransformer(c)
        x = torch.randint(0, V, (3, 17))
        out = net(x, torch.tensor([0, 1, 2]), torch.tensor([0, 1, 0]))
        assert out.shape == (3, 17, V)
    m = TransformerLM(TConfig(d_model=32, n_layers=1, n_heads=2, d_ff=64, max_len=64), device="cpu")
    r = m.score(TOY)
    assert r["events"] == sum(l.n_glyphs + l.n_words for l in TOY)
    assert math.isclose(r["bits"], sum(m.line_bits(l).sum() for l in TOY), rel_tol=1e-4)
    assert len(m.sample_lines([("A", True), ("B", False)], seed=0)) == 2


def test_no_locked_leaf_in_dev_streams():
    locked = locked_set()
    assert len(locked) == 15
    assert not ({l.leaf for l in dev_lines()} & locked)
    assert not (set(fold_map()) & locked)
    for f in range(5):
        tr, te = dev_fold_split(f)
        a, b = inner_split(tr)
        assert not ({l.leaf for l in tr + te + a + b} & locked)
        assert not ({l.leaf for l in tr} & {l.leaf for l in te})
        assert not ({l.leaf for l in a} & {l.leaf for l in b})


def test_locked_lines_require_explicit_confirmation():
    with pytest.raises(PermissionError):
        locked_test_lines()


def test_ppc_statistics_on_toy_samples():
    st = cf.sample_stats([l.words for l in TOY], [l.currier for l in TOY])
    assert st["n_words"] == sum(l.n_words for l in TOY)
    assert 0 <= st["label_share_all_words"] <= 1
    assert st["q_to_o"]["q"] == 4 and st["q_to_o"]["qo"] == 4


def test_conditioned_kn_sums_to_one_and_scores_every_event():
    from vcl.models.ngram import COND_BASE, ConditionedKN
    m = ConditionedKN(3).fit(TOY)
    for ctx in ((BOS_ID, BOS_ID, COND_BASE + 53), (0, 1, COND_BASE + 2 * 24), (5, 5, COND_BASE + 1)):
        p = m._dist_ctx(ctx)
        assert np.all(p > 0) and abs(p.sum() - 1) < 1e-9
    assert len(m.line_bits(TOY[2])) == TOY[2].n_glyphs + TOY[2].n_words
