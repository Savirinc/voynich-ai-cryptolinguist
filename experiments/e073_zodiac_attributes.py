"""E073: do zodiac figures with the same label look alike? See reports/E073_PREREG.md.
Run: .venv/bin/python experiments/e073_zodiac_attributes.py
"""
from __future__ import annotations

import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RES = ROOT / "experiments/results"
ANN, CHK, OUT = RES / "e073_annotations.json", RES / "e073_annotations_check.json", RES / "e073.json"
PAGES = ["f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v"]
FEATS = ["BARREL", "CLOTHED", "HEAD", "HANDSTAR", "FACING"]
SEEDS = list(range(73001, 73011))
SHUF = 2000
Z_BAR = 3.0


def log(*a):
    print(*a, flush=True)


def ring_of(head):
    h = (head or "").lower()
    if "top" in h:
        return "top"
    if "outer" in h:
        return "outer"
    if "inner" in h:
        return "inner"
    if "second" in h or "middle" in h or "petersen" in h:
        return "middle"
    return None


def clean(s):
    s = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", s)
    s = re.sub(r"<[^>]*>", "", s)
    return re.sub(r"[{}.,\s]", "", s)


def labels():
    from vcl.corpus.ivtff import read_docx_lines
    rows, cur, head = [], None, None
    for l in read_docx_lines():
        m = re.match(r"^<(f\w+?)>", l)
        if m and not re.match(r"^<f\w+?\.", l):
            cur, head = m.group(1), None; continue
        if cur not in PAGES:
            continue
        if l.startswith("#"):
            if ring_of(l[1:]) and any(k in l.lower() for k in ("label", "ring", "row", "band", "petersen")):
                head = l[1:].strip()
            continue
        m = re.match(r"^<(f\w+?)\.(\d+),[@&+=*~]?(\w+)>\s*(?:<!([^>]*)>)?(.*)$", l)
        if m and m.group(3).startswith("L"):
            w = clean(m.group(5)); ck = m.group(4)
            if not ck or not re.match(r"^\d\d:\d\d$", ck) or "?" in w or not w:
                continue
            rows.append({"page": cur, "ring": ring_of(head), "clock": ck, "label": w, "line": int(m.group(2))})
    return rows


def angle(ck):
    h, m = map(int, ck.split(":"))
    return ((h % 12) * 30 + m * 0.5) % 360


def adist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def join(ann, labs):
    """Returns list of (figure, label_row, angular error) and stats."""
    out, nlab = [], len(labs)
    groups = defaultdict(lambda: ([], []))
    for f in ann:
        groups[(f["page"], f["ring"])][0].append(f)
    for r in labs:
        groups[(r["page"], r["ring"])][1].append(r)
    for key, (F, L) in groups.items():
        if not F or not L:
            continue
        F = sorted(F, key=lambda f: angle(f["clock"])); L = sorted(L, key=lambda r: angle(r["clock"]))
        if len(F) == len(L):
            n = len(F)
            best = min(range(n), key=lambda s: sum(adist(angle(F[i]["clock"]), angle(L[(i + s) % n]["clock"])) for i in range(n)))
            pairs = [(F[i], L[(i + best) % n]) for i in range(n)]
        else:
            C = np.array([[adist(angle(f["clock"]), angle(r["clock"])) for r in L] for f in F])
            ri, ci = linear_sum_assignment(C)
            pairs = [(F[i], L[j]) for i, j in zip(ri, ci)]
        for f, r in pairs:
            e = adist(angle(f["clock"]), angle(r["clock"]))
            if e <= 45:
                out.append((f, r, e))
    return out, {"labels": nlab, "joined": len(out), "share": len(out) / nlab,
                 "mean_err": float(np.mean([e for _, _, e in out])) if out else None}


def kappa(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x != "?" and y != "?"]
    if len(pairs) < 5:
        return None
    po = sum(x == y for x, y in pairs) / len(pairs)
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / len(pairs) ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def sim(f, g, feats):
    eq = [f[k] == g[k] for k in feats if f[k] != "?" and g[k] != "?"]
    return sum(eq) / len(eq) if eq else None


def pair_sim(J, labfun, feats, cross_only=False):
    by = defaultdict(list)
    for f, r, _ in J:
        k = labfun(r)
        if k is not None:
            by[k].append(f)
    vals = []
    for fs in by.values():
        for i in range(len(fs)):
            for j in range(i + 1, len(fs)):
                if cross_only and fs[i]["page"] == fs[j]["page"]:
                    continue
                s = sim(fs[i], fs[j], feats)
                if s is not None:
                    vals.append(s)
    return (float(np.mean(vals)) if vals else float("nan")), len(vals)


def perm_z(J, labfun, feats, cross_only=False, seeds=SEEDS, shuf=SHUF):
    obs, n = pair_sim(J, labfun, feats, cross_only)
    grp = defaultdict(list)
    for idx, (f, r, e) in enumerate(J):
        grp[(f["page"], f["ring"])].append(idx)
    zs = []
    for sd in seeds:
        rng = random.Random(sd); vals = []
        for _ in range(shuf):
            rs = [r for _, r, _ in J]
            for idxs in grp.values():
                sub = [rs[i] for i in idxs]; rng.shuffle(sub)
                for i, r in zip(idxs, sub):
                    rs[i] = r
            vals.append(pair_sim([(J[i][0], rs[i], 0) for i in range(len(J))], labfun, feats, cross_only)[0])
        vals = [v for v in vals if not math.isnan(v)]
        mu, sg = float(np.mean(vals)), float(np.std(vals, ddof=1))
        zs.append((obs - mu) / sg if sg > 0 else 0.0)
    return {"SIM": obs, "pairs": n, "z_median": float(np.median(zs)), "z": zs,
            "above": sum(z > Z_BAR for z in zs), "within": sum(z <= Z_BAR for z in zs)}


def remainder(r):
    m = re.match(r"^o[tkpf](.+)$", r["label"])
    return m.group(1) if m else None


def known_answer(ann):
    calls, ok = [], 0
    g = defaultdict(list)
    for f in ann:
        g[(f["page"], f["ring"])].append(f)
    for f in g[("f72r1", "inner")]:
        calls.append(f["BARREL"] == 1)
    for f in g[("f72r1", "outer")]:
        calls.append(f["BARREL"] == 0)
    for f in g[("f71v", "outer")]:
        calls.append(f["BARREL"] == 1)
    for f in g[("f70v2", "inner")]:
        calls.append(f["BARREL"] == 1)
    inner71v = g[("f71v", "inner")]
    clothed = sum(f["CLOTHED"] == 1 for f in inner71v); naked = sum(f["CLOTHED"] == 0 for f in inner71v)
    calls += [True] * min(clothed, 4) + [False] * max(0, 4 - clothed)
    calls += [True] * min(naked, 1) + [False] * max(0, 1 - naked)
    return sum(calls) / len(calls) if calls else 0.0, len(calls)


def main():
    t0 = __import__("time").time()
    ann = json.loads(ANN.read_text()); labs = labels()
    res = {"experiment": "E073", "n_figures": len(ann), "n_labels": len(labs)}
    log(f"figures {len(ann)}, labels {len(labs)}; per page {Counter(f['page'] for f in ann)}")
    ka, nka = known_answer(ann); res["known_answer"] = {"agreement": ka, "calls": nka}
    log(f"[check 1] transcriber-note agreement {ka:.3f} on {nka} calls (bar 0.90)")
    feats = list(FEATS); kap = {}
    if CHK.exists():
        chk = json.loads(CHK.read_text())
        J2 = []
        for c in chk:
            cand = [f for f in ann if f["page"] == c["page"] and f["ring"] == c["ring"]]
            if cand:
                f = min(cand, key=lambda f: adist(angle(f["clock"]), angle(c["clock"])))
                if adist(angle(f["clock"]), angle(c["clock"])) <= 20:
                    J2.append((f, c))
        for k in FEATS:
            kap[k] = kappa([str(f[k]) for f, _ in J2], [str(c[k]) for _, c in J2])
        feats = [k for k in FEATS if kap[k] is not None and kap[k] >= 0.5]
        res["reliability"] = {"matched": len(J2), "kappa": kap, "kept": feats}
        log(f"[check 2] second annotator matched {len(J2)} figures; kappa {kap}; kept {feats}")
    else:
        res["reliability"] = None; log("[check 2] no second annotation file"); feats = []
    J, js = join(ann, labs); res["join"] = js
    log(f"[check 3] joined {js['joined']}/{js['labels']} ({js['share']:.2f}), mean angular error {js['mean_err']:.1f} deg")
    valid = ka >= 0.90 and len(feats) >= 3 and js["share"] >= 0.85 and js["mean_err"] <= 20
    res["validated"] = valid
    log(f"[validity] {'VALID' if valid else 'VOID'}")
    use = feats if len(feats) >= 3 else FEATS
    prim = perm_z(J, lambda r: r["label"], use); res["same_label"] = prim
    log(f"[primary] same-label pairs {prim['pairs']} SIM {prim['SIM']:.3f} z {prim['z_median']:+.2f} ({prim['above']}/10 > 3)")
    cross = perm_z(J, lambda r: r["label"], use, cross_only=True, seeds=SEEDS[:3]); res["same_label_cross_page"] = cross
    rem = perm_z(J, remainder, use, seeds=SEEDS[:3]); res["same_remainder"] = rem
    log(f"[reported] cross-page same-label pairs {cross['pairs']} SIM {cross['SIM']:.3f} z {cross['z_median']:+.2f}")
    log(f"[reported] same-remainder pairs {rem['pairs']} SIM {rem['SIM']:.3f} z {rem['z_median']:+.2f}")
    per = {}
    for k in use:
        per[k] = perm_z(J, lambda r: r["label"], [k], seeds=SEEDS[:3])
        log(f"[reported] feature {k}: SIM {per[k]['SIM']:.3f} z {per[k]['z_median']:+.2f} ({per[k]['pairs']} pairs)")
    res["per_feature"] = per
    res["feature_counts"] = {k: dict(Counter(str(f[k]) for f in ann)) for k in FEATS}
    res["joined_pairs"] = [{"page": f["page"], "ring": f["ring"], "fig_clock": f["clock"], "lab_clock": r["clock"],
                            "label": r["label"], **{k: f[k] for k in FEATS}} for f, r, _ in J]
    if not valid:
        v, fct = "VOID", "none"
    elif prim["above"] >= 8:
        v, fct = "PICTURE LINK", "M x1/3"
    elif prim["within"] >= 8:
        v, fct = "NO LINK", "M x1.5"
    else:
        v, fct = "INCONCLUSIVE (seed rule)", "none"
    res.update(verdict=v, factor=fct, runtime_s=__import__("time").time() - t0)
    log(f"VERDICT {v} | factor {fct}")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
