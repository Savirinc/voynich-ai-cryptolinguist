"""E025 (methodology A4): does any candidate system produce Voynich's line effects for free?

Pre-registered in reports/E025_PREREG.md. Effects (tokens of lines with >= 3 words; positions: first word, last
word, medial words):
  V_first  Cramer's V between (line-initial vs medial) and the word's FIRST glyph
  V_last   Cramer's V between (line-final vs medial) and the word's LAST glyph
  LEN_first, LEN_last  mean length of line-initial / line-final words divided by mean medial length
Families (20 samples each at DEV size; E019 sources, E014 specs; lines by twins.wrap_lines unless the generator
makes its own): word (4 languages x 5), compound (E020; 4 x 5), naibbe_noline (E014 naibbe spec with p_m = 0,
4 x 5), naibbe_spec (E014 spec incl. its fitted line-end m), rugg_rep, self_citation_rep (E014 specs).
A family produces an effect FOR FREE if its mean is within 3 SD of Voynich (and it has no explicit line rule).

Run: caffeinate -ims .venv/bin/python experiments/e025_line_effects.py [--workers 3] [--smoke]
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

SEED = 25025
PREREG = ROOT / "reports/E025_PREREG.md"
OUT = ROOT / "experiments/results/e025.json"
FEATS = ["V_first", "V_last", "LEN_first", "LEN_last"]
FAMS = ["word", "compound", "naibbe_noline", "naibbe_spec", "rugg_rep", "self_citation_rep"]
EXPLICIT = {"naibbe_spec", "rugg_rep", "self_citation_rep"}   # have a fitted line-end rule (p_m) or line copying
G = A.G


def cramer_v(pairs):
    rows = sorted({a for a, _ in pairs}); cols = sorted({b for _, b in pairs})
    ri = {r: i for i, r in enumerate(rows)}; ci = {c: i for i, c in enumerate(cols)}
    M = np.zeros((len(rows), len(cols)))
    for a, b in pairs:
        M[ri[a], ci[b]] += 1
    M = M[:, M.sum(0) >= 5]
    n = M.sum(); e = M.sum(1, keepdims=True) * M.sum(0, keepdims=True) / n
    x2 = float(((M - e) ** 2 / np.where(e > 0, e, 1)).sum())
    return float(np.sqrt(x2 / (n * (min(M.shape) - 1))))


def effects(lines):
    lines = [[w for w in l if w] for l in lines]
    lines = [l for l in lines if len(l) >= 3]
    f = [("init", l[0][0]) for l in lines] + [("med", w[0]) for l in lines for w in l[1:-1]]
    la = [("fin", l[-1][-1]) for l in lines] + [("med", w[-1]) for l in lines for w in l[1:-1]]
    med = np.mean([len(w) for l in lines for w in l[1:-1]])
    return {"V_first": cramer_v(f), "V_last": cramer_v(la),
            "LEN_first": float(np.mean([len(l[0]) for l in lines]) / med),
            "LEN_last": float(np.mean([len(l[-1]) for l in lines]) / med), "n_lines": len(lines)}


def gen_lines(fam, lg, seed, N):
    rng = random.Random(seed ^ 0xA4)
    if fam in ("word", "compound"):
        words = A.generate("word", lg, seed, N) if fam == "word" else B.gen("compound", lg, seed, N)
        return T.wrap_lines(words, rng)
    if fam.startswith("naibbe"):
        spec = dict(G["e14"].get(("naibbe_rep", lg), G["e14"][("naibbe_rep", "la")]))
        if fam == "naibbe_noline":
            spec["p_m"] = 0.0
        plain = " ".join(A.source_words([lg] * 4, 14000, random.Random(seed)))
        return R.generate("naibbe_rep", spec, seed, G["pools"], N, G["C"], G["nulls"], plain=plain)["lines"]
    return R.generate(fam, G["e14"][(fam, None)], seed, G["pools"], N, G["C"], G["nulls"])["lines"]


def run(task):
    fam, lg, seed, N = task
    return {"family": fam, "lang": lg, "seed": seed, **effects(gen_lines(fam, lg, seed, N))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    lines, _, dev_words, _ = E.voynich_lines()
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = {}
    for b in load_books():
        if b["lang"] in A.LANGS and roles.get(b["id"], {}).get("role") in ("tune", "ref"):
            books.setdefault(b["lang"], []).append([w for w in (NX.clean(x) for x in b["text"][2000:].split()) if w])
    e14 = {(c["family"], c["lang"]): c["params"]
           for c in json.loads((ROOT / "experiments/results/e014.json").read_text())["combos"]}
    state = {"books": books, "e14": e14, "C": X.coupling_matrix(lines), "nulls": R.null_pool(dev_words),
             "pools": T.chunk_pools(dev_words), "dev_words": dev_words}
    N = sum(1 for l in lines for w in l if w)
    per = 5 if not a.smoke else 1
    rng = random.Random(SEED)
    tasks = []
    for f in FAMS:
        if f in ("rugg_rep", "self_citation_rep"):
            tasks += [(f, None, rng.randrange(2 ** 20), N) for _ in range(per * 4)]
        else:
            tasks += [(f, lg, rng.randrange(2 ** 20), N) for lg in A.LANGS for _ in range(per)]
    with Pool(a.workers, initializer=A._init, initargs=(state,)) as pool:
        twins = list(pool.imap_unordered(run, tasks))
    res = {"experiment": "e025", "prereg_sha256": prereg_sha, "seed": SEED, "twins": twins}
    if a.smoke:   # never compute the target statistic in a smoke run
        for f in FAMS:
            rows = [t for t in twins if t["family"] == f]
            print(f"  {f:18s}", {k: round(float(np.mean([r[k] for r in rows])), 3) for k in FEATS})
        return
    v = effects(lines)
    print("voynich", {k: round(x, 3) for k, x in v.items()})
    fo = {}
    for f in FAMS:
        rows = [t for t in twins if t["family"] == f]
        mu = {k: float(np.mean([r[k] for r in rows])) for k in FEATS}
        sd = {k: max(float(np.std([r[k] for r in rows], ddof=1)), 0.005) for k in FEATS}
        z = {k: (v[k] - mu[k]) / sd[k] for k in FEATS}
        fo[f] = {"mean": mu, "sd": sd, "z": z, "explicit_line_rule": f in EXPLICIT,
                 "reproduces": [k for k in FEATS if abs(z[k]) <= 3]}
        print(f"  {f:18s} " + " ".join(f"{k} {mu[k]:.3f} (z {z[k]:+.1f})" for k in FEATS), flush=True)
    free = {k: [f for f in FAMS if f not in EXPLICIT and k in fo[f]["reproduces"]] for k in FEATS}
    res.update({"voynich": v, "families": fo, "for_free": free})
    print("produced for free:", free)
    OUT.write_text(json.dumps(res, indent=1, default=str))
    from vcl.eval.ledger import append
    append([dict(experiment="E025", model=f"line_effects/{f}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="voynich_DEV_lines", metric=f"z_{k}", value=round(fo[f]["z"][k], 2), command=" ".join(sys.argv),
                 notes="explicit line rule" if f in EXPLICIT else "no line rule") for f in FAMS for k in ("V_first", "V_last")])


if __name__ == "__main__":
    main()
