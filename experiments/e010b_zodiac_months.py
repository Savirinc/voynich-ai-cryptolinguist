"""E010B: pre-registered zodiac month-name (H1) and day-label (H2) tests, with synthetic controls (H3).

Hypotheses, candidate sets, statistics, nulls and alpha are fixed in reports/E010B_PREREG.md (sha256 checked below;
the run aborts if the file changed). Nothing here reads or glosses any Voynich word.

Run:  .venv/bin/python experiments/e010b_zodiac_months.py [--workers 3] [--reps 100]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.anchors import ZODIAC_FOLIOS, _parsed, locked_leaves, zodiac_pages  # noqa: E402
from vcl.eval.ledger import append  # noqa: E402
from vcl.synthetic import encoders as E  # noqa: E402
from vcl.synthetic.schema import BOUNDARY  # noqa: E402

PREREG = ROOT / "reports/E010B_PREREG.md"
PREREG_SHA256 = "dfb39b9e6cbc7fc9782707ddbe58fccf3d07ca092304750a2db7836b99c98597"
OUT = ROOT / "experiments/results/e010b.json"
SEED = 20261017
ALPHA = 0.01

# predicted-similar pairs on month SLOTS (slot i = i-th page in ZODIAC order)
SAME = [(1, 2), (3, 4)]
BRE = [8, 9, 10, 11]
P_PAIRS = SAME + [(a, b) for i, a in enumerate(BRE) for b in BRE[i + 1:]]

MONTHS = {
    "fr": ["mars", "avril", "avril", "mai", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
           "décembre"],
    "la": ["martius", "aprilis", "aprilis", "maius", "maius", "iunius", "iulius", "augustus", "september",
           "october", "november", "december"],
}
DAYS = {
    "fr": ["un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize",
           "quatorze", "quinze", "seize", "dixsept", "dixhuit", "dixneuf", "vingt", "vingtetun", "vingtdeux",
           "vingttrois", "vingtquatre", "vingtcinq", "vingtsix", "vingtsept", "vingthuit", "vingtneuf", "trente"],
    "la": ["unus", "duo", "tres", "quattuor", "quinque", "sex", "septem", "octo", "novem", "decem", "undecim",
           "duodecim", "tredecim", "quattuordecim", "quindecim", "sedecim", "septendecim", "duodeviginti",
           "undeviginti", "viginti", "unusetviginti", "duoetviginti", "tresetviginti", "quattuoretviginti",
           "quinqueetviginti", "sexetviginti", "septemetviginti", "duodetriginta", "undetriginta", "triginta"],
}
TUNE_BOOK = {"fr": "70746", "la": "828"}  # tune-role books (data/derived/benchmark_v1/book_roles.json)


# ------------------------------------------------------------------ similarity matrices (vectorised)
def _codes(words, right=False, L=None):
    L = L or max(1, max(len(w) for w in words))
    a = np.full((len(words), L), -1, dtype=np.int32)
    for i, w in enumerate(words):
        c = [ord(ch) for ch in w[:L]]
        if right:
            a[i, L - len(c):] = c
        else:
            a[i, :len(c)] = c
    return a


def affix_sim(X, Y):
    """max(longest common prefix, longest common suffix) for all pairs."""
    L = max(max(len(w) for w in X), max(len(w) for w in Y))
    out = np.zeros((len(X), len(Y)), dtype=np.int16)
    for side in (False, True):
        a, b = _codes(X, side, L), _codes(Y, side, L)
        b = np.where(b < 0, -2, b)
        for s in range(0, len(X), 200):
            eq = a[s:s + 200, None, :] == b[None, :, :]
            if side:
                eq = eq[:, :, ::-1]
            out[s:s + 200] = np.maximum(out[s:s + 200], np.cumprod(eq, axis=2).sum(2))
    return out


def lev_sim(X, Y):
    """1 - Levenshtein / max length, all pairs (vectorised Wagner-Fischer)."""
    la = np.array([len(w) for w in X]); lb = np.array([len(w) for w in Y])
    LA, LB = max(1, la.max()), max(1, lb.max())
    a, b = _codes(X, L=LA), np.where(_codes(Y, L=LB) < 0, -2, _codes(Y, L=LB))
    res = np.zeros((len(X), len(Y)))
    for s in range(0, len(X), 100):
        A = a[s:s + 100]; n = len(A)
        prev = np.broadcast_to(np.arange(LB + 1), (n, len(Y), LB + 1)).astype(np.int16).copy()
        final = np.zeros((n, len(Y)), dtype=np.int16)
        lav = la[s:s + 100]
        idx = np.arange(len(Y))
        mask0 = lav == 0
        if mask0.any():
            final[mask0] = prev[mask0][:, idx, lb]
        for i in range(LA):
            cur = np.empty_like(prev); cur[..., 0] = i + 1
            cost = (A[:, None, i, None] != b[None, :, :]).astype(np.int16)
            for j in range(LB):
                cur[..., j + 1] = np.minimum(np.minimum(prev[..., j + 1] + 1, cur[..., j] + 1), prev[..., j] + cost[..., j])
            m = lav == i + 1
            if m.any():
                final[m] = cur[m][:, idx, lb]
            prev = cur
        mx = np.maximum(lav[:, None], lb[None, :]).clip(min=1)
        res[s:s + 100] = 1 - final / mx
    return res


def pval(obs, null):
    null = np.asarray(null)
    return float((1 + (null >= obs - 1e-12).sum()) / (1 + len(null)))


def summ(obs, null):
    null = np.asarray(null, dtype=float)
    sd = null.std()
    return {"obs": float(obs), "null_mean": float(null.mean()), "null_sd": float(sd),
            "z": float((obs - null.mean()) / sd) if sd > 0 else None, "p": pval(obs, null), "n_null": len(null)}


# ------------------------------------------------------------------ structures
def wslot():
    W = np.zeros((12, 12))
    Pset = set(P_PAIRS)
    nQ = 66 - len(P_PAIRS)
    for i in range(12):
        for j in range(i + 1, 12):
            W[i, j] = W[j, i] = (1 / len(P_PAIRS)) if (i, j) in Pset else (-1 / nQ)
    return W


W_SLOT = wslot()
IU = np.triu_indices(12, 1)


def T_from_S(S, perm=None):
    if perm is not None:
        S = S[np.ix_(perm, perm)]
    return float((S * W_SLOT)[IU].sum())  # = mean_P - mean_Q (weights carry 1/|P|, -1/|Q|)


class H1Data:
    """K: list (12) of candidate word lists; F: list (12) of full page word pools."""

    def __init__(self, K, F):
        self.K, self.F = K, F
        self.kw = [w for ws in K for w in ws]
        self.kpage = np.array([p for p, ws in enumerate(K) for _ in ws])
        self.M = affix_sim(self.kw, self.kw).astype(float)
        self.blocks = [np.where(self.kpage == p)[0] for p in range(12)]

    def S(self, how="max"):
        S = np.zeros((12, 12))
        for p in range(12):
            for q in range(p + 1, 12):
                sub = self.M[np.ix_(self.blocks[p], self.blocks[q])]
                S[p, q] = S[q, p] = sub.max() if how == "max" else sub.mean()
        return S

    def search(self, Wp, rng, restarts=20):
        """max over one-word-per-page choices of sum Wp[p,q] sim(c_p,c_q) (coordinate ascent)."""
        best = -1e9
        Wc = Wp[self.kpage]  # (n_c, 12)
        for _ in range(restarts):
            c = np.array([rng.choice(b) for b in self.blocks])
            for _sweep in range(30):
                changed = False
                for p in range(12):
                    g = (self.M[:, c] * Wc).sum(1)  # gain of each candidate vs current others
                    g_p = g[self.blocks[p]] - self.M[self.blocks[p], c[p]] * Wc[self.blocks[p], p]
                    a = self.blocks[p][int(np.argmax(g_p))]
                    if a != c[p] and g_p.max() > g_p[list(self.blocks[p]).index(c[p])] + 1e-12:
                        c[p] = a; changed = True
                if not changed:
                    break
            val = float(sum(Wp[p, q] * self.M[c[p], c[q]] for p in range(12) for q in range(p + 1, 12)))
            best = max(best, val)
        return best

    def random_selection_T(self, rng, n):
        out = np.empty(n)
        for k in range(n):
            c = np.array([rng.choice(b) for b in self.blocks])
            S = self.M[np.ix_(c, c)]
            out[k] = (S * W_SLOT)[IU].sum()
        return out


def run_h1(K, F, n_perm, n_search_perm, seed):
    rng = np.random.default_rng(seed); prng = random.Random(seed)
    d = H1Data(K, F)
    S_max, S_mean = d.S("max"), d.S("mean")
    perms = [rng.permutation(12) for _ in range(n_perm)]
    res = {"K_sizes": [len(k) for k in K]}
    res["T1_N1"] = summ(T_from_S(S_max), [T_from_S(S_max, p) for p in perms])
    res["T2_N1"] = summ(T_from_S(S_mean), [T_from_S(S_mean, p) for p in perms])
    # N2: resample K_p from F_p
    fw = [w for ws in F for w in ws]; fpage = np.array([p for p, ws in enumerate(F) for _ in ws])
    MF = affix_sim(fw, fw).astype(float)
    fblocks = [np.where(fpage == p)[0] for p in range(12)]
    null = []
    for _ in range(n_perm):
        idx = [rng.choice(fblocks[p], size=min(len(K[p]), len(fblocks[p])), replace=False) for p in range(12)]
        S = np.zeros((12, 12))
        for p in range(12):
            for q in range(p + 1, 12):
                S[p, q] = MF[np.ix_(idx[p], idx[q])].max()
        null.append(T_from_S(S))
    res["T1_N2"] = summ(T_from_S(S_max), null)
    # T3: search-corrected
    obs = d.search(W_SLOT, prng)
    nullS = [d.search(W_SLOT[np.ix_(np.argsort(p), np.argsort(p))], prng) for p in perms[:n_search_perm]]
    res["T3_N1"] = summ(obs, nullS)
    res["T3_uncorrected_vs_random_selection"] = summ(obs, d.random_selection_T(rng, n_perm))
    return res


class H2Data:
    def __init__(self, pages_labels, pool=None):
        """pages_labels: list(12) of label-string lists (transcription order). pool: other-section labels."""
        self.labels = [l for ls in pages_labels for l in ls]
        self.sizes = [len(ls) for ls in pages_labels]
        self.page = np.array([p for p, ls in enumerate(pages_labels) for _ in ls])
        self.starts = np.cumsum([0] + self.sizes[:-1])
        self.pool = pool or []
        allw = self.labels + self.pool
        self.E = lev_sim(allw, allw)
        types = {w: i for i, w in enumerate(sorted(set(allw)))}
        self.tid = np.array([types[w] for w in allw]); self.ntypes = len(types)
        # gather plan for A: for every page pair, shifts c, positions i
        rows, cols, seg_pair = [], [], []
        self.pair_shift_counts = []
        for p in range(12):
            for q in range(p + 1, 12):
                n_p, n_q = self.sizes[p], self.sizes[q]
                n = min(n_p, n_q)
                for c in range(n_q):
                    i = np.arange(n)
                    rows.append(self.starts[p] + i); cols.append(self.starts[q] + (i + c) % n_q)
                self.pair_shift_counts.append((n_q, n))
        self.rows = np.concatenate(rows); self.cols = np.concatenate(cols)
        seglen = [n for (nq, n) in self.pair_shift_counts for _ in range(nq)]
        self.seg_starts = np.cumsum([0] + seglen[:-1]); self.seglen = np.array(seglen)
        self.pair_starts = np.cumsum([0] + [nq for nq, _ in self.pair_shift_counts[:-1]])

    def stats(self, m):
        """m: array mapping locus index -> label index (into self.labels+self.pool)."""
        t = self.tid[m]
        B = np.zeros((12, self.ntypes), dtype=np.int32)
        B[self.page, t] = 1
        O = int(np.triu(B @ B.T, 1).sum())
        v = self.E[m[self.rows], m[self.cols]]
        means = np.add.reduceat(v, self.seg_starts) / self.seglen
        A = float(np.maximum.reduceat(means, self.pair_starts).mean())
        return O, A

    def run(self, n_perm, rng, pool_by_len=None):
        n = len(self.labels)
        ident = np.arange(n)
        O, A = self.stats(ident)
        Ob, Ab = zip(*[self.stats(rng.permutation(n)) for _ in range(n_perm)])
        res = {"O_Nb": summ(O, Ob), "A_Nb": summ(A, Ab)}
        if pool_by_len:
            lens = [len(w) for w in self.labels]
            keys = np.array(sorted(pool_by_len))
            choice = []
            for L in lens:
                k = keys[np.argmin(np.abs(keys - L))]
                choice.append(np.array(pool_by_len[k]) + n)
            Oa, Aa = zip(*[self.stats(np.array([rng.choice(c) for c in choice])) for _ in range(n_perm)])
            res["O_Na"] = summ(O, Oa); res["A_Na"] = summ(A, Aa)
        return res


def holm(ps: dict, alpha=ALPHA):
    items = sorted(ps.items(), key=lambda kv: kv[1]); m = len(items); out = {}; stop = False
    for k, (name, p) in enumerate(items):
        thr = alpha / (m - k)
        rej = (not stop) and p <= thr
        stop = stop or not rej
        out[name] = {"p": p, "holm_threshold": thr, "reject": rej}
    return out


# ------------------------------------------------------------------ Voynich data per prereg
def clean(tok):
    return tok and "?" not in tok and "@" not in tok


def voynich_sets():
    zp = zodiac_pages()
    K, F, LAB, counts = [], [], [], []
    for p in zp:
        k = []
        for g in p["label_groups"]:
            h = g["heading"].lower()
            if "inner" in h or "central" in h:
                k += [t for l in g["labels"] for t in l["tokens"] if clean(t)]
        ring = p["text_rings"][-1]["tokens"]
        if ring and clean(ring[0]):
            k.append(ring[0])
        f = [t for g in p["label_groups"] for l in g["labels"] for t in l["tokens"] if clean(t)]
        f += [t for r in p["text_rings"] for t in r["tokens"] if clean(t)]
        labs = [l["eva"] for g in p["label_groups"] for l in g["labels"]]
        good = [l for l in labs if all(clean(t) for t in l.split("."))]
        K.append(k); F.append(f); LAB.append(good)
        counts.append({"folio": p["folio"], "sign": p["sign"], "month_latin_script": p["month_latin_script"],
                       "leaf": p["leaf"], "locked": p["locked"], "n_labels": p["n_labels"],
                       "groups": [(g["heading"], len(g["labels"])) for g in p["label_groups"]],
                       "n_labels_excluded_unclean": len(labs) - len(good), "n_text_rings": len(p["text_rings"]),
                       "K_size": len(k), "F_size": len(f)})
    return K, F, LAB, counts


def other_label_pool():
    locked = locked_leaves()
    pages, toks = _parsed()
    loci = {}
    for t in toks:
        if t.locus_type == "L" and t.folio not in ZODIAC_FOLIOS and t.leaf not in locked:
            loci.setdefault((t.folio, t.line_no), []).append(t.eva)
    labs = [".".join(v) for v in loci.values() if all(clean(x) for x in v)]
    return labs


# ------------------------------------------------------------------ synthetic controls (H3)
def filler_words(lang):
    from vcl.synthetic.corpora import load_books
    book = [b for b in load_books() if b["id"] == TUNE_BOOK[lang]][0]
    c = Counter(book["text"].split())
    return sorted(w for w, n in c.items() if 3 <= len(w) <= 9 and n >= 2)


def encode_words(words, mech, rng):
    plain = " ".join(words)
    if mech == "mono":
        syms, *_ = E.mono(plain, rng)
    elif mech == "homophonic":
        syms, *_ = E.homophonic(plain, rng)
    else:  # verbose homophonic (local): homophonic + fixed modifier glyph after 1/3 of the letters
        syms, *_ = E.homophonic(plain, rng)
        alpha = sorted({ch for ch in plain if ch != " "})
        heavy = set(rng.sample(alpha, max(1, len(alpha) // 3)))
        used = set(syms)
        mods = [g for g in E.GLYPHS if g not in used]
        modmap = {ch: rng.choice(mods[:3]) for ch in heavy}
        out = []
        for ch, s in zip(plain, syms):
            out.append(s)
            if ch in modmap:
                out.append(modmap[ch])
        syms = out
    words_out, cur = [], []
    for s in syms + [BOUNDARY]:
        if s == BOUNDARY:
            words_out.append("".join(cur)); cur = []
        else:
            cur.append(s)
    assert len(words_out) == len(words), (len(words_out), len(words))
    return words_out


def synth_replicate(args):
    mech, lang, cond, rep, n_perm, n_search, struct, fill = args
    seed = SEED + int(hashlib.sha256(f"{mech}|{lang}|{cond}|{rep}".encode()).hexdigest(), 16) % 10**6
    rng = random.Random(seed); nrng = np.random.default_rng(seed)
    months = list(MONTHS[lang]); days = DAYS[lang]
    if cond == "control":
        rng.shuffle(months)
    # build plaintext pages following the Voynich structure
    pagesK, pagesF, pagesL = [], [], []
    split_first = {1: True, 2: False, 3: True, 4: False}
    for pi, st in enumerate(struct):
        labels = []
        for gi, gsize in enumerate(st["groups"]):
            labels.append([rng.choice(fill) for _ in range(gsize)])
        if cond in ("h2", "control"):
            flat_n = sum(st["groups"])
            if pi in split_first:
                seq = days[:15] if split_first[pi] else days[15:]
            else:
                seq = days
            seq = (seq + seq)[:flat_n]
            k = 0
            for g in labels:
                for j in range(len(g)):
                    g[j] = seq[k]; k += 1
        rings = [[rng.choice(fill) for _ in range(n)] for n in st["rings"]]
        kslots = [(gi, j) for gi in st["k_groups"] for j in range(st["groups"][gi])] + [("ring", 0)]
        if cond in ("h1", "control"):
            gi, j = rng.choice(kslots)
            if gi == "ring":
                rings[-1][0] = months[pi]
            else:
                labels[gi][j] = months[pi]
        pagesL.append(labels); pagesF.append(rings)
    if cond == "control":  # shuffle day labels across loci too
        flat = [w for pg in pagesL for g in pg for w in g]
        rng.shuffle(flat); it = iter(flat)
        pagesL = [[[next(it) for _ in g] for g in pg] for pg in pagesL]
    # encode the whole synthetic manuscript with one key
    order = [w for pg, rg in zip(pagesL, pagesF) for g in pg for w in g] + \
            [w for rg in pagesF for r in rg for w in r]
    pool_plain = [rng.choice(fill) for _ in range(600)]
    enc = encode_words(order + pool_plain, mech, rng)
    it = iter(enc)
    encL = [[[next(it) for _ in g] for g in pg] for pg in pagesL]
    encR = [[[next(it) for _ in r] for r in rg] for rg in pagesF]
    pool = [next(it) for _ in pool_plain]
    K, F, LAB = [], [], []
    for pi, st in enumerate(struct):
        k = [w for gi in st["k_groups"] for w in encL[pi][gi]] + [encR[pi][-1][0]]
        K.append(k)
        F.append([w for g in encL[pi] for w in g] + [w for r in encR[pi] for w in r])
        LAB.append([w for g in encL[pi] for w in g])
    out = {"mech": mech, "lang": lang, "cond": cond, "rep": rep}
    h1 = run_h1(K, F, n_perm, n_search, seed)
    pbl = {}
    for i, w in enumerate(pool):
        pbl.setdefault(len(w), []).append(i)
    h2 = H2Data(LAB, pool).run(n_perm, nrng, pbl)
    out["p"] = {"H1-T1-N1": h1["T1_N1"]["p"], "H1-T1-N2": h1["T1_N2"]["p"], "H1-T2-N1": h1["T2_N1"]["p"],
                "H1-T3-N1": h1["T3_N1"]["p"], "H2-O-Nb": h2["O_Nb"]["p"], "H2-A-Nb": h2["A_Nb"]["p"],
                "H2-O-Na": h2["O_Na"]["p"], "H2-A-Na": h2["A_Na"]["p"]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--perm", type=int, default=10000); ap.add_argument("--search-perm", type=int, default=2000)
    ap.add_argument("--synth-perm", type=int, default=1000); ap.add_argument("--synth-search", type=int, default=100)
    ap.add_argument("--skip-synth", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    if sha != PREREG_SHA256:
        raise SystemExit(f"prereg changed ({sha}); create E010B_PREREG_v2.md and log in FAILURES.md")
    t0 = time.time()
    K, F, LAB, counts = voynich_sets()
    struct = []
    for p in zodiac_pages():
        groups = [len(g["labels"]) for g in p["label_groups"]]
        kg = [i for i, g in enumerate(p["label_groups"]) if "inner" in g["heading"].lower() or "central" in g["heading"].lower()]
        struct.append({"groups": groups, "k_groups": kg, "rings": [len(r["tokens"]) for r in p["text_rings"]]})
    res = {"experiment": "E010B", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": sha,
           "prereg_written_utc": "2026-10-17T06:35Z", "seed": SEED, "alpha_familywise": ALPHA,
           "command": " ".join(["experiments/e010b_zodiac_months.py"] + sys.argv[1:]),
           "locked_zodiac_leaves": sorted({c["leaf"] for c in counts if c["locked"]}),
           "page_counts": counts, "total_labels": sum(c["n_labels"] for c in counts)}
    # --- Voynich
    h1 = run_h1(K, F, a.perm, a.search_perm, SEED)
    pool = other_label_pool()
    pbl = {}
    for i, w in enumerate(pool):
        pbl.setdefault(len(w), []).append(i)
    h2d = H2Data(LAB, pool)
    h2 = h2d.run(a.perm, np.random.default_rng(SEED + 1), pbl)
    fam = {"H1-T1-N1": h1["T1_N1"]["p"], "H1-T1-N2": h1["T1_N2"]["p"], "H1-T2-N1": h1["T2_N1"]["p"],
           "H1-T3-N1": h1["T3_N1"]["p"], "H2-O-Nb": h2["O_Nb"]["p"], "H2-A-Nb": h2["A_Nb"]["p"],
           "H2-O-Na": h2["O_Na"]["p"], "H2-A-Na": h2["A_Na"]["p"]}
    res["voynich"] = {"H1": h1, "H2": h2, "n_other_labels_pool": len(pool), "holm": holm(fam)}
    res["voynich_wall_s"] = round(time.time() - t0, 1)
    print(json.dumps(res["voynich"]["holm"], indent=1))
    # --- H3 synthetic controls
    if not a.skip_synth:
        jobs = []
        for mech in ["mono", "homophonic", "verbose_homophonic"]:
            for lang in ["fr", "la"]:
                fill = filler_words(lang)
                for cond in ["h1", "h2", "control"]:
                    for rep in range(a.reps):
                        jobs.append((mech, lang, cond, rep, a.synth_perm, a.synth_search, struct, fill))
        rows = []
        with ProcessPoolExecutor(max_workers=min(3, a.workers)) as ex:
            for i, r in enumerate(ex.map(synth_replicate, jobs, chunksize=4)):
                rows.append(r)
                if i % 100 == 0:
                    print(i, len(jobs), round(time.time() - t0), flush=True)
        power = {}
        for mech in ["mono", "homophonic", "verbose_homophonic"]:
            for lang in ["fr", "la"]:
                for cond in ["h1", "h2", "control"]:
                    sel = [r for r in rows if (r["mech"], r["lang"], r["cond"]) == (mech, lang, cond)]
                    power[f"{mech}|{lang}|{cond}"] = {t: float(np.mean([r["p"][t] < ALPHA for r in sel]))
                                                      for t in fam}
        res["synthetic"] = {"reps": a.reps, "perm": a.synth_perm, "search_perm": a.synth_search,
                            "rate_p_below_alpha": power}
    # --- decision per prereg section 4
    hv = res["voynich"]["holm"]
    def powered(test):
        if "synthetic" not in res:
            return None
        cond = "h1" if test.startswith("H1") else "h2"
        return any(v[test] >= 0.8 for k, v in res["synthetic"]["rate_p_below_alpha"].items() if k.endswith(cond))
    dec = {}
    for H, tests in [("H1", ["H1-T1-N1"]), ("H2", ["H2-O-Nb", "H2-A-Nb"])]:
        if any(hv[t]["reject"] for t in tests):
            dec[H] = "supported (structure present; NOT a reading)"
        elif any(powered(t) for t in tests):
            dec[H] = "negative (test was powered on synthetic controls and did not fire)"
        else:
            dec[H] = "uninformative (test not powered on synthetic controls)"
    res["decision"] = dec
    res["wall_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    append([{"experiment": "E010B", "model": "zodiac_prereg_v1", "checkpoint_sha256": sha, "split": "DEV(zodiac f70-f73)",
             "metric": f"p_{k}", "value": v["p"], "command": res["command"],
             "notes": f"holm_reject={v['reject']}; decision {dec}"} for k, v in hv.items()])
    print(json.dumps(dec, indent=1), res["wall_s"])


if __name__ == "__main__":
    main()
