"""E038 (attack step 1b): the true sign inventory, key-free, with controls. See reports/E038_PREREG.md.

Part A  five alternations (e/ee, r/l, t/k, d+-, q+-): are the two forms the same sign?
  For every minimal pair of word types (w1, w2 differing by the alternation, both >= 5 tokens) two similarities:
    PAGE  cosine of the two words' distributions over pages (Voynich folios; controls: chunks of the same mean size)
    NBR   cosine of their neighbour distributions (left+right neighbours within the line; neighbours in the top 300
          types kept as words, others reduced to '<R:last glyph>'; neighbours equal or edit-distance 1 to the word
          itself are dropped)
  Each is placed between two baselines with exactly the same token counts (20 draws per pair):
    SELF  one word of similar count, its tokens split at random into n1 and n2  (ceiling: same word)
    RAND  two different, unrelated words of similar counts                        (floor: different words)
  S = sum(sim - rand) / sum(self - rand) over pairs (1 = like the same word, 0 = like unrelated words).
  Calibration on Latin (first E033 window of latVUC):
    F  free-variant control: every 'e' independently written 'E' with probability 0.5 -> pairs e/E
    C  contrast control: natural Latin minimal pairs r/l, t/s, e/i in the plain text
  t = (S - C) / (F - C) per measure; a measure is VOID if F - C < 0.4.
Part B  positional forms (like Arabic/Urdu letter shapes): glyph pairs in complementary position (overlap of
  initial/medial/final profiles < 0.10, both >= 200 occurrences) whose comparable in-word context (left glyph if
  neither is mostly initial, right glyph if neither is mostly final) is similar. Control: Latin with word-final 's'
  written 'S'. Initial-vs-final pairs have no comparable context and are listed only.
Part C  q: the q+- row of Part A, plus where q-forms are used (Currier A/B, line position).
Run: caffeinate -ims .venv/bin/python experiments/e038_sign_inventory.py
"""
from __future__ import annotations

import json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e030_reduplication import ed1, tokens  # noqa: E402
from e033_language_features import N  # noqa: E402
from e035_spelling_variation import windows  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED, MINC, DRAWS, TOPN, BOOT = 38038, 5, 20, 300, 1000
OUT = ROOT / "experiments/results/e038.json"


# ------------------------------------------------------------------ data
def voynich():
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    L, meta = defaultdict(list), {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t.eva if t.is_clean else None)
            meta[(t.folio, t.line_no)] = (t.folio, t.currier)
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    ref = E.voynich_lines()[0]
    assert [L[k] for k in order] == ref
    lines = [[w for w in L[k] if w] for k in order]
    return [(l, meta[k][0], meta[k][1]) for k, l in zip(order, lines) if l], sorted(locked)


def chunked(words, page):
    return [(words[i:i + page], i // page, "-") for i in range(0, len(words), page)]


# ------------------------------------------------------------------ context vectors
class Ctx:
    def __init__(self, lines):
        self.occ = defaultdict(list)                     # word -> [(page, left, right)]
        wc = Counter(w for l, _, _ in lines for w in l)
        top = {w for w, _ in wc.most_common(TOPN)}
        red = lambda x: x if x in top else "<R:%s>" % x[-1]
        pages = {}
        for l, pg, _ in lines:
            p = pages.setdefault(pg, len(pages))
            for i, w in enumerate(l):
                self.occ[w].append((p, red(l[i - 1]) if i and l[i - 1] != w and not ed1(l[i - 1], w) else None,
                                    red(l[i + 1]) if i + 1 < len(l) and l[i + 1] != w and not ed1(l[i + 1], w) else None))
        self.wc = wc
        self.by_count = sorted(wc, key=wc.get)

    @staticmethod
    def vec(sub):
        pg, nb = Counter(), Counter()
        for p, a, b in sub:
            pg[p] += 1
            if a: nb[a] += 1
            if b: nb[b] += 1
        return pg, nb


def cos(a, b):
    num = sum(v * b[k] for k, v in a.items() if k in b)
    da, db = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def sims(o1, o2):
    p1, n1 = Ctx.vec(o1); p2, n2 = Ctx.vec(o2)
    return cos(p1, p2), cos(n1, n2)


def pick(ctx, n, rng, lo=0.67, hi=1.5, exclude=()):
    c = [w for w in ctx.by_count if lo * n <= ctx.wc[w] <= hi * n and w not in exclude]
    if not c:
        c = sorted(ctx.wc, key=lambda w: abs(ctx.wc[w] - n))[:20]
    return rng.choice(c)


def score_pairs(ctx, pairs, rng):
    rows = []
    for w1, w2 in pairs:
        o1, o2 = ctx.occ[w1], ctx.occ[w2]
        n1, n2 = len(o1), len(o2)
        sp, sn = sims(o1, o2)
        selfp, selfn, rp, rn = [], [], [], []
        for _ in range(DRAWS):
            u = pick(ctx, n1 + n2, rng, 1.0, 2.0, (w1, w2))
            oo = ctx.occ[u]
            sub = rng.sample(oo, min(len(oo), n1 + n2)); k = round(len(sub) * n1 / (n1 + n2))
            a, b = sims(sub[:k], sub[k:]); selfp.append(a); selfn.append(b)
            u1 = pick(ctx, n1, rng, exclude=(w1, w2)); u2 = pick(ctx, n2, rng, exclude=(w1, w2, u1))
            while ed1(u1, u2):
                u2 = pick(ctx, n2, rng, exclude=(w1, w2, u1))
            a, b = sims(rng.sample(ctx.occ[u1], min(n1, ctx.wc[u1])), rng.sample(ctx.occ[u2], min(n2, ctx.wc[u2])))
            rp.append(a); rn.append(b)
        rows.append({"w1": w1, "w2": w2, "n1": n1, "n2": n2, "page": sp, "nbr": sn,
                     "self_page": float(np.mean(selfp)), "self_nbr": float(np.mean(selfn)),
                     "rand_page": float(np.mean(rp)), "rand_nbr": float(np.mean(rn))})
    return rows


def S(rows, m):
    num = sum(r[m] - r["rand_" + m] for r in rows); den = sum(r["self_" + m] - r["rand_" + m] for r in rows)
    return num / den if den else float("nan")


def summary(rows, rng):
    out = {"n_pairs": len(rows)}
    for m in ("page", "nbr"):
        out["S_" + m] = S(rows, m)
        bs = [S([rows[rng.randrange(len(rows))] for _ in rows], m) for _ in range(BOOT)] if rows else []
        out["CI_" + m] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None
    return out


# ------------------------------------------------------------------ minimal pairs
def subst_pairs(wc, x, y):
    P = set()
    for w in wc:
        for i, g in enumerate(w):
            if g == x:
                v = w[:i] + y + w[i + 1:]
                if v in wc: P.add((w, v))
    return P


def ins_pairs(wc, g, run_only):
    """(w, v): v = w with one more g; run_only -> only next to an existing g (e/ee)."""
    P = set()
    for w in wc:
        for i in range(len(w) + 1):
            if run_only and not ((i > 0 and w[i - 1] == g) or (i < len(w) and w[i] == g)):
                continue
            v = w[:i] + g + w[i:]
            if v in wc: P.add((w, v))
    return P


def keep(P, wc):
    return sorted((a, b) for a, b in P if wc[a] >= MINC and wc[b] >= MINC)


ALTS = {"e/ee": lambda wc: ins_pairs(wc, "e", True), "r/l": lambda wc: subst_pairs(wc, "r", "l"),
        "t/k": lambda wc: subst_pairs(wc, "t", "k"), "d+-": lambda wc: ins_pairs(wc, "d", False),
        "q+-": lambda wc: {(w[1:], w) for w in wc if w.startswith("q") and w[1:] in wc}}


# ------------------------------------------------------------------ part B
def positions(words):
    prof, left, right, tot = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), Counter()
    for w in words:
        if len(w) < 2:
            continue
        for i, g in enumerate(w):
            pos = "I" if i == 0 else "F" if i == len(w) - 1 else "M"
            prof[g][pos] += 1; tot[g] += 1
            left[g]["^" if i == 0 else w[i - 1]] += 1; right[g]["$" if i == len(w) - 1 else w[i + 1]] += 1
    return prof, left, right, tot


def part_b(words, min_n=200):
    prof, left, right, tot = positions(words)
    G = sorted(g for g in tot if tot[g] >= min_n)
    norm = {g: {p: prof[g][p] / tot[g] for p in "IMF"} for g in G}
    rows, allcos = [], []
    for i, x in enumerate(G):
        for y in G[i + 1:]:
            ov = sum(min(norm[x][p], norm[y][p]) for p in "IMF")
            mostly = lambda g, p: norm[g][p] >= 0.5
            if not (mostly(x, "I") or mostly(y, "I")):
                side, c = "left", cos(left[x], left[y])
            elif not (mostly(x, "F") or mostly(y, "F")):
                side, c = "right", cos(right[x], right[y])
            else:
                side, c = None, None
            if c is not None:
                allcos.append(c)
            rows.append({"x": x, "y": y, "overlap": ov, "side": side, "cos": c,
                         "prof_x": norm[x], "prof_y": norm[y]})
    p90 = float(np.percentile(allcos, 90)) if allcos else float("nan")
    for r in rows:
        r["pct"] = float(np.mean([c <= r["cos"] for c in allcos])) if r["cos"] is not None else None
    return rows, p90


# ------------------------------------------------------------------ main
def main():
    rng = random.Random(SEED)
    vlines, locked = voynich()
    vwords = [w for l, _, _ in vlines for w in l]
    assert len(vwords) == N
    page = round(len(vwords) / len({f for _, f, _ in vlines}))
    lat = tokens("latVUC")[windows()["latVUC"][0]:][:N]
    latF = ["".join("E" if c == "e" and rng.random() < 0.5 else c for c in w) for w in lat]
    res = {"page_size": page}

    # controls, part A
    ctxF, ctxC = Ctx(chunked(latF, page)), Ctx(chunked(lat, page))
    rowsF = score_pairs(ctxF, keep(subst_pairs(ctxF.wc, "e", "E"), ctxF.wc), rng)
    rowsC = []
    for x, y in (("r", "l"), ("t", "s"), ("e", "i")):
        rowsC += score_pairs(ctxC, keep(subst_pairs(ctxC.wc, x, y), ctxC.wc), rng)
    F, C = summary(rowsF, rng), summary(rowsC, rng)
    res["control_free"], res["control_contrast"] = F, C
    void = {m: (F["S_" + m] - C["S_" + m]) < 0.4 for m in ("page", "nbr")}
    res["void"] = void
    print(f"page size {page} | FREE control {F} | CONTRAST control {C} | void {void}", flush=True)

    # Voynich, part A
    ctxV = Ctx(vlines)
    A = {}
    for name, fn in ALTS.items():
        rows = score_pairs(ctxV, keep(fn(ctxV.wc), ctxV.wc), rng)
        s = summary(rows, rng)
        t = {m: (s["S_" + m] - C["S_" + m]) / (F["S_" + m] - C["S_" + m]) for m in ("page", "nbr")}
        if s["n_pairs"] < 10:
            v = "INSUFFICIENT"
        elif void["nbr"] or void["page"]:
            v = "VOID"
        elif t["nbr"] >= 0.75 and t["page"] >= 0.75:
            v = "FREE VARIANT"
        elif t["nbr"] >= 0.75 and t["page"] <= 0.5:
            v = "SCRIBAL/SECTIONAL VARIANT"
        elif t["page"] >= 0.75 and t["nbr"] <= 0.25:
            v = "GRAMMATICAL (related forms)"
        elif t["nbr"] <= 0.25 and t["page"] <= 0.25:
            v = "CONTRASTIVE (different signs)"
        else:
            v = "MIXED"
        A[name] = {**s, "t": t, "verdict": v, "pairs": rows}
        print(f"{name:5s} pairs {s['n_pairs']:3d} S_page {s['S_page']:.2f} {s['CI_page']} S_nbr {s['S_nbr']:.2f} "
              f"{s['CI_nbr']} | t_page {t['page']:.2f} t_nbr {t['nbr']:.2f} -> {v}", flush=True)
    res["partA"] = A

    # part B
    latS = [w[:-1] + "S" if len(w) >= 2 and w.endswith("s") else w for w in lat]
    rB_lat, p90_lat = part_b(latS)
    ctl = next(r for r in rB_lat if {r["x"], r["y"]} == {"s", "S"})
    ctl_pass = ctl["overlap"] < 0.10 and ctl["cos"] is not None and ctl["pct"] >= 0.90
    rB, p90 = part_b(vwords)
    cands = [r for r in rB if r["overlap"] < 0.10 and r["cos"] is not None
             and r["cos"] >= 0.8 * ctl["cos"] and r["pct"] >= 0.90]
    listed = [r for r in rB if r["overlap"] < 0.10 and r["cos"] is None]
    res["partB"] = {"control": ctl, "control_pass": ctl_pass, "candidates": cands,
                    "complementary_untestable": listed, "all": rB, "p90": p90,
                    "verdict": "VOID" if not ctl_pass else ("CANDIDATES FOUND" if cands else "NONE FOUND")}
    print(f"part B control s/S: overlap {ctl['overlap']:.2f} cos {ctl['cos']} pct {ctl['pct']} pass {ctl_pass}")
    for r in sorted(rB, key=lambda r: r["overlap"])[:15]:
        print(f"  {r['x']}/{r['y']} overlap {r['overlap']:.2f} side {r['side']} cos {r['cos'] if r['cos'] is None else round(r['cos'], 2)} pct {r['pct']}")
    print("part B:", res["partB"]["verdict"], [(r["x"], r["y"]) for r in cands])

    # part C
    qw = Counter(); tot = Counter()
    for l, f, cur in vlines:
        for i, w in enumerate(l):
            k = (cur, "first" if i == 0 else "other")
            tot[k] += 1; qw[k] += w.startswith("q")
    res["partC"] = {"q_share": {f"{a}/{b}": qw[(a, b)] / tot[(a, b)] for a, b in tot if tot[(a, b)] >= 100},
                    "q_pairs_verdict": A["q+-"]["verdict"]}
    print("part C q share:", {k: round(v, 3) for k, v in res["partC"]["q_share"].items()})
    res["locked_test_excluded"] = locked
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
