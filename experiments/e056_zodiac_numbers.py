"""E056: are the zodiac nymph labels NUMBERS (a count or degrees in ring order)? See reports/E056_PREREG.md.
Labels: DEV zodiac folios, mode 'label', one label = one transcription line (in ring order as transcribed); the
label's first word is used (all words reported too).
A  positional alignment: over all pairs of zodiac pages and positions k = 1..min(n_i, n_j), share of positions where
   the two pages' labels are identical. Null: labels shuffled within each page (10,000 permutations, seed 56056).
B  closed set: type/token ratio of the labels; number of label types needed to cover 80% of label tokens.
Positive control (same page sizes): labels replaced by 30 'number words' (30 distinct real Voynich label words drawn
   at random) by position index, then 12% of labels get one random glyph edit and 20% are replaced by a random
   non-number label word. Negative control: real labels shuffled across all zodiac pages.
Run: .venv/bin/python -I experiments/e056_zodiac_numbers.py
"""
from __future__ import annotations

import json, random, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED, NPERM = 56056, 10000
OUT = ROOT / "experiments/results/e056.json"
ZODIAC = ["f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v"]


def labels():
    _, toks = parse(); lk = set(locked_test_leaves(toks))
    pages = defaultdict(lambda: defaultdict(list))
    for t in toks:
        if t.folio in ZODIAC and t.mode == "label" and t.leaf not in lk and t.is_clean:
            pages[t.folio][t.line_no].append(t.eva)
    return {f: [ws for _, ws in sorted(pages[f].items())] for f in ZODIAC if f in pages}


def align(P):
    m = n = 0
    for a, b in combinations(P, 2):
        for k in range(min(len(a), len(b))):
            n += 1; m += a[k] == b[k]
    return m / n if n else 0.0


def perm_p(P, rng):
    obs = align(P); ge = 0
    for _ in range(NPERM):
        Q = [rng.sample(p, len(p)) for p in P]
        ge += align(Q) >= obs
    return obs, (ge + 1) / (NPERM + 1)


def closed(P):
    toks = [w for p in P for w in p]; c = Counter(toks)
    acc = k = 0
    for _, v in c.most_common():
        acc += v; k += 1
        if acc >= 0.8 * len(toks):
            break
    return {"tokens": len(toks), "types": len(c), "type_token": len(c) / len(toks), "types_for_80pct": k,
            "top": c.most_common(12)}


def edit(w, rng, glyphs):
    i = rng.randrange(len(w)); return w[:i] + rng.choice(glyphs) + w[i + 1:]


def main():
    rng = random.Random(SEED)
    L = labels()
    P = [[ws[0] for ws in L[f]] for f in L]
    sizes = [len(p) for p in P]
    vocab = sorted({w for p in P for w in p}); glyphs = sorted({c for w in vocab for c in w})
    obs, p = perm_p(P, rng); cl = closed(P)
    nums = rng.sample(vocab, 30)
    pos = []
    for s in sizes:
        page = []
        for k in range(s):
            w = nums[k % 30]
            r = rng.random()
            if r < 0.20:
                w = rng.choice(vocab)
            elif r < 0.32:
                w = edit(w, rng, glyphs)
            page.append(w)
        pos.append(page)
    pobs, pp = perm_p(pos, rng); pcl = closed(pos)
    flat = [w for p_ in P for w in p_]; rng.shuffle(flat); neg, i = [], 0
    for s in sizes:
        neg.append(flat[i:i + s]); i += s
    nobs, npv = perm_p(neg, rng)
    valid = pp < 0.01 and pcl["type_token"] < 0.5
    if not valid:
        verdict, bf = "VOID (positive control not detected)", {}
    elif p < 0.01:
        verdict, bf = "LABELS ALIGN BY POSITION (number-like)", {"NUMBERS": 10.0}
    elif p >= 0.2 and cl["type_token"] > 0.6:
        verdict, bf = "NOT NUMBERS (no positional alignment, open vocabulary)", {"NUMBERS": 0.1}
    else:
        verdict, bf = "INCONCLUSIVE", {}
    print("pages and label counts:", dict(zip(L, sizes)))
    print(f"Voynich: positional identity rate {obs:.4f}, p {p:.4f}; closed-set {{tokens {cl['tokens']}, types {cl['types']}, type/token {cl['type_token']:.2f}, types for 80% {cl['types_for_80pct']}}}")
    print("   commonest labels:", cl["top"])
    print(f"positive control (numbers): rate {pobs:.4f}, p {pp:.4f}, type/token {pcl['type_token']:.2f}")
    print(f"negative control (shuffled across pages): rate {nobs:.4f}, p {npv:.4f}")
    print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E056", "labels": L, "voynich": {"rate": obs, "p": p, **cl},
                               "positive": {"rate": pobs, "p": pp, "type_token": pcl["type_token"]},
                               "negative": {"rate": nobs, "p": npv}, "valid": valid, "verdict": verdict,
                               "bayes_factors": bf}, indent=1))


if __name__ == "__main__":
    main()
