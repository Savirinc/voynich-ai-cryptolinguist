"""E095 (Test B, Arham): do the zodiac pages' words encode their own sign's meanings? See reports/E095_PREREG.md.

Meanings (reports/data/e095_concepts.json): per sign, two months (annotator's and the one-month-earlier Julian
convention), sign name, animal or figure, ruling planet, element, season, in 8 languages (Latin, French/Occitan, Catalan,
Italian, German, Greek, Hebrew and Arabic consonantal). Targets shorter than 4 letters are dropped.
Words: W1 = zodiac-only word types of each page (absent from every other DEV page); W2 = all clean word types of each page.
Units: K1 = EVA characters; K2 = E024 S3 units (ch, sh, cth, iin, ee, qo, dy ...).
A key maps every unit to one letter (many-to-one allowed). A word MATCHES a target if, decoded with the key, it equals the
target (exact) or the target's first n letters with n >= MIN_PREFIX units (abbreviation), read forwards or backwards.
Score of a key = number of pages (0-12) holding at least one word that matches a target of THAT page's sign.
Fit: greedy consistent key construction, RESTARTS random page orders, maximising pages covered.
Null: the same fit with the 10 sign meaning-sets shuffled among the 10 signs (two-page signs stay together), N_PERM times.
Max-T over the 32 configurations (8 languages x 2 unit types x 2 word sets): T = max over configs of (S - null mean) /
null sd; the same statistic is computed for every permutation (leave-one-out null moments) -> p.
Calibration (power): one planted sign word per page (random injective key) in W2 for Latin, French/Occitan, Hebrew (K1),
all signs (must give p <= 0.01); plus Latin with half the signs planted (descriptive).
Language-free part: do pages sharing a planet / element / season share more words or glyph trigrams (same-sign and
adjacent pages excluded)? Permutation of signs.
Run: caffeinate -ims .venv/bin/python experiments/e095_zodiac_meaning.py [--smoke-null] [--workers 3]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time
from collections import Counter, defaultdict
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e024_atoms as A24  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED = 95095
OUT = ROOT / "experiments/results/e095.json"
CONCEPTS = json.loads((ROOT / "reports/data/e095_concepts.json").read_text())
ORDER = ["f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v"]
MIN_TARGET, MIN_PREFIX = 4, 6
RESTARTS = 300
N_PERM, N_PERM_CAL, N_ATTR_PERM = 99, 99, 9999
SIGNS = CONCEPTS["signs"]


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ data
def zodiac_words():
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    dev = [t for t in toks if t.leaf not in locked and t.is_clean]
    other = {t.eva for t in dev if t.illustration != "Z"}
    W2 = {p: sorted({t.eva for t in dev if t.folio == p}) for p in ORDER}
    W1 = {p: [w for w in W2[p] if w not in other] for p in ORDER}
    return W1, W2


def units(w, kind):
    return list(w) if kind == "K1" else A24.segment(w, A24.SEGS["S3"])


def targets(lang):
    L = CONCEPTS["languages"][lang]; out = {}
    for s in SIGNS:
        a = CONCEPTS["attributes"][s]; t = set()
        for m in a["months"]:
            t |= set(L["months"][m])
        t |= set(L["sign"][s]) | set(L["animal"][s]) | set(L["planet"][a["planet"]]) | set(L["element"][a["element"]]) | set(L["season"][a["season"]])
        cs = (lambda x: x) if lang in ("hebrew", "arabic") else str.lower
        out[s] = sorted({cs(x) for x in t if len(x) >= MIN_TARGET})
    return out


# ------------------------------------------------------------------ candidates
def build(words, kind, tg):
    """returns unit index, letter index, and cand[(page, sign)] = list of constraint tuples ((u, l), ...)"""
    U = sorted({u for p in ORDER for w in words[p] for u in units(w, kind)})
    Lt = sorted({c for s in SIGNS for t in tg[s] for c in t})
    ui = {u: i for i, u in enumerate(U)}; li = {c: i for i, c in enumerate(Lt)}
    cand = {}
    for p in ORDER:
        seqs = [[ui[u] for u in units(w, kind)] for w in words[p]]
        for s in SIGNS:
            cs = set()
            for wi, sq in enumerate(seqs):
                for seq in (sq, sq[::-1]):
                    n = len(seq)
                    for t in tg[s]:
                        if n == len(t) or (MIN_PREFIX <= n < len(t)):
                            m = {}
                            ok = True
                            for u, c in zip(seq, t[:n]):
                                if m.setdefault(u, li[c]) != li[c]:
                                    ok = False; break
                            if ok:
                                cs.add((wi, tuple(sorted(m.items()))))
            cand[(p, s)] = sorted(cs)
    return len(U), len(Lt), cand


def fit(nU, nL, active, rng):
    """active: list of (page_idx, constraints). Greedy consistent key construction with random restarts: pages in random
    order; on each page choose, among candidates consistent with the partial key, one adding the fewest new unit
    assignments (ties at random). Returns (best pages covered, candidates consistent with that key)."""
    if not active:
        return 0, 0
    bypage = defaultdict(list)
    for p, cons in active:
        bypage[p].append(cons)
    pages = list(bypage); best = (0, 0)
    for _ in range(RESTARTS):
        rng.shuffle(pages); key = {}; cov = 0
        for p in pages:
            opts, bestn = [], 99
            for cons in bypage[p]:
                new = 0; ok = True
                for u, l in cons:
                    k = key.get(u)
                    if k is None:
                        new += 1
                    elif k != l:
                        ok = False; break
                if ok:
                    if new < bestn:
                        opts, bestn = [cons], new
                    elif new == bestn:
                        opts.append(cons)
            if opts:
                for u, l in rng.choice(opts):
                    key[u] = l
                cov += 1
        if cov > best[0]:
            nsat = sum(all(key.get(u) == l for u, l in cons) for _, cons in active)
            best = (cov, nsat)
            if cov == len(pages):
                break
    return best


def active_for(cand, assign):
    """assign: sign -> meaning-set sign"""
    act = []
    for pi, p in enumerate(ORDER):
        s = assign[CONCEPTS["pages"][p]]
        act += [(pi, cons) for _, cons in cand[(p, s)]]
    return act


def perms(n, rng):
    out = []
    for _ in range(n):
        sh = SIGNS[:]; rng.shuffle(sh); out.append(dict(zip(SIGNS, sh)))
    return out


def job(args):
    name, nU, nL, cand, assign, seed = args
    return name, fit(nU, nL, active_for(cand, assign), random.Random(seed))


# ------------------------------------------------------------------ calibration
def plant(W2, lang, rng, share=1.0):
    tg = targets(lang); letters = sorted({c for s in SIGNS for t in tg[s] for c in t})
    eva = sorted({c for p in ORDER for w in W2[p] for c in w}); rng.shuffle(eva)
    enc = {c: eva[i % len(eva)] for i, c in enumerate(letters)}  # injective while units last
    out = {}
    chosen = set(rng.sample(SIGNS, round(share * len(SIGNS))))
    for p in ORDER:
        s = CONCEPTS["pages"][p]; t = rng.choice(tg[s])
        out[p] = sorted(set(W2[p]) | ({"".join(enc[c] for c in t)} if s in chosen else set()))
    return out


# ------------------------------------------------------------------ language-free attributes
def attr_test(W2, rng):
    tri = {p: Counter(w[i:i + 3] for w in W2[p] for i in range(len(w) - 2)) for p in ORDER}
    def jac(a, b):
        A, B = set(W2[a]), set(W2[b]); return len(A & B) / len(A | B)
    def cos(a, b):
        x, y = tri[a], tri[b]; num = sum(x[k] * y.get(k, 0) for k in x)
        return num / math.sqrt(sum(v * v for v in x.values()) * sum(v * v for v in y.values()))
    pairs = [(a, b) for a, b in combinations(ORDER, 2)
             if CONCEPTS["pages"][a] != CONCEPTS["pages"][b] and abs(ORDER.index(a) - ORDER.index(b)) > 1]
    sims = {"words": {pr: jac(*pr) for pr in pairs}, "trigrams": {pr: cos(*pr) for pr in pairs}}
    def stat(attr, simk, assign):
        same, diff = [], []
        for a, b in pairs:
            sa, sb = assign[CONCEPTS["pages"][a]], assign[CONCEPTS["pages"][b]]
            (same if CONCEPTS["attributes"][sa][attr] == CONCEPTS["attributes"][sb][attr] else diff).append(sims[simk][(a, b)])
        return (np.mean(same) - np.mean(diff)) if same and diff else 0.0
    ident = dict(zip(SIGNS, SIGNS)); res = {}
    P = perms(N_ATTR_PERM, rng)
    for attr in ("planet", "element", "season"):
        for simk in ("words", "trigrams"):
            r = stat(attr, simk, ident); nl = [stat(attr, simk, a) for a in P]
            res[f"{attr}/{simk}"] = {"delta": r, "p": (1 + sum(x >= r for x in nl)) / (1 + len(nl))}
    return res


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke-null", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(); t0 = time.time(); rng = random.Random(SEED)
    W1, W2 = zodiac_words()
    log("words per page W1/W2:", {p: (len(W1[p]), len(W2[p])) for p in ORDER})
    langs = list(CONCEPTS["languages"])
    configs = {}
    for lang in langs:
        tg = targets(lang)
        for kind in ("K1", "K2"):
            for wsn, ws in (("W1", W1), ("W2", W2)):
                nU, nL, cand = build(ws, kind, tg)
                configs[f"{lang}/{kind}/{wsn}"] = (nU, nL, cand)
    log(f"configs {len(configs)}; candidates per config (true assignment): " +
        ", ".join(f"{k}:{len(active_for(v[2], dict(zip(SIGNS, SIGNS))))}" for k, v in list(configs.items())[:6]) + f" ... | {time.time() - t0:.0f}s")
    ident = dict(zip(SIGNS, SIGNS))
    P = perms(N_PERM, rng)
    if a.smoke_null:
        # NULL ONLY (no true assignment): ceiling check on 5 permutations x 4 configs
        ks = list(configs)[:2] + list(configs)[-2:]
        with Pool(a.workers) as pool:
            r = pool.map(job, [(k, *configs[k][:3], P[i], rng.randrange(1 << 30)) for k in ks for i in range(5)])
        log("smoke null pages covered:", [(n, c) for n, c in r]); return
    # calibration first
    cal = {}
    with Pool(a.workers) as pool:
        for lang, share in (("latin", 1.0), ("french_occitan", 1.0), ("hebrew", 1.0), ("latin_half", 0.5)):
            pw = plant(W2, lang.replace("_half", ""), rng, share); nU, nL, cand = build(pw, "K1", targets(lang.replace("_half", "")))
            jobs = [("real", nU, nL, cand, ident, rng.randrange(1 << 30))] + [(f"p{i}", nU, nL, cand, P[i], rng.randrange(1 << 30)) for i in range(N_PERM_CAL)]
            r = dict(pool.map(job, jobs)); s = r["real"][0]; nl = [r[f"p{i}"][0] for i in range(N_PERM_CAL)]
            cal[lang] = {"real": s, "null": nl, "p": (1 + sum(x >= s for x in nl)) / (1 + len(nl))}
            log(f"calibration {lang}: planted pages covered {s}/12, null mean {np.mean(nl):.2f} max {max(nl)}, p {cal[lang]['p']:.3f} | {time.time() - t0:.0f}s")
        validated = all(cal[l]["p"] <= 0.01 for l in ("latin", "french_occitan", "hebrew"))
        R = {}
        for k, (nU, nL, cand) in configs.items():
            jobs = [("real", nU, nL, cand, ident, rng.randrange(1 << 30))] + [(f"p{i}", nU, nL, cand, P[i], rng.randrange(1 << 30)) for i in range(N_PERM)]
            r = dict(pool.map(job, jobs))
            R[k] = {"real": r["real"][0], "real_sat": r["real"][1], "null": [r[f"p{i}"][0] for i in range(N_PERM)]}
            nl = R[k]["null"]; R[k]["p"] = (1 + sum(x >= R[k]["real"] for x in nl)) / (1 + N_PERM)
            log(f"{k:28s} real {R[k]['real']:2d}/12  null mean {np.mean(nl):5.2f} sd {np.std(nl):4.2f} max {max(nl):2d}  p {R[k]['p']:.2f} | {time.time() - t0:.0f}s")
    # max-T
    def zs(k, x, excl=None):
        nl = [v for i, v in enumerate(R[k]["null"]) if i != excl]; sd = np.std(nl) or 1.0
        return (x - np.mean(nl)) / sd
    Treal = max(zs(k, R[k]["real"]) for k in R)
    Tnull = [max(zs(k, R[k]["null"][i], excl=i) for k in R) for i in range(N_PERM)]
    pT = (1 + sum(x >= Treal for x in Tnull)) / (1 + N_PERM)
    bestk = max(R, key=lambda k: zs(k, R[k]["real"]))
    if not validated:
        verdict = "VOID (calibration failed)"
    elif pT <= 0.01:
        verdict = f"CLAIM (max-T {Treal:.2f}, p {pT:.3f}, best {bestk}) - seed check and blind reading follow"
    else:
        verdict = f"NO CLAIM (max-T {Treal:.2f}, p {pT:.2f}, best {bestk})"
    attr = attr_test(W2, random.Random(SEED + 1))
    for k, v in attr.items():
        log(f"  attribute {k:18s} delta {v['delta']:+.4f} p {v['p']:.3f}")
    log(f"VERDICT {verdict} | calibration {[(l, c['real'], round(c['p'], 3)) for l, c in cal.items()]} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E095", "seed": SEED, "calibration": cal, "validated": validated, "results": R,
                               "maxT": Treal, "maxT_null": Tnull, "p_maxT": pT, "best_config": bestk, "attributes": attr,
                               "verdict": verdict, "runtime_s": time.time() - t0}, indent=1))


if __name__ == "__main__":
    main()
