"""E093 (approach check 4): the simplest writing process for the solid facts, and whether the free choices follow the
pictures. See reports/E093_PREREG.md.

PART 1, process ladder (4 models, declared now; no others). Words are cut into front + middle + ending with the E074
lists (10 fronts, 20 endings incl. empty, built from DEV types; greedy: longest ending, then longest front). Middles come
from a glyph-bigram chain that starts from the front's last glyph.
  P1 (front, ending) drawn from one table; words independent
  P2 + the table depends on line position (first / inside / last word)
  P3 + the table also depends on the previous word's ending (same line)
  P4 + copying: with probability c a word is one of the last k words on the page, unchanged or (probability a) with one
       alternation (e/ee, r/l, t/k, d+-, q+-); c, a, k fitted by likelihood on a grid
Smoothing: back-off with beta 5; middle chain add-0.1. Held-out bits per word: fit on half the bifolios, test on the
other half. P* = lowest held-out bits. Samples (5 seeds, fitted on all DEV, Voynich's own page and line lengths) are
scored on 13 battery items; an item is REPRODUCED iff >= 4 of 5 samples pass.
PART 2, subject tracking. Page = line-internal clean words (first and last word of each line dropped). Similarity =
cosine of word counts with the text's 50 commonest types removed. Pairs: same hand and Currier, different bifolio,
order distance >= 2; distance quintile bins; DELTA = weighted mean over (stratum, bin) of mean(same section) - mean(other
section), weight min(n_same, n_other). z against 1,000 permutations of section labels within stratum.
Known answers: Vulgate and KJV, 200-word chunks (every k-th, about 170 pages), section = genre. False-claim controls:
Timm-Schinner generator and a P* sample, each poured into Voynich's line structure and given Voynich's page labels.
Run: caffeinate -ims .venv/bin/python experiments/e093_explanation_model.py [--smoke]
"""
from __future__ import annotations

import argparse, glob, json, math, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e052_shortlist_attack as S52  # noqa: E402
import e066_word_individuality_v3_v2 as E66  # noqa: E402
import e067_gibberish_vocabulary as E67  # noqa: E402
import e068_gibberish_battery as E68  # noqa: E402
import e069_word_partners as E69  # noqa: E402
import e070_content_partners_v2 as E70  # noqa: E402
import e086_spaces_and_lines as E86  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e058_word_repeat_individuality_v2 import stats  # noqa: E402
from e074_slot_coverage import lists  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED = 93093
OUT = ROOT / "experiments/results/e093.json"
BETA, ADD = 5.0, 0.1
GRID_C, GRID_A, GRID_K = [0.05, 0.1, 0.2, 0.3], [0.0, 0.3, 0.6], [10, 30, 100]
N_SAMPLES, N_PERM, TOP_DROP, CHUNK, N_PAGES = 5, 1000, 50, 200, 170
GENRE = {**{b: "law" for b in "GEN EXO LEV NUM DEU".split()},
         **{b: "history" for b in "JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST TOB JDT 1MA 2MA".split()},
         **{b: "wisdom" for b in "JOB PSA PRO ECC SNG WIS SIR".split()},
         **{b: "prophets" for b in "ISA JER LAM BAR EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL REV".split()},
         **{b: "gospels" for b in "MAT MRK LUK JHN ACT".split()},
         **{b: "letters" for b in "ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD".split()}}


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ data
def voynich():
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L, meta = defaultdict(list), {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t.eva if t.is_clean else None)
            meta[t.folio] = {"hand": t.hand, "currier": t.currier, "section": t.illustration, "bifolio": t.bifolio_id}
    key = lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f)
    order = sorted(L, key=lambda k: (key(k[0]), k))
    pages = defaultdict(list)
    for k in order:
        pages[k[0]].append([w for w in L[k] if w])
    folios = sorted(pages, key=key)
    return [pages[f] for f in folios], [meta[f] for f in folios], sorted(locked)


# ------------------------------------------------------------------ alternations
_VAR = {}


def variants(w):
    if w in _VAR:
        return _VAR[w]
    out = set()
    i = 0
    while i < len(w):
        if w[i] == "e":
            j = i
            while j < len(w) and w[j] == "e":
                j += 1
            if j - i == 1:
                out.add(w[:i] + "ee" + w[j:])
            elif j - i == 2:
                out.add(w[:i] + "e" + w[j:])
            i = j
        else:
            i += 1
    for i, ch in enumerate(w):
        for a, b in (("r", "l"), ("l", "r"), ("t", "k"), ("k", "t")):
            if ch == a:
                out.add(w[:i] + b + w[i + 1:])
    for p in ("d", "q"):
        out.add(w[1:] if w.startswith(p) else p + w)
    out.discard(w); out.discard("")
    _VAR[w] = out
    return out


# ------------------------------------------------------------------ process models
class Proc:
    def __init__(self, F, E):
        self.F = sorted(F, key=len, reverse=True); self.E = sorted(E, key=len, reverse=True)
        self.FE = [(f, e) for f in F for e in E]; self.idx = {fe: i for i, fe in enumerate(self.FE)}
        self._parse = {}

    def parse(self, w):
        if w not in self._parse:
            for e in self.E:
                if w.endswith(e):
                    rest = w[:len(w) - len(e)]
                    for f in self.F:
                        if rest.startswith(f):
                            self._parse[w] = (f, rest[len(f):], e); break
                    break
        return self._parse[w]

    @staticmethod
    def contexts(page):
        """yield (word, pos, prev_ending_word) over a page; pos 0 first, 1 inside, 2 last"""
        for l in page:
            for i, w in enumerate(l):
                pos = 0 if i == 0 else (2 if i == len(l) - 1 else 1)
                yield w, pos, (l[i - 1] if i else None)

    def fit(self, pages):
        n = len(self.FE)
        self.c1 = np.zeros(n); self.c2 = defaultdict(lambda: np.zeros(n)); self.c3 = defaultdict(lambda: np.zeros(n))
        self.big = defaultdict(Counter); self.syms = set("$")
        for p in pages:
            for w, pos, pw in self.contexts(p):
                f, m, e = self.parse(w); i = self.idx[(f, e)]
                pe = self.parse(pw)[2] if pw else "^"
                self.c1[i] += 1; self.c2[pos][i] += 1; self.c3[(pos, pe)][i] += 1
                prev = f[-1] if f else "^"
                for ch in m + "$":
                    self.big[prev][ch] += 1; prev = ch; self.syms.add(ch)
        self.syms = sorted(self.syms)
        self.p1 = (self.c1 + 0.5) / (self.c1.sum() + 0.5 * n)
        self._p = {}
        return self

    def pfe(self, level, pos, pe):
        k = (level, pos, pe)
        if k not in self._p:
            if level == 1:
                p = self.p1
            elif level == 2:
                c = self.c2[pos]; p = (c + BETA * self.p1) / (c.sum() + BETA)
            else:
                c = self.c3[(pos, pe)]; p2 = self.pfe(2, pos, None); p = (c + BETA * p2) / (c.sum() + BETA)
            self._p[k] = p
        return self._p[k]

    def pmid(self, f, m):
        prev = f[-1] if f else "^"; lp = 0.0; V = len(self.syms)
        for ch in m + "$":
            c = self.big[prev]; lp += math.log((c[ch] + ADD) / (sum(c.values()) + ADD * V)); prev = ch
        return lp

    def logp_fresh(self, w, level, pos, pe):
        f, m, e = self.parse(w)
        return math.log(self.pfe(level, pos, pe)[self.idx[(f, e)]]) + self.pmid(f, m)

    def copy_terms(self, page, kmax):
        """per token: list of (distance, exact, variant weight) over the previous kmax words on the page"""
        flat = [w for l in page for w in l]; out = []
        for t, w in enumerate(flat):
            row = []
            for d in range(1, min(kmax, t) + 1):
                r = flat[t - d]
                if r == w:
                    row.append((d, 1, 0.0))
                else:
                    V = variants(r)
                    if w in V:
                        row.append((d, 0, 1.0 / len(V)))
            out.append(row)
        return out

    def page_bits(self, page, level, copy=None, terms=None):
        lps = []
        for t, (w, pos, pw) in enumerate(self.contexts(page)):
            pe = self.parse(pw)[2] if pw else "^"
            lf = self.logp_fresh(w, min(level, 3), pos, pe)
            if copy is None:
                lps.append(lf); continue
            c, a, k = copy
            n_rec = min(k, t)
            if n_rec == 0:
                lps.append(lf); continue
            q = sum(((1 - a) if ex else a * vw) for d, ex, vw in terms[t] if d <= k) / n_rec
            lps.append(math.log((1 - c) * math.exp(lf) + c * q))
        return lps

    def bits(self, pages, level, copy=None, terms=None):
        tot, n = 0.0, 0
        for i, p in enumerate(pages):
            lps = self.page_bits(p, level, copy, terms[i] if terms else None); tot += sum(lps); n += len(lps)
        return -tot / n / math.log(2)

    def sample(self, shape, level, copy, rng):
        """shape: list of pages, each a list of line lengths"""
        cum = {}
        def draw_fe(pos, pe):
            k = (pos, pe)
            if k not in cum:
                cum[k] = np.cumsum(self.pfe(min(level, 3), pos, pe if level >= 3 else None))
            return self.FE[int(np.searchsorted(cum[k], rng.random() * cum[k][-1]))]
        bcum = {}
        def draw_mid(f):
            prev = f[-1] if f else "^"; m = ""
            for _ in range(12):
                if prev not in bcum:
                    c = self.big[prev]; ws = np.array([c[s] + ADD for s in self.syms]); bcum[prev] = np.cumsum(ws)
                ch = self.syms[int(np.searchsorted(bcum[prev], rng.random() * bcum[prev][-1]))]
                if ch == "$":
                    break
                m += ch; prev = ch
            return m
        out = []
        for lens in shape:
            page, flat = [], []
            for L in lens:
                line = []
                for i in range(L):
                    pos = 0 if i == 0 else (2 if i == L - 1 else 1)
                    pe = self.parse(line[-1])[2] if line else "^"
                    w = None
                    if copy and flat and rng.random() < copy[0]:
                        r = flat[-1 - rng.randrange(min(copy[2], len(flat)))]
                        V = sorted(variants(r))
                        w = rng.choice(V) if (V and rng.random() < copy[1]) else r
                    while not w:
                        f, e = draw_fe(pos, pe); w = f + draw_mid(f) + e
                    line.append(w); flat.append(w)
                page.append(line)
            out.append(page)
        return out


# ------------------------------------------------------------------ battery
def battery(pages, ref, rng_seed):
    lines = [l for p in pages for l in p if l]
    toks = [w for l in lines for w in l]
    c = Counter(toks); res = {}
    res["B1_vocab"] = {"types": len(c), "hapax": sum(v == 1 for v in c.values()) / len(c)}
    res["B1_vocab"]["pass"] = abs(len(c) - ref["types"]) <= 0.1 * ref["types"] and abs(res["B1_vocab"]["hapax"] - ref["hapax"]) <= 0.03
    W67 = E67.windows(toks, E67.N_VOY, random.Random(E67.SEED + rng_seed))
    dT = (np.mean([m["T"] for m in W67]) - ref["T"]) / ref["sdT"]; dH = (np.mean([m["H"] for m in W67]) - ref["H"]) / ref["sdH"]
    res["B2_vocab150"] = {"d_T": float(dT), "d_H": float(dH), "pass": bool(abs(dT) <= 0.5 and abs(dH) <= 1)}
    W68 = E68.windows(toks, E68.N_VOY, random.Random(E68.SEED + rng_seed))
    J = E68.judge(ref["VOY68"], {"x": E68.group_value(ref["VOY68"])}, W68, W68, E68.SEED)
    for k in E68.FEATS:
        r = J["rows"][k]
        res[f"B3_{k}"] = {"value": r["gibberish"], "voynich": r["voynich"], "sd_v": r["sd_v"],
                          "pass": bool(abs(r["gibberish"] - r["voynich"]) < r["sd_v"])}
    z66 = stats(lines, True, random.Random(E66.SEED))["z"]
    res["B4_family"] = {"z": z66, "pass": bool(z66 <= ref["gen_median_z66"])}
    st = E69.stability(lines, seed=0)["STAB"]
    res["B5_STAB"] = {"STAB": st, "pass": bool(0.053 < st < 0.083)}
    ps = E70.stability_pso(lines, seed=0)["PSO"]
    res["B6_PSO"] = {"PSO": ps, "pass": bool(ps < 0.018)}
    z86 = E86.continuity([[l for l in p if l] for p in pages], random.Random(E86.SEED))["z"]
    res["B7_lines"] = {"z": z86, "pass": bool(abs(z86) < 13)}
    return res


# ------------------------------------------------------------------ part 2
def page_vecs(pages_words):
    allc = Counter(w for p in pages_words for w in p)
    drop = {w for w, _ in allc.most_common(TOP_DROP)}
    vocab = {w: i for i, w in enumerate(sorted(w for w in allc if w not in drop))}
    X = np.zeros((len(pages_words), len(vocab)))
    for i, p in enumerate(pages_words):
        for w in p:
            if w in vocab:
                X[i, vocab[w]] += 1
    n = np.linalg.norm(X, axis=1, keepdims=True); n[n == 0] = 1
    X = X / n
    return X @ X.T


def tracking(pages_words, labels, rng):
    """labels: list of dicts with section, stratum, bifolio, order"""
    S = page_vecs(pages_words)
    I, J, D, G = [], [], [], []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            if a["stratum"] != b["stratum"] or a["bifolio"] == b["bifolio"] or abs(a["order"] - b["order"]) < 2:
                continue
            I.append(i); J.append(j); D.append(abs(a["order"] - b["order"])); G.append(a["stratum"])
    I, J, D = np.array(I), np.array(J), np.array(D)
    if len(I) == 0:
        return {"pairs": 0, "z": None}
    qs = np.quantile(D, [0.2, 0.4, 0.6, 0.8]); bins = np.searchsorted(qs, D, side="right")
    strata = sorted(set(G)); gid = np.array([strata.index(g) * 5 + b for g, b in zip(G, bins)])
    sim = S[I, J]
    sec = np.array([l["section"] for l in labels])
    strat_of = [l["stratum"] for l in labels]

    def delta(sec):
        same = sec[I] == sec[J]; tot, wsum = 0.0, 0.0
        for g in np.unique(gid):
            m = gid == g; s1 = same & m; s0 = (~same) & m
            n1, n0 = s1.sum(), s0.sum()
            if n1 and n0:
                w = min(n1, n0); tot += w * (sim[s1].mean() - sim[s0].mean()); wsum += w
        return tot / wsum if wsum else 0.0

    real = delta(sec)
    null = []
    by = defaultdict(list)
    for i, s in enumerate(strat_of):
        by[s].append(i)
    for _ in range(N_PERM):
        p = sec.copy()
        for s, ix in by.items():
            vals = list(sec[ix]); rng.shuffle(vals); p[ix] = vals
        null.append(delta(p))
    mu, sd = float(np.mean(null)), float(np.std(null, ddof=1))
    return {"pairs": int(len(I)), "same_pairs": int((sec[I] == sec[J]).sum()), "delta": real, "null_mean": mu, "null_sd": sd,
            "z": (real - mu) / sd if sd > 0 else 0.0}


def bible_pages(bid):
    fs = sorted(glob.glob(str(ROOT / f"data/external/bibles/{bid}/txt/*_read.txt")))
    words, gen = [], []
    for f in fs:
        b = Path(f).name.split("_")[2]
        if b not in GENRE:
            continue
        w = S52.norm("\n".join(Path(f).read_text(encoding="utf-8-sig").splitlines()[1:]))
        words += w; gen += [GENRE[b]] * len(w)
    chunks = [(words[i:i + CHUNK], Counter(gen[i:i + CHUNK]).most_common(1)[0][0]) for i in range(0, len(words) - CHUNK, CHUNK)]
    k = max(1, len(chunks) // N_PAGES); sel = chunks[::k]
    return [c[0] for c in sel], [{"section": c[1], "stratum": "one", "bifolio": i, "order": i} for i, c in enumerate(sel)]


def internal(pages):
    return [[w for l in p for w in l[1:-1]] for p in pages]


def labels_of(meta):
    return [{"section": m["section"], "stratum": (m["hand"], m["currier"]), "bifolio": m["bifolio"], "order": i} for i, m in enumerate(meta)]


def pour(lines_src, shape):
    flat = [w for l in lines_src for w in l if w]; out, i = [], 0
    for lens in shape:
        page = []
        for L in lens:
            page.append(flat[i:i + L]); i += L
        out.append(page)
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    global N_SAMPLES, N_PERM
    if a.smoke:
        N_SAMPLES, N_PERM = 1, 50
    pages, meta, locked = voynich()
    shape = [[len(l) for l in p] for p in pages]
    types = sorted({w for p in pages for l in p for w in l})
    F, _, E = lists(types, 10, 30, 20)
    log(f"Voynich DEV pages {len(pages)}, tokens {sum(map(sum, shape))}; fronts {F}; endings {E}")
    # held-out ladder
    bif = sorted({m["bifolio"] for m in meta}); half = {b: i % 2 for i, b in enumerate(bif)}
    fitp = [p for p, m in zip(pages, meta) if half[m["bifolio"]] == 0]; testp = [p for p, m in zip(pages, meta) if half[m["bifolio"]] == 1]
    pr = Proc(F, E).fit(fitp)
    ladder = {f"P{l}": pr.bits(testp, l) for l in (1, 2, 3)}
    tfit = [pr.copy_terms(p, max(GRID_K)) for p in fitp]; ttest = [pr.copy_terms(p, max(GRID_K)) for p in testp]
    grid = {}
    for c in GRID_C:
        for al in GRID_A:
            for k in GRID_K:
                grid[(c, al, k)] = pr.bits(fitp, 3, (c, al, k), tfit)
    best = min(grid, key=grid.get)
    ladder["P4"] = pr.bits(testp, 3, best, ttest)
    pstar = min(ladder, key=ladder.get)
    log(f"held-out bits/word {ladder}; P4 copy params (c, a, k) {best}; P* = {pstar} | {time.time() - t0:.0f}s")
    # references for the battery
    vt = [w for p in pages for l in p for w in l]; vc = Counter(vt)
    V67 = E67.windows(vt, E67.N_VOY, random.Random(E67.SEED))
    e66 = json.loads((ROOT / "experiments/results/e066.json").read_text())
    ref = {"types": len(vc), "hapax": sum(v == 1 for v in vc.values()) / len(vc),
           "T": float(np.mean([m["T"] for m in V67])), "sdT": float(np.std([m["T"] for m in V67], ddof=1)),
           "H": float(np.mean([m["H"] for m in V67])), "sdH": float(np.std([m["H"] for m in V67], ddof=1)),
           "VOY68": E68.windows(vt, E68.N_VOY, random.Random(E68.SEED)),
           "gen_median_z66": float(np.median([e66["results"]["generator"][f"gen{k}"]["z"] for k in range(10)]))}
    vb = battery(pages, ref, 0)
    log("Voynich itself: " + ", ".join(f"{k} {'pass' if v['pass'] else 'FAIL'}" for k, v in vb.items()))
    full = Proc(F, E).fit(pages)
    lev = {"P1": (1, None), "P2": (2, None), "P3": (3, None), "P4": (3, best)}
    B, samples = {}, {}
    for name, (level, cp) in lev.items():
        rows = []
        for s in range(N_SAMPLES):
            smp = full.sample(shape, level, cp, random.Random(SEED + 100 * level + s + (7 if cp else 0)))
            if s == 0:
                samples[name] = smp
            rows.append(battery(smp, ref, s + 1))
        items = list(rows[0])
        B[name] = {k: {"passes": sum(r[k]["pass"] for r in rows), "reproduced": sum(r[k]["pass"] for r in rows) >= (4 if N_SAMPLES == 5 else 1),
                       "values": [{x: y for x, y in r[k].items() if x != "pass"} for r in rows]} for k in items}
        log(f"{name}: reproduced {sum(v['reproduced'] for v in B[name].values())}/{len(items)} | " +
            ", ".join(f"{k} {v['passes']}/{N_SAMPLES}" for k, v in B[name].items()) + f" | {time.time() - t0:.0f}s")
        log("   sample: " + " ".join(smp[0][0][:12]))
    n_items = len(B[pstar]); n_rep = sum(v["reproduced"] for v in B[pstar].values())
    part1 = ("M HAS A WORKING PROCESS" if n_rep == n_items else "NO WORKING PROCESS") + f" ({pstar} reproduces {n_rep}/{n_items})"
    fails = [k for k, v in B[pstar].items() if not v["reproduced"]]
    log(f"PART 1 {part1}; not reproduced: {fails}")
    # part 2
    rng = random.Random(SEED)
    T = {}
    for bid in ("latVUC", "eng-kjv"):
        pw, lab = bible_pages(bid); T[bid] = tracking(pw, lab, rng)
    vl = labels_of(meta)
    T["generator"] = tracking(internal(pour(gen_lines(), shape)), vl, rng)
    T["P*_sample"] = tracking(internal(samples[pstar]), vl, rng)
    T["VOYNICH"] = tracking(internal(pages), vl, rng)
    for k, v in T.items():
        log(f"  {k:10s} pairs {v['pairs']} same {v.get('same_pairs')} delta {v['delta']:+.4f} null {v['null_mean']:+.4f} ± {v['null_sd']:.4f} z {v['z']:+.2f}")
    valid = all(T[b]["z"] >= 3 for b in ("latVUC", "eng-kjv")) and all(T[c]["z"] < 2 for c in ("generator", "P*_sample"))
    zv = T["VOYNICH"]["z"]
    if not valid:
        part2 = "VOID (known answers or false-claim controls failed)"
    elif zv >= 3:
        part2 = "TRACKS SUBJECT"
    elif zv < 1:
        part2 = "NO TRACKING"
    else:
        part2 = "INCONCLUSIVE"
    fM = (3.0 if part1.startswith("M HAS") else 1.0) * (1 / 3 if part2 == "TRACKS SUBJECT" else 1.0)
    log(f"PART 2 {part2} (Voynich z {zv:+.2f}) | M x{fM:.3g} | {time.time() - t0:.0f}s")
    OUT.with_name("e093_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(
        {"experiment": "E093", "seed": SEED, "fronts": F, "endings": E, "ladder_bits": ladder, "copy_grid": {str(k): v for k, v in grid.items()},
         "copy_best": best, "pstar": pstar, "voynich_battery": vb, "battery": B, "part1": part1, "part1_fails": fails,
         "tracking": T, "part2": part2, "factor_M": fM, "samples_first_lines": {k: [" ".join(l) for l in v[0][:5]] for k, v in samples.items()},
         "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
