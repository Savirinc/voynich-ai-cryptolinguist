import random
from collections import Counter

from vcl.solvers.segment import ending_features, segment_types


def _marked(seed=0, n_stems=300, n_tok=6000):
    rng = random.Random(seed)
    EG, SG = "abcdef", "ghiklmnopqrsty"
    stems = list({"".join(rng.choice(SG) for _ in range(rng.randint(2, 5))) for _ in range(n_stems)})
    ends = [""] + list({"".join(rng.choice(EG) for _ in range(rng.randint(1, 3))) for _ in range(12)})
    para = {s: rng.sample(ends, 4) for s in stems}
    toks, truth = [], {}
    for _ in range(n_tok):
        s = rng.choice(stems); e = rng.choice(para[s]); w = s + e
        toks.append(w); truth[w] = len(s)
    return toks, truth


def test_marked_split_recovered():
    toks, truth = _marked()
    split = segment_types(Counter(toks), max_suf=4, sweeps=60)
    acc = sum(split[w] == truth[w] for w in toks) / len(toks)
    assert acc > 0.95
    f = ending_features(toks, split)
    assert f["DIST"] > 0.8 and f["NSUF95"] <= 15
