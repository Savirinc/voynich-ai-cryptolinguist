"""E109 (Arham): do f and p sit in opposite halves of rings elsewhere in the book, as on f57v? See reports/E109_PREREG.md.

Rings: ZL 'circle' lines, DEV only (LOCKED_TEST leaves excluded), f57v excluded (the pattern was found there). A ring's
text is its clean tokens joined; each f and p gets a position x = (character offset + 0.5) / ring length on [0, 1),
treated as a circle (where the transcriber started reading does not matter). For a ring with >= 1 f and >= 1 p,
SPLIT = max over 72 cut points of (share of its f inside a half-circle) - (share of its p inside that same half).
TOTAL = sum of SPLIT over such rings. Null: f/p labels permuted among the ring's f+p positions, 10,000 times.
Known answers on the same rings (same counts, synthetic positions): PERFECT split (all f in one half, all p in the other),
80% split (each letter on its side with probability 0.8), RANDOM (uniform). 200 replicates each.
Validity: PERFECT p < 0.01 in >= 90% of replicates and RANDOM p < 0.01 in <= 5%.
  SPLIT ACROSS THE BOOK  Voynich p < 0.01
  WEAK                   0.01 <= p < 0.05
  NO SPLIT               p >= 0.05
No Bayes factor. Unscored: per-ring SPLIT; whether f sits before p in reading order (as on f57v).
Run: .venv/bin/python experiments/e109_fp_halves.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED = 109109
OUT = ROOT / "experiments/results/e109.json"
CUTS = np.linspace(0, 1, 72, endpoint=False)


def split(pf, pp):
    pf, pp = np.array(pf), np.array(pp)
    best = 0.0
    for th in CUTS:
        a = (((pf - th) % 1) < 0.5).mean() - (((pp - th) % 1) < 0.5).mean()
        best = max(best, a)
    return float(best)


def total(rings):
    return sum(split(f, p) for f, p in rings)


def perm_p(rings, rng, n):
    s0 = total(rings); ge = 0
    for _ in range(n):
        rr = []
        for f, p in rings:
            a = f + p; rng.shuffle(a); rr.append((a[:len(f)], a[len(f):]))
        ge += total(rr) >= s0 - 1e-12
    return s0, (ge + 1) / (n + 1)


def load():
    _, zl = parse(); L = set(locked_test_leaves(zl))
    R, leaf = defaultdict(list), {}
    for t in zl:
        if t.mode == "circle" and t.eva and t.is_clean:
            R[(t.folio, t.line_no)].append(t.eva); leaf[(t.folio, t.line_no)] = t.leaf
    rings = {}
    for k, toks in R.items():
        if leaf[k] in L or k[0] == "f57v":
            continue
        s = "".join(toks); n = len(s)
        pf = [(i + 0.5) / n for i, ch in enumerate(s) if ch == "f"]
        pp = [(i + 0.5) / n for i, ch in enumerate(s) if ch == "p"]
        if pf and pp:
            rings[f"{k[0]}.{k[1]}"] = (pf, pp)
    return rings, sorted(L)


def synth(counts, kind, rng):
    out = []
    for nf, np_ in counts:
        if kind == "random":
            out.append(([rng.random() for _ in range(nf)], [rng.random() for _ in range(np_)]))
        else:
            q = 1.0 if kind == "perfect" else 0.8; o = rng.random()
            side = lambda own: ((o + (0 if own else 0.5) + rng.random() * 0.5) % 1)
            out.append(([side(rng.random() < q) for _ in range(nf)], [side(rng.random() >= q) for _ in range(np_)]))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    rng = random.Random(SEED)
    rings, locked = load(); counts = [(len(f), len(p)) for f, p in rings.values()]
    nrep, nperm = (20, 300) if a.smoke else (200, 2000)
    ka = {}
    for kind in ("perfect", "eighty", "random"):
        ps = [perm_p(synth(counts, kind, rng), rng, nperm)[1] for _ in range(nrep)]
        ka[kind] = {"share_p_lt_0.01": float(np.mean([p < 0.01 for p in ps])), "median_p": float(np.median(ps))}
        print(kind, ka[kind], flush=True)
    valid = ka["perfect"]["share_p_lt_0.01"] >= 0.9 and ka["random"]["share_p_lt_0.01"] <= 0.05
    res = {"experiment": "E109", "seed": SEED, "rings": list(rings), "counts": counts, "known_answers": ka, "valid": bool(valid),
           "locked_test_excluded": locked}
    print("rings", len(rings), "counts", counts, "VALID", valid)
    if not a.smoke:
        s0, p = perm_p(list(rings.values()), rng, 10000)
        per = {k: split(f, pp) for k, (f, pp) in rings.items()}
        order = {k: float(np.mean(pp) - np.mean(f)) for k, (f, pp) in rings.items()}
        v = ("SPLIT ACROSS THE BOOK" if p < 0.01 else ("WEAK" if p < 0.05 else "NO SPLIT")) if valid else "VOID"
        res.update(total=s0, p=p, per_ring=per, p_minus_f_mean_position=order, verdict=v)
        print(f"VOYNICH TOTAL {s0:.3f} p {p:.4f} -> {v}\nper ring {per}\nmean position p - f {order}")
    OUT.with_name("e109_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
