import random

import pytest

from vcl.synthetic.encoders import ENCODERS, decode, GLYPHS, comparable
from vcl.synthetic.decoys import DECOYS
from vcl.synthetic.schema import BOUNDARY

PLAIN = ("the patient researcher tests every hypothesis against evidence and keeps "
         "a ledger of every failure because a result that cannot fail is not a result ") * 4


@pytest.mark.parametrize("fam", sorted(ENCODERS))
def test_round_trip_or_documented(fam):
    rng = random.Random(7)
    syms, key, ident, recov = ENCODERS[fam](PLAIN, rng)
    assert syms and ident in ("unique", "equivalence_class", "non_identifiable")
    letters = {c for c in PLAIN if c != " "}
    assert not (set(syms) - {BOUNDARY}) & letters or fam == "syllabary", "cipher glyphs must not be plaintext letters"
    if key is not None:
        dec = decode(fam, syms, key)
        if dec is not None:
            assert comparable(fam, dec) == comparable(fam, recov)


def test_one_time_pad_marked_non_identifiable():
    _, key, ident, recov = ENCODERS["one_time_pad"](PLAIN, random.Random(1))
    assert key is None and ident == "non_identifiable" and recov is None


@pytest.mark.parametrize("name", sorted(DECOYS))
def test_decoys_generate(name):
    src = ENCODERS["mono"](PLAIN, random.Random(3))[0]
    syms, _ = DECOYS[name](500, random.Random(4), source_symbols=src)
    assert len(syms) >= 400 and set(syms) - {BOUNDARY} <= set(GLYPHS)
