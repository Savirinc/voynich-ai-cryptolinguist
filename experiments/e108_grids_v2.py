"""E108 amendment (see reports/E108_AMENDMENT.md): labelling grids v2. Same records, same grid/cell numbering as the
locked detect stage; each crop is redrawn at 160 px with the detected component tinted red so that G (single gallows)
can be told from M (merged with other letters). Reads only cid/folio/box/grid/cell from records.json.
Run: .venv/bin/python -I experiments/e108_grids_v2.py"""
import importlib.util, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e108", ROOT / "experiments/e108_gallows_shapes.py")
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
CELL = 160
recs = json.loads((E.WORK / "records.json").read_text())
byf = {}
for r in recs:
    byf.setdefault(r["folio"], []).append(r)
crops = {}
for f, rs in byf.items():
    im, lab, _ = E.components(E.IMG / f"{f}.jpg"); a = np.asarray(im).copy()
    for r in rs:
        cid = int(r["cid"].rsplit("_", 1)[1]); x0, y0, x1, y1 = r["box"]
        pad = max(4, int(0.5 * (y1 - y0) / max(1.0, r["ascent"])))
        X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad
        sub = a[Y0:Y1, X0:X1].copy(); m = lab[Y0:Y1, X0:X1] == cid
        sub[m] = [220, 0, 0]
        crops[(r["grid"], r["cell"])] = Image.fromarray(sub)
    print(f, len(rs), flush=True)
for g in sorted({r["grid"] for r in recs}):
    G = Image.new("RGB", (E.COLS * CELL, E.ROWS * (CELL + 18)), "white"); d = ImageDraw.Draw(G)
    for (gg, cell), cr in crops.items():
        if gg != g:
            continue
        cr = cr.copy(); cr.thumbnail((CELL - 6, CELL - 6)); k = cell - 1
        x, y = (k % E.COLS) * CELL, (k // E.COLS) * (CELL + 18)
        G.paste(cr, (x + 3, y + 18)); d.text((x + 4, y + 2), str(cell), fill="blue")
    G.save(E.WORK / f"grid2_{g:02d}.png")
print("done")
