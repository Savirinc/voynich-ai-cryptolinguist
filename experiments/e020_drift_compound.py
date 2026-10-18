"""E020 (methodology A1b): which systems reproduce Voynich's FULL clustering profile?

Pre-registered in reports/E020_PREREG.md. E019 found Voynich word types cluster like real words (I_word 0.387,
top_word 0.285) but within-word glyph pairs cluster more than in any language twin (I_sub 0.150, top_sub 0.582).
Voynich's values are therefore already known: this is a fit test of families whose settings are fixed a priori
(no tuning to Voynich). Features and twin sources exactly as E019 (imported). Families, 10 samples per language
(la, it, fr, de) at DEV size:
  naibbe_drift4 / naibbe_drift8   Naibbe-class verbose cipher (E016 encoder: sandhi, nulls, ditto, merges, line-end m)
                                  with an independent secret key per section (4 or 8 equal sections)
  word_drift4     real words; per section, each letter independently (p=0.3) gets a section-specific variant glyph
                  used with p=0.7 (scribe/dialect spelling drift)
  compound        word = stem codeword + ending: stem (word minus its last 2 letters; whole word if <= 3 letters) ->
                  a Voynich DEV word type by frequency rank (seeded shuffle within rank bands of 20); ending (last 2
                  letters) -> a Naibbe suffix string by a seeded random table
  compound_drift4 compound with an independent ending table per section (4 sections)
Decision: a family is CONSISTENT with Voynich if |z| <= 3 on all four features (z vs the family's 40 samples).

Run: caffeinate -ims .venv/bin/python experiments/e020_drift_compound.py [--workers 3] [--smoke]
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
from vcl.solvers import verbose as V  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 20020
PREREG = ROOT / "reports/E020_PREREG.md"
OUT = ROOT / "experiments/results/e020.json"
FAMS = ["naibbe_drift4", "naibbe_drift8", "word_drift4", "compound", "compound_drift4"]
Z_OK = 3.0
G = A.G
LETTERS = {l for (_, _, l) in NX.load_tables()}


def sections(words, K):
    n = len(words)
    return [words[i * n // K:(i + 1) * n // K] for i in range(K)]


def gen(fam, lg, seed, N):
    rng = random.Random(seed)
    if fam.startswith("naibbe_drift"):
        K = int(fam[-1])
        plain = A.source_words([lg] * 4, 14000, rng)
        out = []
        for i, sec in enumerate(sections(plain, K)):
            txt = "".join(c for c in NX.clean(" ".join(sec)) if c in LETTERS)
            lines, _ = V.encode_labelled(txt, V.random_key(seed * 10 + i), G["C"], G["nulls"],
                                         seed=seed * 10 + i)
            out += [w for l in lines for w in l if w]
        return out[:N]
    words = A.source_words([lg] * 4, N, rng)
    if fam == "word_drift4":
        out = []
        for i, sec in enumerate(sections(words, 4)):
            r = random.Random(seed * 10 + i)
            var = {c: c.upper() if r.random() < 0.3 else None for c in "abcdefghilmnopqrstuvxyz"}
            out += ["".join(var.get(c) if var.get(c) and r.random() < 0.7 else c for c in w) for w in sec]
        return out
    # compound families
    stems = Counter(w[:-2] if len(w) > 3 else w for w in words)
    vt = [w for w, _ in Counter(G["dev_words"]).most_common()]
    ranked = [s for s, _ in stems.most_common()]
    code = {}
    for b in range(0, len(ranked), 20):
        band = vt[b:b + 20] if b < len(vt) else [f"{vt[b % len(vt)]}{b}"] * 20
        band = list(band); rng.shuffle(band)
        for s, c in zip(ranked[b:b + 20], band + [band[0]] * 20):
            code[s] = c
    sufs = sorted({g for (st, _, _), g in NX.load_tables().items() if st == "suffix"})
    ends = sorted({w[-2:] for w in words if len(w) > 3})

    def table(r):
        return {e: r.choice(sufs) for e in ends}
    K = 4 if fam == "compound_drift4" else 1
    out = []
    for i, sec in enumerate(sections(words, K)):
        tab = table(random.Random(seed * 10 + i))
        out += [code[w[:-2]] + tab[w[-2:]] if len(w) > 3 else code[w] for w in sec]
    return out


def run(task):
    fam, lg, seed, N = task
    return {"family": fam, "lang": lg, "seed": seed, "N": N, **A.features(gen(fam, lg, seed, N))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    lines, _, dev_words, _ = E.voynich_lines()
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = {}
    for b in load_books():
        if b["lang"] in A.LANGS and roles.get(b["id"], {}).get("role") in ("tune", "ref"):
            books.setdefault(b["lang"], []).append([w for w in (NX.clean(x) for x in b["text"][2000:].split()) if w])
    state = {"books": books, "C": X.coupling_matrix(lines), "nulls": R.null_pool(dev_words), "dev_words": dev_words}
    vdev = [w for l in lines for w in l if w]
    N = len(vdev)
    n = 10 if not a.smoke else 1
    rng = random.Random(SEED)
    tasks = [(f, lg, rng.randrange(2 ** 20), N) for f in FAMS for lg in A.LANGS for _ in range(n)]
    print(len(tasks), "twin samples", flush=True)
    with Pool(a.workers, initializer=A._init, initargs=(state,)) as pool:
        twins = list(pool.imap_unordered(run, tasks))
    res = {"experiment": "e020", "prereg": str(PREREG.relative_to(ROOT)) if PREREG.exists() else None,
           "prereg_sha256": prereg_sha, "seed": SEED, "command": " ".join(sys.argv), "twins": twins}
    if a.smoke:   # never compute the target statistic in a smoke run
        for f in FAMS:
            rows = [t for t in twins if t["family"] == f]
            print(f, {k: round(float(np.mean([r[k] for r in rows])), 3) for k in A.FEATS})
        out = ROOT / "experiments/results/smoke/e020_smoke.json"
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(res, indent=1, default=str))
        return
    v = A.features(vdev)
    fam_out = {}
    for f in FAMS:
        rows = [t for t in twins if t["family"] == f]
        mu = {k: float(np.mean([r[k] for r in rows])) for k in A.FEATS}
        sd = {k: max(float(np.std([r[k] for r in rows], ddof=1)), 0.01) for k in A.FEATS}
        z = {k: (v[k] - mu[k]) / sd[k] for k in A.FEATS}
        fam_out[f] = {"mean": mu, "sd": sd, "z": z, "rms_z": float(np.sqrt(np.mean([x ** 2 for x in z.values()]))),
                      "range": {k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in A.FEATS},
                      "consistent": bool(all(abs(x) <= Z_OK for x in z.values()))}
        print(f"  {f:16s} rms_z {fam_out[f]['rms_z']:6.2f} " + " ".join(f"{k} {z[k]:+.1f}" for k in A.FEATS)
              + ("  CONSISTENT" if fam_out[f]["consistent"] else ""), flush=True)
    res.update({"voynich": v, "families": fam_out, "consistent": [f for f in FAMS if fam_out[f]["consistent"]],
                "wall_s": round(time.time() - t0)})
    print("consistent", res["consistent"], flush=True)
    OUT.write_text(json.dumps(res, indent=1, default=str))
    from vcl.eval.ledger import append
    append([dict(experiment="E020", model=f"unit_family/{f}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="voynich_DEV_burstiness", metric="rms_z", value=round(fam_out[f]["rms_z"], 3),
                 command=res["command"], notes="CONSISTENT" if fam_out[f]["consistent"] else "inconsistent")
            for f in FAMS])


if __name__ == "__main__":
    main()
