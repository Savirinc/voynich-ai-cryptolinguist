"""Fast tests for E010D (pre-registered same-month sharing tests on the zodiac pages)."""
import hashlib
import importlib.util
import os
import random
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def E():
    spec = importlib.util.spec_from_file_location("e010d", ROOT / "experiments/e010d_zodiac_shared.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def test_prereg_locked(E):
    p = ROOT / "reports/E010D_PREREG.md"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == E.PREREG_SHA256
    assert not os.access(p, os.W_OK) or os.geteuid() == 0


def test_pair_sets_and_config_counts(E):
    assert len(E.H_RUN) == 26 and E.H_RUN[-12:] == E.ZODIAC_FOLIOS
    assert len(E.ZPAIRS) == 66 and len(E.APAIRS) == 25
    assert len(E.CFG_ALL) == 1485 and len(E.CFG_ADJ) == 276 and len(E.CFG_ZADJ) == 45
    assert all(m in E.APAIRS and m in E.ZPAIRS for m in E.SAME)
    assert [E.H_RUN[i] for m in E.SAME for i in m] == ["f70v1", "f71r", "f71v", "f72r1"]


def test_exact_p_extremes(E):
    x = np.zeros(len(E.APAIRS))
    for m in E.SAME:
        x[E.APAIRS.index(m)] = 5.0
    T, p = E.exact_p(x, E.APAIRS, E.CFG_ADJ)
    assert p == pytest.approx(1 / 276) and T == pytest.approx(5.0)
    T0, p0 = E.exact_p(np.zeros(len(E.APAIRS)), E.APAIRS, E.CFG_ADJ)
    assert p0 == 1.0 and T0 == 0.0
    rng = np.random.default_rng(0)
    ps = [E.exact_p(rng.random(len(E.ZPAIRS)), E.ZPAIRS, E.CFG_ALL)[1] for _ in range(300)]
    assert 0.3 < np.mean(ps) < 0.7  # exchangeable scores -> roughly uniform p


def test_holm(E):
    h = E.holm({"T1": 0.001, "T2": 0.004, "T3": 0.5})
    assert h["T1"]["reject"] and h["T2"]["reject"] and not h["T3"]["reject"]
    h = E.holm({"T1": 0.001, "T2": 0.006, "T3": 0.006})
    assert h["T1"]["reject"] and not h["T2"]["reject"] and not h["T3"]["reject"]


def test_features_and_counters(E):
    f = E.tok_feats("qokedy")
    assert "W:qokedy" in f and "N:^qo" in f and "N:edy$" in f and "N:qoked" in f
    wc, fdf, n = E.page_counters([["ab", "cd", None, "ef"], ["ab"]])
    assert n == 4 and wc["ab"] == 2 and fdf["B:ab cd"] == 1 and "B:cd ef" not in fdf


def test_corpus_scores_symmetric_and_rare_only(E):
    base = E.page_counters([["daiin"] * 50 + ["ol"] * 50])
    pages = [[["daiin", "zzqa", "ol"]], [["zzqa", "daiin"]], [["ol", "ykk"]]] + [[["daiin"]]] * 23
    C = E.Corpus(base, pages)
    assert C.s(0, 1) == pytest.approx(C.s(1, 0)) and C.s(0, 1) > 0      # zzqa: f_rest = 0
    assert C.s(0, 2) == 0                                              # 'ol' is common elsewhere
    assert 0 < C.c(0, 1) <= 1 and C.c(0, 1) == pytest.approx(C.c(1, 0))


def test_random_tables_are_permutations(E):
    from vcl.synthetic import naibbe_exact as NX
    tab = NX.load_tables()
    k = E.random_tables(random.Random(1))
    for state in ("unigram", "prefix", "suffix"):
        for t in NX.TABLES:
            orig = sorted(g for (s, tt, _), g in tab.items() if s == state and tt == t)
            new = sorted(g for (s, tt, _), g in k["tables"].items() if s == state and tt == t)
            assert orig == new
    words, _ = NX.encode_tokens("aberil", k, 3)
    assert 3 <= len(words) <= 6 and all(words)


def test_synthetic_insertion_and_null(E):
    rng = random.Random(0)
    layout = [[("C", 20), ("L", 5)] for _ in E.H_RUN]
    filler = [f"w{i}" for i in range(2000)] * 3
    base = E.page_counters([filler])
    E._init(base, layout, filler)
    pages = E.synth_manuscript("a2", rng)
    assert [sum(len(l) for l in pg) for pg in pages] == [25] * 26
    a, b = (pages[i] for i in E.SAME[0])
    assert set(w for l in a for w in l) & set(w for l in b for w in l) - set(filler)  # shared novel codeword
    r = E.synth_replicate(("c", 0))
    assert set(r["p"]) == {"T1", "T2", "T3"} and all(0 < v <= 1 for v in r["p"].values())
