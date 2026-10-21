"""E034 (ledger test 5): do practical / list-type texts (recipes, farming manuals, a herbal) close the gap E033 found?
Same 8 spelling-independent features as E033. See reports/E034_PREREG.md.

Texts (pooled in the order listed, words = lowercase letter runs):
  LAT_PRACTICAL  Apicius 1-5 + Cato De agri cultura + Varro Res rusticae 1-3   (Latin Library)
  LAT_COLUMELLA  Columella Res rustica 1-12 + De arboribus                       (Latin Library)
  ENG_HERBAL     Culpeper, The Complete Herbal (1653), PG #49513, between the PG START/END markers
Samples: all non-overlapping consecutive 28,841-token windows (max 10, seed 34034 if more).
sd per feature = max(own window sd if >= 3 windows, median window sd over the 12 E033 Bibles, 2% |Voynich|, 0.01).
Run: caffeinate -ims .venv/bin/python experiments/e034_genre_features.py LATLIB_DIR PG_HERBAL_FILE
"""
from __future__ import annotations

import hashlib, json, random, re, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e033_language_features import FEATS, N, Z_OK, feats  # noqa: E402

SEED, KMAX = 34034, 10
OUT = ROOT / "experiments/results/e034.json"
LAT = {"LAT_PRACTICAL": [f"apicius/apicius{i}.txt" for i in range(1, 6)] + ["cato/cato.agri.txt"]
       + [f"varro.rr{i}.txt" for i in (1, 2, 3)],
       "LAT_COLUMELLA": [f"columella/columella.rr{i}.txt" for i in range(1, 13)] + ["columella/columella.arbor.txt"]}


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def main():
    latlib, herbal = Path(sys.argv[1]), Path(sys.argv[2])
    rng = random.Random(SEED)
    lines, _, dev_words, locked = E.voynich_lines()
    V = feats([[w for w in l if w] for l in lines if any(l)], SEED)
    texts, sha = {}, {}
    for g, fs in LAT.items():
        raw = [(latlib / f).read_bytes() for f in fs]
        sha[g] = hashlib.sha256(b"".join(raw)).hexdigest()
        texts[g] = words(" ".join(r.decode("utf-8", errors="ignore") for r in raw))
    hb = herbal.read_bytes(); sha["ENG_HERBAL"] = hashlib.sha256(hb).hexdigest()
    ht = hb.decode("utf-8", errors="ignore")
    ht = ht[ht.index("*** START"):ht.index("*** END")]
    texts["ENG_HERBAL"] = words(ht.split("\n", 1)[1])
    e033 = json.loads((ROOT / "experiments/results/e033.json").read_text())
    bible_sd = {k: float(np.median([t["sd"][k] for t in e033["texts"].values()])) for k in FEATS}
    # e033 stored floored sds; recompute raw window sds is not possible from the summary, so the floored medians are used
    T = {}
    for g, w in texts.items():
        nwin = len(w) // N
        starts = [j * N for j in range(nwin)]
        pick = sorted(rng.sample(starts, min(KMAX, nwin)))
        G = [feats([w[s:s + N]], SEED + i) for i, s in enumerate(pick)]
        M = {k: float(np.mean([x[k] for x in G])) for k in FEATS}
        own = {k: float(np.std([x[k] for x in G], ddof=1)) if len(G) >= 3 else 0.0 for k in FEATS}
        S = {k: max(own[k], bible_sd[k], 0.02 * abs(V[k]), 0.01) for k in FEATS}
        Z = {k: round((V[k] - M[k]) / S[k], 2) for k in FEATS}
        T[g] = {"tokens": len(w), "n_windows": len(G), "mean": M, "sd": S, "z": Z,
                "fail": [k for k in FEATS if abs(Z[k]) > Z_OK]}
    best = min(T, key=lambda g: (len(T[g]["fail"]), float(np.sqrt(np.mean([T[g]["z"][k] ** 2 for k in FEATS])))))
    verdict, bf = ("A PRACTICAL TEXT MATCHES", {"L": 3.0}) if len(T[best]["fail"]) <= 1 else ("NO MATCH", {})
    out = {"experiment": "E034", "voynich": V, "texts": T, "sha256": sha, "best": best, "verdict": verdict,
           "bayes_factors": bf, "locked_test_excluded": locked}
    OUT.write_text(json.dumps(out, indent=1))
    for g, t in T.items():
        print(f"{g:14s} tokens {t['tokens']:7d} n={t['n_windows']} fails {len(t['fail'])}: "
              + " ".join(f"{k} {t['z'][k]:+.1f}" for k in FEATS))
        print(" " * 15 + "means: " + " ".join(f"{k} {t['mean'][k]:.3g}" for k in FEATS))
    print("Voynich: " + " ".join(f"{k} {V[k]:.3g}" for k in FEATS))
    print("best", best, T[best]["fail"], "|", verdict, bf)


if __name__ == "__main__":
    main()
