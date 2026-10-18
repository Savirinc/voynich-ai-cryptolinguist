"""E024 (methodology A3): what are Voynich's real letters? Which glyph segmentation gives alphabet-like statistics?

Pre-registered in reports/E024_PREREG.md. Voynich DEV prose words (clean), segmented greedily (longest match first)
into units under four fixed segmentations:
  S0  single EVA characters
  S1  + benches and pedestalled gallows as one unit: cth ckh cph cfh ch sh
  S2  S1 + i-runs with their final and e-runs: iiin iin in iiir iir ir eee ee
  S3  S2 + the two most rigid glyph pairs: qo dy
Metrics (text = words separated by one space symbol): h1 = unigram entropy (bits, space included);
h2 = conditional entropy of a unit given the previous one; L = mean word length in units; K = number of unit
types covering 99.9% of tokens. References: 36 languages of the plaintext corpus, 28,841 words each
(lowercased letters only, words in book order from the start of the concatenated books after 2,000 chars).

Run: .venv/bin/python experiments/e024_atoms.py
"""
from __future__ import annotations

import hashlib, json, math, re, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

PREREG = ROOT / "reports/E024_PREREG.md"
OUT = ROOT / "experiments/results/e024.json"
SEGS = {"S0": [], "S1": ["cth", "ckh", "cph", "cfh", "ch", "sh"]}
SEGS["S2"] = SEGS["S1"] + ["iiin", "iin", "in", "iiir", "iir", "ir", "eee", "ee"]
SEGS["S3"] = SEGS["S2"] + ["qo", "dy"]
METRICS = ["h1", "h2", "L"]


def segment(word, units):
    units = sorted(units, key=len, reverse=True)
    out, i = [], 0
    while i < len(word):
        for u in units:
            if word.startswith(u, i):
                out.append(u); i += len(u); break
        else:
            out.append(word[i]); i += 1
    return out


def metrics(words_units):
    seq = []
    for w in words_units:
        seq += w + [" "]
    c1 = Counter(seq)
    n = len(seq)
    h1 = -sum(v / n * math.log2(v / n) for v in c1.values())
    c2 = Counter(zip(seq, seq[1:]))
    n2 = n - 1
    h12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    cum, K = 0, 0
    for _, v in c1.most_common():
        cum += v; K += 1
        if cum / n >= 0.999:
            break
    return {"h1": h1, "h2": h12 - h1, "L": float(np.mean([len(w) for w in words_units])), "K": K}


def main():
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if prereg_sha is None:
        sys.exit("pre-registration missing")
    lines, _, _, _ = E.voynich_lines()
    vw = [w for l in lines for w in l if w]
    N = len(vw)
    refs = {}
    by = {}
    for b in load_books():
        by.setdefault(b["lang"], []).append(b["text"][2000:])
    for lg, ts in sorted(by.items()):
        ws = [w for w in re.findall(r"[^\W\d_]+", " ".join(ts).lower())][:N]
        if len(ws) == N:
            refs[lg] = metrics([list(w) for w in ws])
    lo = {k: min(r[k] for r in refs.values()) for k in METRICS}
    hi = {k: max(r[k] for r in refs.values()) for k in METRICS}
    mu = {k: float(np.mean([r[k] for r in refs.values()])) for k in METRICS}
    sd = {k: float(np.std([r[k] for r in refs.values()], ddof=1)) for k in METRICS}
    res = {"experiment": "e024", "prereg_sha256": prereg_sha, "n_words": N, "refs": refs,
           "ref_range": {k: [lo[k], hi[k]] for k in METRICS}, "segmentations": {}}
    for s, units in SEGS.items():
        m = metrics([segment(w, units) for w in vw])
        inside = {k: bool(lo[k] <= m[k] <= hi[k]) for k in METRICS}
        near = sorted(refs, key=lambda lg: sum(((m[k] - refs[lg][k]) / sd[k]) ** 2 for k in METRICS))[:3]
        res["segmentations"][s] = {**m, "inside": inside, "alphabet_like": all(inside.values()), "nearest": near,
                                   "z": {k: (m[k] - mu[k]) / sd[k] for k in METRICS}}
        print(s, {k: round(v, 3) for k, v in m.items()}, "inside", inside, "nearest", near, flush=True)
    print("ref range", {k: [round(lo[k], 3), round(hi[k], 3)] for k in METRICS}, "n langs", len(refs))
    res["verdict"] = [s for s, v in res["segmentations"].items() if v["alphabet_like"]] or "NONE"
    print("alphabet-like:", res["verdict"])
    OUT.write_text(json.dumps(res, indent=1))
    from vcl.eval.ledger import append
    append([dict(experiment="E024", model=f"segmentation/{s}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="voynich_DEV", metric=k, value=round(v[k], 4), command=" ".join(sys.argv),
                 notes="alphabet-like" if v["alphabet_like"] else "outside")
            for s, v in res["segmentations"].items() for k in ("h1", "h2")])


if __name__ == "__main__":
    main()
