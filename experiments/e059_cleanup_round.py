"""E059 (clean-up round): line position and writing session as confounds. See reports/E059_PREREG.md.

Part A1  five alternations (e/ee, r/l, t/k, d+-, q+-) in ONE logistic model: form ~ pair + POS + PARA + PREVY + HAND
         + QUIRE + SEC. Drop-one LRT per factor, share of pair-only deviance, bias-corrected by 50 within-pair
         permutations, 100 page-cluster bootstraps for stability. PRESENT: p < 0.001 and share_excess >= 0.01.
         Known-answer controls planted on the d+- tokens (line / scribe / location / junction habits, 10% flips).
Part A2  next-glyph distributions after e, ee, eee (JS divergence), calibrated on Latin (floor: random ee doubling;
         ceiling: e/i and r/l contrasts).
Part B1  page-pair cosine similarity (WORD counts, GLYPH bigrams) by physical relation: L0 same leaf, L1 same sheet
         other leaf, R1 adjacent in reading order (other sheet), Q same quire other sheet, S other quire; pairs with
         the same scribe and section only. Null: 2,000 shuffles of physical slots within (quire, hand, section).
Part B2  I_word (E019 definition) under 32 reading-order chunks, 49 sheets, 49 reading-order chunks.
Part B3  label echo: own page vs same leaf, other leaf of the sheet, adjacent page, random same-section page, each
         against frequency-matched words; sign-flip test own vs other leaf; absolute rates by section.
Run: caffeinate -ims .venv/bin/python experiments/e059_cleanup_round.py
"""
from __future__ import annotations

import json, math, random, re, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e038_sign_inventory_v2 import ALTS, keep  # noqa: E402

SEED = 59059
OUT = ROOT / "experiments/results/e059.json"
PERMS_A, BOOT_A, RIDGE = 50, 100, 1e-4
ALPHA_A, SHARE_BAR = 0.001, 0.01
PERMS_B, ALPHA_B = 2000, 0.01
MIN_PAGE_TOKENS, MIN_LABEL_TEXT, N_RANDOM_PAGES, BASE_DRAWS = 50, 20, 5, 20
BORDER = (0.005, 0.02)
FACTORS = ["POS", "PARA", "PREVY", "HAND", "QUIRE", "SEC"]
LOC_SET = set("DEFGH")


def log(*a):
    print(*a, flush=True)


# =============================================================================================== shared helpers
def folio_key(folio):
    m = re.match(r"f(\d+)([rv]?)(\d*)", folio)
    if not m:
        return (10 ** 6, folio, 0)
    return (int(m.group(1)), m.group(2), int(m.group(3) or 0))


def dev_tokens():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    all_folios = sorted({t.folio for t in toks}, key=folio_key)          # names only, for reading order
    return [t for t in toks if t.leaf not in locked], all_folios, sorted(locked, key=lambda x: (len(x), x))


# =============================================================================================== Part A1
def pair_roles(wc):
    roles = {}
    for name, fn in ALTS.items():
        pairs = keep(fn(wc), wc)
        role, used = {}, set()
        for i, (a, b) in enumerate(pairs):
            if a in used or b in used:
                continue
            used |= {a, b}; role[a] = (i, 0); role[b] = (i, 1)
        roles[name] = role
    return roles


def line_rows(P):
    """Per prose token: pos, para, prevy plus hand/quire/sec/folio. P must be in file order."""
    rows, lines = [], defaultdict(list)
    for t in P:
        lines[(t.folio, t.line_no)].append(t)
    for key, ts in lines.items():
        ts.sort(key=lambda t: t.idx)
        for j, t in enumerate(ts):
            n = t.n_in_line
            pos = "first" if t.idx == 0 else "last" if t.idx == n - 1 else "mid"
            prev = ts[j - 1] if j and ts[j - 1].idx == t.idx - 1 else None   # adjacent clean neighbour only
            rows.append(dict(eva=t.eva, POS=pos, PARA=int(t.para_start), PREVY=int(bool(prev) and prev.eva.endswith("y")),
                             HAND=t.hand, QUIRE=t.quire, SEC=t.illustration, folio=t.folio))
    return rows


def design(T):
    """Columns: pair dummies then factor dummies; returns X, y, groups {factor: [col indices]}, pages."""
    pairs = sorted({r["p"] for r in T})
    pidx = {p: i for i, p in enumerate(pairs)}
    cols, groups = [], {}
    n = len(T)
    X = [np.zeros((n, len(pairs)))]
    for i, r in enumerate(T):
        X[0][i, pidx[r["p"]]] = 1.0
    k = len(pairs)
    levels = {"POS": ["first", "last"], "PARA": [1], "PREVY": [1],
              "HAND": [h for h in ["2", "3", "4", "5"] if any(r["HAND"] == h for r in T)]}
    qc = Counter(r["QUIRE"] for r in T); qref = qc.most_common(1)[0][0]
    levels["QUIRE"] = [q for q in sorted(qc) if q != qref]
    sc = Counter(r["SEC"] for r in T)
    levels["SEC"] = [s for s in sorted(sc) if s != "H"]
    for f in FACTORS:
        idx = []
        for lv in levels[f]:
            col = np.array([1.0 if r[f] == lv else 0.0 for r in T])
            if col.sum() == 0 or col.sum() == n:
                continue
            X.append(col[:, None]); idx.append(k); k += 1
        groups[f] = idx
    X = np.hstack(X)
    y = np.array([r["f"] for r in T], dtype=float)
    pages = np.array([r["folio"] for r in T])
    return X, y, groups, pages, qref


def fit_logit(X, y, w=None, ridge=RIDGE, iters=60):
    """IRLS logistic regression with a small ridge; returns deviance (weighted)."""
    n, k = X.shape
    w = np.ones(n) if w is None else w

    def deviance(b):
        eta = np.clip(X @ b, -30, 30)
        mu = np.clip(1 / (1 + np.exp(-eta)), 1e-12, 1 - 1e-12)
        return -2 * float(np.sum(w * (y * np.log(mu) + (1 - y) * np.log(1 - mu)))) + ridge * float(b @ b)

    beta = np.zeros(k)
    dev_old = deviance(beta)
    for _ in range(iters):
        eta = np.clip(X @ beta, -30, 30)
        mu = np.clip(1 / (1 + np.exp(-eta)), 1e-9, 1 - 1e-9)
        W = w * mu * (1 - mu)
        z = eta + (y - mu) / (mu * (1 - mu))
        XtW = X.T * W
        A = XtW @ X + ridge * np.eye(k)
        new = np.linalg.solve(A, XtW @ z)
        dev = deviance(new)
        step = 1.0
        while dev > dev_old + 1e-9 and step > 1e-4:        # step halving keeps the deviance decreasing
            step /= 2
            new = beta + step * (new - beta)
            dev = deviance(new)
        beta = new
        if abs(dev_old - dev) < 1e-7 * max(1.0, dev):
            dev_old = dev
            break
        dev_old = dev
    return dev_old - ridge * float(beta @ beta)


def drop_one(X, y, groups, npairs, w=None):
    full = fit_logit(X, y, w)
    d0 = fit_logit(X[:, :npairs], y, w)
    out = {}
    for f, idx in groups.items():
        if not idx:
            out[f] = dict(lrt=0.0, df=0, p=1.0, share=0.0); continue
        keep_cols = [c for c in range(X.shape[1]) if c not in set(idx)]
        red = fit_logit(X[:, keep_cols], y, w)
        lrt = max(0.0, red - full)
        out[f] = dict(lrt=lrt, df=len(idx), p=float(chi2.sf(lrt, len(idx))), share=lrt / d0 if d0 else float("nan"))
    return full, d0, out


def analyse_alt(T, rng, label):
    t0 = time.time()
    X, y, groups, pages, qref = design(T)
    npairs = len({r["p"] for r in T})
    full, d0, obs = drop_one(X, y, groups, npairs)
    # bias: permute f within pair cells
    byp = defaultdict(list)
    for i, r in enumerate(T):
        byp[r["p"]].append(i)
    null = defaultdict(list)
    for _ in range(PERMS_A):
        yp = y.copy()
        for ii in byp.values():
            yp[ii] = rng.sample(list(y[ii]), len(ii))
        _, _, o = drop_one(X, yp, groups, npairs)
        for f in FACTORS:
            null[f].append(o[f]["share"])
    # stability: page-cluster bootstrap (weights = page draw counts)
    upages = sorted(set(pages))
    boot = defaultdict(list)
    for _ in range(BOOT_A):
        draw = Counter(rng.choices(upages, k=len(upages)))
        w = np.array([draw.get(p, 0) for p in pages], dtype=float)
        if w.sum() == 0:
            continue
        _, _, o = drop_one(X, y, groups, npairs, w)
        for f in FACTORS:
            boot[f].append(o[f]["share"] - float(np.mean(null[f])))
    res = {"tokens": len(T), "n_pairs": npairs, "deviance_full": full, "deviance_pair_only": d0, "quire_ref": qref,
           "factors": {}}
    for f in FACTORS:
        se = obs[f]["share"] - float(np.mean(null[f]))
        v = "PRESENT" if obs[f]["p"] < ALPHA_A and se >= SHARE_BAR else "TRACE" if obs[f]["p"] < ALPHA_A else "ABSENT"
        res["factors"][f] = dict(obs[f], share_null_mean=float(np.mean(null[f])), share_excess=se,
                                 boot_ci=[float(np.percentile(boot[f], 2.5)), float(np.percentile(boot[f], 97.5))] if boot[f] else None,
                                 verdict=v)
    log(f"[A1 {label}] n {len(T)} pairs {npairs} D0 {d0:.1f} full {full:.1f} ({time.time() - t0:.0f}s)")
    for f in FACTORS:
        r = res["factors"][f]
        log(f"   {f:6s} df {r['df']:2d} LRT {r['lrt']:8.1f} p {r['p']:.2e} share {r['share']:.4f} excess {r['share_excess']:.4f} "
            f"ci {r['boot_ci']} -> {r['verdict']}")
    return res


def present(res, f):
    return res["factors"][f]["verdict"] == "PRESENT"


def headline(name, res):
    loc = present(res, "QUIRE") or present(res, "SEC")
    if name == "d+-":
        if present(res, "HAND"):
            return "C18 STANDS"
        return "C18 WAS A LINE ARTEFACT" if present(res, "POS") else "C18 NOT REPRODUCED"
    if name in ("q+-", "r/l"):
        if loc:
            return "C19 STANDS"
        if present(res, "PREVY"):
            return "JUNCTION FORM"
        if present(res, "POS"):
            return "LINE ARTEFACT"
        return "C19 NOT REPRODUCED"
    return "reported"


def part_a1(P, rng):
    wc = Counter(t.eva for t in P)
    roles = pair_roles(wc)
    rows = line_rows(P)
    out = {"alternations": {}, "controls": {}}
    for name, role in roles.items():
        T = [dict(r, p=role[r["eva"]][0], f=role[r["eva"]][1]) for r in rows if r["eva"] in role]
        if len({r["p"] for r in T}) < 10:
            out["alternations"][name] = {"tokens": len(T), "headline": "INSUFFICIENT"}
            log(f"[A1 {name}] fewer than 10 pairs: INSUFFICIENT"); continue
        res = analyse_alt(T, rng, name)
        res["headline"] = headline(name, res)
        log(f"   => {name}: {res['headline']}")
        out["alternations"][name] = res
    # known-answer controls on the d+- tokens
    role = roles["d+-"]
    base = [dict(r, p=role[r["eva"]][0]) for r in rows if r["eva"] in role]
    flip = lambda v: 1 - v if rng.random() < 0.1 else v
    plants = {"planted_line": ("POS", lambda r: int(r["POS"] == "last")),
              "planted_scribe": ("HAND", lambda r: int(r["HAND"] == "1")),
              "planted_location": ("QUIRE", lambda r: int(r["QUIRE"] in LOC_SET)),
              "planted_junction": ("PREVY", lambda r: int(r["PREVY"] == 1))}
    ok_all = True
    for cname, (target, fn) in plants.items():
        T = [dict(r, f=flip(fn(r))) for r in base]
        res = analyse_alt(T, rng, cname)
        hit = present(res, target)
        others = [f for f in FACTORS if f != target and present(res, f)]
        ok = hit and not others
        res["control"] = dict(target=target, planted_found=hit, false_present=others, pass_=ok)
        log(f"   => {cname}: target {target} found {hit}, false PRESENT {others} -> {'PASS' if ok else 'FAIL'}")
        out["controls"][cname] = res
        ok_all &= ok
    out["status"] = "VALID" if ok_all else "VOID"
    log(f"[A1] controls {'PASS' if ok_all else 'FAIL'} -> {out['status']}")
    return out


# =============================================================================================== Part A2
def next_after_runs(words, ch):
    """Counter per run length (1,2,3+) of the glyph following a maximal run of ch ('$' = end of word)."""
    out = {1: Counter(), 2: Counter(), 3: Counter()}
    pat = re.compile(re.escape(ch) + "+")
    for w in words:
        for m in pat.finditer(w):
            L = min(3, m.end() - m.start())
            out[L][w[m.end()] if m.end() < len(w) else "$"] += 1
    return out


def next_after(words, ch):
    c = Counter()
    for w in words:
        for i, g in enumerate(w):
            if g == ch:
                c[w[i + 1] if i + 1 < len(w) else "$"] += 1
    return c


def js(a, b):
    keys = set(a) | set(b)
    ta, tb = sum(a.values()), sum(b.values())
    if not ta or not tb:
        return float("nan")
    s = 0.0
    for k in keys:
        p, q = a[k] / ta, b[k] / tb
        m = (p + q) / 2
        if p: s += 0.5 * p * math.log2(p / m)
        if q: s += 0.5 * q * math.log2(q / m)
    return s


def part_a2(vwords, rng):
    from e030_reduplication import tokens as btokens
    from e035_spelling_variation import windows
    N = len(vwords)
    lat = btokens("latVUC")[windows()["latVUC"][0]:][:N]
    latF = ["".join("ee" if c == "e" and rng.random() < 0.5 else c for c in w) for w in lat]
    rv = next_after_runs(vwords, "e")
    res = {"voynich": {"n_runs": {k: sum(v.values()) for k, v in rv.items()},
                       "JS_e_ee": js(rv[1], rv[2]), "JS_ee_eee": js(rv[2], rv[3]), "JS_e_eee": js(rv[1], rv[3]),
                       "JS_r_l": js(next_after(vwords, "r"), next_after(vwords, "l")),
                       "JS_t_k": js(next_after(vwords, "t"), next_after(vwords, "k")),
                       "top_next": {k: v.most_common(6) for k, v in rv.items()}}}
    rf = next_after_runs(latF, "e")
    F = js(rf[1], rf[2])
    C_ei = js(next_after(lat, "e"), next_after(lat, "i")); C_rl = js(next_after(lat, "r"), next_after(lat, "l"))
    C = (C_ei + C_rl) / 2
    res["latin"] = {"floor_F": F, "n_runs_F": {k: sum(v.values()) for k, v in rf.items()}, "C_e_i": C_ei, "C_r_l": C_rl, "ceiling_C": C}
    t = (res["voynich"]["JS_e_ee"] - F) / (C - F) if C - F else float("nan")
    res["t"] = t
    res["verdict"] = "VOID" if C - F < 0.05 else "FREE VARIANT" if t < 0.25 else "MIXED" if t < 0.75 else "DISTINCT"
    log(f"[A2] Voynich JS e/ee {res['voynich']['JS_e_ee']:.4f} ee/eee {res['voynich']['JS_ee_eee']:.4f} e/eee {res['voynich']['JS_e_eee']:.4f}"
        f" | r/l {res['voynich']['JS_r_l']:.4f} t/k {res['voynich']['JS_t_k']:.4f} | Latin F {F:.4f} C {C:.4f} | t {t:.3f} -> {res['verdict']}")
    return res


# =============================================================================================== Part B1
def cos(a, b):
    num = sum(v * b[k] for k, v in a.items() if k in b)
    da = math.sqrt(sum(v * v for v in a.values())); db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def bigrams(words):
    c = Counter()
    for w in words:
        s = "^" + w + "$"
        c.update(zip(s, s[1:]))
    return c


def page_table(D, all_folios):
    rank = {f: i for i, f in enumerate(all_folios)}
    text, meta = defaultdict(list), {}
    for t in D:
        if t.mode != "label" and t.is_clean:
            text[t.folio].append(t.eva)
            meta[t.folio] = dict(quire=t.quire, bif=t.bifolio_id, leaf=t.leaf, hand=t.hand, sec=t.illustration, rank=rank[t.folio])
    pages = [f for f in text if len(text[f]) >= MIN_PAGE_TOKENS]
    pages.sort(key=folio_key)
    return pages, text, meta


def category(a, b):
    """Physical relation of two pages (slot dicts with quire, bif, leaf, rank)."""
    if a["quire"] != b["quire"]:
        return "S"
    if a["leaf"] == b["leaf"]:
        return "L0"
    if a["bif"] == b["bif"]:
        return "L1"
    if abs(a["rank"] - b["rank"]) == 1:
        return "R1"
    return "Q"


def cat_means(pairs, slots, sims):
    acc = defaultdict(list)
    for i, j in pairs:
        acc[category(slots[i], slots[j])].append(sims[i, j])
    return {c: float(np.mean(v)) for c, v in acc.items()}, {c: len(v) for c, v in acc.items()}


def part_b1(D, all_folios, rng):
    pages, text, meta = page_table(D, all_folios)
    n = len(pages)
    vec_w = [Counter(text[f]) for f in pages]
    vec_g = [bigrams(text[f]) for f in pages]
    simW = np.zeros((n, n)); simG = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            simW[i, j] = simW[j, i] = cos(vec_w[i], vec_w[j])
            simG[i, j] = simG[j, i] = cos(vec_g[i], vec_g[j])
    slots = [dict(quire=meta[f]["quire"], bif=meta[f]["bif"], leaf=meta[f]["leaf"], rank=meta[f]["rank"]) for f in pages]
    same = [(i, j) for i in range(n) for j in range(i + 1, n) if meta[pages[i]]["hand"] == meta[pages[j]]["hand"]
            and meta[pages[i]]["sec"] == meta[pages[j]]["sec"]]
    allp = [(i, j) for i in range(n) for j in range(i + 1, n)]
    res = {"n_pages": n, "n_same_hand_sec_pairs": len(same)}
    cells = defaultdict(list)
    for i, f in enumerate(pages):
        cells[(meta[f]["quire"], meta[f]["hand"], meta[f]["sec"])].append(i)
    for mname, sims in (("WORD", simW), ("GLYPH", simG)):
        m, cnt = cat_means(same, slots, sims)
        m_all, cnt_all = cat_means(allp, slots, sims)
        d_sess = m.get("L1", float("nan")) - m.get("Q", float("nan"))
        d_adj = m.get("R1", float("nan")) - m.get("Q", float("nan"))
        null_s, null_a = [], []
        for _ in range(PERMS_B):
            sl = list(slots)
            for ii in cells.values():
                perm = ii[:]; rng.shuffle(perm)
                for a, b in zip(ii, perm):
                    sl[a] = slots[b]
            mm, _ = cat_means(same, sl, sims)
            null_s.append(mm.get("L1", np.nan) - mm.get("Q", np.nan)); null_a.append(mm.get("R1", np.nan) - mm.get("Q", np.nan))
        null_s = np.array(null_s, dtype=float); null_a = np.array(null_a, dtype=float)
        p_s = (1 + np.sum(null_s[~np.isnan(null_s)] >= d_sess)) / (1 + np.sum(~np.isnan(null_s)))
        p_a = (1 + np.sum(null_a[~np.isnan(null_a)] >= d_adj)) / (1 + np.sum(~np.isnan(null_a)))
        z_s = (d_sess - np.nanmean(null_s)) / np.nanstd(null_s) if np.nanstd(null_s) else float("nan")
        z_a = (d_adj - np.nanmean(null_a)) / np.nanstd(null_a) if np.nanstd(null_a) else float("nan")
        v = []
        if p_s < ALPHA_B: v.append("SESSION EFFECT")
        if p_a < ALPHA_B: v.append("ADJACENCY EFFECT")
        res[mname] = dict(means_same_hand_sec=m, counts=cnt, means_all=m_all, counts_all=cnt_all,
                          delta_session=d_sess, p_session=float(p_s), z_session=float(z_s),
                          delta_adjacent=d_adj, p_adjacent=float(p_a), z_adjacent=float(z_a),
                          borderline=[k for k, p in (("session", p_s), ("adjacent", p_a)) if BORDER[0] <= p <= BORDER[1]],
                          verdict=" + ".join(v) if v else "NEITHER")
        log(f"[B1 {mname}] pages {n} pairs {len(same)} means {{{', '.join(f'{k} {m[k]:.3f} (n {cnt[k]})' for k in sorted(m))}}}"
            f" | session Δ {d_sess:+.4f} z {z_s:+.1f} p {p_s:.4f} | adjacent Δ {d_adj:+.4f} z {z_a:+.1f} p {p_a:.4f} -> {res[mname]['verdict']}")
    w = res["WORD"]["verdict"]
    res["C7_reading"] = ("C7 RESTATED: words cluster by sheet (session), not by reading order" if w == "SESSION EFFECT" else
                         "C7 STANDS as reading-order clustering" if "ADJACENCY" in w else
                         "C7 clustering is quire-level or coarser")
    log(f"[B1] {res['C7_reading']}")
    return res


# =============================================================================================== Part B2
def i_word(tokens, chunk_of, n_chunks, rng, min_n=8, n_shuf=5):
    toks = np.array(tokens); ch = np.array(chunk_of)
    wc = Counter(tokens)
    types = [w for w, c in wc.items() if c >= min_n]

    def H(counts):
        p = counts[counts > 0] / counts.sum()
        return float(-(p * np.log2(p)).sum())

    def ent(ch_arr):
        out = {}
        for w in types:
            idx = np.where(toks == w)[0]
            out[w] = H(np.bincount(ch_arr[idx], minlength=n_chunks).astype(float))
        return out

    obs = ent(ch)
    shuf = []
    for _ in range(n_shuf):
        c2 = ch.copy(); rng.shuffle(c2)
        shuf.append(ent(c2))
    return float(np.mean([np.mean([s[w] for s in shuf]) - obs[w] for w in types])), len(types)


def part_b2(P, rng):
    toks = [t.eva for t in P]
    n = len(toks)
    c32 = [(i * 32) // n for i in range(n)]
    c49 = [(i * 49) // n for i in range(n)]
    sheets = sorted({t.bifolio_id for t in P}); sid = {s: i for i, s in enumerate(sheets)}
    csh = [sid[t.bifolio_id] for t in P]
    r = {}
    r["I_reading32"], r["types"] = i_word(toks, c32, 32, random.Random(rng.random()))
    r["I_reading49"], _ = i_word(toks, c49, 49, random.Random(rng.random()))
    r["I_sheet"], _ = i_word(toks, csh, len(sheets), random.Random(rng.random()))
    r["n_sheets"] = len(sheets)
    r["ratio_sheet_over_reading49"] = r["I_sheet"] / r["I_reading49"] if r["I_reading49"] else float("nan")
    log(f"[B2] I_word reading32 {r['I_reading32']:.3f} (C7 0.387) | reading49 {r['I_reading49']:.3f} | sheet({len(sheets)}) {r['I_sheet']:.3f}"
        f" | ratio {r['ratio_sheet_over_reading49']:.2f}")
    return r


# =============================================================================================== Part B3
def part_b3(D, all_folios, rng):
    rank = {f: i for i, f in enumerate(all_folios)}
    text, labels, meta = defaultdict(Counter), defaultdict(list), {}
    for t in D:
        if not t.is_clean:
            continue
        meta[t.folio] = dict(quire=t.quire, bif=t.bifolio_id, leaf=t.leaf, sec=t.illustration, rank=rank[t.folio])
        if t.mode == "label":
            if len(t.eva) >= 3:
                labels[t.folio].append(t.eva)
        else:
            text[t.folio][t.eva] += 1
    ok_text = {f for f in text if sum(text[f].values()) >= MIN_LABEL_TEXT}
    lab_pages = sorted((f for f in labels if f in ok_text), key=folio_key)
    allc = Counter()
    for c in text.values():
        allc.update(c)
    bycount = defaultdict(list)
    for w, c in allc.items():
        bycount[min(c, 50)].append(w)

    def excess(words, T):
        hits, bases = [], []
        for w in words:
            hits.append(float(w in text[T]))
            pool = bycount.get(min(allc.get(w, 0), 50)) or bycount[1]
            bases.append(float(np.mean([rng.choice(pool) in text[T] for _ in range(BASE_DRAWS)])))
        return float(np.mean(hits)), float(np.mean(bases))

    per_page, per_sec = [], defaultdict(lambda: {"hit": [], "base": [], "n": 0})
    for f in lab_pages:
        m = meta[f]
        comp = {"OWN": [f],
                "SAME-LEAF": [g for g in ok_text if g != f and meta[g]["leaf"] == m["leaf"]],
                "OTHER-LEAF": [g for g in ok_text if meta[g]["bif"] == m["bif"] and meta[g]["leaf"] != m["leaf"]],
                "ADJACENT": [g for g in ok_text if abs(meta[g]["rank"] - m["rank"]) == 1 and meta[g]["bif"] != m["bif"]]}
        pool = sorted(g for g in ok_text if meta[g]["sec"] == m["sec"] and meta[g]["quire"] != m["quire"])
        comp["RANDOM"] = rng.sample(pool, min(N_RANDOM_PAGES, len(pool)))
        row = {"page": f, "sec": m["sec"], "n_labels": len(labels[f]), "cats": {}}
        for cat, Ts in comp.items():
            vals = [excess(labels[f], T) for T in Ts]
            if vals:
                h = float(np.mean([v[0] for v in vals])); b = float(np.mean([v[1] for v in vals]))
                row["cats"][cat] = dict(hit=h, base=b, excess=h - b, n_pages=len(Ts))
        per_page.append(row)
        own = row["cats"]["OWN"]
        s = per_sec[m["sec"]]; s["hit"].append(own["hit"] * len(labels[f])); s["base"].append(own["base"] * len(labels[f])); s["n"] += len(labels[f])
    n_lab = sum(r["n_labels"] for r in per_page)

    def pooled(cat):
        rows = [r for r in per_page if cat in r["cats"]]
        n = sum(r["n_labels"] for r in rows)
        h = sum(r["cats"][cat]["hit"] * r["n_labels"] for r in rows) / n if n else float("nan")
        b = sum(r["cats"][cat]["base"] * r["n_labels"] for r in rows) / n if n else float("nan")
        return dict(hit=h, base=b, excess=h - b, ratio=h / b if b else float("nan"), label_tokens=n, pages=len(rows))

    cats = {c: pooled(c) for c in ("OWN", "SAME-LEAF", "OTHER-LEAF", "ADJACENT", "RANDOM")}

    def signflip(cat_a, cat_b):
        d = np.array([r["cats"][cat_a]["excess"] - r["cats"][cat_b]["excess"] for r in per_page
                      if cat_a in r["cats"] and cat_b in r["cats"]])
        wts = np.array([r["n_labels"] for r in per_page if cat_a in r["cats"] and cat_b in r["cats"]], dtype=float)
        obs = float(np.sum(d * wts) / wts.sum())
        null = [float(np.sum(d * wts * np.array([rng.choice((-1, 1)) for _ in d])) / wts.sum()) for _ in range(PERMS_B)]
        p = (1 + sum(x >= obs for x in null)) / (PERMS_B + 1)
        return dict(obs=obs, p=float(p), z=float((obs - np.mean(null)) / np.std(null)) if np.std(null) else float("nan"), pages=len(d))

    t_own = signflip("OWN", "OTHER-LEAF")
    t_sess = signflip("OTHER-LEAF", "RANDOM")
    if t_own["p"] < ALPHA_B:
        v = "PAGE-SPECIFIC ECHO"
    elif t_sess["p"] < ALPHA_B:
        v = "SESSION ECHO"
    else:
        v = "NO ECHO"
    by_sec = {s: dict(hit=sum(x["hit"]) / x["n"], base=sum(x["base"]) / x["n"], label_tokens=x["n"]) for s, x in per_sec.items()}
    res = dict(label_pages=len(lab_pages), label_tokens=n_lab, categories=cats, by_section=by_sec,
               test_own_vs_other_leaf=t_own, test_other_leaf_vs_random=t_sess, verdict=v,
               borderline=[k for k, p in (("own_vs_other_leaf", t_own["p"]), ("other_leaf_vs_random", t_sess["p"])) if BORDER[0] <= p <= BORDER[1]],
               per_page=per_page)
    log(f"[B3] {len(lab_pages)} label pages, {n_lab} label tokens | " +
        " | ".join(f"{c}: hit {x['hit']:.3f} base {x['base']:.3f} excess {x['excess']:+.3f}" for c, x in cats.items()))
    log(f"[B3] by section: " + ", ".join(f"{s}: {x['hit']:.3f} vs {x['base']:.3f} (n {x['label_tokens']})" for s, x in sorted(by_sec.items())))
    log(f"[B3] own vs other leaf: Δ {t_own['obs']:+.4f} z {t_own['z']:+.1f} p {t_own['p']:.4f} | other leaf vs random: Δ {t_sess['obs']:+.4f} p {t_sess['p']:.4f} -> {v}")
    return res


# =============================================================================================== main
def main():
    """Optional argv[1]: an alternative seed, used only for the pre-registered 10-seed check of borderline permutation
    p-values (output then goes to e059_seed<seed>.json)."""
    global SEED, OUT
    if len(sys.argv) > 1:
        SEED = int(sys.argv[1]); OUT = ROOT / f"experiments/results/e059_seed{SEED}.json"
    t0 = time.time()
    rng = random.Random(SEED)
    D, all_folios, locked = dev_tokens()
    P_all = [t for t in D if t.mode == "prose" and t.is_clean]
    P = [t for t in P_all if t.hand != "@"]
    log(f"DEV prose clean tokens {len(P_all)}, with scribe {len(P)}; locked leaves excluded: {locked}")
    res = {"experiment": "E059", "seed": SEED, "locked_test_excluded": locked}
    res["A1"] = part_a1(P, random.Random(SEED + 1))
    res["A2"] = part_a2([t.eva for t in P_all], random.Random(SEED + 2))
    res["B1"] = part_b1(D, all_folios, random.Random(SEED + 3))
    res["B2"] = part_b2(P_all, random.Random(SEED + 4))
    res["B3"] = part_b3(D, all_folios, random.Random(SEED + 5))
    res["runtime_s"] = time.time() - t0
    OUT.write_text(json.dumps(res, indent=1, default=str))
    log(f"done in {res['runtime_s']:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
