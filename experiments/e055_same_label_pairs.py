"""E055: do pharmaceutical drawings that carry the SAME label look like the same plant? See reports/E055_PREREG.md.
Stage 'build': from the label->drawing maps (scratchpad/beinecke/map_*.json, made by vision sub-agents; DEV folios
only), form (a) all same-label pairs of located plant drawings, (b) 4 control pairs per same-label pair: one drawing
from each of the same two folios (or two from the same folio), labels different and not within edit distance 1,
seed 55055, (c) 6 identity pairs (one drawing cropped twice with different margins). Every crop has all mapped label
positions on that image blanked. Pair images are shuffled and named P01..; the key is written separately.
Stage 'score': reads two judges' scores (0-10) and computes the decision.
Run: .venv/bin/python -I experiments/e055_same_label_pairs.py build BEINECKE_DIR
     .venv/bin/python -I experiments/e055_same_label_pairs.py score BEINECKE_DIR JUDGE1.json JUDGE2.json
"""
from __future__ import annotations

import glob, json, random, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SEED, NCTRL, NID = 55055, 4, 6
OUT = Path(__file__).resolve().parents[1] / "experiments/results/e055.json"


def ed1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return a == b
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    s, l = (a, b) if len(a) < len(b) else (b, a)
    return any(l[:i] + l[i + 1:] == s for i in range(len(l)))


def load(B):
    items = []
    for f in sorted(glob.glob(str(B / "map_*.json"))):
        for x in json.load(open(f)):
            if x.get("kind") == "plant" and x.get("drawing_box") and x.get("confidence") in ("high", "medium", "low"):
                img = x["image"] if x["image"].startswith("..") else "hi/" + x["image"]
                x["img_path"] = str((B / "hi" / x["image"]) if not x["image"].startswith("..") else (B / "img/f88r.jpg"))
                items.append(x)
    return items


def crop(B, it, all_items, margin=0.06):
    im = Image.open(it["img_path"]).convert("RGB"); W, H = im.size
    d = ImageDraw.Draw(im); r = int(0.022 * W)
    for o in all_items:
        if o["img_path"] == it["img_path"] and o.get("label_xy"):
            x, y = o["label_xy"]; d.rectangle([x - 2 * r, y - r, x + 2 * r, y + r], fill=(236, 226, 205))
    x0, y0, x1, y1 = it["drawing_box"]; mx, my = margin * (x1 - x0), margin * (y1 - y0)
    c = im.crop((max(0, x0 - mx), max(0, y0 - my), min(W, x1 + mx), min(H, y1 + my)))
    c.thumbnail((600, 600)); return c


def pair_img(a, b):
    h = max(a.height, b.height); out = Image.new("RGB", (a.width + b.width + 30, h), (255, 255, 255))
    out.paste(a, (0, 0)); out.paste(b, (a.width + 30, 0)); return out


def build(B):
    rng = random.Random(SEED)
    items = load(B)
    same = [(i, j) for i in range(len(items)) for j in range(i + 1, len(items))
            if items[i]["label"] == items[j]["label"] and items[i]["drawing_box"] != items[j]["drawing_box"]]
    pairs = [("same", i, j) for i, j in same]
    for i, j in same:
        fa, fb = items[i]["folio"], items[j]["folio"]
        A = [k for k, x in enumerate(items) if x["folio"] == fa]; Bk = [k for k, x in enumerate(items) if x["folio"] == fb]
        n = 0
        while n < NCTRL:
            a, b = rng.choice(A), rng.choice(Bk)
            if a == b or items[a]["drawing_box"] == items[b]["drawing_box"] or ed1(items[a]["label"], items[b]["label"]):
                continue
            pairs.append(("control", a, b)); n += 1
    for k in rng.sample(range(len(items)), NID):
        pairs.append(("identity", k, k))
    rng.shuffle(pairs)
    od = B / "e055_pairs"; od.mkdir(exist_ok=True)
    key = {}
    for n, (kind, i, j) in enumerate(pairs, 1):
        a = crop(B, items[i], items); b = crop(B, items[j], items, margin=0.15 if kind == "identity" else 0.06)
        if kind == "identity":
            b = b.rotate(0); b = b.resize((int(b.width * 0.9), int(b.height * 0.9)))
        pid = f"P{n:02d}"; pair_img(a, b).save(od / f"{pid}.jpg", quality=88)
        key[pid] = {"kind": kind, "a": [items[i]["folio"], items[i]["n"], items[i]["label"], items[i]["confidence"]],
                    "b": [items[j]["folio"], items[j]["n"], items[j]["label"], items[j]["confidence"]]}
    (B / "e055_key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(pairs)} pairs written ({sum(p[0]=='same' for p in pairs)} same-label, {sum(p[0]=='control' for p in pairs)} control, {NID} identity)")


def score(B, j1, j2):
    key = json.loads((B / "e055_key.json").read_text())
    s1, s2 = json.loads(Path(j1).read_text()), json.loads(Path(j2).read_text())
    sc = {p: (float(s1[p]) + float(s2[p])) / 2 for p in key}
    grp = lambda k, ok=lambda v: True: [sc[p] for p, v in key.items() if v["kind"] == k and ok(v)]
    idm, ctm = float(np.mean(grp("identity"))), float(np.mean(grp("control")))
    valid = all(np.mean([float(s[p]) for p, v in key.items() if v["kind"] == "identity"]) >= 8 and
                np.mean([float(s[p]) for p, v in key.items() if v["kind"] == "identity"]) >= np.mean([float(s[p]) for p, v in key.items() if v["kind"] == "control"]) + 3
                for s in (s1, s2))
    rng = np.random.default_rng(SEED)
    res = {"identity_mean": idm, "control_mean": ctm}
    for name, ok in (("all", lambda v: True), ("both_med_or_high", lambda v: v["a"][3] in ("high", "medium") and v["b"][3] in ("high", "medium"))):
        S = grp("same", ok); C = grp("control")
        diff = float(np.mean(S) - np.mean(C)); allv = np.array(S + C); n = len(S)
        perm = [np.mean(p[:n]) - np.mean(p[n:]) for p in (rng.permutation(allv) for _ in range(20000))]
        p = float((1 + sum(x >= diff for x in perm)) / 20001)
        res[name] = {"n_same": n, "same_mean": float(np.mean(S)), "diff": diff, "p": p}
    a = res["all"]
    if not valid:
        verdict, bf = "VOID (a judge failed the identity check)", {}
    elif a["p"] < 0.01 and a["diff"] >= 1.5:
        verdict, bf = "SAME LABEL = SAME-LOOKING PLANT", {"M": 1 / 3}
    else:
        verdict, bf = "NOT SHOWN", {}
    res.update({"valid": valid, "verdict": verdict, "bayes_factors": bf, "scores": sc})
    OUT.write_text(json.dumps(res, indent=1)); print(json.dumps({k: v for k, v in res.items() if k != "scores"}, indent=1))


if __name__ == "__main__":
    B = Path(sys.argv[2])
    build(B) if sys.argv[1] == "build" else score(B, sys.argv[3], sys.argv[4])
