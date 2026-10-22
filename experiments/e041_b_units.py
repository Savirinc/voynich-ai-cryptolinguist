"""E041: is Currier B back inside the simple-syllable range when qo and dy are read as single signs (E024's S3)?
See reports/E041_PREREG.md. Cleaned inventory N1 (E040). Texts: Currier A, Currier B (all lines), and B on 10 runs of
consecutive lines of A's token count (seed 41041). Segmentations S2 (as E040) and S3 (= S2 + qo, dy), E024 code.
Run: caffeinate -ims .venv/bin/python experiments/e041_b_units.py
"""
from __future__ import annotations

import json, random, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e024_atoms as A  # noqa: E402
from e040_clean_profile import n1  # noqa: E402

SEED, DRAWS = 41041, 10
OUT = ROOT / "experiments/results/e041.json"
E027 = json.loads((ROOT / "experiments/results/e027.json").read_text())
RS, SD = E027["range_simple"], E027["sd33"]
SIMPLE = {t: x for t, x in E027["texts"].items() if t.split("/")[0] in ("haw1868", "ton", "mri2012", "vie1934", "cmn-cu89s")}
K = ("h1", "h2", "L")


def unit_metrics(words, seg):
    m = A.metrics([A.segment(w, A.SEGS[seg]) for w in words])
    d = {t: float(np.sqrt(sum(((m[k] - x[k]) / SD[k]) ** 2 for k in K))) for t, x in SIMPLE.items()}
    return {**{k: m[k] for k in K}, "inside": {k: bool(RS[k][0] <= m[k] <= RS[k][1]) for k in K},
            "INSIDE": all(RS[k][0] <= m[k] <= RS[k][1] for k in K), "nearest": min(d, key=d.get), "dist": min(d.values())}


def main():
    rng = random.Random(SEED)
    lines, cur, _, locked = E.voynich_lines()
    clean = [[n1(w) for w in l if w] for l in lines]
    Al = [l for l, c in zip(clean, cur) if l and c == "A"]; Bl = [l for l, c in zip(clean, cur) if l and c == "B"]
    nA = sum(len(l) for l in Al)
    res = {}
    for seg in ("S2", "S3"):
        res[f"A/{seg}"] = unit_metrics([w for l in Al for w in l], seg)
        res[f"B/{seg}"] = unit_metrics([w for l in Bl for w in l], seg)
        runs = []
        for _ in range(DRAWS):
            s = rng.randrange(len(Bl)); sel, k, i = [], 0, s
            while k < nA:
                sel.append(Bl[i % len(Bl)]); k += len(Bl[i % len(Bl)]); i += 1
            runs.append(unit_metrics([w for l in sel for w in l], seg))
        res[f"B(A-size)/{seg}"] = {**{k: float(np.mean([r[k] for r in runs])) for k in K},
                                   "INSIDE_share": float(np.mean([r["INSIDE"] for r in runs]))}
        for name in ("A", "B", "B(A-size)"):
            r = res[f"{name}/{seg}"]
            print(f"{name:9s} {seg} " + " ".join(f"{k} {r[k]:.3f}" for k in K)
                  + (f" INSIDE {r['INSIDE']} nearest {r['nearest']} ({r['dist']:.2f})" if "INSIDE" in r else f" inside in {r['INSIDE_share']:.0%} of runs"), flush=True)
    b = res["B/S3"]["INSIDE"]
    res["verdict"] = "B INSIDE AT S3: step 2 uses A and B" if b else "B STILL OUTSIDE: step 2 uses A; B reported separately"
    res["range_simple"] = RS; res["locked_test_excluded"] = locked
    print("VERDICT:", res["verdict"])
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
