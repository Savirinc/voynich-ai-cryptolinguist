"""E086: are Voynich's spaces mechanical, and is each line its own record? See reports/E086_PREREG.md.

Part A (spaces): every gap between two adjacent glyphs inside a line (within a word or between two clean words) is
labelled space / no space. Context = 2 glyphs left + 2 glyphs right (spaces ignored, line edge padded). Table built on
the first half of lines, scored on the second: PRED = 1 - H(label | context) / H(label) (add-0.5 smoothing).
Part B (lines): word-bigram model (add-0.1) from the first half of lines; on the second half, D = mean log-prob of the
cross-line pairs (last word of line i -> first word of line i+1, same page) minus the same with the following line
replaced by a random other line of the same page (200 shuffles); z of the real value against the shuffles.
Run: caffeinate -ims .venv/bin/python experiments/e086_spaces_and_lines.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, math, random, sys, time, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
OUT = ROOT / "experiments/results/e086.json"
SEED, N, SHUF, PAGE = 86086, 28841, 200, 25
LANGS = ["latVUC", "deu1912", "eng-kjv", "ita1885", "turytc", "hun", "ces1613", "indayt", "hboWLC", "arb-vd"]


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


# ------------------------------------------------------------------- Part A
def gaps(lines):
    """(context, label) for every glyph gap inside each line; lines = lists of words (None breaks)."""
    out = []
    for l in lines:
        segs, cur = [], []
        for w in l:
            if w is None:
                if cur:
                    segs.append(cur); cur = []
            else:
                cur.append(w)
        if cur:
            segs.append(cur)
        for s in segs:
            chars, lab = [], []
            for i, w in enumerate(s):
                for j, c in enumerate(w):
                    chars.append(c)
                    lab.append(1 if (j == len(w) - 1 and i < len(s) - 1) else 0)
            padded = ["^", "^"] + chars + ["$", "$"]
            for k in range(len(chars) - 1):
                ctx = tuple(padded[k:k + 2] + [padded[k + 2]] + padded[k + 3:k + 5])
                out.append((ctx, lab[k]))
    return out


def pred(lines):
    h = len(lines) // 2
    tr, te = gaps(lines[:h]), gaps(lines[h:])
    t = defaultdict(lambda: [0.5, 0.5])
    for c, y in tr:
        t[c][y] += 1
    p1 = sum(y for _, y in tr) / len(tr)
    H0 = -(p1 * math.log2(p1) + (1 - p1) * math.log2(1 - p1))
    Hc = 0.0
    for c, y in te:
        a, b = t[c] if c in t else (0.5 + (1 - p1), 0.5 + p1)
        Hc -= math.log2((b if y else a) / (a + b))
    Hc /= len(te)
    return {"PRED": 1 - Hc / H0, "space_rate": p1, "H0": H0, "H_ctx": Hc, "gaps": len(te)}


# ------------------------------------------------------------------- Part B
def continuity(pages, rng):
    """pages: list of lists of lines (lists of words, None allowed)."""
    h = len(pages) // 2
    tr = [w for p in pages[:h] for l in p for w in l]
    uni, big = Counter(), Counter()
    for p in pages[:h]:
        for l in p:
            ws = [w for w in l if w]
            uni.update(ws); big.update(zip(ws, ws[1:]))
    V = len(uni) + 1
    lp = lambda a, b: math.log((big.get((a, b), 0) + 0.1) / (uni.get(a, 0) + 0.1 * V))
    test = pages[h:]
    def score(order_fn):
        v = []
        for p in test:
            ls = [[w for w in l if w] for l in p]
            ls = [l for l in ls if l]
            nxt = order_fn(ls)
            for i in range(len(ls) - 1):
                v.append(lp(ls[i][-1], nxt[i][0]))
        return float(np.mean(v)), len(v)
    real, n = score(lambda ls: ls[1:])
    null = []
    for _ in range(SHUF):
        def shuf(ls):
            out = []
            for i in range(len(ls) - 1):
                cand = [j for j in range(len(ls)) if j != i and j != i + 1]
                out.append(ls[rng.choice(cand)] if cand else ls[i + 1])
            return out
        null.append(score(shuf)[0])
    mu, sd = float(np.mean(null)), float(np.std(null, ddof=1))
    # within-line reference
    wl = []
    for p in test:
        for l in p:
            ws = [w for w in l if w]
            wl += [lp(a, b) for a, b in zip(ws, ws[1:])]
    return {"cross_real": real, "cross_shuffled": mu, "z": (real - mu) / sd if sd > 0 else 0.0, "pairs": n,
            "within_line": float(np.mean(wl))}


# ------------------------------------------------------------------- texts
def voynich_pages():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L = defaultdict(list)
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t.eva if t.is_clean else None)
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    pages = defaultdict(list)
    for k in order:
        pages[k[0]].append(L[k])
    folios = sorted(pages, key=lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f))
    return [pages[f] for f in folios], sorted(locked, key=lambda x: (len(x), x))


def as_pages(lines):
    return [lines[i:i + PAGE] for i in range(0, len(lines), PAGE)]


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time(); rng = random.Random(SEED)
    vp, locked = voynich_pages()
    vlines = [l for p in vp for l in p]
    lens = [len([w for w in l if w]) for l in vlines]; lens = [x for x in lens if x]
    from e058_word_repeat_individuality_v2 import pseudo
    from e064_early_audit import tok
    res = {"experiment": "E086", "locked_test_excluded": locked, "texts": {}}
    def run(name, lines, pages):
        a = pred(lines); b = continuity(pages, random.Random(SEED + 1))
        res["texts"][name] = {"A": a, "B": b}
        log(f"{name:14s} A: PRED {a['PRED']:.3f} (space rate {a['space_rate']:.3f}) | B: cross-line real {b['cross_real']:.3f} "
            f"vs shuffled {b['cross_shuffled']:.3f} z {b['z']:+.2f} (pairs {b['pairs']}; within-line {b['within_line']:.3f})")
    run("VOYNICH", vlines, vp)
    for bid in LANGS:
        w = tok(bid)[10000:10000 + N]
        if bid in ("hboWLC", "arb-vd"):
            w = [x for x in (cons(t) for t in w) if x]
        L = pseudo(w, lens)
        run(bid, L, as_pages(L))
    # Naibbe single-table cipher (Latin) in Voynich line lengths, and the copy generator
    from e062_scribe_tables import plaintext, dev_lines, encipher
    from vcl.synthetic import naibbe_exact as NX
    dl, _ = dev_lines(); k0 = NX.key({}, 0, ""); keys = {h: k0 for h in "12345"}
    ml, _, _, _ = encipher(plaintext("latVUC"), dl, keys, SEED)
    run("naibbe_latin", ml, as_pages(ml))
    from e032_copy_generator import generate
    for s in (31, 32):
        gl = generate(gen_dir, java, s, N, ROOT / "data/external/e086_gen_work")
        run(f"generator_{s}", gl, as_pages(gl))
    T = res["texts"]
    langA = [T[b]["A"]["PRED"] for b in LANGS]; langB = [T[b]["B"]["z"] for b in LANGS]
    vA, vB = T["VOYNICH"]["A"]["PRED"], T["VOYNICH"]["B"]["z"]
    validB = sum(z > 3 for z in langB) >= 8
    mu, sd = float(np.mean(langA)), float(np.std(langA, ddof=1))
    if vA > max(langA) and vA > mu + 2 * sd:
        ra = "SPACES MECHANICAL (more predictable than every language)"
    elif vA < min(langA):
        ra = "SPACES LESS PREDICTABLE THAN EVERY LANGUAGE"
    else:
        ra = "SPACES LANGUAGE-LIKE"
    if not validB:
        rb = "VOID (languages do not show line continuity at this size)"
    elif vB > 3:
        rb = "LINES CONTINUE (running text)"
    elif abs(vB) <= 3:
        rb = "LINES INDEPENDENT (record-like)"
    else:
        rb = "LINES LESS CONNECTED THAN RANDOM"
    res.update(partA=ra, partB=rb, languages_PRED=[min(langA), max(langA), mu, sd], languages_z=langB, runtime_s=time.time() - t0)
    log(f"[A] Voynich PRED {vA:.3f}; languages {min(langA):.3f}-{max(langA):.3f} (mean {mu:.3f}, sd {sd:.3f}) -> {ra}")
    log(f"[B] Voynich z {vB:+.2f}; languages z {[round(z, 1) for z in langB]} (valid {validB}) -> {rb}")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
