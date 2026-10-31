"""E107 (Arham): are gallows decorative anywhere in a word (like Arabic kashida)? See reports/E107_PREREG.md.

A decoration does not change the word, so a word with and without the gallows should be used in the same contexts.
PAIRS: (w, w') where w' is w with one gallows (EVA t/k/p/f, also inside benches) deleted, both words occurring >= 30
times. Context of an occurrence = previous word and next word within the line ('#' at line edges), as two tagged
items. CD (context difference) of a pair: draw 15 occurrences of each word, Jensen-Shannon divergence (bits) of the
two context distributions; SAME = the same for two disjoint draws of 15 from one word (average of w and w');
RAND = the same for w against frequency-matched random words (count within 0.7-1.4x). 30 draws each.
CD = (JSD_pair - SAME) / (RAND - SAME): 0 = interchangeable, 1 = as different as unrelated words. Text CD = median.
Known answers (5 languages: latVUC, ita1885, deu1912, ces1613, turytc, cut to 28,841 tokens):
  REAL minimal pairs: (w, w with one letter deleted), both >= 30 times -> word-distinguishing level.
  PLANTED decoration: a mark inserted at a random interior position of 30% of tokens; pairs (decorated, plain).
Validity: planted CD max < real-pair CD min (over the 5 languages).
  DECORATIVE-LIKE      Voynich gallows CD <= planted max
  WORD-DISTINGUISHING  Voynich gallows CD >= real-pair min
  PARTLY               otherwise;   VOID if validity fails
No Bayes factor. Unscored: Voynich non-gallows deletion pairs (e.g. e, o, y); copy generator (10 stretches) gallows pairs;
per gallows letter; per scribe where >= 5 pairs.
Run: caffeinate -ims .venv/bin/python experiments/e107_gallows_context.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e099_phrase_repeats_v2 as P  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED = 107107
OUT = ROOT / "experiments/results/e107.json"
GAL = set("tkpf")
MINC, K, DRAWS, PLANT, MARK = 30, 15, 30, 0.30, "ʘ"
LANGS = ["latVUC", "ita1885", "deu1912", "ces1613", "turytc"]
log = P.log


def contexts(lines):
    ctx = defaultdict(list)
    for l in lines:
        for i, w in enumerate(l):
            ctx[w].append(("<" + (l[i - 1] if i else "#"), ">" + (l[i + 1] if i + 1 < len(l) else "#")))
    return ctx


def jsd(a, b):
    ca, cb = Counter(x for o in a for x in o), Counter(x for o in b for x in o)
    na, nb = sum(ca.values()), sum(cb.values()); s = 0.0
    for k in set(ca) | set(cb):
        p, q = ca[k] / na, cb[k] / nb; m = (p + q) / 2
        if p:
            s += 0.5 * p * np.log2(p / m)
        if q:
            s += 0.5 * q * np.log2(q / m)
    return s


def pair_cd(w, v, ctx, freq_words, rng):
    pj, sm, rd = [], [], []
    for _ in range(DRAWS):
        pj.append(jsd(rng.sample(ctx[w], K), rng.sample(ctx[v], K)))
        for x in (w, v):
            s = rng.sample(ctx[x], 2 * K); sm.append(jsd(s[:K], s[K:]))
        n = len(ctx[v]); cand = [u for u in freq_words if 0.7 * n <= len(ctx[u]) <= 1.4 * n and u not in (w, v)]
        if cand:
            rd.append(jsd(rng.sample(ctx[w], K), rng.sample(ctx[rng.choice(cand)], K)))
    S, Rn = float(np.mean(sm)), float(np.mean(rd))
    return (float(np.mean(pj)) - S) / (Rn - S) if Rn > S else float("nan")


def deletion_pairs(c, pred):
    out = []
    for w, n in c.items():
        if n < MINC:
            continue
        for i, ch in enumerate(w):
            if pred(ch, w, i):
                v = w[:i] + w[i + 1:]
                if v and c.get(v, 0) >= MINC:
                    out.append((w, v, ch))
    return sorted(set(out))


def evaluate(lines, pred, rng):
    c = Counter(w for l in lines for w in l); ctx = contexts(lines)
    fw = [w for w, n in c.items() if n >= 2 * K]
    pairs = deletion_pairs(c, pred)
    cds = [(w, v, ch, pair_cd(w, v, ctx, fw, rng)) for w, v, ch in pairs if len(ctx[w]) >= 2 * K and len(ctx[v]) >= 2 * K]
    vals = [x[3] for x in cds if x[3] == x[3]]
    return {"CD": float(np.median(vals)) if vals else float("nan"), "n_pairs": len(vals), "pairs": cds}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, _, locked = P.E.voynich_lines()
    segs = []
    for l in lines:
        cur = []
        for w in l:
            if w:
                cur.append(w)
            else:
                if cur:
                    segs.append(cur)
                cur = []
        if cur:
            segs.append(cur)
    vl = [[w for w in l if w] for l in lines if any(l)]; lens = [len(l) for l in vl]; N = sum(lens)
    langs = LANGS[:2] if a.smoke else LANGS
    R = {"real": {}, "planted": {}}
    for b in langs:
        L = P.pour(P.cut(P.tok(b), N, rng), lens)
        R["real"][b] = m = evaluate(L, lambda ch, w, i: True, rng)
        Lp = [[(w[:j] + MARK + w[j:]) if (len(w) >= 2 and rng.random() < PLANT and (j := rng.randrange(1, len(w)))) else w for w in l] for l in L]
        R["planted"][b] = mp = evaluate(Lp, lambda ch, w, i: ch == MARK, rng)
        log(f"{b:8s} real minimal pairs CD {m['CD']:.3f} (n {m['n_pairs']}) | planted decoration CD {mp['CD']:.3f} (n {mp['n_pairs']})")
    rmin = min(v["CD"] for v in R["real"].values()); pmax = max(v["CD"] for v in R["planted"].values())
    valid = pmax < rmin
    log(f"planted max {pmax:.3f} | real-pair min {rmin:.3f} | VALID {valid}")
    gflat = [w for l in gen_lines() for w in l]
    GEN = {}
    for s in range(1 if a.smoke else 10):
        GEN[s] = m = evaluate(P.pour(gflat[s * N:(s + 1) * N], lens), lambda ch, w, i: ch in GAL, rng)
        m.pop("pairs"); log(f"gen{s} gallows CD {m['CD']:.3f} (n {m['n_pairs']})")
    res = {"experiment": "E107", "seed": SEED, "results": {k: {b: {kk: vv for kk, vv in v.items() if kk != "pairs"} for b, v in d.items()} for k, d in R.items()},
           "generator": GEN, "planted_max": pmax, "real_min": rmin, "valid": bool(valid), "locked_test_excluded": locked}
    if not a.smoke:
        V = evaluate(segs, lambda ch, w, i: ch in GAL, rng)
        O = evaluate(segs, lambda ch, w, i: ch not in GAL, rng)
        cd = V["CD"]
        v = ("DECORATIVE-LIKE" if cd <= pmax else ("WORD-DISTINGUISHING" if cd >= rmin else "PARTLY")) if valid else "VOID"
        byg = defaultdict(list)
        for w, u, ch, x in V["pairs"]:
            byg[ch].append(x)
        byo = defaultdict(list)
        for w, u, ch, x in O["pairs"]:
            byo[ch].append(x)
        res.update(voynich={"CD": cd, "n_pairs": V["n_pairs"], "pairs": V["pairs"],
                            "by_gallows": {k: (float(np.median(x)), len(x)) for k, x in byg.items()}},
                   voynich_other={"CD": O["CD"], "n_pairs": O["n_pairs"], "by_letter": {k: (float(np.median(x)), len(x)) for k, x in byo.items()}},
                   verdict=v)
        log(f"VOYNICH gallows pairs CD {cd:.3f} (n {V['n_pairs']}) by gallows {res['voynich']['by_gallows']}")
        log(f"  examples {[(w, u, round(x, 2)) for w, u, ch, x in V['pairs'][:12]]}")
        log(f"VOYNICH other-letter deletion pairs CD {O['CD']:.3f} (n {O['n_pairs']}) by letter {res['voynich_other']['by_letter']}")
        log(f"VERDICT {v} (no factor)")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e107_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
