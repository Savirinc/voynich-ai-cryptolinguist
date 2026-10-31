"""E106b: standing rule 8 seed check for E106 (Voynich z +2.21, 0.21 sd from the z = 2 boundary). The locked E106
measure() is reused unchanged with 10 fresh bootstrap seeds; >= 8 of 10 must give z > 2 for DECORATIVE to stand.
Run: .venv/bin/python experiments/e106b_seed_check.py"""
import json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import e106_gallows_capitals as G
vl, para, _ = G.voynich()
zs = [G.measure(vl, para, random.Random(G.SEED + 1000 + s))["z"] for s in range(10)]
ok = sum(z > 2 for z in zs)
out = {"z": zs, "n_above_2": ok, "stands": ok >= 8}
(ROOT / "experiments/results/e106b.json").write_text(json.dumps(out, indent=1))
print(" ".join(f"{z:+.2f}" for z in zs), "| above 2:", ok, "/10 | DECORATIVE stands:", ok >= 8)
