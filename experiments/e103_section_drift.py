"""E103 (Arham): section-by-section vocabulary drift, a confirmatory test of a pattern seen after E102. See reports/E103_PREREG.md.

Groups and pairs as E102 (same Currier, scribe, section; different sheets; pages >= 60 clean tokens; groups >= 5 pages).
COMPACT = mean of group DRIFT over the three compact sections: bathing B scribe 2, stars B scribe 3, pharma A scribe 1.
Page metadata (Currier, scribe, section, sheet) always comes from ZL. Four variants:
  V1 ZL, cosine (seen in E102)   V2 ZL, Jaccard of word types (words >= 5 uses)
  V3 Takahashi (IT), cosine      V4 Glen Claston (GC), cosine
In each variant, every control is poured into that variant's own line lengths and pages: 69 meaningful texts (E099 set)
and 60 generator stretches (E032 x 10, E100 grid x 50). L band = meaningful COMPACT [p10, p90]; G band = generator
COMPACT [p10, p90]; a variant is valid iff the bands do not overlap. At least 3 of 4 variants must be valid (else VOID).
  GENERATOR-LIKE  Voynich COMPACT in G band and outside L band in every valid variant -> M x 2
  LANGUAGE-LIKE   Voynich COMPACT in L band and outside G band in every valid variant -> M x 1/2
  MIXED / VOID                                                                        -> none
Factors are reduced from E102's x3 because the pattern was found after looking (V1). Rule 8 per variant: within 0.5
page-bootstrap sd of a band edge -> 10 bootstraps, >= 8 agree, else that variant counts as disagreeing.
Unscored: herbal A (scribe 1) DRIFT and every group's DRIFT per variant; Naibbe (5 texts) in V1.
Run: caffeinate -ims .venv/bin/python experiments/e103_section_drift.py [--smoke]
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
import e102_drift as D2  # noqa: E402
import e092_transcription_check as T  # noqa: E402

SEED = 103103
OUT = ROOT / "experiments/results/e103.json"
COMPACT = [("B", "2", "B"), ("B", "3", "S"), ("A", "1", "P")]
HERB = ("A", "1", "H")
log = P.log


def jaccard_sims(lines, page_of, keep, pairs):
    c = Counter(w for l in lines for w in l)
    sets = defaultdict(set); pos = set(keep)
    for p, l in zip(page_of, lines):
        if p in pos:
            sets[p] |= {w for w in l if c[w] >= D2.MINW}
    S = [sets[p] for p in keep]
    return [len(S[a] & S[b]) / max(1, len(S[a] | S[b])) for a, b, _ in pairs]


def cos_sims(lines, page_of, keep, pairs):
    X = D2.page_vectors(lines, page_of, keep)
    return [float((X[a] * X[b]).sum()) for a, b, _ in pairs]


def group_drift(sims, pairs, groups):
    out = {}
    for g in groups:
        ix = [i for i, p in enumerate(pairs) if p[2] == g]
        out[g] = float(-spearmanr([sims[i] for i in ix], [pairs[i][1] - pairs[i][0] for i in ix]).correlation)
    return out


def variant_structs():
    _, zl = D2.parse(); locked = set(D2.locked_test_leaves(zl))
    _, _, meta, _ = D2.voynich_pages()
    V, info = {}, {}
    def build(toks, clean):
        L = defaultdict(list)
        for t in toks:
            if t.mode == "prose" and t.leaf not in locked:
                L[(t.folio, t.line_no)].append(t.eva if clean(t) else None)
        order = [k for k in sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k)) if any(L[k])]
        return [[w for w in L[k] if w] for k in order], [k[0] for k in order]
    V["ZL"] = build(zl, lambda t: t.is_clean)
    for name, (fn, sha) in T.FILES.items():
        raw = (T.TR / fn).read_bytes(); assert T.hashlib.sha256(raw).hexdigest() == sha, fn
        _, toks = T.parse(raw.decode("ascii").splitlines())
        V[name] = build(toks, (lambda t: t.is_clean) if name == "IT" else T.gc_clean)
    for n, (lines, page_of) in V.items():
        meta_n = {p: meta[p] for p in set(page_of) if p in meta}
        lines2 = [l for l, p in zip(lines, page_of) if p in meta_n]; page2 = [p for p in page_of if p in meta_n]
        keep, idx, pairs = D2.structure(lines2, page2, meta_n)
        info[n] = (lines2, page2, keep, pairs)
    return info, meta, sorted(locked)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    info, meta, locked = variant_structs()
    VARS = {"V1_ZL_cos": ("ZL", cos_sims), "V2_ZL_jac": ("ZL", jaccard_sims), "V3_IT_cos": ("IT", cos_sims), "V4_GC_cos": ("GC", cos_sims)}
    texts = {}
    for bid in sorted(d.name for d in P.BIB.iterdir() if d.is_dir() and d.name not in P.SKIP):
        texts["bible:" + bid] = P.tok(bid)
    for k, p in P.OTHER.items():
        texts["other:" + k] = P.clean_tokens(p)
    texts["other:latin_farming"] = P.farm_tokens()
    N0 = sum(len(l) for l in info["ZL"][0])
    gflat = [w for l in D2.gen_lines() for w in l]
    gens = {f"e032_gen{g}": gflat[g * N0:(g + 1) * N0 + 2000] for g in range(10)}
    for d in sorted(D2.E100W.iterdir()):
        gens["e100_" + d.name] = [w for ln in (d / "generate/generated_text.txt").read_text().splitlines()
                                  if ln.strip() and not ln.startswith("#") for w in ln.split()]
    if a.smoke:
        texts = {k: v for k, v in texts.items() if k in ("bible:latVUC", "bible:eng-kjv", "other:culpeper")}
        gens = dict(list(gens.items())[:3])
    groups = COMPACT + [HERB]
    res = {"experiment": "E103", "seed": SEED, "variants": {}, "locked_test_excluded": locked}
    for vn, (src, simf) in VARS.items():
        lines, page_of, keep, pairs = info[src]
        lens = [len(l) for l in lines]; N = sum(lens)
        have = {p[2] for p in pairs}; assert all(g in have for g in groups), (vn, have)
        def score(toks):
            G = group_drift(simf(P.pour(toks, lens), page_of, keep, pairs), pairs, groups)
            return float(np.mean([G[g] for g in COMPACT])), {"|".join(g): v for g, v in G.items()}
        R = {"meaningful": {}, "generator": {}}
        for k, t in texts.items():
            c = P.cut(t, N, rng)
            if c is not None:
                s, G = score(c); R["meaningful"][k] = {"compact": s, "groups": G}
        for k, t in gens.items():
            if len(t) >= N:
                s, G = score(t[:N]); R["generator"][k] = {"compact": s, "groups": G}
        le = np.array([v["compact"] for v in R["meaningful"].values()]); ge = np.array([v["compact"] for v in R["generator"].values()])
        Lb = (float(np.percentile(le, 10)), float(np.percentile(le, 90))); Gb = (float(np.percentile(ge, 10)), float(np.percentile(ge, 90)))
        valid = Lb[1] < Gb[0] or Gb[1] < Lb[0]
        out = {"N": N, "pages": len(keep), "pairs": len(pairs), "n_meaningful": len(le), "n_generator": len(ge),
               "L_band": Lb, "G_band": Gb, "valid": bool(valid), "results": R}
        log(f"{vn}: pages {len(keep)} pairs {len(pairs)} | L band {Lb[0]:+.3f}..{Lb[1]:+.3f} (n {len(le)}) | G band {Gb[0]:+.3f}..{Gb[1]:+.3f} (n {len(ge)}) | VALID {valid}")
        if not a.smoke:
            sims = simf(lines, page_of, keep, pairs)
            G = group_drift(sims, pairs, groups); vc = float(np.mean([G[g] for g in COMPACT]))
            inL = lambda x: Lb[0] <= x <= Lb[1]; inG = lambda x: Gb[0] <= x <= Gb[1]
            side = lambda x: "G" if (inG(x) and not inL(x)) else ("L" if (inL(x) and not inG(x)) else "-")
            boot = []
            for s_ in range(200):
                r2 = random.Random(SEED + 7 + s_); pick = {r2.randrange(len(keep)) for _ in keep}
                ix = [i for i, p in enumerate(pairs) if p[0] in pick and p[1] in pick]
                Gb_ = group_drift([sims[i] for i in ix], [pairs[i] for i in ix], COMPACT)
                boot.append(float(np.mean(list(Gb_.values()))))
            sd = float(np.nanstd(boot, ddof=1)); sv = side(vc)
            if valid and min(abs(vc - b) for b in (*Lb, *Gb)) < 0.5 * sd:
                reps = [side(x) for x in boot[:10]]; out["seed_check"] = reps
                if sum(r == sv for r in reps) < 8:
                    sv = "-"
            out["voynich"] = {"compact": vc, "sd": sd, "groups": {"|".join(g): v for g, v in G.items()}, "side": sv}
            log(f"  VOYNICH COMPACT {vc:+.3f} (sd {sd:.3f}) side {sv} | groups " + " ".join(f"{'|'.join(g)} {v:+.3f}" for g, v in G.items()))
        res["variants"][vn] = out
    if not a.smoke:
        vs = [v for v in res["variants"].values() if v["valid"]]
        if len(vs) < 3:
            verdict = "VOID"
        elif all(v["voynich"]["side"] == "G" for v in vs):
            verdict = "GENERATOR-LIKE"
        elif all(v["voynich"]["side"] == "L" for v in vs):
            verdict = "LANGUAGE-LIKE"
        else:
            verdict = "MIXED"
        fM = {"GENERATOR-LIKE": 2.0, "LANGUAGE-LIKE": 0.5}.get(verdict, 1.0)
        res.update(verdict=verdict, factor_M=fM, n_valid=len(vs))
        log(f"VERDICT {verdict} ({len(vs)} valid variants) | M x {fM:g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e103_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
