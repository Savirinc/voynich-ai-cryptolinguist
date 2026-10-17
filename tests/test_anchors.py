"""Fast tests for E010 (anchor dataset + power-analysis machinery) and E010B (pre-registered zodiac tests)."""
import hashlib
import importlib.util
import json
import random
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def anchors():
    from vcl.anchors import load_anchors
    return load_anchors()


def test_anchor_rows_schema(anchors):
    req = {"id", "anchor_type", "tier", "folio", "leaf", "locked", "usable", "word_level", "sources",
           "proposed_meaning", "voynich_eva", "contested", "verified"}
    assert len({r["id"] for r in anchors}) == len(anchors)
    for r in anchors:
        assert req <= set(r), r["id"]
        assert r["tier"] in "ABCD"
        assert r["sources"], r["id"]
        if r["word_level"]:
            assert r["usable"] and r["voynich_eva"]


def test_locked_leaves_excluded(anchors):
    locked = set(json.loads((ROOT / "data/derived/splits.json").read_text())["locked_test_leaves"])
    for r in anchors:
        assert r["locked"] == (r["leaf"] in locked)
        if r["locked"]:
            assert not r["usable"] and not r["word_level"]
    ids = {r["id"] for r in anchors if r["locked"]}
    assert {"plant_id_f9v", "plant_id_f35v", "plant_id_f1v"} <= ids


def test_zodiac_rows(anchors):
    z = [r for r in anchors if r["anchor_type"] == "zodiac_month"]
    assert len(z) == 12 and all(r["tier"] == "A" and not r["locked"] for r in z)
    assert sum(r["n_candidate_loci"] for r in z) == 299  # voynich.nu labels page: 299 zodiac labels
    assert [r["meaning_text_on_page"] for r in z][:4] == ["mars", "aberil", "aberil", "may"]
    d = [r for r in anchors if r["tier"] == "D"]
    assert len(d) == 1 and "L0" in d[0]["note"]


def test_zodiac_structure_counts():
    from vcl.anchors import zodiac_pages
    n = {p["folio"]: p["n_labels"] for p in zodiac_pages()}
    assert n["f70v1"] == n["f71r"] == n["f71v"] == n["f72r1"] == 15
    assert n["f72r2"] == 29 and n["f70v2"] == 30


def test_prereg_hash_frozen():
    m = _load("e010b", "experiments/e010b_zodiac_months.py")
    assert hashlib.sha256((ROOT / "reports/E010B_PREREG.md").read_bytes()).hexdigest() == m.PREREG_SHA256
    assert len(m.P_PAIRS) == 8


def test_e010b_similarity_and_holm():
    m = _load("e010b", "experiments/e010b_zodiac_months.py")
    e = _load("e010", "experiments/e010_anchor_power.py")
    X, Y = ["kitten", "abc", "", "otaly"], ["sitting", "abd", "x", "okaly", ""]
    L = m.lev_sim(X, Y)
    for i, a in enumerate(X):
        for j, b in enumerate(Y):
            mx = max(len(a), len(b))
            assert L[i, j] == pytest.approx(1 - e.lev(a, b) / mx if mx else 1.0)
    A = m.affix_sim(["otaly", "abc"], ["okaly", "otal", "xbc", "otaly"])
    assert A.tolist() == [[3, 4, 0, 5], [0, 0, 2, 0]]
    h = m.holm({"a": 0.001, "b": 0.006, "c": 0.5}, alpha=0.01)
    assert h["a"]["reject"] and not h["b"]["reject"] and not h["c"]["reject"]


def test_e010_true_key_scores_one_and_wrong_lower():
    e = _load("e010", "experiments/e010_anchor_power.py")
    for mech in e.MECHS:
        rng = random.Random(3)
        A = e.make_anchors(rng, "fr", mech, 6, 1.0)
        S = e.Scorer(A, mech, "fr")
        K = e.true_key(S, A)
        assert S.score(K) == pytest.approx(1.0)
        assert np.mean([S.score(S.random_key(rng)) for _ in range(20)]) < 0.6
        A0 = e.make_anchors(rng, "fr", mech, 6, 0.0)
        S0 = e.Scorer(A0, mech, "fr")
        assert S0.score(e.true_key(S0, A0)) < 0.9
