"""E096 (Route 2, Arham 2026-10-29): do the zodiac figure labels follow the period degree tables? See reports/E096_PREREG.md.

Each zodiac figure (one label line in ZL) is taken as one degree of its sign (E094). Period tables (Lilly CA 1647
pp.116-118, the Arabic tradition of Al-Biruni and Alcabitius; reports/data/degree_tables.json) sort the 30 degrees of each
sign into classes. Three columns: GENDER (M/F), LIGHT (light/dark/smoky/void), TERMS (5 planets, sign-specific bounds).
Label similarity: Dice coefficient of glyph bigrams (with word-boundary marks) of the figure's label words (EVA, alternates
and uncertainty marks stripped). Per sign and column: D = mean similarity of figure pairs in the same class - mean of pairs
in different classes, maximised over alignments (ring order listed/reversed x direction as listed/reversed x circular start;
Aries and Taurus: also page order); statistic = sum of D over the 10 signs.
Null: the 12 sign tables assigned to the 10 signs at random (no sign keeps its own table), the same maximisation; 999 draws.
Max-T over the 3 columns (each column's statistic standardised by its null). Calibration before Voynich: planted labels\n(class shown by the label's front piece, fidelity 0.8), and a false-claim control with rotated tables.
Run: caffeinate -ims .venv/bin/python experiments/e096_degree_tables.py [--calibration-only]
"""
from __future__ import annotations

import argparse, json, random, re, sys, time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED, N_PERM, N_CAL, FID, N_CTRL = 96196, 999, 10, 0.9, 20
OUT = ROOT / "experiments/results/e096.json"
TABLES = json.loads((ROOT / "reports/data/degree_tables.json").read_text())["tables"]
SIGNS12 = list(TABLES)
PAGES = {"Pisces": ["f70v2"], "Aries": ["f70v1", "f71r"], "Taurus": ["f71v", "f72r1"], "Gemini": ["f72r2"], "Cancer": ["f72r3"],
         "Leo": ["f72v3"], "Virgo": ["f72v2"], "Libra": ["f72v1"], "Scorpio": ["f73r"], "Sagittarius": ["f73v"]}
SIGNS = list(PAGES)
COLUMNS = {"gender": lambda r: r["gender"][:1], "light": lambda r: r["light"][:1], "terms": lambda r: r["term"]}


def log(*a):
    print(*a, flush=True)


def clean(w):
    w = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", w)
    return re.sub(r"[^a-z]", "", w)


def rings(folio, toks):
    """label lines of a page grouped into rings (a circle-text line separates rings), in ZL order"""
    out, cur, seen = [], [], {}
    for t in toks:
        if t.folio != folio:
            continue
        if t.mode != "label":
            if t.line_no not in seen and cur:
                out.append(cur); cur = []
            seen[t.line_no] = 1
            continue
        if t.line_no not in seen:
            seen[t.line_no] = 1; cur.append([])
        w = clean(t.eva)
        if w:
            cur[-1].append(w)
    if cur:
        out.append(cur)
    return [[" ".join(f) for f in r if f] for r in out if any(r)]


def bigrams(s):
    s = "#" + s.replace(" ", "#") + "#"
    return {s[i:i + 2] for i in range(len(s) - 1)}


def sim_matrix(labels):
    B = [bigrams(x) for x in labels]; n = len(B); S = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            S[i, j] = S[j, i] = 2 * len(B[i] & B[j]) / (len(B[i]) + len(B[j]))
    return S


def orderings(sign_rings):
    """all figure orders considered: per page ring order x direction; pages in order or swapped; circular start"""
    pages = list(sign_rings)
    variants = []
    for porder in ([pages, pages[::-1]] if len(pages) == 2 else [pages]):
        for rrev in (False, True):
            for drev in (False, True):
                seq = []
                for pg in porder:
                    rs = sign_rings[pg][::-1] if rrev else sign_rings[pg]
                    for r in rs:
                        seq += r[::-1] if drev else r
                variants.append(seq)
    out = []
    for seq in variants:
        n = len(seq)
        for k in range(n):
            out.append(seq[k:] + seq[:k])
    return out


def classes(table, col, n):
    lab = [COLUMNS[col](r) for r in table]
    return [lab[min(29, int(i * 30 / n))] for i in range(n)]


def D_for(S, orders, cls):
    """max over orders of mean same-class sim - mean different-class sim; S over figure indices, orders = index lists"""
    c = np.array(cls); same = c[:, None] == c[None, :]; iu = np.triu_indices(len(c), 1)
    sm, df = same[iu], ~same[iu]
    best = -9.0
    for o in orders:
        So = S[np.ix_(o, o)][iu]
        if sm.any() and df.any():
            best = max(best, So[sm].mean() - So[df].mean())
    return best


def prepare(R):
    """R: sign -> {page: rings of labels}; returns per sign (S, orders as index lists, n)"""
    P = {}
    for s in SIGNS:
        labels = [f for pg in R[s] for r in R[s][pg] for f in r]
        pos = {}; k = 0; idx_rings = {}
        for pg in R[s]:
            idx_rings[pg] = []
            for r in R[s][pg]:
                idx_rings[pg].append(list(range(k, k + len(r)))); k += len(r)
        P[s] = (sim_matrix(labels), orderings(idx_rings), len(labels))
    return P


def statistic(P, assign, col, cache):
    tot = 0.0
    for s in SIGNS:
        t = assign[s]; key = (s, t, col)
        if key not in cache:
            S, orders, n = P[s]; cache[key] = D_for(S, orders, classes(TABLES[t], col, n))
        tot += cache[key]
    return tot


def derangements(rng, n):
    out = []
    while len(out) < n:
        t = SIGNS12[:]; rng.shuffle(t); a = dict(zip(SIGNS, t))
        if all(a[s] != s for s in SIGNS):
            out.append(a)
    return out


def evaluate(P, perms):
    cache = {}; ident = {s: s for s in SIGNS}; res = {}
    for col in COLUMNS:
        tr = statistic(P, ident, col, cache); nl = np.array([statistic(P, a, col, cache) for a in perms])
        res[col] = {"true": tr, "null_mean": float(nl.mean()), "null_sd": float(nl.std()), "z": float((tr - nl.mean()) / (nl.std() or 1e-9)),
                    "p": float((1 + (nl >= tr).sum()) / (1 + len(nl))), "null": nl}
    Z = {c: (res[c]["null"] - res[c]["null_mean"]) / (res[c]["null_sd"] or 1e-9) for c in COLUMNS}
    Tn = np.max(np.vstack([Z[c] for c in COLUMNS]), axis=0); Tr = max(res[c]["z"] for c in COLUMNS)
    pT = float((1 + (Tn >= Tr).sum()) / (1 + len(Tn)))
    for c in res:
        res[c].pop("null")
    return res, Tr, pT


FRONTS = ["ot", "ok", "o", "y", "ch"]


def front(w):
    for f in ("ot", "ok", "op", "of", "ch", "sh", "o", "y"):
        if w.startswith(f):
            return f
    return "x"


def planted(R, col, rng, fid, model="front"):
    """replace labels: degree class c -> a label from pool c with prob fid, else from another pool; a random alignment
    per sign. model 'front' (scored): pools = real zodiac labels by front piece (ot, ok, o, y, ch; one per class, drawn at
    random per sign). model 'cluster' (descriptive): pools = k similarity clusters around random medoids."""
    allv = sorted({f for s in SIGNS for pg in R[s] for r in R[s][pg] for f in r})
    S = sim_matrix(allv) if model == "cluster" else None
    out = {}
    for s in SIGNS:
        n = sum(len(r) for pg in R[s] for r in R[s][pg]); cls = classes(TABLES[s], col, n); ks = sorted(set(cls))
        if model == "front":
            fr = rng.sample(FRONTS[:max(len(ks), 2) + 1], len(ks)); pools = {k: [w for w in allv if front(w) == f] for k, f in zip(ks, fr)}
        else:
            med = rng.sample(range(len(allv)), len(ks)); asg = np.argmax(S[:, med] + np.eye(len(allv))[:, med], axis=1)
            pools = {k: [allv[i] for i in range(len(allv)) if asg[i] == j] or [allv[med[j]]] for j, k in enumerate(ks)}
        seq = [rng.choice(pools[c if rng.random() < fid or len(ks) == 1 else rng.choice([x for x in ks if x != c])]) for c in cls]
        struct, k0 = {}, 0
        for pg in R[s]:
            struct[pg] = []
            for r in R[s][pg]:
                struct[pg].append(list(range(k0, k0 + len(r)))); k0 += len(r)
        o = rng.choice(orderings(struct)); lab = [None] * n
        for deg, fig in enumerate(o):
            lab[fig] = seq[deg]
        it = iter(lab); out[s] = {pg: [[next(it) for _ in r] for r in R[s][pg]] for pg in R[s]}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--calibration-only", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    assert not {t.leaf for t in toks if t.folio in sum(PAGES.values(), [])} & locked
    R = {s: {pg: rings(pg, toks) for pg in PAGES[s]} for s in SIGNS}
    log("figures per sign:", {s: sum(len(r) for pg in R[s] for r in R[s][pg]) for s in SIGNS},
        "| rings per page:", {pg: [len(r) for r in R[s][pg]] for s in SIGNS for pg in R[s]})
    perms = derangements(rng, N_PERM)
    cal = {}
    for col in COLUMNS:
        ps = []
        for k in range(N_CAL):
            res, _, _ = evaluate(prepare(planted(R, col, rng, FID)), perms[:199])
            ps.append(res[col]["p"])
        cal[col] = {"p": ps, "pass": sum(p <= 0.01 for p in ps)}
        log(f"CAL planted {col} fid {FID}: p {ps} -> {cal[col]['pass']}/{N_CAL} at p<=0.01")
    half = {col: evaluate(prepare(planted(R, col, rng, 0.6)), perms[:199])[0][col]["p"] for col in COLUMNS}
    clus = {col: evaluate(prepare(planted(R, col, rng, FID, "cluster")), perms[:199])[0][col]["p"] for col in COLUMNS}
    log("descriptive, front fidelity 0.6:", half, "| similarity-cluster plant, fidelity 0.8:", clus)
    validated = all(cal[c]["pass"] >= 8 for c in COLUMNS)
    log(f"calibration {'PASSED' if validated else 'FAILED'} | {time.time() - t0:.0f}s")
    out = {"experiment": "E096", "seed": SEED, "calibration": cal, "fidelity_0.6": half, "cluster_plant": clus, "validated": validated}
    if not a.calibration_only:
        # false-claim control: real labels, each sign given a random table built by shuffling run blocks of its own table
        fc = 0; ctrl = []
        P = prepare(R)
        for k in range(N_CTRL):
            saved = dict(TABLES)
            for s in SIGNS12:
                rows = TABLES[s]; sh = rng.randrange(1, 30); TABLES[s] = rows[sh:] + rows[:sh]
            res, Tr, pT = evaluate(P, perms[:199]); TABLES.update(saved)
            ctrl.append(pT); fc += pT <= 0.01
        log(f"false-claim control (tables rotated): max-T p {ctrl} -> {fc}/{N_CTRL} claims")
        res, Tr, pT = evaluate(P, perms)
        for c in COLUMNS:
            log(f"VOYNICH {c:7s} D {res[c]['true']:+.4f} null {res[c]['null_mean']:+.4f} sd {res[c]['null_sd']:.4f} z {res[c]['z']:+.2f} p {res[c]['p']:.3f}")
        if not validated or fc > 1:
            verdict = "VOID (calibration or false-claim control failed)"
        elif pT <= 0.01:
            verdict = f"DEGREE-TABLE LINK (max-T {Tr:.2f}, p {pT:.3f}) - M x 1/5"
        else:
            verdict = f"NO LINK (max-T {Tr:.2f}, p {pT:.3f}) - no factor"
        log(f"VERDICT {verdict} | {time.time() - t0:.0f}s")
        out.update({"false_claim_control": ctrl, "voynich": res, "maxT": Tr, "p_maxT": pT, "verdict": verdict})
    OUT.with_name("e096_calibration_smoke.json" if a.calibration_only else OUT.name).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
