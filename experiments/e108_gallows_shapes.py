"""E108 (Arham): do the scribes draw gallows differently, and are gallows at word starts drawn larger (calligraphy)?
See reports/E108_PREREG.md.

Stage 'detect': on 37 allowed full-resolution pages (data/external/e108_page_list.txt; no LOCKED_TEST leaf, no f102,
single-page canvases), ink is found with a page-adaptive threshold and connected components; a GALLOWS CANDIDATE is a
component 1.8-9 x-heights tall, 0.4-5 wide, sitting on the baseline of >= 3 letter-sized neighbours and rising >= 2.2
x-heights above that baseline. Up to 40 candidates per page are sampled (seed 108108). For each: crop, features and
position class are stored. All crops are shuffled across pages into numbered 8x6 grids for blind labelling.
Stage 'analyze' (after labels exist in reports/data/e108_labels.csv): see the prereg.
Run: .venv/bin/python -I experiments/e108_gallows_shapes.py detect | analyze
"""
from __future__ import annotations

import csv, json, random, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "data/external/beinecke_hi_e108"
WORK = ROOT / "data/external/e108_work"
LIST = ROOT / "data/external/e108_page_list.txt"
LABELS = ROOT / "reports/data/e108_labels.csv"
OUT = ROOT / "experiments/results/e108.json"
SEED, PER_PAGE, CELL, COLS, ROWS = 108108, 40, 120, 8, 6
LOCKED = {"1", "8", "9", "30", "35", "38", "51", "52", "56", "75", "86", "87", "102", "105", "114"}


def otsu(x):
    h, e = np.histogram(x, bins=256); c = (e[:-1] + e[1:]) / 2; w = np.cumsum(h); m = np.cumsum(h * c)
    wt, mt = w[-1], m[-1]; best, t = -1, c[0]
    for i in range(1, 255):
        if w[i] == 0 or w[i] == wt:
            continue
        mb = m[i] / w[i]; mf = (mt - m[i]) / (wt - w[i]); v = w[i] * (wt - w[i]) * (mb - mf) ** 2
        if v > best:
            best, t = v, c[i]
    return t


def components(path):
    im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(float)
    gray = a.mean(axis=2)
    bg = nd.median_filter(gray[::4, ::4], size=25); bg = np.kron(bg, np.ones((4, 4)))[:gray.shape[0], :gray.shape[1]]
    sat = a.max(axis=2) - a.min(axis=2); diff = bg - gray
    t = max(18.0, otsu(diff[diff > 8]))
    ink = (diff > t) & (sat < 100)
    ink = nd.binary_opening(nd.binary_closing(ink, np.ones((3, 3))), np.ones((2, 2)))
    lab, _ = nd.label(ink, structure=np.ones((3, 3)))
    comps = []
    for i, s in enumerate(nd.find_objects(lab)):
        h = s[0].stop - s[0].start; w = s[1].stop - s[1].start; area = int((lab[s] == i + 1).sum())
        if area >= 15:
            comps.append(dict(id=i + 1, y0=s[0].start, y1=s[0].stop, x0=s[1].start, x1=s[1].stop, h=h, w=w, area=area))
    return im, lab, comps


def candidates(comps):
    small = [c for c in comps if 8 <= c["h"] <= 40 and 4 <= c["w"] <= 60]
    h0 = float(np.median([c["h"] for c in small]))
    out = []
    for c in comps:
        if not (1.8 * h0 <= c["h"] <= 9 * h0 and 0.4 * h0 <= c["w"] <= 5 * h0):
            continue
        nb = [d for d in small if d is not c and 0.6 * h0 <= d["h"] <= 1.4 * h0 and d["y1"] > c["y0"] + c["h"] * 0.4
              and d["y1"] <= c["y1"] + 0.8 * h0 and min(abs(d["x0"] - c["x1"]), abs(c["x0"] - d["x1"])) <= 5 * h0]
        if len(nb) < 3:
            continue
        base = float(np.median([d["y1"] for d in nb])); xtop = float(np.median([d["y0"] for d in nb])); xh = max(base - xtop, 1.0)
        if abs(c["y1"] - base) > 0.6 * xh:
            continue
        asc = (base - c["y0"]) / xh
        if asc >= 2.2:
            out.append(dict(c, xh=xh, base=base, xtop=xtop, ascent=asc))
    return out


def features(c, lab):
    m = lab[c["y0"]:c["y1"], c["x0"]:c["x1"]] == c["id"]
    ys, xs = np.nonzero(m)
    cov = np.cov(np.vstack([xs - xs.mean(), ys - ys.mean()]))
    ev, evec = np.linalg.eigh(cov); v = evec[:, np.argmax(ev)]
    slant = float(np.degrees(np.arctan2(v[0], v[1] if v[1] != 0 else 1e-9)))
    slant = (slant + 90) % 180 - 90
    holes_lab, nh = nd.label(~m)
    border = set(np.unique(np.concatenate([holes_lab[0], holes_lab[-1], holes_lab[:, 0], holes_lab[:, -1]])))
    holes = sum(1 for k in range(1, nh + 1) if k not in border and (holes_lab == k).sum() >= 6)
    return {"ascent": c["ascent"], "relwidth": c["w"] / c["xh"], "slant": slant, "fill": float(m.sum() / m.size), "holes": holes}


def position(c, comps):
    left = [d for d in comps if d["x1"] <= c["x0"] + 2 and d["id"] != c["id"] and d["y1"] > c["xtop"] and d["y0"] < c["base"]
            and c["x0"] - d["x1"] <= 6 * c["xh"] and d["h"] <= 9 * c["xh"]]
    if not left:
        return "line-initial", None
    gap = float(c["x0"] - max(d["x1"] for d in left)) / c["xh"]
    return ("word-initial" if gap >= 0.5 else "internal"), gap


def detect():
    WORK.mkdir(parents=True, exist_ok=True); rng = random.Random(SEED); recs = []
    for line in LIST.read_text().split("\n"):
        if not line.strip():
            continue
        hand, folio, sec, _ = line.split()
        leaf = "".join(ch for ch in folio if ch.isdigit())
        assert leaf not in LOCKED, folio
        im, lab, comps = components(IMG / f"{folio}.jpg"); cs = candidates(comps)
        pick = rng.sample(cs, min(PER_PAGE, len(cs)))
        for c in pick:
            pos, gap = position(c, comps)
            pad = int(0.5 * c["xh"])
            crop = im.crop((max(0, c["x0"] - pad), max(0, c["y0"] - pad), c["x1"] + pad, c["y1"] + pad))
            cid = f"{folio}_{c['id']}"
            crop.save(WORK / f"{cid}.png")
            recs.append(dict(cid=cid, folio=folio, hand=hand, sec=sec, pos=pos, gap=gap, box=[c["x0"], c["y0"], c["x1"], c["y1"]],
                             **features(c, lab)))
        print(folio, len(cs), len(pick), flush=True)
    order = list(range(len(recs))); rng.shuffle(order)
    per = COLS * ROWS; grids = []
    for gi in range(0, len(order), per):
        g = Image.new("RGB", (COLS * CELL, ROWS * (CELL + 18)), "white"); d = ImageDraw.Draw(g)
        for k, ri in enumerate(order[gi:gi + per]):
            r = recs[ri]; cr = Image.open(WORK / f"{r['cid']}.png"); cr.thumbnail((CELL - 6, CELL - 6))
            x, y = (k % COLS) * CELL, (k // COLS) * (CELL + 18)
            g.paste(cr, (x + 3, y + 18)); d.text((x + 4, y + 2), str(k + 1), fill="red")
            r["grid"], r["cell"] = gi // per + 1, k + 1
        g.save(WORK / f"grid_{gi // per + 1:02d}.png"); grids.append(gi // per + 1)
    (WORK / "records.json").write_text(json.dumps(recs))
    print("records", len(recs), "grids", len(grids))


def loo_accuracy(X, y):
    ok = 0
    for i in range(len(y)):
        tr = [j for j in range(len(y)) if j != i]
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9; Z = (X - mu) / sd
        cents = {c: Z[[j for j in tr if y[j] == c]].mean(0) for c in set(y[j] for j in tr)}
        ok += min(cents, key=lambda c: ((Z[i] - cents[c]) ** 2).sum()) == y[i]
    return ok / len(y)


def scribe_test(pages, rng, nperm=1000):
    F = ["ascent", "relwidth", "slant", "fill", "holes"]
    X = np.array([[p[f] for f in F] for p in pages]); y = [p["hand"] for p in pages]
    acc = loo_accuracy(X, y); ge = 0
    for _ in range(nperm):
        yy = y[:]; rng.shuffle(yy); ge += loo_accuracy(X, yy) >= acc
    return {"accuracy": acc, "p": (ge + 1) / (nperm + 1), "n_pages": len(y), "chance": max(y.count(h) for h in set(y)) / len(y)}


def analyze():
    rng = random.Random(SEED + 1)
    recs = json.loads((WORK / "records.json").read_text())
    lab = {(int(r["grid"]), int(r["cell"])): r["label"].strip().upper() for r in csv.DictReader(LABELS.open())}
    for r in recs:
        r["label"] = lab.get((r["grid"], r["cell"]), "?")
    cnt = {k: sum(r["label"] == k for r in recs) for k in "GBMNU?"}
    G = [r for r in recs if r["label"] == "G"]
    F = ["ascent", "relwidth", "slant", "fill", "holes"]
    pages = []
    for f in sorted({r["folio"] for r in G}):
        rs = [r for r in G if r["folio"] == f]
        if len(rs) >= 5:
            pages.append({"folio": f, "hand": rs[0]["hand"], "sec": rs[0]["sec"], "n": len(rs), **{k: float(np.mean([r[k] for r in rs])) for k in F}})
    per_scribe = {h: {"pages": sum(p["hand"] == h for p in pages), "gallows": sum(r["hand"] == h for r in G)} for h in "1235"}
    valid = all(v["pages"] >= 4 and v["gallows"] >= 15 for v in per_scribe.values())
    res = {"experiment": "E108", "label_counts": cnt, "per_scribe": per_scribe, "valid_scribe": valid, "pages": pages}
    res["scribe_all"] = scribe_test(pages, rng)
    herb = [p for p in pages if p["sec"] == "H"]
    res["scribe_herbal"] = scribe_test(herb, rng) if len({p["hand"] for p in herb}) >= 2 else None
    pa = res["scribe_all"]["p"]
    res["verdict_scribe"] = ("SCRIBES DIFFER" if pa < 0.01 else ("NO DIFFERENCE SHOWN" if pa >= 0.05 else "WEAK")) if valid else "VOID"
    res["feature_means_by_scribe"] = {h: {k: float(np.mean([r[k] for r in G if r["hand"] == h])) for k in F} for h in "1235" if any(r["hand"] == h for r in G)}
    diffs = {"ascent": [], "relwidth": []}; used = []
    for f in sorted({r["folio"] for r in G}):
        wi = [r for r in G if r["folio"] == f and r["pos"] == "word-initial"]; it = [r for r in G if r["folio"] == f and r["pos"] == "internal"]
        if len(wi) >= 3 and len(it) >= 3:
            used.append(f)
            for k in diffs:
                diffs[k].append(np.mean([r[k] for r in wi]) / np.mean([r[k] for r in it]) - 1)
    pos = {"pages": len(used)}
    dec = False
    for k, v in diffs.items():
        if len(v) >= 8:
            p = float(wilcoxon(v, alternative="greater").pvalue); med = float(np.median(v))
            pos[k] = {"median_rel_increase": med, "p": p}
            dec |= (p < 0.005 and med >= 0.10)
    res["position"] = pos
    res["verdict_position"] = ("DECORATED AT WORD START" if dec else "NOT LARGER AT WORD START") if len(used) >= 8 else "VOID"
    res["line_initial_vs_internal"] = {k: float(np.mean([r[k] for r in G if r["pos"] == "line-initial"]) / np.mean([r[k] for r in G if r["pos"] == "internal"]) - 1)
                                      for k in ("ascent", "relwidth")} if any(r["pos"] == "line-initial" for r in G) else None
    B = [r for r in recs if r["label"] == "B"]
    res["bench_vs_plain"] = {"n_bench": len(B), **{k: (float(np.mean([r[k] for r in B])) if B else None, float(np.mean([r[k] for r in G]))) for k in ("ascent", "relwidth", "holes")}}
    OUT.write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "pages"}, indent=1, default=str))


if __name__ == "__main__":
    {"detect": detect, "analyze": analyze}[sys.argv[1]]()
