"""E021 (methodology A1c): drift vs topic -- do the most common Voynich words persist across the whole book?

Pre-registered in reports/E021_PREREG.md. In a language, topics change but grammar doesn't: the most frequent types
(function words) occur in every part of a text. If a cipher's key or tables change by section, all frequent types
are replaced together at a boundary. Spelling drift by scribes replaces some of them.
Text cut into K = 8 equal chunks in reading order. For each of the top-T types (T = 30, overall frequency):
  ratio_c = rate in chunk c / overall rate.
  PERS_T = mean over the top-T types of min_c ratio_c   (0 = some chunk lacks it entirely; 1 = perfectly even)
  COV_T  = mean over the top-T types of the share of chunks with ratio_c >= 0.25
Reported also for T = 100. Families and twin sources: E019 (word, syll, naibbe fixed key, rugg_rep,
self_citation_rep) and E020 (naibbe_drift4, naibbe_drift8, word_drift4, compound, compound_drift4) generators,
unchanged. 40 samples per language family (10 x la/it/fr/de), 20 per generator, at DEV size and Currier B size.

Run: caffeinate -ims .venv/bin/python experiments/e021_persistence.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e019_unit_burstiness as A  # noqa: E402
import e020_drift_compound as B  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 21021
PREREG = ROOT / "reports/E021_PREREG.md"
OUT = ROOT / "experiments/results/e021.json"
K = 8
FEATS = ["PERS_30", "COV_30", "PERS_100", "COV_100"]
DECISION = ["PERS_30", "COV_30"]
LANG_FAMS = ["word", "syll", "naibbe", "naibbe_drift4", "naibbe_drift8", "word_drift4", "compound", "compound_drift4"]
GEN_FAMS = ["rugg_rep", "self_citation_rep"]
Z_OK = 3.0


def persistence(tokens, K=K):
    n = len(tokens)
    chunks = [Counter(tokens[i * n // K:(i + 1) * n // K]) for i in range(K)]
    sizes = [sum(c.values()) for c in chunks]
    tot = Counter(tokens)
    out = {}
    for Tn in (30, 100):
        top = [w for w, _ in tot.most_common(Tn)]
        mins, covs = [], []
        for w in top:
            r = tot[w] / n
            ratios = [chunks[c][w] / sizes[c] / r for c in range(K)]
            mins.append(min(ratios)); covs.append(np.mean([x >= 0.25 for x in ratios]))
        out[f"PERS_{Tn}"] = float(np.mean(mins)); out[f"COV_{Tn}"] = float(np.mean(covs))
    return out


def run(task):
    fam, lg, seed, N = task
    toks = B.gen(fam, lg, seed, N) if fam in B.FAMS else A.generate(fam, lg, seed, N)
    return {"family": fam, "lang": lg, "seed": seed, "N": N, **persistence(toks)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    lines, cur, dev_words, _ = E.voynich_lines()
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = {}
    for b in load_books():
        if b["lang"] in A.LANGS and roles.get(b["id"], {}).get("role") in ("tune", "ref"):
            books.setdefault(b["lang"], []).append([w for w in (NX.clean(x) for x in b["text"][2000:].split()) if w])
    e14 = {(c["family"], c["lang"]): c["params"]
           for c in json.loads((ROOT / "experiments/results/e014.json").read_text())["combos"]}
    state = {"books": books, "e14": e14, "C": X.coupling_matrix(lines), "nulls": R.null_pool(dev_words),
             "pools": T.chunk_pools(dev_words), "dev_words": dev_words}
    vdev = [w for l in lines for w in l if w]
    vB = [w for l, c in zip(lines, cur) if c == "B" for w in l if w]
    sizes = {"DEV": len(vdev), "B": len(vB)}
    nl, ng = (10, 20) if not a.smoke else (1, 1)
    rng = random.Random(SEED)
    tasks = []
    for part, N in sizes.items():
        if a.smoke and part == "B":
            continue
        tasks += [(f, lg, rng.randrange(2 ** 20), N) for f in LANG_FAMS for lg in A.LANGS for _ in range(nl)]
        tasks += [(f, None, rng.randrange(2 ** 20), N) for f in GEN_FAMS for _ in range(ng)]
    print(len(tasks), "twin samples", sizes, flush=True)
    with Pool(a.workers, initializer=A._init, initargs=(state,)) as pool:
        twins = list(pool.imap_unordered(run, tasks))
    res = {"experiment": "e021", "prereg_sha256": prereg_sha, "seed": SEED, "command": " ".join(sys.argv),
           "sizes": sizes, "twins": twins, "parts": {}}
    fams = LANG_FAMS + GEN_FAMS
    if a.smoke:   # never compute the target statistic in a smoke run
        for f in fams:
            rows = [t for t in twins if t["family"] == f]
            print(f"  {f:18s}", {k: round(float(np.mean([r[k] for r in rows])), 3) for k in FEATS})
        out = ROOT / "experiments/results/smoke/e021_smoke.json"
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(res, indent=1, default=str))
        return
    for part, toks in (("DEV", vdev), ("B", vB)):
        v = persistence(toks)
        fo = {}
        for f in fams:
            rows = [t for t in twins if t["family"] == f and t["N"] == sizes[part]]
            mu = {k: float(np.mean([r[k] for r in rows])) for k in FEATS}
            sd = {k: max(float(np.std([r[k] for r in rows], ddof=1)), 0.01) for k in FEATS}
            z = {k: (v[k] - mu[k]) / sd[k] for k in FEATS}
            fo[f] = {"mean": mu, "sd": sd, "z": z, "range": {k: [min(r[k] for r in rows), max(r[k] for r in rows)]
                                                             for k in FEATS},
                     "consistent": bool(all(abs(z[k]) <= Z_OK for k in DECISION))}
        res["parts"][part] = {"voynich": v, "families": fo, "consistent": [f for f in fams if fo[f]["consistent"]]}
        print(part, {k: round(v[k], 3) for k in FEATS}, flush=True)
        for f in fams:
            o = fo[f]
            print(f"  {f:18s} " + " ".join(f"{k} {o['mean'][k]:.3f} (z {o['z'][k]:+.1f})" for k in FEATS)
                  + ("  CONSISTENT" if o["consistent"] else ""), flush=True)
        print("  consistent", res["parts"][part]["consistent"], flush=True)
    res["wall_s"] = round(time.time() - t0)
    OUT.write_text(json.dumps(res, indent=1, default=str))
    from vcl.eval.ledger import append
    d = res["parts"]["DEV"]["families"]
    append([dict(experiment="E021", model=f"unit_family/{f}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="voynich_DEV_persistence", metric="z_PERS_30", value=round(d[f]["z"]["PERS_30"], 2),
                 command=res["command"], notes="CONSISTENT" if d[f]["consistent"] else "inconsistent") for f in fams])


if __name__ == "__main__":
    main()
