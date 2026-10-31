"""E109b: standing rule 8 seed check for E109 (p 0.041, near the 0.05 boundary). Locked load()/perm_p() reused unchanged,
10 fresh seeds x 10,000 permutations. Run: .venv/bin/python experiments/e109b_seed_check.py"""
import json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import e109_fp_halves as E
rings, _ = E.load()
ps = [E.perm_p(list(rings.values()), random.Random(E.SEED + 700 + s), 10000)[1] for s in range(10)]
(ROOT / "experiments/results/e109b.json").write_text(json.dumps({"p": ps}, indent=1))
print(" ".join(f"{p:.4f}" for p in ps), "| p<0.05:", sum(p < 0.05 for p in ps), "/10")
