"""E046: is C21 (no avoidance of identical neighbours, AS ~ 1) spread through the whole book, or concentrated in some
pages, scribes or sections? A measurement. See reports/E046_PREREG.md.
Voynich DEV prose, clean tokens (raw EVA), own lines; per line: folio, hand (Davis/ZL), quire, Currier.
AS = sum O / sum E with E = sum_w n_w (n_w - 1) / L per line (E045 formula).
Per scribe and per quire: AS with a 95% interval from resampling pages (2,000 draws, seed 46046).
Dispersion over pages: D = sum_p (O_p - AS_all E_p)^2 / (AS_all E_p) over pages with E_p > 0; null: O_p ~ Poisson(AS_all
E_p), 2,000 simulations; p-value one-sided. Concentration: share of all O from the 10% of pages with highest O - E,
against the same share in the simulations.
Run: .venv/bin/python -I experiments/e046_as_location.py
"""
from __future__ import annotations

import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED, BOOT = 46046, 2000
OUT = ROOT / "experiments/results/e046.json"


def oe(l):
    if len(l) < 2:
        return 0, 0.0
    return sum(a == b for a, b in zip(l, l[1:])), sum(c * (c - 1) for c in Counter(l).values()) / len(l)


def ci(pages, rng):
    keys = list(pages)
    b = []
    for _ in range(BOOT):
        s = [pages[rng.choice(keys)] for _ in keys]
        e = sum(x[1] for x in s)
        b.append(sum(x[0] for x in s) / e if e else np.nan)
    return [float(np.nanpercentile(b, 2.5)), float(np.nanpercentile(b, 97.5))]


def main():
    rng = random.Random(SEED); nrng = np.random.default_rng(SEED)
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L, meta = defaultdict(list), {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked and t.is_clean:
            L[(t.folio, t.line_no)].append(t.eva); meta[(t.folio, t.line_no)] = (t.folio, t.hand, t.quire, t.currier)
    page = defaultdict(lambda: [0, 0.0]); grp = {"hand": defaultdict(dict), "quire": defaultdict(dict)}
    for k, l in L.items():
        o, e = oe(l); f, h, q, c = meta[k]
        page[f][0] += o; page[f][1] += e
        for g, v in (("hand", h), ("quire", q)):
            grp[g][v].setdefault(f, [0, 0.0]); grp[g][v][f][0] += o; grp[g][v][f][1] += e
    O = sum(v[0] for v in page.values()); Eall = sum(v[1] for v in page.values()); A = O / Eall
    res = {"all": {"O": O, "E": Eall, "AS": A}}
    for g in ("hand", "quire"):
        res[g] = {}
        for v, pg in sorted(grp[g].items(), key=lambda x: str(x[0])):
            o = sum(x[0] for x in pg.values()); e = sum(x[1] for x in pg.values())
            if e >= 10:
                res[g][str(v)] = {"pages": len(pg), "O": o, "E": round(e, 1), "AS": o / e, "ci95": ci(pg, rng)}
    P = [(f, v[0], v[1]) for f, v in page.items() if v[1] > 0]
    lam = np.array([A * e for _, _, e in P]); obs = np.array([o for _, o, _ in P])
    D = float(np.sum((obs - lam) ** 2 / lam))
    sims = nrng.poisson(lam, size=(BOOT, len(lam)))
    Dn = np.sum((sims - lam) ** 2 / lam, axis=1)
    p = float((1 + np.sum(Dn >= D)) / (BOOT + 1))
    k = max(1, len(P) // 10)
    top = np.argsort(-(obs - lam))[:k]
    share = float(obs[top].sum() / obs.sum())
    sh_null = [float(s[np.argsort(-(s - lam))[:k]].sum() / max(1, s.sum())) for s in sims[:500]]
    res["dispersion"] = {"pages": len(P), "D": D, "p": p, "top10pct_share_of_O": share,
                         "top10pct_share_null_mean": float(np.mean(sh_null)), "top10pct_share_null_p95": float(np.percentile(sh_null, 95)),
                         "top_pages": [(P[i][0], int(obs[i]), round(float(lam[i] / A), 1)) for i in top]}
    conc = p < 0.01 and share >= 2 * float(np.mean(sh_null))
    hands_ok = all(v["AS"] >= 0.75 for v in res["hand"].values() if v["E"] >= 20)
    res["verdict"] = "CONCENTRATED" if conc else ("WIDESPREAD" if hands_ok else "UNEVEN (some scribe below 0.75)")
    print(f"all: AS {A:.2f} (O {O}, E {Eall:.1f})")
    for g in ("hand", "quire"):
        for v, r in res[g].items():
            print(f"  {g:5s} {v:3s} pages {r['pages']:3d} O {r['O']:4d} E {r['E']:6.1f} AS {r['AS']:.2f} [{r['ci95'][0]:.2f}-{r['ci95'][1]:.2f}]")
    d = res["dispersion"]
    print(f"dispersion over {d['pages']} pages: D {d['D']:.1f} p {d['p']:.4f}; top-10% pages hold {d['top10pct_share_of_O']:.2f} of repeats "
          f"(null mean {d['top10pct_share_null_mean']:.2f}, 95th {d['top10pct_share_null_p95']:.2f}); top pages {d['top_pages']}")
    print("VERDICT:", res["verdict"])
    res["locked_test_excluded"] = sorted(locked)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
