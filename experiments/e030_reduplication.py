"""E030 (ledger test 1): do languages that double words come near Voynich's attraction of a word to a copy of itself?
See reports/E030_PREREG.md. No key, no search.

Statistic per text: R = (adjacent repeats / adjacent pairs) / sum_w p_w^2, i.e. observed repeat rate over the rate
expected if words were in random order. Secondary: raw repeat rate; near-repeat rate (pairs differing by one letter).
Bibles from eBible.org in data/external/bibles (not redistributed; zip sha256 recorded). Hyphens split words, so
"orang-orang" counts as a repeat.
Run: caffeinate -ims .venv/bin/python experiments/e030_reduplication.py
"""
from __future__ import annotations

import hashlib, json, random, re, sys, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from e011_twin_search import voynich_lines  # noqa: E402
from e027_simple_syllables import bible_text  # noqa: E402

BIB = ROOT / "data/external/bibles"
PRIMARY = ["indayt", "zlmKSZI", "tglulb", "cebulb", "swhulb", "yor", "hausa", "haw1868", "ton", "mri2012"]
SECONDARY = ["vie1934", "cmn-cu89s"]          # tokens are syllables
ANCHORS = ["latVUC", "eng-kjv"]
N, K, SEED = 28841, 10, 29029


def tokens(bid):
    t = bible_text(bid)
    if bid.startswith("cmn"):
        from pypinyin import Style, lazy_pinyin
        han = "".join(re.findall(r"[一-鿿]+", t))
        return lazy_pinyin(han, style=Style.TONE3, neutral_tone_with_five=True)   # toned: fewer false merges
    t = unicodedata.normalize("NFC", t.lower()).replace("’", "'").replace("ʻ", "'")
    return re.findall(r"[^\W\d_]+", t)


def ed1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    s, l = (a, b) if len(a) < len(b) else (b, a)
    return any(l[:i] + l[i + 1:] == s for i in range(len(l)))


def stats(seqs):
    """seqs: list of token lists; pairs are counted only inside each list."""
    wc = Counter(w for s in seqs for w in s)
    tot = sum(wc.values())
    p2 = sum((c / tot) ** 2 for c in wc.values())
    rep = near = n = 0
    for s in seqs:
        for a, b in zip(s, s[1:]):
            n += 1; rep += a == b; near += ed1(a, b)
    raw = rep / n
    return {"R": raw / p2, "raw": raw, "near": near / n, "pairs": n}


def text_stats(bid, rng):
    w = tokens(bid)
    wins = []
    for _ in range(K):
        s = rng.randrange(0, len(w) - N)
        wins.append(stats([w[s:s + N]]))
    return {"tokens": len(w), **{k: float(np.mean([x[k] for x in wins])) for k in ("R", "raw", "near")},
            "R_min": float(min(x["R"] for x in wins)), "R_max": float(max(x["R"] for x in wins)),
            "zip_sha256": hashlib.sha256((BIB / bid / f"{bid}.zip").read_bytes()).hexdigest()}


def main():
    rng = random.Random(SEED)
    lines = voynich_lines()[0]
    V = stats([[x for x in l if x] for l in lines])   # within-line pairs, clean tokens
    T = {b: text_stats(b, rng) for b in ANCHORS + PRIMARY + SECONDARY}
    gate = all(T[b]["R"] < 1.0 for b in ANCHORS)
    mx = max(T[b]["R"] for b in PRIMARY)
    if not gate:
        verdict, bf = "VOID", {}
    elif mx >= 1.5:
        verdict, bf = "LANGUAGES CAN DO IT", {"L": 3.0}
    elif mx < 1.0:
        verdict, bf = "NO LANGUAGE ATTRACTS REPEATS", {"L": 0.1, "C": 1 / 3}
    else:
        verdict, bf = "NEUTRAL", {}
    out = {"experiment": "E030", "voynich_dev": V, "texts": T, "gate_anchors_below_1": gate,
           "primary_max_R": mx, "primary_argmax": max(PRIMARY, key=lambda b: T[b]["R"]),
           "verdict": verdict, "bayes_factors": bf}
    (ROOT / "experiments/results/e030.json").write_text(json.dumps(out, indent=1))
    print(f"Voynich R {V['R']:.2f} raw {100*V['raw']:.3f}% near {100*V['near']:.2f}%")
    for b in ANCHORS + PRIMARY + SECONDARY:
        x = T[b]
        print(f"{b:10s} R {x['R']:.2f} [{x['R_min']:.2f}-{x['R_max']:.2f}] raw {100*x['raw']:.3f}% near {100*x['near']:.2f}%")
    print("gate", gate, "| primary max", round(mx, 2), out["primary_argmax"], "|", verdict, bf)


if __name__ == "__main__":
    main()
