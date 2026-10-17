"""Round-trip, determinism and decoy-class tests for the Voynich twin generators (E011)."""
import random

import pytest

from vcl.synthetic import twins as T

# small synthetic EVA word list standing in for Voynich DEV words (tests must not need the transcription)
EVA = ("daiin ol chedy shedy aiin chol or chey qokeey qokeedy ar s qokedy qokain qokaiin y dar shey dy okaiin al "
       "dal qokal chor dain cheey shol cheol okeey l otedy qotchy lchedy kchdy pchedy ckhy cthol sheckhy oteedy "
       "qokchedy okal otal chodaiin shodaiin cphy dchedy ykeedy ytedy qopchedy").split() * 3
POOLS = T.chunk_pools(EVA)
LATIN = ("in principio creavit deus caelum et terram terra autem erat inanis et vacua et tenebrae super faciem "
         "abyssi et spiritus dei ferebatur super aquas dixitque deus fiat lux et facta est lux et vidit deus lucem "
         "quod esset bona et divisit lucem ac tenebras appellavitque lucem diem et tenebras noctem factumque est "
         "vespere et mane dies unus dixit quoque deus fiat firmamentum in medio aquarum et dividat aquas ab aquis")
ITALIAN = ("nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura che la diritta via era smarrita "
           "ahi quanto a dir qual era è cosa dura esta selva selvaggia e aspra e forte che nel pensier rinova la paura")


@pytest.mark.parametrize("plain", [LATIN, ITALIAN])
@pytest.mark.parametrize("seed", [0, 7, 123])
def test_naibbe_roundtrip(plain, seed):
    for params in ({}, {"n_tables": 1, "p_bigram": 0.8}, {"share": 0.8, "economy": 4}):
        key = T.naibbe_key(params, seed, plain, POOLS)
        words = T.naibbe_encode(plain, key, seed + 1)
        assert T.naibbe_decode(words, key) == plain.replace(" ", "")
        assert all(set(w) <= set("abcdefghijklmnopqrstuvwxyz") for w in words)


def test_naibbe_tables_ratio_and_structure():
    key = T.naibbe_key({}, 1, LATIN, POOLS)
    assert len(key["P"]) == 6 and key["table_weights"] == [5, 2, 2, 2, 1, 1]
    pcodes = [c for tab in key["P"] for c in tab.values()]
    for a in pcodes:            # prefix-free bigram-prefix set
        assert not any(b != a and b.startswith(a) for b in pcodes)


@pytest.mark.parametrize("plain", [LATIN, ITALIAN])
@pytest.mark.parametrize("seed", [0, 5])
def test_abbreviation_roundtrip(plain, seed):
    for params in ({}, {"p_suspend": 0.5, "p_contract": 0.5, "n_word_signs": 0}, {"n_hom": 3, "positional": 0}):
        key = T.abbreviation_key(params, seed, plain, POOLS)
        words = T.abbreviation_encode(plain, key, seed + 3)
        target = ["".join(u) for u in T.abbreviate(plain, key, seed + 3)]
        assert T.abbreviation_decode(words, key).split(" ") == target
    # with no lossy steps the expansion is exact
    key = T.abbreviation_key({"p_suspend": 0.0, "p_contract": 0.0}, seed, plain, POOLS)
    words = T.abbreviation_encode(plain, key, 9)
    assert T.abbreviation_decode(words, key, expand=True) == plain


def test_abbreviation_is_shorter():
    key = T.abbreviation_key({"p_suspend": 0.4, "p_contract": 0.4}, 0, LATIN, POOLS)
    units = T.abbreviate(LATIN, key, 1)
    assert sum(map(len, units)) < len(LATIN.replace(" ", ""))


def test_syllabify():
    assert T.syllabify("principio", max_onset=1) == ["prin", "ci", "pio"]
    assert T.syllabify("principio", max_onset=2) == ["pri", "nci", "pio"]
    assert "".join(T.syllabify("tenebrae")) == "tenebrae"


@pytest.mark.parametrize("plain", [LATIN, ITALIAN])
@pytest.mark.parametrize("upw", [0, 1, 2, 4])
def test_syllabary_roundtrip(plain, upw):
    for params in ({"units_per_word": upw}, {"units_per_word": upw, "n_syll": 10, "n_hom": 2, "positional": 0}):
        key = T.syllabary_key(params, 3, plain, POOLS)
        words = T.syllabary_encode(plain, key, 4)
        dec = T.syllabary_decode(words, key)
        assert dec == (plain if upw == 0 else plain.replace(" ", ""))


@pytest.mark.parametrize("fam", list(T.FAMILIES))
def test_generate_deterministic(fam):
    rng = random.Random(0)
    p = T.random_params(fam, rng)
    a = T.generate(fam, p, 42, POOLS, 300, plain=LATIN * 4)
    b = T.generate(fam, p, 42, POOLS, 300, plain=LATIN * 4)
    assert a["lines"] == b["lines"] and len([w for l in a["lines"] for w in l]) > 0
    assert a["is_language"] == T.FAMILIES[fam].is_language
    c = T.generate(fam, p, 43, POOLS, 300, plain=LATIN * 4)
    assert c["lines"] != a["lines"]


def test_decoys_are_marked_meaningless():
    assert not T.FAMILIES["rugg_grille"].is_language and not T.FAMILIES["self_citation"].is_language
    for fam in ("rugg_grille", "self_citation"):
        g = T.generate(fam, {}, 1, POOLS, 200)
        assert g["plaintext"] is None and not g["is_language"]


@pytest.mark.parametrize("fam", list(T.FAMILIES))
def test_random_params_within_bounds(fam):
    rng = random.Random(1)
    for _ in range(20):
        p = T.perturb_params(fam, T.random_params(fam, rng), rng)
        for k, (lo, hi) in T.FAMILIES[fam].bounds.items():
            assert lo <= p[k] <= hi
