"""E062 (campaign step 2): a verbose (Naibbe-type) cipher with one table set per scribe. See reports/E062_PREREG.md.

Twins: Naibbe port (published tables) where, for scribe h, the glyph strings within every (state, table) group are
permuted among the letters (seed 1000*h + sample seed). DEV prose lines in manuscript order carry their hand; runs of
consecutive same-hand lines are enciphered with that hand's tables, consuming one plaintext in order, cut into the
Voynich line lengths. 3% adjacent-word merging as in the port. Single-table variant: published tables for everyone.
Plaintexts: latVUC, deu1912, turytc, hboWLC (Hebrew consonants transliterated). 10 seeds x 4 languages x 2 variants.
Judging: E032's 13 features and rule (|z| > 3 fails; <= 1 fail REPRODUCES, 2-4 PARTIAL, >= 5 for all CLASS FAILS).
Sanity: decode of unmerged words recovers >= 95% of plaintext characters for one sample per language.
Run: caffeinate -ims .venv/bin/python experiments/e062_scribe_tables.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time, unicodedata
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e032_copy_generator import FEATS, Z_OK, features  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

SEED, N, START = 62062, 28841, 10000
OUT = ROOT / "experiments/results/e062.json"
LANGS = ["latVUC", "deu1912", "turytc", "hboWLC"]
SEEDS = list(range(1, 11))
HEB = dict(zip("אבגדהוזחטיכךלמםנןסעפףצץקרשת", list("abgdhuzxticclmmnnsoppqqyref")))


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------------------------------------ texts
def plaintext(bid):
    from e042_language_shortlist import words
    w = words(bid)[START:]
    if bid == "hboWLC":
        w = ["".join(HEB.get(c, "") for c in x) for x in w]
    return " ".join(w)


def dev_lines():
    """DEV prose lines in e011 order: (hand, n_clean_words)."""
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    L, hand = {}, {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            k = (t.folio, t.line_no)
            L[k] = L.get(k, 0) + (1 if t.is_clean else 0); hand[k] = t.hand
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    out = [(hand[k] if hand[k] != "@" else "3", L[k]) for k in order if L[k] > 0]
    assert sum(n for _, n in out) == N, sum(n for _, n in out)
    return out, sorted(locked, key=lambda x: (len(x), x))


# ------------------------------------------------------------------------------------------------ keys
def permuted_key(seed):
    """Published tables with glyph strings permuted among letters within each (state, table) group."""
    base = NX.key({}, 0, "")
    tab = dict(base["tables"])
    rng = random.Random(seed)
    groups = {}
    for (state, table, letter) in tab:
        groups.setdefault((state, table), []).append(letter)
    new = {}
    for (state, table), letters in groups.items():
        letters = sorted(letters)
        strings = [tab[(state, table, l)] for l in letters]
        rng.shuffle(strings)
        for l, s in zip(letters, strings):
            new[(state, table, l)] = s
    return {**base, "tables": new, "unigrams": {g for (s, _, _), g in new.items() if s == "unigram"}}


def encipher(plain, lines, keys, seed):
    """keys: hand -> key. Returns (cipher lines with merging, unmerged words, grams) following the hand runs."""
    rng = random.Random(seed)
    text = "".join(c for c in NX.clean(plain) if c in keys["1"]["letters"])
    pos, words_all, grams_all, hands_all, out_lines = 0, [], [], [], []
    i = 0
    while i < len(lines):
        h = lines[i][0]; j = i
        need = 0
        while j < len(lines) and lines[j][0] == h:
            need += lines[j][1]; j += 1
        chunk = text[pos:pos + need * 3 + 50]
        words, grams = NX.encode_tokens(chunk, keys[h], rng.randrange(1 << 30))
        assert len(words) >= need, "plaintext exhausted"
        words, grams = words[:need], grams[:need]
        pos += sum(len(g) for g in grams)
        words_all += words; grams_all += grams; hands_all += [h] * len(words)
        k = 0
        for _, n in lines[i:j]:
            out_lines.append(words[k:k + n]); k += n
        i = j
    # 3% merging of adjacent words within a line (port's space removal)
    merged = []
    for l in out_lines:
        m = []
        for w in l:
            if m and rng.random() < NX.SPACE_REMOVAL_RATE:
                m[-1] += w
            else:
                m.append(w)
        merged.append(m)
    return merged, words_all, grams_all, hands_all


def decode_accuracy(words, grams, hands, keys):
    """Character accuracy of decoding each unmerged word with its own scribe's tables."""
    ok = tot = 0
    for w, g, h in zip(words, grams, hands):
        d = NX.decode([w], keys[h])
        ok += sum(a == b for a, b in zip(d, g)); tot += len(g)
    return ok / tot


def task(args):
    bid, seed, variant, lines, plain = args
    if variant == "scribe":
        keys = {h: permuted_key(1000 * int(h) + seed) for h in "12345"}
    else:
        k0 = NX.key({}, 0, ""); keys = {h: k0 for h in "12345"}
    ml, words, grams, hands = encipher(plain, lines, keys, SEED + seed)
    toks = [w for l in ml for w in l]
    f = features(ml, SEED + seed)
    f["n_tokens"] = len(toks)
    f["decode_acc"] = decode_accuracy(words[:3000], grams[:3000], hands[:3000], keys) if seed == 1 else None
    return bid, seed, variant, f


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time()
    lines, locked = dev_lines()
    log(f"DEV lines {len(lines)}, tokens {sum(n for _, n in lines)}; hands {Counter(h for h, _ in lines)}")
    from e011_twin_search import voynich_lines
    vl, _, _, _ = voynich_lines()
    vl = [[w for w in l if w] for l in vl if any(l)]
    V = features(vl, SEED)
    log("Voynich:", {k: round(V[k], 4) for k in FEATS})
    plains = {bid: plaintext(bid) for bid in LANGS}
    jobs = [(bid, s, var, lines, plains[bid]) for bid in LANGS for var in ("scribe", "single") for s in SEEDS]
    with Pool(a.workers) as pool:
        rows = pool.map(task, jobs)
    res = {"experiment": "E062", "seed": SEED, "voynich": V, "locked_test_excluded": locked, "sets": {}}
    best = None
    for bid in LANGS:
        for var in ("scribe", "single"):
            G = [f for b, s, v, f in rows if b == bid and v == var]
            M = {k: float(np.mean([g[k] for g in G])) for k in FEATS}
            S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in FEATS}
            Z = {k: round((V[k] - M[k]) / S[k], 2) for k in FEATS}
            fail = [k for k in FEATS if abs(Z[k]) > Z_OK]
            border = [k for k in FEATS if abs(abs(Z[k]) - Z_OK) < 0.5]
            acc = [g["decode_acc"] for g in G if g["decode_acc"] is not None]
            res["sets"][f"{bid}_{var}"] = {"mean": M, "sd": S, "z": Z, "fail": fail, "n_fail": len(fail), "borderline": border,
                                           "decode_acc": acc, "samples": G}
            log(f"[{bid} {var:6s}] fails {len(fail):2d} {fail} | decode {acc} | z " +
                " ".join(f"{k} {Z[k]:+.1f}" for k in FEATS))
            if var == "scribe" and (best is None or len(fail) < best[1]):
                best = (bid, len(fail))
    sane = all(min(res["sets"][f"{bid}_scribe"]["decode_acc"]) >= 0.95 for bid in LANGS)
    if not sane:
        v, bf = "VOID", "none"
    elif best[1] <= 1:
        v, bf = "C REPRODUCES", "C x3"
    elif best[1] <= 4:
        v, bf = "PARTIAL", "none"
    else:
        v, bf = "CLASS FAILS", "C x1/3"
    res.update(verdict=v, factor=bf, best_scribe_set=best, sanity_pass=sane, runtime_s=time.time() - t0)
    log(f"VERDICT {v} | factor {bf} | best per-scribe set {best} | sanity {sane} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
