"""E045: does HUMAN-written gibberish avoid putting a word next to an identical word (C21)? See reports/E045_PREREG.md.
Data: Gaskell & Bowern (2022), github.com/danielgaskell/voynich @ d076a7d0: 38 gibberish transcriptions (human
volunteers) and 72 meaningful texts (modern, historical, conlang), all with their own line breaks.
AS with the exact expectation: per line of length L with word counts n_w, expected identical neighbour pairs under a
random order of that line's words E = sum_w n_w (n_w - 1) / L; O = observed identical neighbour pairs; AS = sum O /
sum E. Lines of < 2 words and separator lines (only _ or -) are skipped; words = whitespace tokens, lowercased.
Gibberish: pooled over writers, 95% interval by resampling writers (2,000 draws, seed 45045).
Meaningful: per text (whole text), and pooled.
Voynich: Currier A and Currier B (raw EVA, clean tokens, own lines), same formula.
Run: .venv/bin/python -I experiments/e045_human_gibberish.py GASKELL_UNZIPPED_DIR
"""
from __future__ import annotations

import glob, hashlib, json, random, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402

SEED, BOOT = 45045, 2000
OUT = ROOT / "experiments/results/e045.json"


def file_lines(f):
    out = []
    for l in Path(f).read_text(encoding="utf-8", errors="ignore").lower().splitlines():
        w = l.split()
        if len(w) >= 2 and not set(l.strip()) <= set("_-"):
            out.append(w)
    return out


def OE(lines):
    o = sum(a == b for l in lines for a, b in zip(l, l[1:]))
    e = sum(sum(c * (c - 1) for c in Counter(l).values()) / len(l) for l in lines if len(l) >= 2)
    return o, e


def main():
    d = Path(sys.argv[1]); rng = random.Random(SEED)
    lines, cur, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines]
    V = {}
    for t in ("A", "B"):
        o, e = OE([l for l, c in zip(vl, cur) if c == t and len(l) >= 2]); V[t] = {"O": o, "E": e, "AS": o / e}
    gib = {Path(f).name: OE(file_lines(f)) for f in sorted(glob.glob(str(d / "gib/*.txt")))}
    mean = {Path(f).name: OE(file_lines(f)) for f in sorted(glob.glob(str(d / "mean/texts/*.txt")))}
    sha = hashlib.sha256(b"".join(Path(f).read_bytes() for f in sorted(glob.glob(str(d / "gib/*.txt"))))).hexdigest()
    go = sum(o for o, _ in gib.values()); ge = sum(e for _, e in gib.values())
    names = list(gib)
    boot = []
    for _ in range(BOOT):
        s = [gib[rng.choice(names)] for _ in names]
        boot.append(sum(o for o, _ in s) / max(1e-9, sum(e for _, e in s)))
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    per = {n: {"O": o, "E": e, "AS": o / e if e else None} for n, (o, e) in mean.items()}
    mas = [v["AS"] for v in per.values() if v["AS"] is not None and v["E"] >= 5]
    share085 = float(np.mean([a >= 0.85 for a in mas]))
    mo = sum(o for o, _ in mean.values()); me = sum(e for _, e in mean.values())
    vA = V["A"]["AS"]
    if lo <= vA <= hi and share085 < 0.05:
        verdict, bf = "HUMAN GIBBERISH LIKE VOYNICH", {"M": 3.0}
    elif hi < 0.75:
        verdict, bf = "HUMAN GIBBERISH AVOIDS ADJACENCY", {"M": 1 / 3}
    else:
        verdict, bf = "INCONCLUSIVE", {}
    print("Voynich", {t: {k: round(v[k], 2) for k in v} for t, v in V.items()})
    print(f"gibberish pooled AS {go / ge:.2f} (O {go}, E {ge:.1f}), 95% {lo:.2f}-{hi:.2f}; writers {len(gib)}")
    print(f"meaningful pooled AS {mo / me:.2f}; per-text (E>=5, n={len(mas)}) median {np.median(mas):.2f}, max {max(mas):.2f}, share >= 0.85: {share085:.2f}")
    for n, v in sorted(per.items(), key=lambda x: -(x[1]["AS"] or 0))[:12]:
        print(f"   {v['AS'] if v['AS'] is None else round(v['AS'], 2)}  E {v['E']:.1f}  {n[:70]}")
    print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E045", "voynich": V, "gibberish": {"pooled_AS": go / ge, "O": go, "E": ge,
                               "ci95": [lo, hi], "per_writer": {n: list(v) for n, v in gib.items()}, "sha256": sha},
                               "meaningful": {"pooled_AS": mo / me, "per_text": per, "share_ge_085_E5": share085},
                               "verdict": verdict, "bayes_factors": bf, "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
