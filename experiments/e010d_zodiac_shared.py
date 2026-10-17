"""E010D: do the two pages of the same zodiac month (April: f70v1/f71r; May: f71v/f72r1) share material?

Pre-registered in reports/E010D_PREREG.md (sha256 checked below; the run aborts if the file changed).
  T1  codebook: shared rare word types (f_rest <= 3), size-normalised, same-month vs other zodiac pairs (exact, 1485)
  T2  codebook vs adjacency: same statistic vs the 23 other consecutive pairs of the hand-4 run f67r1-f73v (exact, 276)
  T3  verbose cipher, unknown tables: idf-weighted chunk/word/bigram cosine, same adjacency null (exact, 276)
Synthetic power / FPR: a1 random codebook, a2 novel codebook, b random Naibbe-like tables, c none, d drift, a1+d, b+d.
Nothing here reads or glosses any Voynich word.

Run: caffeinate -ims .venv/bin/python experiments/e010d_zodiac_shared.py [--reps 200] [--workers 3]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.anchors import ZODIAC, ZODIAC_FOLIOS, _parsed, locked_leaves  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

PREREG = ROOT / "reports/E010D_PREREG.md"
PREREG_SHA256 = "59fbea3e072848e3f692740ff1833c977cf8b223733b467fe446c17ee6dbb3af"
PREREG_WRITTEN_UTC = "2026-10-17T08:51:41Z"
OUT = ROOT / "experiments/results/e010d.json"
SEED = 20261019
ALPHA = 0.01
K_RARE = 3
RHO_DRIFT = 0.25
NGRAM_N = (3, 4, 5)

H_RUN = ["f67r1", "f67r2", "f67v2", "f67v1", "f68r1", "f68r2", "f68r3", "f68v3", "f68v2", "f68v1", "f69r", "f69v",
         "f70r1", "f70r2"] + ZODIAC_FOLIOS
Z_IDX = [H_RUN.index(f) for f in ZODIAC_FOLIOS]           # positions of zodiac pages in H
SAME = [(H_RUN.index("f70v1"), H_RUN.index("f71r")), (H_RUN.index("f71v"), H_RUN.index("f72r1"))]
MONTH = {f: m for f, _, m, _, _ in ZODIAC}


# ------------------------------------------------------------------ pair sets and exact nulls
def disjoint_pair_configs(pairs):
    """All unordered choices of 2 disjoint pairs from `pairs` (list of (a,b)); returns index pairs into `pairs`."""
    return [(i, j) for i, j in combinations(range(len(pairs)), 2) if not set(pairs[i]) & set(pairs[j])]


ZPAIRS = list(combinations(Z_IDX, 2))                       # 66 zodiac pairs (H indices)
APAIRS = [(i, i + 1) for i in range(len(H_RUN) - 1)]         # 25 consecutive pairs of the run
ZAPAIRS = [(Z_IDX[i], Z_IDX[i + 1]) for i in range(len(Z_IDX) - 1)]  # 11 consecutive zodiac pairs
CFG_ALL, CFG_ADJ, CFG_ZADJ = (disjoint_pair_configs(P) for P in (ZPAIRS, APAIRS, ZAPAIRS))
assert len(CFG_ALL) == 1485 and len(CFG_ADJ) == 276 and len(CFG_ZADJ) == 45


def exact_p(x, pairs, cfgs):
    """T = mean(chosen 2) - mean(rest) is monotone in the chosen sum, so p = share of configs with sum >= observed."""
    x = np.asarray(x, dtype=float)
    obs_idx = [pairs.index(m) for m in SAME]
    obs = x[obs_idx].sum()
    sums = np.array([x[i] + x[j] for i, j in cfgs])
    rest = np.delete(x, obs_idx)
    T = obs / 2 - rest.mean()
    return float(T), float((sums >= obs - 1e-12).mean())


def holm(ps: dict, alpha=ALPHA):
    items = sorted(ps.items(), key=lambda kv: kv[1]); m = len(items); out = {}; stop = False
    for k, (name, p) in enumerate(items):
        thr = alpha / (m - k)
        rej = (not stop) and p <= thr
        stop = stop or not rej
        out[name] = {"p": p, "holm_threshold": thr, "reject": rej}
    return out


# ------------------------------------------------------------------ text features
@lru_cache(maxsize=None)
def tok_feats(w: str) -> tuple:
    s = "^" + w + "$"
    f = {"N:" + s[i:i + n] for n in NGRAM_N for i in range(len(s) - n + 1)}
    f.add("W:" + w)
    return tuple(f)


def page_counters(lines):
    """lines: list of token lists (None = non-clean token, breaks bigrams). Returns (word counts, feature df, n)."""
    wc, fdf, n = Counter(), Counter(), 0
    for line in lines:
        prev = None
        for w in line:
            if w is None:
                prev = None; continue
            n += 1; wc[w] += 1
            for g in tok_feats(w):
                fdf[g] += 1
            if prev is not None:
                fdf["B:" + prev + " " + w] += 1
            prev = w
    return wc, fdf, n


class Corpus:
    """DEV = base (everything outside H) + the 26 H pages. All 'rest' quantities subtract the two pair pages."""

    def __init__(self, base, pages_lines):
        self.bwc, self.bfdf, self.bn = base
        self.pc = [page_counters(l) for l in pages_lines]
        self.hwc, self.hfdf, self.hn = Counter(), Counter(), 0
        for wc, fdf, n in self.pc:
            self.hwc.update(wc); self.hfdf.update(fdf); self.hn += n
        self.N = self.bn + self.hn

    def shared_rare(self, p, q, K=K_RARE):
        (wp, _, np_), (wq, _, nq) = self.pc[p], self.pc[q]
        nrest = self.N - np_ - nq
        out = []
        for w in wp.keys() & wq.keys():
            fr = self.bwc[w] + self.hwc[w] - wp[w] - wq[w]
            if fr <= K:
                out.append((w, fr, math.log2((nrest + 1) / (fr + 1))))
        return out

    def s(self, p, q, K=K_RARE, normalise=True):
        S = sum(x[2] for x in self.shared_rare(p, q, K))
        return S / (self.pc[p][2] * self.pc[q][2] / 1e4) if normalise else S

    def idf(self, g, p, q):
        df = self.bfdf[g] + self.hfdf[g] - self.pc[p][1][g] - self.pc[q][1][g]
        return math.log((self.N - self.pc[p][2] - self.pc[q][2] + 1) / (df + 1))

    def c(self, p, q, top=0):
        fp, fq = self.pc[p][1], self.pc[q][1]
        sp = sum(self.idf(g, p, q) ** 2 for g in fp)
        sq = sum(self.idf(g, p, q) ** 2 for g in fq)
        sh = [(g, self.idf(g, p, q)) for g in fp.keys() & fq.keys()]
        val = sum(v * v for _, v in sh) / math.sqrt(sp * sq) if sp and sq else 0.0
        if top:
            return val, sorted(sh, key=lambda t: -t[1])[:top]
        return val


def run_tests(C: Corpus, secondary=False):
    sz = {pr: C.s(*pr) for pr in set(ZPAIRS) | set(APAIRS)}
    cz = {pr: C.c(*pr) for pr in (set(APAIRS) | set(ZPAIRS) if secondary else set(APAIRS))}
    T1, p1 = exact_p([sz[pr] for pr in ZPAIRS], ZPAIRS, CFG_ALL)
    T2, p2 = exact_p([sz[pr] for pr in APAIRS], APAIRS, CFG_ADJ)
    T3, p3 = exact_p([cz[pr] for pr in APAIRS], APAIRS, CFG_ADJ)
    res = {"T1": {"T": T1, "p": p1}, "T2": {"T": T2, "p": p2}, "T3": {"T": T3, "p": p3}}
    res["holm"] = holm({"T1": p1, "T2": p2, "T3": p3})
    if secondary:
        sec = {}
        sec["T1stat_zodiac_adjacency_null_45"] = dict(zip(("T", "p"), exact_p([sz[pr] for pr in ZAPAIRS], ZAPAIRS, CFG_ZADJ)))
        sec["T3stat_all_relabel_null_1485"] = dict(zip(("T", "p"), exact_p([cz[pr] for pr in ZPAIRS], ZPAIRS, CFG_ALL)))
        for K in (0, 10):
            sec[f"T1_K{K}"] = dict(zip(("T", "p"), exact_p([C.s(*pr, K=K) for pr in ZPAIRS], ZPAIRS, CFG_ALL)))
            sec[f"T2_K{K}"] = dict(zip(("T", "p"), exact_p([C.s(*pr, K=K) for pr in APAIRS], APAIRS, CFG_ADJ)))
        sec["T1_unnormalised"] = dict(zip(("T", "p"), exact_p([C.s(*pr, normalise=False) for pr in ZPAIRS], ZPAIRS, CFG_ALL)))
        sec["T2_unnormalised"] = dict(zip(("T", "p"), exact_p([C.s(*pr, normalise=False) for pr in APAIRS], APAIRS, CFG_ADJ)))
        res["secondary"] = sec
        res["pair_scores"] = {"s_adjacent": {f"{H_RUN[a]}|{H_RUN[b]}": round(sz[(a, b)], 4) for a, b in APAIRS},
                              "c_adjacent": {f"{H_RUN[a]}|{H_RUN[b]}": round(cz[(a, b)], 5) for a, b in APAIRS},
                              "s_zodiac_mean_other": float(np.mean([sz[pr] for pr in ZPAIRS if pr not in SAME]))}
    return res


# ------------------------------------------------------------------ data
def dev_data():
    """Base counters (DEV outside H), real H page lines, DEV-outside-H token list, per-page line layout."""
    locked = locked_leaves()
    pages, toks = _parsed()
    base_lines, h_lines = {}, {f: {} for f in H_RUN}
    for t in toks:
        if t.leaf in locked:
            continue
        w = t.eva if t.is_clean else None
        if t.folio in h_lines:
            h_lines[t.folio].setdefault(t.line_no, (t.locus_type, []))[1].append(w)
        else:
            base_lines.setdefault((t.folio, t.line_no), []).append(w)
    base = page_counters(list(base_lines.values()))
    H = [[v[1] for _, v in sorted(h_lines[f].items())] for f in H_RUN]
    layout = [[(v[0], sum(x is not None for x in v[1])) for _, v in sorted(h_lines[f].items())] for f in H_RUN]
    for zi in Z_IDX:
        assert all(lt in ("L", "C") for lt, n in layout[zi] if n), H_RUN[zi]
    filler = [w for l in base_lines.values() for w in l if w is not None]
    meta = {f: {"quire": pages[f].quire, "leaf": pages[f].leaf, "illustration": pages[f].illustration,
                "hand": pages[f].hand, "currier": pages[f].currier} for f in H_RUN}
    return base, H, layout, filler, meta


def relation(meta, a, b):
    ma, mb = meta[a], meta[b]
    if ma["leaf"] == mb["leaf"]:
        r = "same leaf (foldout panels or recto/verso)"
    else:
        r = "facing pages of an opening"
    if ma["quire"] != mb["quire"]:
        r += f", quire boundary {ma['quire']}/{mb['quire']}"
    return r


# ------------------------------------------------------------------ synthetic manuscripts
_G = {}


def _init(base, layout, filler):
    _G["base"], _G["layout"], _G["filler"] = base, layout, filler
    _G["types"] = sorted(set(filler))
    _G["dev_types"] = set(_G["types"])


def random_tables(rng):
    tab = NX.load_tables()
    new = {}
    for state in ("unigram", "prefix", "suffix"):
        for t in NX.TABLES:
            letters = sorted(l for (s, tt, l) in tab if s == state and tt == t)
            glyphs = [tab[(state, t, l)] for l in letters]
            rng.shuffle(glyphs)
            new.update({(state, t, l): g for l, g in zip(letters, glyphs)})
    return {"tables": new, "letters": sorted({l for (_, _, l) in new}),
            "unigrams": {g for (s, _, _), g in new.items() if s == "unigram"}, "space_removal": 0.0}


def novel_word(rng, used):
    T = _G["types"]
    while True:
        a, b = rng.choice(T), rng.choice(T)
        w = a[:max(1, (len(a) + 1) // 2)] + b[len(b) // 2:]
        if w not in _G["dev_types"] and w not in used and len(w) >= 3:
            return w


def synth_manuscript(mech, rng):
    filler, layout = _G["filler"], _G["layout"]
    drift = "d" in mech.split("+")
    pages, prev = [], None
    for lay in layout:
        lines = []
        for lt, n in lay:
            toks = [filler[rng.randrange(len(filler))] for _ in range(n)]
            if drift and prev:
                toks = [rng.choice(prev) if rng.random() < RHO_DRIFT else w for w in toks]
            lines.append([lt, toks])
        prev = [w for _, t in lines for w in t]
        pages.append(lines)
    kind = mech.split("+")[0]
    months = sorted(set(MONTH.values()), key=list(MONTH.values()).index)
    if kind in ("a1", "a2"):
        used = []
        for _ in months:
            used.append(rng.choice(_G["types"]) if kind == "a1" else novel_word(rng, used))
            while kind == "a1" and used.count(used[-1]) > 1:
                used[-1] = rng.choice(_G["types"])
        code = dict(zip(months, used))
        for zi in Z_IDX:
            pos = [(li, j) for li, (_, t) in enumerate(pages[zi]) for j in range(len(t))]
            li, j = rng.choice(pos)
            pages[zi][li][1][j] = code[MONTH[H_RUN[zi]]]
    elif kind == "b":
        key = random_tables(rng)
        for zi in Z_IDX:
            enc, _ = NX.encode_tokens(MONTH[H_RUN[zi]], key, rng.randrange(2 ** 31))
            cl = [li for li, (lt, t) in enumerate(pages[zi]) if lt == "C" and t]
            fit = [li for li in cl if len(pages[zi][li][1]) >= len(enc)]
            li = rng.choice(fit) if fit else max(cl, key=lambda i: len(pages[zi][i][1]))
            t = pages[zi][li][1]
            s = rng.randrange(0, max(1, len(t) - len(enc) + 1))
            t[s:s + len(enc)] = enc
    return [[t for _, t in pg] for pg in pages]


def synth_replicate(args):
    mech, rep = args
    seed = SEED + int(hashlib.sha256(f"{mech}|{rep}".encode()).hexdigest(), 16) % 10 ** 8
    rng = random.Random(seed)
    C = Corpus(_G["base"], synth_manuscript(mech, rng))
    r = run_tests(C)
    return {"mech": mech, "rep": rep, "p": {k: r[k]["p"] for k in ("T1", "T2", "T3")},
            "holm": {k: r["holm"][k]["reject"] for k in ("T1", "T2", "T3")}}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--mechs", default="a1,a2,b,c,d,a1+d,b+d")
    a = ap.parse_args()
    sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    if sha != PREREG_SHA256:
        raise SystemExit(f"prereg changed ({sha}); create E010D_PREREG_v2.md and log in FAILURES.md")
    t0 = time.time()
    base, H, layout, filler, meta = dev_data()
    res = {"experiment": "E010D", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": sha,
           "prereg_written_utc": PREREG_WRITTEN_UTC, "seed": SEED, "alpha_familywise": ALPHA, "K": K_RARE,
           "command": " ".join(["experiments/e010d_zodiac_shared.py"] + sys.argv[1:]),
           "H_run": H_RUN, "page_meta": meta,
           "page_sizes_clean_tokens": {f: sum(n for _, n in l) for f, l in zip(H_RUN, layout)},
           "adjacent_pairs": [{"pair": f"{H_RUN[x]}|{H_RUN[y]}", "same_month": (x, y) in SAME,
                               "relation": relation(meta, H_RUN[x], H_RUN[y])} for x, y in APAIRS],
           "n_configs": {"all_relabel": len(CFG_ALL), "adjacent": len(CFG_ADJ), "zodiac_adjacent": len(CFG_ZADJ)},
           "dev_tokens_outside_H": base[2]}

    # --- synthetic controls first (power), then the real pages
    mechs = a.mechs.split(",")
    jobs = [(m, r) for m in mechs for r in range(a.reps)]
    rows = []
    with ProcessPoolExecutor(max_workers=min(3, a.workers), initializer=_init, initargs=(base, layout, filler)) as ex:
        for i, r in enumerate(ex.map(synth_replicate, jobs, chunksize=8)):
            rows.append(r)
            if i % 200 == 0:
                print("synthetic", i, len(jobs), round(time.time() - t0), "s", flush=True)
    syn = {}
    for m in mechs:
        sel = [r for r in rows if r["mech"] == m]
        syn[m] = {"n": len(sel),
                  "rate_p_below_alpha": {t: float(np.mean([r["p"][t] < ALPHA for r in sel])) for t in ("T1", "T2", "T3")},
                  "rate_holm_reject": {t: float(np.mean([r["holm"][t] for r in sel])) for t in ("T1", "T2", "T3")},
                  "codebook_joint_T1_T2_holm": float(np.mean([r["holm"]["T1"] and r["holm"]["T2"] for r in sel])),
                  "median_p": {t: float(np.median([r["p"][t] for r in sel])) for t in ("T1", "T2", "T3")}}
    res["synthetic"] = syn
    print(json.dumps(syn, indent=1), flush=True)

    # --- real pages
    C = Corpus(base, H)
    real = run_tests(C, secondary=True)
    desc = {}
    loc = {}
    for f, lines, lay in zip(H_RUN, H, layout):
        for (lt, _), l in zip(lay, lines):
            for w in l:
                if w is not None:
                    loc.setdefault((f, w), set()).add(lt)
    for x, y in SAME:
        fx, fy = H_RUN[x], H_RUN[y]
        sr = sorted(C.shared_rare(x, y, K=10), key=lambda t: t[1])
        cval, top = C.c(x, y, top=15)
        desc[f"{fx}|{fy}"] = {
            "month": MONTH[fx], "s": C.s(x, y), "c": cval,
            "shared_types_f_rest_le_10": [{"word": w, "f_rest": fr, "counted_in_T1": fr <= K_RARE,
                                           "locus_types": {fx: sorted(loc[(fx, w)]), fy: sorted(loc[(fy, w)])}}
                                          for w, fr, _ in sr],
            "n_shared_word_types_total": len(C.pc[x][0].keys() & C.pc[y][0].keys()),
            "top15_shared_T3_features_by_idf": [{"feature": g, "idf": round(v, 3)} for g, v in top]}
    res["voynich"] = real
    res["descriptive_same_month"] = desc

    # --- decisions per prereg section 4
    hv = real["holm"]
    flags = {t: (syn["c"]["rate_p_below_alpha"][t] > 0.03 if "c" in syn else None) for t in ("T1", "T2", "T3")}
    flags_drift = {t: (syn["d"]["rate_holm_reject"][t] > 0.03 if "d" in syn else None) for t in ("T1", "T2", "T3")}
    pow_cb = syn.get("a1", {}).get("codebook_joint_T1_T2_holm")
    pow_cb2 = syn.get("a2", {}).get("codebook_joint_T1_T2_holm")
    pow_v = syn.get("b", {}).get("rate_holm_reject", {}).get("T3")
    calib_ok = lambda ts: not any(flags[t] or flags_drift[t] for t in ts)

    def verdict(supported, power, ok, sep_note=None):
        if supported and ok:
            return "SUPPORTED"
        if supported and not ok:
            return "NOT SUPPORTED (test miscalibrated on controls)"
        base_v = "NEGATIVE" if power is not None and power >= 0.8 else "UNINFORMATIVE (power < 0.8)"
        return base_v + (f"; {sep_note}" if sep_note else "")
    note = ("T1 rejected but T2 not: same-month sharing not separable from adjacency"
            if hv["T1"]["reject"] and not hv["T2"]["reject"] else None)
    # T1 is expected to fail the drift guard (prereg s4); the codebook decision requires T2's calibration.
    dec = {"codebook_a1": verdict(hv["T1"]["reject"] and hv["T2"]["reject"], pow_cb,
                                  not (flags["T1"] or flags["T2"] or flags_drift["T2"]), note),
           "codebook_a2_scoped": verdict(hv["T1"]["reject"] and hv["T2"]["reject"], pow_cb2,
                                         not (flags["T1"] or flags["T2"] or flags_drift["T2"]), note),
           "verbose_b": verdict(hv["T3"]["reject"], pow_v, calib_ok(["T3"]))}
    res["calibration_flags"] = {"fpr_c_gt_0.03": flags, "holm_reject_drift_d_gt_0.03": flags_drift}
    res["power_used"] = {"codebook_a1_joint": pow_cb, "codebook_a2_joint": pow_cb2, "verbose_b_T3": pow_v}
    res["decision"] = dec
    res["wall_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    from vcl.eval.ledger import append
    rows_l = [dict(experiment="E010D", model="zodiac_same_month_sharing_v1", checkpoint_sha256=f"prereg={sha[:12]}",
                   split="DEV(hand-4 run f67r1-f73v)", metric=f"p_{t}", value=round(hv[t]["p"], 6),
                   command=res["command"], notes=f"holm_reject={hv[t]['reject']}; T={real[t]['T']:.4g}")
              for t in ("T1", "T2", "T3")]
    rows_l += [dict(experiment="E010D", model="zodiac_same_month_sharing_v1", checkpoint_sha256=f"prereg={sha[:12]}",
                    split="synthetic", metric=m, value=v, command=res["command"], notes=f"decision {dec}")
               for m, v in (("power_codebook_a1", pow_cb), ("power_codebook_a2", pow_cb2), ("power_verbose_b_T3", pow_v),
                            ("fpr_c_T1", syn.get("c", {}).get("rate_p_below_alpha", {}).get("T1")),
                            ("fpr_c_T2", syn.get("c", {}).get("rate_p_below_alpha", {}).get("T2")),
                            ("fpr_c_T3", syn.get("c", {}).get("rate_p_below_alpha", {}).get("T3")))]
    append(rows_l)
    print(json.dumps({k: res[k] for k in ("decision", "power_used", "calibration_flags", "wall_s")}, indent=1))
    print(json.dumps({t: real[t] for t in ("T1", "T2", "T3")}, indent=1), json.dumps(hv, indent=1))
    print(json.dumps(real["secondary"], indent=1))
    print(json.dumps(desc, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
