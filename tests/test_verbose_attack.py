from vcl.solvers import verbose as V
from vcl.synthetic import naibbe_exact as NX

TEXT = NX.clean("in principio erat verbum et verbum erat apud deum et deus erat verbum " * 40)
LINES = [["qokeedy", "chedy", "daiin", "shol"], ["okaiin", "chokain", "chey", "qodam"]] * 30


def test_random_key_keeps_inventory_and_changes_letters():
    k, tab = V.random_key(1), NX.load_tables()
    for st in ("unigram", "prefix", "suffix"):
        assert {g for (s, _, _), g in k.items() if s == st} == {g for (s, _, _), g in tab.items() if s == st}
    assert sum(k[x] != tab[x] for x in tab) > 300


def test_labelled_encoding_parses_back_to_truth_with_the_key():
    from vcl.synthetic import edge_twins as X
    key = V.random_key(2)
    C = X.coupling_matrix(LINES, min_count=5)
    lines, labs = V.encode_labelled(TEXT, key, C, {"s": 1, "l": 1}, seed=3, p_merge=0.0, p_m=0.0)
    words, labels = [w for l in lines for w in l], [x for l in labs for x in l]
    assert "".join(labels) and len(words) == len(labels)
    inv = V.inventory()
    rev = {("U" if s == "unigram" else s[0].upper(), g): l for (s, _, l), g in key.items()}
    dec = []
    for w in words:
        p = V.parse_word(w, inv)
        dec.append("".join(rev.get(c, "?") for c in p) if p else "")
    assert V.char_accuracy(dec, labels) > 0.95


def test_lexical_coverage():
    from vcl.solvers.verbose import lexical_coverage
    voc = {"dominus", "spiritus"}
    assert lexical_coverage("xxdominusyyspiritus", voc, min_len=7) == 15 / 19
    assert lexical_coverage("abcdefgh", voc, min_len=7) == 0.0
