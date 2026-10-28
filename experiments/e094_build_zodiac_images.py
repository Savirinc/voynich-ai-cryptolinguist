"""E094 (Test A, Arham): build the blind zodiac image sets. See reports/E094_PREREG.md.
Crops the 12 zodiac pages (full circle and central medallion) from the DEV canvases already on disk, paints over the
later-hand month names (and three other later marks), and writes degraded versions of the medallion:
  L0 clean | L1 blur r6 | L2 blur r14 | L3 pixelated (40 px) | L4 grey + noise | L5 4x4 tiles shuffled
Images are named by random codes per condition; the key goes to experiments/results/e094_key.json (not in the image dir).
Run: .venv/bin/python experiments/e094_build_zodiac_images.py OUT_IMAGE_DIR
"""
from __future__ import annotations

import json, random, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/external/beinecke_images/zodiac"
KEY = ROOT / "experiments/results/e094_key.json"
SEED = 94094
# page: canvas, full-circle centre and radius, medallion centre and half-size
PAGES = {
    "f70v2": ("c1006200", (1968, 1681, 1500), (1968, 1751, 560)),
    "f70v1": ("c1006201", (1335, 1528, 1400), (1772, 1674, 520)),
    "f71r": ("c1006202", (1178, 1636, 1400), (1184, 1782, 540)),
    "f71v": ("c1006203", (1312, 1345, 1050), (1410, 1394, 420)),
    "f72r1": ("c1006203", (3247, 1312, 1050), (3186, 1361, 420)),
    "f72r2": ("c1006203", (5084, 1410, 1250), (5084, 1410, 450)),
    "f72r3": ("c1006203", (6986, 1410, 1250), (6986, 1440, 450)),
    "f72v3": ("c1006204", (2196, 1951, 1350), (2118, 1826, 480)),
    "f72v2": ("c1006204", (4479, 1785, 1450), (4631, 1819, 500)),
    "f72v1": ("c1006205", (1546, 1747, 1400), (1627, 1714, 480)),
    "f73r": ("c1006206", (1348, 1849, 1350), (1246, 1802, 470)),
    "f73v": ("c1006207", (1343, 1707, 1350), (1664, 1754, 470)),
}
# month-name boxes in the E094 inspection crops: (crop centre x, y, half-size, u0, v0, u1, v1 in 0-100 units)
MONTH_BOX = {
    "f70v2": ((1968, 1751, 560), (33, 46, 52, 57)), "f70v1": ((1595, 1674, 520), (50, 56, 70, 66)),
    "f71r": ((1324, 1782, 540), (37, 55, 55, 65)), "f71v": ((1410, 1394, 420), (34, 66, 48, 77)),
    "f72r1": ((3186, 1361, 420), (34, 62, 49, 74)), "f72r2": ((5084, 1410, 450), (42, 53, 58, 64)),
    "f72r3": ((6986, 1440, 450), (39, 61, 54, 71)), "f72v3": ((2118, 1826, 480), (50, 61, 68, 72)),
    "f72v2": ((4631, 1819, 500), (22, 47, 42, 58)), "f72v1": ((1627, 1714, 480), (44, 54, 69, 71)),
    "f73r": ((1246, 1802, 470), (35, 58, 62, 70)),
}
# other boxes directly in canvas pixels: f73v month scribble between the archer's feet; f73v top marks; f72v2 'A' mark
CANVAS_BOX = {"f73v": [(1640, 1840, 1800, 1905), (1000, 560, 1340, 880)],
              "f72v2": [(4631 - 500 + int(0.33 * 1000), 1819 - 500 + int(0.85 * 1000), 4631 - 500 + int(0.41 * 1000), 1819 - 500 + int(0.94 * 1000))]}
LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]


def masks(page):
    out = list(CANVAS_BOX.get(page, []))
    if page in MONTH_BOX:
        (cx, cy, r), (u0, v0, u1, v1) = MONTH_BOX[page]
        out.append((cx - r + u0 * 2 * r // 100, cy - r + v0 * 2 * r // 100, cx - r + u1 * 2 * r // 100, cy - r + v1 * 2 * r // 100))
    return out


def painted(canvas, boxes):
    im = canvas.copy(); a = np.asarray(im).astype(float)
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in boxes:
        pad = 40
        ring = np.concatenate([a[max(0, y0 - pad):y0, x0:x1].reshape(-1, 3), a[y1:y1 + pad, x0:x1].reshape(-1, 3)])
        col = tuple(int(v) for v in np.median(ring, axis=0))
        d.rectangle((x0, y0, x1, y1), fill=col)
    return im.filter(ImageFilter.GaussianBlur(0)) if False else im


def degrade(img, level, rng):
    if level == "L0":
        return img
    if level == "L1":
        return img.filter(ImageFilter.GaussianBlur(6))
    if level == "L2":
        return img.filter(ImageFilter.GaussianBlur(14))
    if level == "L3":
        return img.resize((40, 40), Image.BILINEAR).resize(img.size, Image.NEAREST)
    if level == "L4":
        g = np.asarray(img.convert("L")).astype(float)
        g = 128 + 0.6 * (g - 128) + np.random.default_rng(rng.randrange(1 << 30)).normal(0, 60, g.shape)
        return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGB")
    if level == "L5":
        n = 4; w, h = img.size; tw, th = w // n, h // n
        tiles = [img.crop((i * tw, j * th, (i + 1) * tw, (j + 1) * th)) for j in range(n) for i in range(n)]
        rng.shuffle(tiles); out = Image.new("RGB", (tw * n, th * n))
        for k, t in enumerate(tiles):
            out.paste(t, ((k % n) * tw, (k // n) * th))
        return out
    raise ValueError(level)


def main():
    out = Path(sys.argv[1]); rng = random.Random(SEED)
    cache, key = {}, {}
    conds = ["FULL"] + [f"CENTRE_{l}" for l in LEVELS]
    for cond in conds:
        (out / cond).mkdir(parents=True, exist_ok=True)
        codes = rng.sample(range(100, 1000), len(PAGES)); key[cond] = {}
        for code, (page, (cv, (fx, fy, fr), (mx, my, mr))) in zip(codes, PAGES.items()):
            if cv not in cache:
                cache[cv] = Image.open(SRC / f"{cv}.jpg").convert("RGB")
            pk = (cv, page)
            if pk not in cache:
                cache[pk] = painted(cache[cv], masks(page))
            im = cache[pk]
            if cond == "FULL":
                img = im.crop((max(0, fx - fr), max(0, fy - fr), min(im.width, fx + fr), min(im.height, fy + fr)))
                img.thumbnail((1600, 1600))
            else:
                img = im.crop((mx - mr, my - mr, mx + mr, my + mr)).resize((800, 800))
                img = degrade(img, cond.split("_")[1], rng)
            img.save(out / cond / f"img_{code}.jpg", quality=90)
            key[cond][f"img_{code}"] = page
    KEY.write_text(json.dumps({"experiment": "E094", "seed": SEED, "key": key, "masks": {p: masks(p) for p in PAGES}}, indent=1))
    print("built", {c: len(v) for c, v in key.items()})


if __name__ == "__main__":
    main()
