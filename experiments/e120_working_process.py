"""E120 (Arham, 'do 1'): can ONE meaningless writing process reproduce the Voynich's solid facts? See reports/E120_PREREG.md.

Process P5 ("habit writer", after quimqu 2026 thread-6219 rules and Parisel 2026's per-folio switch), one family,
grid GRID (32 settings, declared; rule 9):
  * Two habit states, A and B (each page takes its Currier language; '?' counts as A), each with its own piece weights,
    letter chain, position habits and habit lexicon (LX pseudo-words drawn from the E114 piece lists, sizes 20/60/40,
    with the state's weights; word r has weight r^-ZIPF).
  * Sessions: every (sheet, state) gets its own lexicon and piece weights, multiplied by exp(SIGMA * N(0,1)).
  * Each token: with probability COPY copy an earlier token of the current or previous page (the word directly above
    with probability ABOVE, else lag ~ geometric with mean LAG), then with probability MUT change it by one of six
    moves (e<->ee, r<->l, t<->k, d+/-, q+/-, new ending); otherwise, with probability LEXP, draw a habit word (lexicon
    reweighted by the position habit: front ratio at line start, ending ratio at line end, front ratio in
    paragraph-first lines), else a new word from the state's order-2 letter chain (best of NCAND draws by the same
    position weights).
  * Book shape: the Voynich DEV pages, lines, line lengths, paragraph flags, sheets, Currier states and scribes.
Stage 1 (tuning, the 13-feature E032 battery only): every grid setting x 2 seeds; judged as E098 against the Voynich
(z = (V - mean) / max(sd, 2%|V|, 0.01), fail if |z| > 3). Best = fewest fails, then smallest sum |z|.
Stage 2 (held-out, computed ONCE, on the best setting x 5 fresh seeds; mean over seeds must fall in the band):
  H1 phrase reuse Q3 (E100)            Voynich +-25%
  H2 repeated 4-word phrases RP4        <= 20            (Voynich 0; languages >= 223)
  H3 pair asymmetry ASYM (E104)         <= 0.30          (Voynich 0.18; languages >= 0.43)
  H4 family-level repeats z (E066)      |z| <= 2         (Voynich -1.2; languages +4..+14)
  H5 distinct words per 150 (E067)      Voynich +-8      (Voynich ~112; languages 95, copy generator 94)
  H6 sheet / reading-order I_word (E059) >= 1.10         (Voynich 1.25)
  H7 page-opening surprise HEAD (X117)  0.60..1.20       (Voynich +0.89; all controls <= 0.74)
  H8 lines independent z (E086)         |z| < 3          (Voynich +0.2; languages +26..+46)
  H9 common-word partner STAB (E069)    0.055..0.083     (Voynich 0.073; generator <= 0.053; languages p10 0.083)
  H10 letter link MIDMI (X115)          8.3e-4..16e-4    (Voynich 11.9e-4; meaningful texts <= 8.2e-4)
Verdict: WORKING PROCESS  battery <= 1 fail and >= 9/10 held-out -> M x 3
         PARTIAL          battery <= 2 fails and 6..8 held-out  -> none
         NO WORKING PROCESS otherwise                           -> M x 0.9 (as E114)
Rule 8: any held-out fact whose 5-seed mean lies within 0.5 seed-sd of a band edge is re-run on 10 fresh seeds and
counts as reproduced only if >= 8 of 10 seeds are inside the band.
Run: caffeinate -ims .venv/bin/python experiments/e120_working_process.py [--dev]
--dev: stage 1 on 4 grid corners only (no held-out fact is computed on any generated book).
"""
from __future__ import annotations

import argparse, itertools, json, math, random, re, sys, time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e093_explanation_model as E93  # noqa: E402
import e114_dice_generator as D  # noqa: E402
from e032_copy_generator import FEATS, Z_OK, features  # noqa: E402
from e098_cipher_classes import judge  # noqa: E402

SEED = 120120
OUT = ROOT / "experiments/results/e120.json"
LX, SIZE = 4000, (20, 60, 40)
GRID = {"COPY": [0.4, 0.55], "MUT": [0.5, 0.7], "LEXP": [0.2, 0.35], "LAG": [8, 16], "SIGMA": [0.1, 0.25]}
ZIPF, ABOVE, NCAND = 1.0, 0.1, 4
TUNE_SEEDS, HELD_SEEDS = (1, 2), (101, 102, 103, 104, 105)


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ Voynich shape and habits
def voynich_book():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    pages, meta, locked = E93.voynich()
    _, toks = parse(); lk = set(locked_test_leaves(toks))
    F = {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in lk:
            k = (t.folio, t.line_no); F[k] = F.get(k, False) or bool(t.para_start)
    key = lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f)
    order = sorted(F, key=lambda k: (key(k[0]), k))
    byf = defaultdict(list)
    for k in order:
        byf[k[0]].append(F[k])
    folios = sorted(byf, key=key)
    flags = [byf[f] for f in folios]
    assert [len(x) for x in flags] == [len(p) for p in pages]
    return pages, meta, flags, locked


def parser(ms):
    Fs = sorted((p for p, _ in ms["F"]), key=len, reverse=True); Ms = {p for p, _ in ms["M"]}
    Es = sorted((p for p, _ in ms["E"]), key=len, reverse=True); cache = {}

    def parse(w):
        if w not in cache:
            cache[w] = None
            for f in Fs:
                if w.startswith(f):
                    for e in Es:
                        if len(f) + len(e) <= len(w) and (not e or w.endswith(e)) and w[len(f):len(w) - len(e)] in Ms:
                            cache[w] = (f, w[len(f):len(w) - len(e)], e); break
                if cache[w]:
                    break
        return cache[w]
    return parse


def habits(pages, flags, ms):
    parse = parser(ms)
    cnt = {k: Counter() for k in ("F", "Finit", "Fpara", "E", "Efinal")}
    for p, fl in zip(pages, flags):
        for l, f in zip(p, fl):
            for i, w in enumerate(l):
                r = parse(w)
                if not r:
                    continue
                cnt["F"][r[0]] += 1; cnt["E"][r[2]] += 1
                if i == 0:
                    cnt["Finit"][r[0]] += 1
                if i == len(l) - 1:
                    cnt["Efinal"][r[2]] += 1
                if f:
                    cnt["Fpara"][r[0]] += 1
    ratio = lambda num, den: {k: ((num[k] + 1) / (sum(num.values()) + len(den))) / ((den[k] + 1) / (sum(den.values()) + len(den))) for k in den}
    return {"init": ratio(cnt["Finit"], cnt["F"]), "final": ratio(cnt["Efinal"], cnt["E"]), "para": ratio(cnt["Fpara"], cnt["F"])}


def state_masters(pages, meta, ms):
    """the same piece inventory, token weights counted separately on Currier A and B pages ('?' pages count as A)"""
    parse = parser(ms); out = {}
    for st in ("A", "B"):
        wf, wm, we = Counter(), Counter(), Counter()
        for p, m in zip(pages, meta):
            if (m["currier"] == "B") == (st == "B"):
                for l in p:
                    for w in l:
                        r = parse(w)
                        if r:
                            wf[r[0]] += 1; wm[r[1]] += 1; we[r[2]] += 1
        out[st] = {k: [(x, W[x] + 0.5) for x, _ in ms[k]] for k, W in (("F", wf), ("M", wm), ("E", we))}
    return out


def markov(pages, meta, st):
    """order-2 letter chain over word tokens of one habit state ('^' start, '$' end)"""
    c = defaultdict(Counter)
    for p, m in zip(pages, meta):
        if (m["currier"] == "B") == (st == "B"):
            for l in p:
                for w in l:
                    s = "^^" + w + "$"
                    for i in range(2, len(s)):
                        c[s[i - 2:i]][s[i]] += 1
    return {k: ([x for x in v], np.cumsum([v[x] for x in v])) for k, v in c.items()}


def chain_word(mk, rng):
    for _ in range(20):
        ctx, out = "^^", ""
        while len(out) < 15:
            ch, cu = mk[ctx]; x = ch[int(np.searchsorted(cu, rng.random() * cu[-1]))]
            if x == "$":
                break
            out += x; ctx = ctx[1] + x
        if out:
            return out
    return "y"


def lexicon(ms, rng):
    pf = [(p, w) for p, w in ms["F"]]; pm = ms["M"]; pe = ms["E"]
    tot = lambda L: sum(w for _, w in L)
    seen, out = set(), []
    tries = 0
    while len(out) < LX and tries < LX * 200:
        tries += 1
        f = rng.choices(pf, weights=[w for _, w in pf])[0]; m = rng.choices(pm, weights=[w for _, w in pm])[0]
        e = rng.choices(pe, weights=[w for _, w in pe])[0]
        w = f[0] + m[0] + e[0]
        if w and w not in seen:
            seen.add(w); out.append((w, f[0], e[0], f[1] / tot(pf) * m[1] / tot(pm) * e[1] / tot(pe)))
    out.sort(key=lambda x: -x[3])
    return out


# ------------------------------------------------------------------ process
ALT = [("ee", "e"), ("e", "ee"), ("r", "l"), ("l", "r"), ("t", "k"), ("k", "t")]


def mutate(w, eends, rng):
    mv = rng.randrange(6)
    if mv == 0:                                   # e <-> ee
        a, b = ALT[rng.randrange(2)]
    elif mv == 1:
        a, b = ALT[2 + rng.randrange(2)]
    elif mv == 2:
        a, b = ALT[4 + rng.randrange(2)]
    elif mv == 3:                                 # d +/-
        if "d" in w and rng.random() < 0.5:
            i = rng.choice([i for i, c in enumerate(w) if c == "d"]); return (w[:i] + w[i + 1:]) or w
        i = rng.randrange(len(w) + 1); return w[:i] + "d" + w[i:]
    elif mv == 4:                                 # q +/-
        return w[1:] if w.startswith("q") and len(w) > 1 else "q" + w
    else:                                         # new ending
        e = rng.choices(eends[0], weights=eends[1])[0]
        for k in range(min(4, len(w) - 1), 0, -1):
            if w[-k:] in eends[2]:
                return w[:-k] + e
        return w + e
    idx = [m.start() for m in re.finditer(re.escape(a), w)]
    if not idx:
        return w
    i = rng.choice(idx); return w[:i] + b + w[i + len(a):]


def tables(ctx, st):
    ms, lex, hab = ctx["sms"][st], ctx["lex"][st], ctx["hab"][st]
    T = {"words": [x[0] for x in lex], "base": np.arange(1, len(lex) + 1, dtype=float) ** -ZIPF,
         "fi": np.array([hab["init"].get(x[1], 1.0) for x in lex]), "ef": np.array([hab["final"].get(x[2], 1.0) for x in lex]),
         "fp": np.array([hab["para"].get(x[1], 1.0) for x in lex])}
    T["FP"], T["FW"] = [p for p, _ in ms["F"]], np.array([w for _, w in ms["F"]], float)
    T["MP"], T["MW"] = [p for p, _ in ms["M"]], np.array([w for _, w in ms["M"]], float)
    T["EP"], T["EW"] = [p for p, _ in ms["E"]], np.array([w for _, w in ms["E"]], float)
    T["eends"] = ([p for p in T["EP"] if p], [w for p, w in zip(T["EP"], T["EW"]) if p], {p for p in T["EP"] if p})
    T["pf_init"] = np.array([hab["init"].get(p, 1.0) for p in T["FP"]]); T["pf_para"] = np.array([hab["para"].get(p, 1.0) for p in T["FP"]])
    T["pe_final"] = np.array([hab["final"].get(p, 1.0) for p in T["EP"]])
    return T


def book(setting, ctx, seed):
    C, MU, LP, LG, SIGMA = setting
    rng = random.Random(SEED * 7919 + seed); nrng = np.random.default_rng(SEED * 7919 + seed)
    TS = {st: tables(ctx, st) for st in ("A", "B")}
    parse = parser(ctx["ms"])
    sess = {}
    out, prev_page = [], []
    pick = lambda cu: int(np.searchsorted(cu, rng.random() * cu[-1]))
    for p_lines, fl, m in zip(ctx["shape"], ctx["flags"], ctx["meta"]):
        st = "B" if m["currier"] == "B" else "A"; T = TS[st]; sh = (m["bifolio"], st)
        words, eends = T["words"], T["eends"]; FP, MP, EP = T["FP"], T["MP"], T["EP"]
        if sh not in sess:
            noise = lambda n: np.exp(SIGMA * nrng.standard_normal(n))
            wv = T["base"] * noise(len(T["base"])); fw = T["FW"] * noise(len(T["FW"])); ew = T["EW"] * noise(len(T["EW"]))
            fi, ef, fp = T["fi"], T["ef"], T["fp"]
            S = {k: np.cumsum(wv * f) for k, f in (("mid", 1.0), ("init", fi), ("final", ef), ("para", fp),
                                                    ("para_init", fp * fi), ("para_final", fp * ef))}
            S["F"] = {"mid": np.cumsum(fw), "init": np.cumsum(fw * T["pf_init"]), "para": np.cumsum(fw * T["pf_para"]),
                      "para_init": np.cumsum(fw * T["pf_init"] * T["pf_para"])}
            S["E"] = {"mid": np.cumsum(ew), "final": np.cumsum(ew * T["pe_final"])}
            S["M"] = np.cumsum(T["MW"])
            sess[sh] = S
        S = sess[sh]
        page, buf = [], list(prev_page)
        prev_line = []
        for L, f in zip(p_lines, fl):
            line = []
            for i in range(L):
                if buf and rng.random() < C:
                    if prev_line and i < len(prev_line) and rng.random() < ABOVE:
                        w = prev_line[i]                                  # the word above
                    else:
                        lag = min(len(buf), 1 + int(nrng.geometric(1.0 / LG))); w = buf[-lag]
                    if rng.random() < MU:
                        w = mutate(w, eends, rng)
                else:
                    pos = "init" if i == 0 else "final" if i == L - 1 else "mid"
                    pk = ("para" if pos == "mid" else "para_" + pos) if f else pos
                    if rng.random() < LP:                                  # a habit word
                        w = words[pick(S[pk])]
                    else:                                                  # a new word from the letter chain,
                        cand = [chain_word(ctx["mk"][st], rng) for _ in range(NCAND)]   # position habit by reweighting
                        wt = []
                        for c_ in cand:
                            r_ = parse(c_); x = 1.0
                            if r_:
                                if pos == "init":
                                    x *= ctx["hab"][st]["init"].get(r_[0], 1.0)
                                if pos == "final":
                                    x *= ctx["hab"][st]["final"].get(r_[2], 1.0)
                                if f:
                                    x *= ctx["hab"][st]["para"].get(r_[0], 1.0)
                            wt.append(x)
                        w = rng.choices(cand, weights=wt)[0]
                line.append(w); buf.append(w)
            page.append(line); prev_line = line
        out.append(page); prev_page = [w for l in page for w in l]
    return out


# ------------------------------------------------------------------ stage tasks
CTX = {}


def _init(c):
    CTX.update(c)


def tune_task(a):
    setting, seed = a
    pages = book(setting, CTX, seed)
    return a, features([l for p in pages for l in p if l], SEED + seed)


def held(pages, ctx, seed):
    import e099_phrase_repeats_v2 as P
    import e104_pair_reversal as E104
    import e086_spaces_and_lines as E86
    import e069_word_partners as E69
    import e117_surprise_map as X117
    import e115_long_range as X115
    from e058_word_repeat_individuality_v2 import stats as e66stats
    from e067_gibberish_vocabulary import windows
    from e059_cleanup_round import i_word
    rng = random.Random(seed)
    lines = [l for p in pages for l in p if l]; toks = [w for l in lines for w in l]; lens = [len(l) for l in lines]
    m = P.measure(toks, lens, rng)
    r = {"H1": m[3]["Q"], "H2": m[4]["RP"], "H3": E104.measure([l for l in lines if len(l) > 1])["ASYM"],
         "H4": e66stats(lines, True, rng)["z"]}
    r["H5"] = float(np.mean([x["T"] for x in windows(toks, 200, rng)]))
    sheets = sorted({mm["bifolio"] for mm in ctx["meta"]}); sid = {s: i for i, s in enumerate(sheets)}
    csh = [sid[mm["bifolio"]] for p, mm in zip(pages, ctx["meta"]) for l in p for w in l]
    n = len(toks); c49 = [(i * 49) // n for i in range(n)]
    a_ = i_word(toks, csh, len(sheets), random.Random(seed))[0]; b_ = i_word(toks, c49, 49, random.Random(seed + 1))[0]
    r["H6"] = a_ / b_ if b_ else float("nan")
    r["H7"] = X117.measure(pages)["HEAD"]
    r["H8"] = E86.continuity(pages, random.Random(E86.SEED))["z"]
    r["H9"] = E69.stability(lines, seed)["STAB"]
    hands = sorted({mm["hand"] for mm in ctx["meta"]}, key=lambda h: -sum(sum(map(len, p)) for p, mm in zip(pages, ctx["meta"]) if mm["hand"] == h))
    blocks = [[w for p, mm in zip(pages, ctx["meta"]) if mm["hand"] == h for l in p for w in l] for h in hands]
    I = X115.glyph_mi(blocks, random.Random(seed)); r["H10"] = float(np.mean([I[d] for d in X115.MID]))
    return r


def held_task(a):
    setting, seed = a
    return a, held(book(setting, CTX, seed), CTX, seed)


def bands(V):
    return {"H1": (0.75 * V["H1"], 1.25 * V["H1"]), "H2": (-1, 20), "H3": (-1, 0.30), "H4": (-2, 2),
            "H5": (V["H5"] - 8, V["H5"] + 8), "H6": (1.10, 99), "H7": (0.60, 1.20), "H8": (-3, 3),
            "H9": (0.055, 0.083), "H10": (8.3e-4, 16e-4)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dev", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    pages, meta, flags, locked = voynich_book()
    ms = D.masters(pages, SIZE)
    sms = state_masters(pages, meta, ms)
    isB = lambda m: m["currier"] == "B"
    sub = lambda st: ([p for p, m in zip(pages, meta) if isB(m) == (st == "B")], [f for f, m in zip(flags, meta) if isB(m) == (st == "B")])
    ctx = {"ms": ms, "sms": sms, "hab": {st: habits(*sub(st), ms) for st in ("A", "B")},
           "mk": {st: markov(pages, meta, st) for st in ("A", "B")},
           "lex": {st: lexicon(sms[st], random.Random(SEED + i)) for i, st in enumerate(("A", "B"))},
           "shape": [[len(l) for l in p] for p in pages], "flags": flags, "meta": meta}
    log(f"lexicons {[len(v) for v in ctx['lex'].values()]} | pages {len(pages)} | sheets {len({m['bifolio'] for m in meta})}")
    V = features([l for p in pages for l in p if l], SEED)
    settings = list(itertools.product(*GRID.values()))
    if a.dev:
        pass
    with Pool(4, initializer=_init, initargs=(ctx,)) as pool:
        R = pool.map(tune_task, [(s, sd) for s in settings for sd in TUNE_SEEDS])
        rows = defaultdict(list)
        for (s, sd), f in R:
            rows[s].append(f)
        J = {s: judge(V, rows[s]) for s in settings}
        rank = sorted(settings, key=lambda s: (J[s]["n_fail"], sum(abs(z) for z in J[s]["z"].values())))
        for s in rank[:10]:
            log(f"setting {dict(zip(GRID, s))} fails {J[s]['n_fail']} {J[s]['fail']}")
        best = rank[0]
        res = {"experiment": "E120", "seed": SEED, "grid": GRID, "voynich_battery": V,
               "tuning": {str(s): J[s] for s in settings}, "best": dict(zip(GRID, best)), "best_battery": J[best],
               "sample": [" ".join(l) for l in book(best, ctx, 1)[0][:4]], "locked_test_excluded": locked}
        log(f"BEST {res['best']} battery fails {J[best]['n_fail']} {J[best]['fail']} | sample {res['sample'][:2]}")
        if not a.dev:
            Vh = held(pages, ctx, SEED); B = bands(Vh)
            H = pool.map(held_task, [(best, sd) for sd in HELD_SEEDS])
            vals = {k: [h[k] for _, h in H] for k in B}
            ok = {}
            for k, (lo, hi) in B.items():
                mu, sd = float(np.mean(vals[k])), float(np.std(vals[k], ddof=1))
                inside = lo <= mu <= hi
                if min(abs(mu - lo), abs(mu - hi)) < 0.5 * sd:
                    H2 = pool.map(held_task, [(best, 1000 + i) for i in range(10)])
                    inside = sum(lo <= h[k] <= hi for _, h in H2) >= 8
                ok[k] = bool(inside)
                log(f"{k}: Voynich {Vh[k]:.4g} | band {lo:.4g}..{hi:.4g} | process mean {mu:.4g} (sd {sd:.3g}) -> {'YES' if inside else 'no'}")
            nh = sum(ok.values()); nb = J[best]["n_fail"]
            v = ("WORKING PROCESS" if nb <= 1 and nh >= 9 else "PARTIAL" if nb <= 2 and 6 <= nh <= 8 else "NO WORKING PROCESS")
            fM = {"WORKING PROCESS": 3.0, "PARTIAL": 1.0}.get(v, 0.9)
            res.update(voynich_held=Vh, bands=B, held=vals, reproduced=ok, n_held=nh, verdict=v, factor_M=fM)
            log(f"VERDICT {v}: battery fails {nb}, held-out {nh}/10 | M x {fM}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e120_dev.json" if a.dev else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
