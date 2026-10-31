"""E110 (Arham): are p and f two forms of one letter, or different (possibly opposite) letters? See reports/E110_PREREG.md.

FRAMES: word pairs identical except one letter, each word containing exactly one of the two letters (Voynich: p<->f, DEV only). TOKENS: every occurrence of either
member, outcome = which letter it has. STRATA (Voynich): scribe x paragraph-first-line x slot of the letter (first letter;
after o/qo/y/l/ch/sh prefix; inside a c?h bench; other). Each frame exists only because both versions occur, so one p-token and one f-token per frame (random) are set aside
and only the remaining tokens are tested. Statistic G = sum over strata of the likelihood-ratio G of the
frame x letter table. Null: letters permuted among tokens within each stratum, 5,000 times. p = share of null G >= observed.
A small p means the letter choice depends on WHICH WORD it is, beyond scribe/position: the two letters act as different
letters. A large p means the choice is the same for every word, like two pen forms of one letter.
Known answers (latVUC, ita1885; strata: line-first x letter-is-word-initial):
  CONTRASTIVE: the consonant pair (from b/p, d/t, c/g, f/v, m/n, r/l, s/t) with the most minimal-pair frames; 20
    subsamples matched to the Voynich size (frames and tokens), each must give p < 0.01 in >= 80%.
  ALLOGRAPH: in the same text, the letter 't' is given a second form 'T' at random (probability 0.3 at word start, 0.1
    elsewhere); frames t/T; 20 size-matched subsamples, p < 0.01 in <= 10%.
Validity: both conditions in both languages.
  WORD-SPECIFIC (different letters)   Voynich p < 0.01
  WEAK                                 0.01 <= p < 0.05
  SAME-LETTER-LIKE (two forms)         p >= 0.05
Rule 8: if 0.005 <= p <= 0.02 or 0.035 <= p <= 0.07, 10 fresh permutation seeds must give the same verdict (>= 8).
Unscored: frames with the strongest own preference; co-location (share of f-version tokens on a page that also has the
p-version, against label permutation within strata).
Run: caffeinate -ims .venv/bin/python experiments/e110_pf_same_or_different.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
import e099_phrase_repeats_v2 as P  # noqa: E402

SEED = 110110
OUT = ROOT / "experiments/results/e110.json"
PAIRS = [("b", "p"), ("d", "t"), ("c", "g"), ("f", "v"), ("m", "n"), ("r", "l"), ("s", "t")]
log = P.log


def gstat(tokens, labels):
    """tokens: list of (stratum, frame); labels: list of 0/1."""
    tab = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for (s, fr), y in zip(tokens, labels):
        tab[s][fr][y] += 1
    G = 0.0
    for s, frs in tab.items():
        n = sum(a + b for a, b in frs.values()); c1 = sum(b for _, b in frs.values()); c0 = n - c1
        if c0 == 0 or c1 == 0 or len(frs) < 2:
            continue
        for a, b in frs.values():
            m = a + b
            for o, col in ((a, c0), (b, c1)):
                e = m * col / n
                if o > 0:
                    G += 2 * o * np.log(o / e)
    return G


def perm_p(tokens, labels, rng, n):
    g0 = gstat(tokens, labels)
    idx = defaultdict(list)
    for i, (s, _) in enumerate(tokens):
        idx[s].append(i)
    ge = 0
    for _ in range(n):
        lab = list(labels)
        for ii in idx.values():
            v = [lab[i] for i in ii]; rng.shuffle(v)
            for i, x in zip(ii, v):
                lab[i] = x
        ge += gstat(tokens, lab) >= g0 - 1e-9
    return g0, (ge + 1) / (n + 1)


def frames_from(words_counts, a, b):
    """Only words with exactly one a-or-b letter, so every word belongs to one frame with one label."""
    out = set()
    for w in words_counts:
        if w.count(a) != 1 or w.count(b) != 0:
            continue
        i = w.index(a); v = w[:i] + b + w[i + 1:]
        if v in words_counts:
            out.add((w, v, i))
    return sorted(out)


def slot(w, i):
    if i == 0:
        return "first"
    if i >= 1 and w[i - 1] == "c" and i + 1 < len(w) and w[i + 1] == "h":
        return "bench"
    if w[:i] in ("o", "qo", "y", "l", "ch", "sh", "ol"):
        return "prefix"
    return "other"


def voynich():
    _, zl = parse(); L = set(locked_test_leaves(zl))
    lines = defaultdict(list)
    for t in zl:
        if t.leaf in L or not t.eva or not t.is_clean:
            continue
        lines[(t.folio, t.line_no, t.mode)].append(t)
    allt = [(t, i) for ts in lines.values() for i, t in enumerate(ts)]
    wc = Counter(t.eva for t, _ in allt)
    fr = frames_from(wc, "p", "f")
    member = {}
    for k, (pw, fw, i) in enumerate(fr):
        member[pw] = (k, 0, i); member[fw] = (k, 1, i)
    toks, labs, pages = [], [], []
    for t, i in allt:
        if t.eva in member:
            k, y, pos = member[t.eva]
            toks.append(((str(t.hand), bool(t.para_start), slot(t.eva, pos)), k)); labs.append(y); pages.append(t.folio)
    toks, labs, pages = drop_witnesses(toks, labs, random.Random(SEED + 1), pages)
    return fr, toks, labs, pages, sorted(L)


def language(bid, rng, N, kind):
    lines = P.pour(P.cut(P.tok(bid), N, rng), [12] * (N // 12))
    if kind == "allograph":
        lines = [[("".join(("T" if (c == "t" and rng.random() < (0.3 if j == 0 else 0.1)) else c) for j, c in enumerate(w))) for w in l] for l in lines]
    wc = Counter(w for l in lines for w in l)
    if kind == "allograph":
        a, b = "t", "T"
    else:
        best = max(PAIRS, key=lambda ab: len(frames_from(wc, ab[0], ab[1])))
        a, b = best
    fr = frames_from(wc, a, b)
    member = {}
    for k, (w1, w2, i) in enumerate(fr):
        member.setdefault(w1, (k, 0, i)); member.setdefault(w2, (k, 1, i))
    toks, labs = [], []
    for l in lines:
        for j, w in enumerate(l):
            if w in member:
                k, y, pos = member[w]
                toks.append(((j == 0, pos == 0), k)); labs.append(y)
    return (a, b), *drop_witnesses(toks, labs, rng)


def drop_witnesses(toks, labs, rng, extra=None):
    """Each frame exists only because both versions occur; set aside one 0-token and one 1-token per frame (chosen at
    random) so the remaining labels are free to vary under the null."""
    idx = defaultdict(lambda: [[], []])
    for i, ((s, k), y) in enumerate(zip(toks, labs)):
        idx[k][y].append(i)
    drop = set()
    for k, (z, o) in idx.items():
        drop.add(rng.choice(z)); drop.add(rng.choice(o))
    keep = [i for i in range(len(toks)) if i not in drop]
    out = ([toks[i] for i in keep], [labs[i] for i in keep])
    return out + (([extra[i] for i in keep],) if extra is not None else ())


def subsample(toks, labs, nfr, ntok, rng):
    frames = sorted({k for _, k in toks}); rng.shuffle(frames)
    keep, n, out = set(), 0, []
    byf = Counter(k for _, k in toks)
    for f in frames:
        if len(keep) >= nfr or n >= ntok:
            break
        keep.add(f); n += byf[f]
    sel = [(t, y) for t, y in zip(toks, labs) if t[1] in keep]
    return [t for t, _ in sel], [y for _, y in sel]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    rng = random.Random(SEED)
    fr, toks, labs, pages, locked = voynich()
    nfr, ntok = len({k for _, k in toks}), len(toks)
    log(f"Voynich frames {nfr} tokens {ntok} (p {labs.count(0)}, f {labs.count(1)})")
    nrep, nperm = (3, 300) if a.smoke else (20, 2000)
    KA = {}
    for bid in ("latVUC", "ita1885"):
        for kind in ("contrastive", "allograph"):
            pair, t_, l_ = language(bid, rng, 28841, kind)
            ps = []
            for _ in range(nrep):
                st, sl = subsample(t_, l_, nfr, ntok, rng)
                ps.append(perm_p(st, sl, rng, nperm)[1])
            KA[f"{bid}:{kind}"] = {"pair": pair, "frames": len({k for _, k in t_}), "tokens": len(t_),
                                   "share_p_lt_0.01": float(np.mean([p < 0.01 for p in ps])), "median_p": float(np.median(ps))}
            log(f"{bid} {kind} {pair}: {KA[f'{bid}:{kind}']}")
    valid = all(KA[f"{b}:contrastive"]["share_p_lt_0.01"] >= 0.8 and KA[f"{b}:allograph"]["share_p_lt_0.01"] <= 0.1 for b in ("latVUC", "ita1885"))
    res = {"experiment": "E110", "seed": SEED, "frames": nfr, "tokens": ntok, "known_answers": KA, "valid": bool(valid), "locked_test_excluded": locked}
    log(f"VALID {valid}")
    if not a.smoke:
        g0, p = perm_p(toks, labs, rng, 5000)

        def verdict(p):
            return "WORD-SPECIFIC" if p < 0.01 else ("WEAK" if p < 0.05 else "SAME-LETTER-LIKE")
        v = verdict(p) if valid else "VOID"
        if valid and (0.005 <= p <= 0.02 or 0.035 <= p <= 0.07):
            reps = [verdict(perm_p(toks, labs, random.Random(SEED + 900 + s), 5000)[1]) for s in range(10)]
            res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "WEAK"
        # unscored: per-frame preference and co-location
        cnt = defaultdict(lambda: [0, 0])
        for (s, k), y in zip(toks, labs):
            cnt[k][y] += 1
        strong = sorted(((fr[k][0], fr[k][1], c[0], c[1]) for k, c in cnt.items() if sum(c) >= 6), key=lambda x: x[3] / (x[2] + x[3]), reverse=True)
        pg = defaultdict(lambda: [set(), set()])
        for (s, k), y, pgn in zip(toks, labs, pages):
            pg[k][y].add(pgn)
        fpages = sum(len(v[1]) for v in pg.values()); shared = sum(len(v[0] & v[1]) for v in pg.values())
        res.update(G=g0, p=p, verdict=v, frames_by_f_share=strong, f_pages=fpages, f_pages_shared_with_p=shared)
        log(f"VOYNICH G {g0:.1f} p {p:.4f} -> {v}")
        log(f"frames (>=6 tokens) by f share: {strong}")
        log(f"co-location: f-version pages {fpages}, also with p-version {shared}")
    OUT.with_name("e110_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
