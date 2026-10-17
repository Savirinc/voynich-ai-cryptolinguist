"""Faithful port of the Naibbe cipher (Greshko 2025) using the author's published tables.

Source: Greshko, Michael A. (2025). The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as
Voynich Manuscript-like ciphertext. Cryptologia. https://doi.org/10.1080/01611194.2025.2566408
Tables and reference code: github.com/greshko/naibbe-cipher @ f2675ec5dd275268bc64dd48ea64fc0e0e9827a2
(modified MIT licence covering software and datasets; vendored copy + licence in external/naibbe/).

Port of `naibbe.py` defaults: respacing 17/36 unigram probability (slight bigram excess), 52-card deck with table
weights alpha 20 / beta1-3 8 each / gamma1-2 4 each, unambiguous bigrams (prefix+suffix never equals a unigram
glyph string), 3% random space removal, plaintext normalised by `clean_line` (diacritics stripped, w->uu, j->i,
k->c, letters only). Differences from the reference: a seeded `random.Random` instead of the global RNG, and the
plaintext is one stream (our line wrapping is applied afterwards, as for every other twin family) rather than
encrypted line by line.
"""
import csv
import random
import unicodedata
from functools import lru_cache
from pathlib import Path

TABLES_CSV = Path(__file__).resolve().parents[3] / "external/naibbe/naibbe_tables.csv"
TABLES_SHA256 = "4e7cfd54b7ec66515d39a51e11ec97e8e19b643b0b189124eebc3982e707dcec"
TABLES = ["alpha", "beta1", "beta2", "beta3", "gamma1", "gamma2"]
CARD_WEIGHTS = {"alpha": 20, "beta1": 8, "beta2": 8, "beta3": 8, "gamma1": 4, "gamma2": 4}
RESPACING = 17
SPACE_REMOVAL_RATE = 0.03
_REPL = {"æ": "ae", "œ": "oe", "ð": "d", "þ": "th", "ł": "l", "ß": "ss", "ø": "o"}

DEFAULTS = dict(space_removal=SPACE_REMOVAL_RATE)
BOUNDS: dict = {}   # no free parameters: the published cipher is used as-is (space_removal fixed at 3%)


@lru_cache(maxsize=1)
def load_tables() -> dict:
    """{(state, table, letter): glyphs} from the vendored CSV."""
    out = {}
    with open(TABLES_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            state, table, letter = r["code"].split("_")
            out[(state, table, letter)] = r["glyphs"]
    return out


def clean(text: str) -> str:
    """Greshko's `clean_line`, applied to a whole text."""
    s = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    s = "".join(_REPL.get(c, c) for c in s.lower())
    s = "".join(c for c in s if c.isalpha())
    return s.replace("w", "uu").replace("j", "i").replace("k", "c")


def key(params: dict, seed: int, plain: str, pools=None) -> dict:
    """The key is the published table set itself; params only carry the space-removal rate."""
    tab = load_tables()
    letters = sorted({l for (_, _, l) in tab})
    return {"tables": tab, "letters": letters, "unigrams": {g for (s, _, _), g in tab.items() if s == "unigram"},
            "space_removal": {**DEFAULTS, **params}["space_removal"]}


def _respace(text: str, rng: random.Random) -> list[str]:
    out, i = [], 0
    while i < len(text):
        if i == len(text) - 1 or rng.random() < RESPACING / 36:
            out.append(text[i]); i += 1
        else:
            out.append(text[i:i + 2]); i += 2
    return out


def encode_tokens(plain: str, k: dict, seed: int) -> tuple[list[str], list[str]]:
    """Return (cipher words before space removal, respaced plaintext n-grams)."""
    rng = random.Random(seed)
    text = "".join(c for c in clean(plain) if c in k["letters"])
    grams = _respace(text, rng)
    tab, deck, di = k["tables"], [], 0

    def draw():
        nonlocal deck, di
        if di >= len(deck):
            deck = [t for t, n in CARD_WEIGHTS.items() for _ in range(n)]
            rng.shuffle(deck); di = 0
        di += 1
        return deck[di - 1]

    words = []
    for g in grams:
        if len(g) == 1:
            words.append(tab[("unigram", draw(), g)])
        else:
            while True:
                w = tab[("prefix", draw(), g[0])] + tab[("suffix", draw(), g[1])]
                if w not in k["unigrams"]:
                    break
            words.append(w)
    return words, grams


def encode(plain: str, k: dict, seed: int) -> list[str]:
    """Cipher words with Greshko's random space removal (adjacent words merged at the given rate)."""
    words, _ = encode_tokens(plain, k, seed)
    rng = random.Random(seed ^ 0x5EED)
    out = []
    for w in words:
        if out and rng.random() < k["space_removal"]:
            out[-1] += w
        else:
            out.append(w)
    return out


def decode(words: list[str], k: dict) -> str:
    """Decode words produced WITHOUT space removal. A unigram glyph string maps to its letter; otherwise the word is
    split into prefix + suffix. Where several readings exist the first found is returned (the published tables are
    not guaranteed injective), so decoding is checked by character accuracy, not exactness."""
    uni, pre, suf = {}, {}, {}
    for (s, _, l), g in k["tables"].items():
        {"unigram": uni, "prefix": pre, "suffix": suf}[s].setdefault(g, l)
    out = []
    for w in words:
        if w in uni:
            out.append(uni[w]); continue
        for i in range(1, len(w)):
            if w[:i] in pre and w[i:] in suf:
                out.append(pre[w[:i]] + suf[w[i:]]); break
        else:
            out.append("?")
    return "".join(out)
