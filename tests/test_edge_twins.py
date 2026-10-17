import random

from vcl.synthetic import edge_twins as X
from vcl.synthetic import naibbe_exact as NX

LINES = [["qokeedy", "chedy", "daiin", "shol"], ["okaiin", "chokain", "chey", "qodam"], ["ytedy", "qokal", "ol"]] * 30
PLAIN = "in principio erat verbum et verbum erat apud deum et deus erat verbum " * 20


def test_coupling_matrix_bounded():
    C = X.coupling_matrix(LINES, min_count=5)
    assert C and all(-3.0 <= v <= 3.0 for v in C.values())
    assert C[("y", "q")] > 0


def test_naibbe_sandhi_is_decodable_and_off_is_plain_naibbe():
    C = X.coupling_matrix(LINES, min_count=5)
    w, g = X.naibbe_sandhi_tokens(PLAIN, C, beta=3.0, k=6, seed=3)
    dec, tgt = NX.decode(w, NX.key({}, 0, PLAIN)), "".join(g)
    assert sum(a == b for a, b in zip(dec, tgt)) / len(tgt) > 0.97
    w0, g0 = X.naibbe_sandhi_tokens(PLAIN, C, beta=0.0, k=1, seed=3)
    assert (w0, g0) == NX.encode_tokens(PLAIN, NX.key({}, 0, PLAIN), 3)


def test_respace_preserves_glyph_stream_and_line_end():
    C = X.coupling_matrix(LINES, min_count=5)
    words = [w for l in LINES for w in l]
    r = X.respace(words, C, 0.3, 0.1, 2.0, random.Random(1))
    assert "".join(r) == "".join(words) and r != words
    out = X.line_end_m([["a", "daiin"], ["b", "ain"]], 1.0, random.Random(0))
    assert out == [["a", "dam"], ["b", "am"]]
