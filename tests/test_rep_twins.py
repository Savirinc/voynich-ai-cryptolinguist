import random

from vcl.synthetic import edge_twins as X
from vcl.synthetic import naibbe_exact as NX
from vcl.synthetic import rep_twins as R

PLAIN = "in principio erat verbum et verbum erat apud deum et deus erat verbum " * 20
LINES = [["qokeedy", "chedy", "daiin", "shol"], ["okaiin", "chokain", "chey", "qodam"]] * 30


def test_off_equals_plain_naibbe_and_memory_decodes():
    C = X.coupling_matrix(LINES, min_count=5)
    k = NX.key({}, 0, PLAIN)
    assert R.naibbe_tokens(PLAIN, C, 0.0, 1, 4) == NX.encode_tokens(PLAIN, k, 4)
    w, g = R.naibbe_tokens(PLAIN, C, 2.0, 4, 4, p_reuse=0.8, mem_window=40)
    dec, tgt = NX.decode(w, k), "".join(g)
    assert sum(a == b for a, b in zip(dec, tgt)) / len(tgt) > 0.97
    assert len(set(w)) < len(set(R.naibbe_tokens(PLAIN, C, 2.0, 4, 4)[0]))


def test_nulls_are_not_cipher_words_and_drop_out():
    nulls = R.null_pool(["s", "y", "l", "o", "daiin", "s", "r"])
    assert "y" not in nulls and set(nulls) == {"s", "l", "o", "r"}
    k = NX.key({}, 0, PLAIN)
    assert all(NX.decode([n], k) == "?" for n in nulls)
    words = ["qokeedy", "chedy", "daiin"] * 50
    out = R.add_nulls_ditto(words, nulls, 0.2, 0.1, random.Random(0))
    assert [w for w in out if w not in nulls] != words and len(out) > len(words)
