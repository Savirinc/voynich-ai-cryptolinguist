"""E102 (Arham, Reddit idea R1): does the vocabulary drift with position in the book, beyond topic? See reports/E102_PREREG.md.

Pages: DEV prose pages with >= 60 clean tokens, in reading order (index 0..). Every control is poured into the Voynich
line lengths, so it has the same pages. PAIRS: page pairs with the same Currier language, same scribe, same section
(illustration), on different sheets (bifolios; C24), in groups of >= 5 pages. Similarity = cosine of word-count vectors
over words occurring >= 5 times in the whole text. DRIFT = -Spearman rho(similarity, page-index distance) over PAIRS
(higher = near pages share more vocabulary than far pages, with topic, scribe, language and sheet held fixed).
Groups: 69 meaningful texts (E099 set); 60 copy-generator stretches (E032 x 10, E100 grid x 50); unscored: 5 Naibbe
texts (one published-type table each, Italian plaintext).
L band = meaningful DRIFT [p10, p90]; G band = generator DRIFT [p10, p90]. Validity: the bands do not overlap.
  LANGUAGE-LIKE   Voynich in L band, outside G band -> M x 1/3
  GENERATOR-LIKE  Voynich in G band, outside L band -> M x 3
  NEITHER / VOID                                   -> none
Rule 8: Voynich within 0.5 sd (200 page bootstraps) of a band edge -> 10 bootstraps, >= 8 agree, else NEITHER.
Unscored: DRIFT per group; pharma (A, scribe 1) pages' similarity to herbal A scribe-1 pages vs to the nearest pages of
other groups (the Reddit "late small-plant pages" claim).
Run: caffeinate -ims .venv/bin/python experiments/e102_drift.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e099_phrase_repeats_v2 as P  # noqa: E402
from e011_twin_search import parse, locked_test_leaves  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e062_scribe_tables import permuted_key  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

SEED = 102102
OUT = ROOT / "experiments/results/e102.json"
E100W = ROOT / "experiments/results/e100_work"
MINP, MINW, MING = 60, 5, 5
log = P.log


def voynich_pages():
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L, meta = defaultdict(list), {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t.eva if t.is_clean else None)
            meta.setdefault(t.folio, (str(t.currier), str(t.hand), str(t.illustration), str(t.bifolio_id)))
    order = [k for k in sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k)) if any(L[k])]
    lines = [[w for w in L[k] if w] for k in order]
    page_of = [k[0] for k in order]
    return lines, page_of, meta, sorted(locked)


def structure(lines, page_of, meta):
    pages = list(dict.fromkeys(page_of))
    size = Counter(p for p, l in zip(page_of, lines) for _ in l)
    keep = [p for p in pages if size[p] >= MINP]
    idx = {p: i for i, p in enumerate(keep)}
    grp = defaultdict(list)
    for p in keep:
        grp[meta[p][:3]].append(p)
    pairs = []
    for g, ps in grp.items():
        if len(ps) < MING:
            continue
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                a, b = ps[i], ps[j]
                if meta[a][3] != meta[b][3]:
                    pairs.append((idx[a], idx[b], g))
    return keep, idx, pairs


def page_vectors(lines, page_of, keep):
    c = Counter(w for l in lines for w in l)
    vocab = {w: i for i, w in enumerate(w for w, n in c.items() if n >= MINW)}
    pos = {p: i for i, p in enumerate(keep)}
    X = np.zeros((len(keep), len(vocab)))
    for p, l in zip(page_of, lines):
        if p in pos:
            for w in l:
                if w in vocab:
                    X[pos[p], vocab[w]] += 1
    n = np.linalg.norm(X, axis=1, keepdims=True); n[n == 0] = 1
    return X / n


def drift(X, pairs):
    s = [float((X[a] * X[b]).sum()) for a, b, _ in pairs]; d = [b - a for a, b, _ in pairs]
    return float(-spearmanr(s, d).correlation)


def by_group(X, pairs):
    g = defaultdict(list)
    for p in pairs:
        g[p[2]].append(p)
    return {"|".join(k): drift(X, v) for k, v in g.items() if len(v) >= 10}


def naibbe_text(plain, N, seed):
    key = permuted_key(seed)
    text = "".join(ch for ch in NX.clean(plain) if ch in key["letters"])
    words, _ = NX.encode_tokens(text[:N * 4], key, seed)
    assert len(words) >= N
    return words[:N]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    vl, page_of, meta, locked = voynich_pages()
    lens = [len(l) for l in vl]; N = sum(lens)
    keep, idx, pairs = structure(vl, page_of, meta)
    log(f"Voynich tokens {N} pages kept {len(keep)} pairs {len(pairs)} groups {sorted(Counter(p[2] for p in pairs).items())}")
    run = lambda toks: (lambda X: (drift(X, pairs), by_group(X, pairs)))(page_vectors(P.pour(toks, lens), page_of, keep))
    texts = {}
    for bid in sorted(d.name for d in P.BIB.iterdir() if d.is_dir() and d.name not in P.SKIP):
        texts["bible:" + bid] = P.tok(bid)
    for k, p in P.OTHER.items():
        texts["other:" + k] = P.clean_tokens(p)
    texts["other:latin_farming"] = P.farm_tokens()
    gflat = [w for l in gen_lines() for w in l]
    gens = {f"e032_gen{g}": gflat[g * N:(g + 1) * N] for g in range(10)}
    for d in sorted(E100W.iterdir()):
        t = [w for ln in (d / "generate/generated_text.txt").read_text().splitlines()
             if ln.strip() and not ln.startswith("#") for w in ln.split()]
        gens["e100_" + d.name] = t[:N]
    if a.smoke:
        texts = {k: v for k, v in texts.items() if k in ("bible:latVUC", "bible:eng-kjv", "other:culpeper")}
        gens = dict(list(gens.items())[:3])
    R = {"meaningful": {}, "generator": {}, "naibbe": {}}
    for k, t in texts.items():
        c = P.cut(t, N, rng)
        if c is None:
            log(f"skip {k}"); continue
        D, G = run(c); R["meaningful"][k] = {"drift": D, "groups": G}; log(f"{k:28s} DRIFT {D:+.3f}")
    for k, t in gens.items():
        assert len(t) == N, k
        D, G = run(t); R["generator"][k] = {"drift": D, "groups": G}; log(f"{k:28s} DRIFT {D:+.3f}")
    ita = " ".join(P.tok("ita1885"))
    for s in range(2 if a.smoke else 5):
        off = rng.randrange(len(ita) // 2)
        D, G = run(naibbe_text(ita[off:], N, SEED + s)); R["naibbe"][f"naibbe{s}"] = {"drift": D, "groups": G}
        log(f"naibbe{s:<22d} DRIFT {D:+.3f}")
    le = np.array([v["drift"] for v in R["meaningful"].values()]); ge = np.array([v["drift"] for v in R["generator"].values()])
    Lb = (float(np.percentile(le, 10)), float(np.percentile(le, 90))); Gb = (float(np.percentile(ge, 10)), float(np.percentile(ge, 90)))
    valid = Lb[1] < Gb[0] or Gb[1] < Lb[0]
    log(f"L band {Lb[0]:+.3f}..{Lb[1]:+.3f} | G band {Gb[0]:+.3f}..{Gb[1]:+.3f} | VALID {valid}")
    res = {"experiment": "E102", "seed": SEED, "N": N, "pages": len(keep), "pairs": len(pairs), "results": R,
           "L_band": Lb, "G_band": Gb, "valid": bool(valid), "locked_test_excluded": locked}
    if not a.smoke:
        X = page_vectors(vl, page_of, keep)
        VD = drift(X, pairs); VG = by_group(X, pairs)
        boot = []
        for s in range(200):
            r2 = random.Random(SEED + 7 + s); pick = sorted({r2.randrange(len(keep)) for _ in keep})
            sp = [p for p in pairs if p[0] in pick and p[1] in pick]; boot.append(drift(X, sp))
        sd = float(np.std(boot, ddof=1))
        inL = lambda x: Lb[0] <= x <= Lb[1]; inG = lambda x: Gb[0] <= x <= Gb[1]

        def verdict(x):
            if inL(x) and not inG(x):
                return "LANGUAGE-LIKE"
            if inG(x) and not inL(x):
                return "GENERATOR-LIKE"
            return "NEITHER"
        v = verdict(VD) if valid else "VOID"
        if valid and min(abs(VD - b) for b in (*Lb, *Gb)) < 0.5 * sd:
            reps = verdict_reps = [verdict(x) for x in boot[:10]]
            res["seed_check"] = reps
            if sum(r == v for r in verdict_reps) < 8:
                v = "NEITHER"
        fM = {"LANGUAGE-LIKE": 1 / 3, "GENERATOR-LIKE": 3.0}.get(v, 1.0)
        # unscored: pharma A1 vs herbal A1 (far, same scribe) and vs nearest other-group pages
        ph = [p for p in keep if meta[p][:3] == ("A", "1", "P")]; hb = [p for p in keep if meta[p][:3] == ("A", "1", "H")]
        far = float(np.mean([(X[idx[a]] * X[idx[b]]).sum() for a in ph for b in hb]))
        near = []
        for a_ in ph:
            others = sorted((p for p in keep if meta[p][:3] != ("A", "1", "P")), key=lambda p: abs(idx[p] - idx[a_]))[:3]
            near += [float((X[idx[a_]] * X[idx[b]]).sum()) for b in others]
        res.update(voynich={"drift": VD, "sd": sd, "groups": VG, "pharma_vs_herbalA1": far, "pharma_vs_nearest_other": float(np.mean(near))},
                   verdict=v, factor_M=fM)
        log(f"VOYNICH DRIFT {VD:+.3f} (sd {sd:.3f}) groups {VG} | pharma~herbalA1 {far:.3f} vs ~nearest other {np.mean(near):.3f}")
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e102_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
