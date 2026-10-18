"""E023: power check for E022 on a real herbal (Culpeper). Pre-registered in reports/E023_PREREG.md.
Same statistic as E022: tf-idf (types on 2-15 entries) cosine of the virtues text vs share of matching visual
features (coded blind from descriptions only), Spearman over pairs >= 4 entries apart, 10,000 permutations.

Run: .venv/bin/python experiments/e023_herbal_power_check.py
"""
from __future__ import annotations

import hashlib, json, math, os, random, re, stat, sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from e022_plant_text_link import FEATS, vis_sim  # noqa: E402

PREREG = ROOT / "reports/E023_PREREG.md"
D = ROOT / "data/derived/e023"
OUT = ROOT / "experiments/results/e023.json"
N_PERM, MIN_GAP, DF_MAX, ALPHA, SEED = 10_000, 4, 15, 0.01, 23023


def run(codes, entries, field_fn):
    ids = [e["id"] for e in entries]
    n = len(ids)
    toks = [re.findall(r"[a-z]+", field_fn(e).lower()) for e in entries]
    df = Counter(w for t in toks for w in set(t))
    vocab = sorted(w for w, d in df.items() if 2 <= d <= DF_MAX)
    vi = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((n, len(vocab)))
    for i, t in enumerate(toks):
        for w, c in Counter(t).items():
            if w in vi:
                M[i, vi[w]] = c * math.log(n / df[w])
    nr = np.linalg.norm(M, axis=1); nr[nr == 0] = 1
    Mn = M / nr[:, None]
    Tm = Mn @ Mn.T
    Vm = np.array([[vis_sim(codes[p], codes[q]) for q in ids] for p in ids])
    I, J = map(np.array, zip(*[(i, j) for i in range(n) for j in range(i + 1, n) if j - i >= MIN_GAP]))
    tr = rankdata(Tm[I, J])

    def r_of(o):
        return float(np.corrcoef(rankdata(Vm[o[I], o[J]]), tr)[0, 1])
    obs = r_of(np.arange(n))
    rng = np.random.default_rng(SEED)
    ge = sum(r_of(rng.permutation(n)) >= obs for _ in range(N_PERM))
    return {"r": obs, "p": (ge + 1) / (N_PERM + 1), "n_pairs": len(I), "n_vocab": len(vocab)}


def main():
    cp = D / "visual_codes.json"
    if os.stat(cp).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
        sys.exit("visual codes must be locked read-only")
    codes = json.loads(cp.read_text())
    entries = json.loads((D / "culpeper_sample.json").read_text())
    prim = run(codes, entries, lambda e: e["virtues"])
    alt = run(codes, entries, lambda e: e["intro"] + " " + e["virtues"])
    res = {"experiment": "e023", "prereg_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest(),
           "codes_sha256": hashlib.sha256(cp.read_bytes()).hexdigest(), "primary_virtues": prim,
           "with_names": alt, "verdict": "POWER SHOWN" if prim["p"] < ALPHA else "NO POWER"}
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    from vcl.eval.ledger import append  # noqa: E402
    append([dict(experiment="E023", model="plant_visual_vs_text/culpeper", checkpoint_sha256=f"codes={res['codes_sha256'][:12]}",
                 split="positive_control_herbal", metric=m, value=round(v, 4), command=" ".join(sys.argv),
                 notes=res["verdict"]) for m, v in (("spearman_r_far", prim["r"]), ("perm_p_far", prim["p"]))])


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    main()
