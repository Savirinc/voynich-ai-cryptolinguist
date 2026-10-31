"""E108b: standing rule 8 seed check for E108's permutation p-values (all pages p 0.016, herbal p 0.00999, both near the
0.01 boundary). The locked scribe_test() is reused unchanged on the same page means with 10 fresh permutation seeds.
Run: .venv/bin/python -I experiments/e108b_seed_check.py"""
import importlib.util, json, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e108", ROOT / "experiments/e108_gallows_shapes.py")
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
res = json.loads((ROOT / "experiments/results/e108.json").read_text())
pages = res["pages"]; herb = [p for p in pages if p["sec"] == "H"]
out = {"all": [E.scribe_test(pages, random.Random(E.SEED + 500 + s))["p"] for s in range(10)],
       "herbal": [E.scribe_test(herb, random.Random(E.SEED + 600 + s))["p"] for s in range(10)]}
(ROOT / "experiments/results/e108b.json").write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(k, " ".join(f"{p:.3f}" for p in v), "| p<0.01:", sum(p < 0.01 for p in v), "| 0.01<=p<0.05:", sum(0.01 <= p < 0.05 for p in v))
