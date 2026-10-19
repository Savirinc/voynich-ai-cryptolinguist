"""E026: does Voynich have a compact ending inventory written with its own glyphs?

Pre-registered in reports/E026_PREREG.md. The unsupervised stem + suffix segmenter (vcl.solvers.segment, settings
fixed below) is run on Voynich DEV / Currier B word types and on twins of every E021 family, plus two new
known-answer controls built from Latin (stem + inflectional ending, each replaced by a code written in EVA letters):
  cmp_marked : endings coded with 6 glyphs of their own (y d n l r m), stems with the other 14   (positive control)
  cmp_random : endings and stems coded with the same 20 glyphs                                   (unmarked control)
Features (vcl.solvers.segment.ending_features): SPLIT, NSUF95, DIST (decision), PAR (reported).

Run: caffeinate -ims .venv/bin/python experiments/e026_endings.py [--workers 3] [--smoke]
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
from vcl.solvers.segment import ending_features, segment_types  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 26026
PREREG = ROOT / "reports/E026_PREREG.md"
OUT = ROOT / "experiments/results/e026.json"
SEG = dict(max_suf=4, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, smooth=0.01)
FEATS = ["SPLIT", "NSUF95", "DIST", "PAR"]
DECISION = ["SPLIT", "NSUF95", "DIST"]
LANG_FAMS = ["word", "syll", "naibbe", "naibbe_drift4", "naibbe_drift8", "word_drift4", "compound", "compound_drift4"]
GEN_FAMS = ["rugg_rep", "self_citation_rep"]
CTRL_FAMS = ["cmp_marked", "cmp_random"]
Z_OK = 3.0
EVA20 = list("ydnlrmacehikopqstfgx")
END = sorted(set("""a ae am arum as is os us i o um orum e em es ibus ium u ui uum ei erum er
o as at amus atis ant eo et emus etis ent it imus itis unt abat abant ebat ebant abam
avit averunt avi isse it ere are ire ari eri iri atur antur etur entur itur untur tur ntur
ndum ndi ndo nda ndae ns ntis nte nti ntem ntes ntium ntur tus ta tum ti tae tos tas tis to
erat erant esse issent isset asset aret eret iret aret arent erent irent""".split()), key=len, reverse=True)


def lat_seg(w):
    if len(w) < 4:
        return w, ""
    for e in END:
        if w.endswith(e) and len(w) - len(e) >= 3:
            return w[:-len(e)], e
    return w, ""


def _codes(items, lo, hi, rng, taken, gl):
    out = {}
    for it in items:
        while True:
            c = "".join(rng.choice(gl) for _ in range(rng.randint(lo, hi)))
            if c not in taken:
                taken.add(c); out[it] = c; break
    return out


def control(fam, seed, N):
    rng = random.Random(seed)
    sp = [lat_seg(w) for w in A.source_words(["la"] * 4, N, rng)]
    EG, SG = (EVA20[:6], EVA20[6:]) if fam == "cmp_marked" else (EVA20, EVA20)
    taken = set()
    ec = _codes(sorted({e for _, e in sp if e}), 1, 3, rng, taken, EG); ec[""] = ""
    sc = _codes(sorted({s for s, _ in sp}), 2, 5, rng, taken, SG)
    toks = [sc[s] + ec[e] for s, e in sp]
    return toks, {sc[s] + ec[e]: len(sc[s]) for s, e in sp}


def tokens_of(fam, lg, seed, N):
    if fam in CTRL_FAMS:
        return control(fam, seed, N)
    return (B.gen(fam, lg, seed, N) if fam in B.FAMS else A.generate(fam, lg, seed, N)), None


def run(task):
    fam, lg, seed, N = task
    toks, truth = tokens_of(fam, lg, seed, N)
    split = segment_types(Counter(toks), seed=seed, **SEG)
    out = {"family": fam, "lang": lg, "seed": seed, "N": N, **ending_features(toks, split)}
    if truth:
        out["split_acc"] = float(np.mean([split[w] == truth[w] for w in toks]))
    return out


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
        tasks += [(f, None, rng.randrange(2 ** 20), N) for f in GEN_FAMS + CTRL_FAMS for _ in range(ng)]
    print(len(tasks), "twin samples", sizes, flush=True)
    with Pool(a.workers, initializer=A._init, initargs=(state,)) as pool:
        twins = list(pool.imap_unordered(run, tasks))
    fams = LANG_FAMS + GEN_FAMS + CTRL_FAMS
    res = {"experiment": "e026", "prereg_sha256": prereg_sha, "seed": SEED, "seg": SEG, "command": " ".join(sys.argv),
           "sizes": sizes, "twins": twins, "parts": {}}
    # positive control and power (no Voynich involved)
    ctrl = {}
    for part, N in sizes.items():
        mk = [t for t in twins if t["family"] == "cmp_marked" and t["N"] == N]
        rd = [t for t in twins if t["family"] == "cmp_random" and t["N"] == N]
        if not mk:
            continue
        pooled = np.sqrt((np.var([t["DIST"] for t in mk], ddof=1) + np.var([t["DIST"] for t in rd], ddof=1)) / 2) \
            if len(mk) > 1 else float("nan")
        ctrl[part] = {"marked_split_acc": [t["split_acc"] for t in mk], "random_split_acc": [t["split_acc"] for t in rd],
                      "share_marked_ge_095": float(np.mean([t["split_acc"] >= 0.95 for t in mk])),
                      "dist_separation_sd": float((np.mean([t["DIST"] for t in mk]) - np.mean([t["DIST"] for t in rd]))
                                                  / max(pooled, 1e-3)) if len(mk) > 1 else None}
        ctrl[part]["gate"] = bool(ctrl[part]["share_marked_ge_095"] >= 0.9 and
                                  (ctrl[part]["dist_separation_sd"] or 0) >= 3.0)
        print(part, "positive control", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in ctrl[part].items()
                                          if not isinstance(v, list)}, flush=True)
    res["control"] = ctrl
    if a.smoke:   # never compute the target statistic in a smoke run
        for f in fams:
            rows = [t for t in twins if t["family"] == f]
            print(f"  {f:18s}", {k: round(float(np.mean([r[k] for r in rows])), 3) for k in FEATS + (["split_acc"] if f in CTRL_FAMS else [])})
        out = ROOT / "experiments/results/smoke/e026_smoke.json"
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(res, indent=1, default=str))
        return
    for part, toks in (("DEV", vdev), ("B", vB)):
        split = segment_types(Counter(toks), seed=SEED, **SEG)
        v = ending_features(toks, split)
        suf = Counter(w[split[w]:] for w in toks)
        top = [(f, round(c / len(toks), 4)) for f, c in suf.most_common(25)]
        fo = {}
        for f in fams:
            rows = [t for t in twins if t["family"] == f and t["N"] == sizes[part]]
            mu = {k: float(np.mean([r[k] for r in rows])) for k in FEATS}
            sd = {k: max(float(np.std([r[k] for r in rows], ddof=1)), {"NSUF95": 1.0}.get(k, 0.01)) for k in FEATS}
            z = {k: (v[k] - mu[k]) / sd[k] for k in FEATS}
            fo[f] = {"mean": mu, "sd": sd, "z": z, "consistent": bool(all(abs(z[k]) <= Z_OK for k in DECISION))}
        word = [t for t in twins if t["family"] == "word" and t["N"] == sizes[part]]
        p95_dist = float(np.percentile([t["DIST"] for t in word], 95))
        p95_nsuf = float(np.percentile([t["NSUF95"] for t in word], 95))
        marked = bool(v["DIST"] > p95_dist and v["NSUF95"] <= p95_nsuf)
        gate = ctrl[part]["gate"]
        verdict = "VOID (positive control failed)" if not gate else ("MARKED ENDINGS" if marked else "NOT MARKED")
        res["parts"][part] = {"voynich": v, "top_suffixes": top, "families": fo,
                              "consistent": [f for f in fams if fo[f]["consistent"]],
                              "word_p95": {"DIST": p95_dist, "NSUF95": p95_nsuf}, "verdict": verdict}
        print(part, {k: round(v[k], 3) for k in FEATS}, "->", verdict, flush=True)
        print("  top suffixes", top[:15], flush=True)
        for f in fams:
            o = fo[f]
            print(f"  {f:18s} " + " ".join(f"{k} {o['mean'][k]:.3f} (z {o['z'][k]:+.1f})" for k in FEATS)
                  + ("  CONSISTENT" if o["consistent"] else ""), flush=True)
        print("  consistent", res["parts"][part]["consistent"], flush=True)
    res["wall_s"] = round(time.time() - t0)
    OUT.write_text(json.dumps(res, indent=1, default=str))
    from vcl.eval.ledger import append
    d = res["parts"]["DEV"]
    rows = [dict(experiment="E026", model=f"endings/{f}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="voynich_DEV_endings", metric="z_DIST", value=round(d["families"][f]["z"]["DIST"], 2),
                 command=res["command"], notes="CONSISTENT" if d["families"][f]["consistent"] else "inconsistent")
            for f in fams]
    rows += [dict(experiment="E026", model="endings/verdict", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                  split=f"voynich_{p}_endings", metric="DIST", value=round(res["parts"][p]["voynich"]["DIST"], 4),
                  command=res["command"], notes=res["parts"][p]["verdict"]) for p in res["parts"]]
    append(rows)


if __name__ == "__main__":
    main()
