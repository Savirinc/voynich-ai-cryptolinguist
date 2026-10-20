"""E027 (Occam rung 0/1): is Voynich's within-word predictability inside the range of natural languages with rigid,
simple syllables, written plainly? No key, no search.

Pre-registered in reports/E027_PREREG.md. Comparison texts: public-domain / redistributable Bibles from eBible.org
(data/external/bibles, not redistributed; sha256 of each zip recorded in the results):
  simple-syllable group: haw1868 (Hawaiian), ton (Tongan), mri2012 (Maori), vie1934 (Vietnamese),
                         cmn-cu89s (Mandarin, converted to pinyin with pypinyin, one word per syllable)
  genre anchors:         latVUC (Latin Vulgate), eng-kjv (English KJV): must fall inside the E024 34-language range
Renderings: NATIVE (Unicode NFC; pinyin without tone marks) and MARKS (NFD, combining marks as separate units;
pinyin with the tone digit as a final unit).
Statistics (E024 metrics on DEV-sized samples, 28,841 words): h1, h2, L. Secondary (reported): E026 ending features.
PRIMARY (E024's rule, unchanged): Voynich segmentation S is INSIDE iff each of h1, h2, L lies in [min, max] of the
simple-syllable group (5 languages x 2 renderings). SECONDARY: MATCH(text, S) iff |difference| <= c * SD33 on each of
h1, h2, L (SD33 = between-language SD of the E024 references without Telugu, whose figures E024 flagged as
distorted); c = the largest of 0.25, 0.5, 0.75, 1.0 whose pair base rate among the 33 languages is <= 0.05.

Run: .venv/bin/python experiments/e027_simple_syllables.py [--calib]   (--calib: references only, no Voynich)
"""
from __future__ import annotations

import argparse, glob, hashlib, itertools, json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e024_atoms as A  # noqa: E402
from vcl.solvers.segment import ending_features, segment_types  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

PREREG = ROOT / "reports/E027_PREREG.md"
OUT = ROOT / "experiments/results/e027.json"
BIB = ROOT / "data/external/bibles"
SIMPLE = ["haw1868", "ton", "mri2012", "vie1934", "cmn-cu89s"]
ANCHORS = ["latVUC", "eng-kjv"]
METRICS = ["h1", "h2", "L"]
SEG = dict(max_suf=4, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, smooth=0.01)   # = E026
N = 28841
SKIP = 2000   # words skipped at the start, as E024 skips 2,000 characters


def bible_text(bid):
    fs = sorted(f for f in glob.glob(str(BIB / bid / "txt" / "*_read.txt")) if "_000_000_000_" not in f)
    out = []
    for f in fs:
        lines = Path(f).read_text(encoding="utf-8-sig").splitlines()
        out += lines[1:]          # line 1 is the book/chapter title
    return "\n".join(out)


def words(bid, rendering):
    t = bible_text(bid)
    if bid.startswith("cmn"):
        from pypinyin import Style, lazy_pinyin
        han = "".join(re.findall(r"[一-鿿]+", t))
        sy = lazy_pinyin(han, style=Style.TONE3 if rendering == "MARKS" else Style.NORMAL, neutral_tone_with_five=True)
        ws = [list(re.sub(r"\d", "", s)) + (re.findall(r"\d", s) if rendering == "MARKS" else []) for s in sy]
        ws = [w for w in ws if w]
    else:
        t = unicodedata.normalize("NFC", t.lower()).replace("’", "'").replace("ʻ", "'")
        raw = re.findall(r"[^\W\d_]+", t)
        if rendering == "MARKS":
            ws = [list(unicodedata.normalize("NFD", w)) for w in raw]
        else:
            ws = [list(w) for w in raw]
    return ws[SKIP:SKIP + N]


def zip_sha(bid):
    return hashlib.sha256((BIB / bid / f"{bid}.zip").read_bytes()).hexdigest()


def ending_feats(ws):
    toks = ["".join(w) for w in ws]
    sp = segment_types(Counter(toks), seed=27027, **SEG)
    return ending_features(toks, sp)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--calib", action="store_true"); a = ap.parse_args()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.calib and prereg_sha is None:
        sys.exit("pre-registration missing")
    # the 34 E024 reference languages, exactly as E024
    by = {}
    for b in load_books():
        by.setdefault(b["lang"], []).append(b["text"][2000:])
    refs = {}
    for lg, ts in sorted(by.items()):
        ws = re.findall(r"[^\W\d_]+", " ".join(ts).lower())[:N]
        if len(ws) == N:
            refs[lg] = A.metrics([list(w) for w in ws])
    lo = {k: min(r[k] for r in refs.values()) for k in METRICS}
    hi = {k: max(r[k] for r in refs.values()) for k in METRICS}
    r33 = {k: v for k, v in refs.items() if k != "te"}
    sd = {k: float(np.std([r[k] for r in r33.values()], ddof=1)) for k in METRICS}
    within = lambda x, y, c: all(abs(x[k] - y[k]) <= c * sd[k] for k in METRICS)
    pairs = list(itertools.permutations(r33, 2))
    rates = {c: float(np.mean([within(r33[p], r33[q], c) for p, q in pairs])) for c in (0.25, 0.5, 0.75, 1.0)}
    C = max([c for c, b in rates.items() if b <= 0.05], default=0.25); base = rates[C]
    match = lambda x, y: within(x, y, C)
    print("tolerance base rates", rates, "-> c =", C, flush=True)
    print(f"34 refs: n={len(refs)} SD34 { {k: round(v, 3) for k, v in sd.items()} } range "
          f"{ {k: [round(lo[k], 3), round(hi[k], 3)] for k in METRICS} }; base rate of pair matches {base:.3f}", flush=True)
    res = {"experiment": "e027", "prereg_sha256": prereg_sha, "N": N, "sd33": sd, "c": C, "rates": rates, "range34": {k: [lo[k], hi[k]] for k in METRICS},
           "base_rate": base, "refs34": refs, "zips": {b: zip_sha(b) for b in SIMPLE + ANCHORS}, "texts": {}}
    for bid in SIMPLE + ANCHORS:
        for r in ("NATIVE", "MARKS"):
            ws = words(bid, r)
            assert len(ws) == N, (bid, r, len(ws))
            m = {**A.metrics(ws), **ending_feats(ws)}
            m["inside34"] = all(lo[k] <= m[k] <= hi[k] for k in METRICS)
            res["texts"][f"{bid}/{r}"] = m
            print(f"  {bid:10s} {r:6s} " + " ".join(f"{k} {m[k]:.3f}" for k in METRICS + ["K"]) +
                  f" | SPLIT {m['SPLIT']:.2f} NSUF95 {m['NSUF95']:.0f} DIST {m['DIST']:.2f} | inside34 {m['inside34']}"
                  f" | e.g. {' '.join(''.join(w) for w in ws[:8])}", flush=True)
    gate = all(res["texts"][f"{b}/NATIVE"]["inside34"] for b in ANCHORS)
    res["anchor_gate"] = gate
    print("anchor gate (Vulgate and KJV inside the 34-language range):", gate, flush=True)
    if a.calib:      # never compute the Voynich statistics in calibration
        (ROOT / "experiments/results/smoke").mkdir(parents=True, exist_ok=True)
        (ROOT / "experiments/results/smoke/e027_calib.json").write_text(json.dumps(res, indent=1)); return
    grp = [x for t, x in res["texts"].items() if t.split("/")[0] in SIMPLE]
    glo = {k: min(x[k] for x in grp) for k in METRICS}; ghi = {k: max(x[k] for x in grp) for k in METRICS}
    res["range_simple"] = {k: [glo[k], ghi[k]] for k in METRICS}
    lines, _, _, _ = E.voynich_lines()
    vw = [w for l in lines for w in l if w]
    res["voynich"] = {}
    for s, units in A.SEGS.items():
        vu = [A.segment(w, units) for w in vw]
        v = {**A.metrics(vu), **(ending_features(vw, segment_types(Counter(vw), seed=27027, **SEG)) if s == "S0" else {})}
        cand = {t: x for t, x in res["texts"].items() if t.split("/")[0] in SIMPLE}
        dist = {t: float(np.sqrt(sum(((v[k] - x[k]) / sd[k]) ** 2 for k in METRICS))) for t, x in cand.items()}
        ms = [t for t, x in cand.items() if match(v, x)]
        ins = {k: bool(glo[k] <= v[k] <= ghi[k]) for k in METRICS}
        res["voynich"][s] = {**v, "inside_simple": ins, "INSIDE": all(ins.values()), "matches": ms, "nearest": sorted(dist, key=dist.get)[:3],
                             "dist": dist, "match34": [lg for lg, x in refs.items() if match(v, x)]}
        print(s, {k: round(v[k], 3) for k in METRICS}, "inside simple range", ins, "matches", ms, "nearest",
              [(t, round(dist[t], 2)) for t in sorted(dist, key=dist.get)[:3]], "34-lang matches", res["voynich"][s]["match34"], flush=True)
    r0 = res["voynich"]["S0"]["INSIDE"]; r1 = any(res["voynich"][s]["INSIDE"] for s in ("S1", "S2", "S3"))
    res["verdict"] = ("VOID (anchor gate failed)" if not gate else
                      "RUNG 0 NOT EXCLUDED" if r0 else "RUNG 1 NOT EXCLUDED" if r1 else "RUNGS 0-1 OUT")
    res["secondary_matches"] = {s: v["matches"] for s, v in res["voynich"].items()}
    print("VERDICT:", res["verdict"], flush=True)
    OUT.write_text(json.dumps(res, indent=1))
    from vcl.eval.ledger import append
    append([dict(experiment="E027", model=f"segmentation/{s}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="voynich_DEV", metric="nearest_simple_dist", value=round(min(v["dist"].values()), 3),
                 command=" ".join(sys.argv), notes=("INSIDE" if v["INSIDE"] else "outside") + "|" + (";".join(v["matches"]) or "no strict match")) for s, v in res["voynich"].items()]
           + [dict(experiment="E027", model="verdict", checkpoint_sha256=f"prereg={prereg_sha[:12]}", split="voynich_DEV",
                   metric="verdict", value=0, command=" ".join(sys.argv), notes=res["verdict"])])


if __name__ == "__main__":
    main()
