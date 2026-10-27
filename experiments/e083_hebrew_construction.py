"""E083: proof by construction - fit a Hebrew -> Voynich transformation, then test the decode. See reports/E083_PREREG.md.

Transformation family (one per source text): source word = prefix state + root letters + suffix state
  front  = PT[prefix state]                (table: source prefix -> Voynich front, 14 options)
  bridge = concat(RT[c] for c in root[:M])  (table: source letter -> Voynich chunk or dropped, 31 options; M = root cap)
  ending = ST[suffix state]                (table: source suffix -> Voynich ending, 23 options)
Fit: simulated annealing over PT, RT, ST, M to maximise the histogram intersection between the token distribution of the
transformed source and Voynich DEV prose (sum over word strings of min(share in transformed, share in Voynich)).
Decode: each Voynich token -> the commonest source word type that transforms to it. Order test: mean word-bigram log
probability (add-0.1, model from a disjoint part of the same source) of decoded consecutive pairs in Voynich's own order,
against 200 shuffles of Voynich's word order (line lengths kept); z.
Run: caffeinate -ims .venv/bin/python experiments/e083_hebrew_construction.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time, unicodedata
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
OUT = ROOT / "experiments/results/e083.json"
SEED, N = 83083, 28841
ITERS, RESTARTS, SHUF = 60000, 3, 200
FRONTS = ["", "o", "q", "qo", "d", "y", "s", "l", "ch", "sh", "ok", "ot", "qok", "qot"]
ENDS = ["", "y", "dy", "edy", "eedy", "ey", "eey", "aiin", "ain", "iin", "in", "ol", "or", "al", "ar", "am", "m", "r", "l", "s", "o", "d", "an"]
CHUNKS = [None, "k", "t", "p", "f", "ch", "sh", "e", "ee", "ke", "te", "ckh", "cth", "cph", "cfh", "a", "o", "l", "r", "d", "s",
          "i", "y", "kch", "tch", "pch", "ol", "al", "ai", "eo", "che"]
MCAPS = [1, 2, 3, 4, 99]
HE_PRE = ["וה", "וב", "ול", "ומ", "וכ", "וש", "ה", "ו", "ב", "ל", "מ", "כ", "ש"]
HE_SUF = ["ים", "ות", "יו", "יה", "הם", "הן", "כם", "נו", "תי", "תם", "ו", "ה", "י", "ך", "ם", "ן", "ת"]
FAMILY = {"hebrew", "hebrew_datadriven", "aramaic_onkelos", "judeoarabic_saadia"}


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


# ----------------------------------------------------------------------------------------------- sources
def source_words(name):
    from e064_early_audit import tok
    if name in ("aramaic_onkelos", "judeoarabic_saadia"):
        from e052_shortlist_attack import norm
        fn = {"aramaic_onkelos": "onkelos.txt", "judeoarabic_saadia": "rasag.txt"}[name]
        return [w for l in (ROOT / "data/external/hebrew_script" / fn).read_text(encoding="utf-8").splitlines() for w in norm(l)]
    bid = {"hebrew": "hboWLC", "hebrew_datadriven": "hboWLC", "hebrew_shuffled": "hboWLC", "latin": "latVUC", "greek": "grcbyz",
           "german": "deu1912", "arabic": "arb-vd", "turkish": "turytc"}[name]
    w = tok(bid)
    if bid in ("hboWLC", "arb-vd"):
        w = [x for x in (cons(t) for t in w) if x]
    if name == "hebrew_shuffled":
        rng = random.Random(SEED)
        w = ["".join(rng.sample(x, len(x))) for x in w]
    return w


def affix_lists(name, types):
    if name in ("hebrew", "hebrew_shuffled", "aramaic_onkelos", "judeoarabic_saadia"):
        return HE_PRE, HE_SUF
    fr, en = Counter(), Counter()
    for w in types:
        for k in (1, 2):
            if len(w) > k + 1:
                fr[w[:k]] += 1; en[w[-k:]] += 1
    return [p for p, _ in fr.most_common(13)], [s for s, _ in en.most_common(17)]


def decompose(w, PRE, SUF):
    p = next((x for x in sorted(PRE, key=len, reverse=True) if w.startswith(x) and len(w) - len(x) >= 2), "")
    r = w[len(p):]
    s = next((x for x in sorted(SUF, key=len, reverse=True) if r.endswith(x) and len(r) - len(x) >= 1), "")
    return p, (r[:len(r) - len(s)] if s else r), s


# ----------------------------------------------------------------------------------------------- fitting
class Fit:
    def __init__(self, types_counts, PRE, SUF, voy, rng):
        self.rng = rng
        self.dec = {w: decompose(w, PRE, SUF) for w in types_counts}
        self.cnt = types_counts; self.tot = sum(types_counts.values())
        self.letters = sorted({c for _, r, _ in self.dec.values() for c in r})
        self.pstates = [""] + PRE; self.sstates = [""] + SUF
        self.voy = voy
        self.PT = {p: rng.randrange(len(FRONTS)) for p in self.pstates}
        self.ST = {s: rng.randrange(len(ENDS)) for s in self.sstates}
        self.RT = {c: rng.randrange(len(CHUNKS)) for c in self.letters}
        self.M = rng.randrange(len(MCAPS))
        self.byP, self.byS, self.byL = defaultdict(list), defaultdict(list), defaultdict(list)
        for w, (p, r, s) in self.dec.items():
            self.byP[p].append(w); self.byS[s].append(w)
            for c in set(r):
                self.byL[c].append(w)
        self.full()

    def enc(self, w):
        p, r, s = self.dec[w]
        b = "".join(CHUNKS[self.RT[c]] or "" for c in r[:MCAPS[self.M]])
        return FRONTS[self.PT[p]] + b + ENDS[self.ST[s]]

    def full(self):
        self.code = {w: self.enc(w) for w in self.cnt}
        self.E = Counter()
        for w, c in self.cnt.items():
            self.E[self.code[w]] += c / self.tot
        self.score = sum(min(v, self.voy.get(k, 0.0)) for k, v in self.E.items())

    def _apply(self, ws):
        delta = 0.0; changes = []
        for w in ws:
            old, new = self.code[w], self.enc(w)
            if old == new:
                continue
            q = self.cnt[w] / self.tot
            for k, d in ((old, -q), (new, q)):
                before = self.E.get(k, 0.0); after = before + d
                v = self.voy.get(k, 0.0)
                delta += min(after, v) - min(before, v)
                self.E[k] = after
            self.code[w] = new; changes.append((w, old))
        return delta, changes

    def _undo(self, changes):
        for w, old in reversed(changes):
            new = self.code[w]; q = self.cnt[w] / self.tot
            self.E[new] -= q; self.E[old] = self.E.get(old, 0.0) + q; self.code[w] = old

    def step(self, T):
        r = self.rng.random()
        if r < 0.25:
            k = self.rng.choice(self.pstates); tab, opts, ws = self.PT, len(FRONTS), self.byP[k]
        elif r < 0.5:
            k = self.rng.choice(self.sstates); tab, opts, ws = self.ST, len(ENDS), self.byS[k]
        elif r < 0.98:
            k = self.rng.choice(self.letters); tab, opts, ws = self.RT, len(CHUNKS), self.byL[k]
        else:
            oldM = self.M; self.M = self.rng.randrange(len(MCAPS))
            d, ch = self._apply(list(self.cnt))
            if d >= 0 or self.rng.random() < math.exp(d / T):
                self.score += d
            else:
                self._undo(ch); self.M = oldM
            return
        old = tab[k]; tab[k] = self.rng.randrange(opts)
        d, ch = self._apply(ws)
        if d >= 0 or self.rng.random() < math.exp(d / T):
            self.score += d
        else:
            self._undo(ch); tab[k] = old

    def run(self, iters):
        for i in range(iters):
            T = 0.01 * (0.0005 / 0.01) ** (i / iters)
            self.step(T)
        self.full()
        return self.score


def fit_task(args):
    name, restart, voy = args
    w = source_words(name)
    rng = random.Random(SEED + 1000 * restart + hash_name(name))
    window = w[10000:10000 + N]
    cnt = Counter(window)
    PRE, SUF = affix_lists(name, sorted(cnt))
    f = Fit(cnt, PRE, SUF, voy, rng)
    s = f.run(ITERS)
    return name, restart, s, {"PT": {p: FRONTS[i] for p, i in f.PT.items()}, "ST": {s_: ENDS[i] for s_, i in f.ST.items()},
                              "RT": {c: CHUNKS[i] for c, i in f.RT.items()}, "M": MCAPS[f.M], "PRE": PRE, "SUF": SUF}


def hash_name(s):
    import zlib
    return zlib.crc32(s.encode()) & 0xFFFF


# ----------------------------------------------------------------------------------------------- decode and order test
def encoder(tables):
    PRE, SUF = tables["PRE"], tables["SUF"]
    def enc(w):
        p, r, s = decompose(w, PRE, SUF)
        return tables["PT"].get(p, "") + "".join((tables["RT"].get(c) or "") for c in r[:tables["M"]]) + tables["ST"].get(s, "")
    return enc


def order_test(name, tables, vlines, rng, lm_words=None):
    w = source_words(name)
    model_part = lm_words if lm_words is not None else (w[:10000] + w[10000 + N:])
    enc = encoder(tables)
    window = Counter(w[10000:10000 + N])
    inv = {}
    for t, c in window.most_common():
        inv.setdefault(enc(t), t)
    uni = Counter(model_part); big = Counter(zip(model_part, model_part[1:])); V = len(uni) + 1
    def lp(a, b):
        return math.log((big.get((a, b), 0) + 0.1) / (uni.get(a, 0) + 0.1 * V))
    def score(lines):
        vals = []
        for l in lines:
            d = [inv.get(x) for x in l]
            for a, b in zip(d, d[1:]):
                if a and b:
                    vals.append(lp(a, b))
        return float(np.mean(vals)) if vals else float("nan"), len(vals)
    obs, npairs = score(vlines)
    flat = [x for l in vlines for x in l]; lens = [len(l) for l in vlines]
    null = []
    for _ in range(SHUF):
        rng.shuffle(flat); out, i = [], 0
        for L in lens:
            out.append(flat[i:i + L]); i += L
        null.append(score(out)[0])
    mu, sd = float(np.mean(null)), float(np.std(null, ddof=1))
    tokens = [x for l in vlines for x in l]
    dec_share = sum(1 for x in tokens if x in inv) / len(tokens)
    sample = [" ".join(inv.get(x, "·") for x in l) for l in vlines[:12]]
    return {"obs": obs, "null_mean": mu, "z": (obs - mu) / sd if sd > 0 else 0.0, "pairs": npairs, "decoded_share": dec_share, "sample": sample}


# ----------------------------------------------------------------------------------------------- known answer
def known_answer_text(rng):
    """Hebrew (window 2) transformed by a hidden random table; returned as lines of Voynich-like strings."""
    w = source_words("hebrew")
    win = w[60000:60000 + N]
    PRE, SUF = HE_PRE, HE_SUF
    letters = sorted({c for x in win for c in decompose(x, PRE, SUF)[1]})
    hidden = {"PT": {p: rng.choice(FRONTS) for p in [""] + PRE}, "ST": {s: rng.choice(ENDS) for s in [""] + SUF},
              "RT": {c: rng.choice(CHUNKS[1:]) for c in letters}, "M": 3, "PRE": PRE, "SUF": SUF}
    enc = encoder(hidden)
    toks = [enc(x) for x in win]
    return toks, hidden, win


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    from e011_twin_search import voynich_lines
    vl, _, _, locked = voynich_lines()
    vl = [[x for x in l if x] for l in vl]; vl = [l for l in vl if l]
    V = Counter(x for l in vl for x in l); tot = sum(V.values()); voy = {k: v / tot for k, v in V.items()}
    # known answer target
    ktoks, hidden, kwin = known_answer_text(rng)
    KC = Counter(ktoks); kt = sum(KC.values()); kvoy = {k: v / kt for k, v in KC.items()}
    sources = ["hebrew", "hebrew_datadriven", "aramaic_onkelos", "judeoarabic_saadia", "latin", "greek", "german", "arabic", "turkish", "hebrew_shuffled"]
    jobs = [("hebrew", r, kvoy) for r in range(RESTARTS)]
    jobs += [(s, r, voy) for s in sources for r in range(RESTARTS)]
    with Pool(a.workers) as pool:
        res = pool.map(fit_task, jobs)
    known = [x for x in res[:RESTARTS]]; fits = res[RESTARTS:]
    kb = max(known, key=lambda x: x[2])
    # known-answer decode accuracy and order test against its own lines
    klines, i = [], 0
    for l in vl:
        klines.append(ktoks[i:i + len(l)]); i += len(l)
        if i >= len(ktoks):
            break
    enc_fit = encoder(kb[3]); inv = {}
    for t, c in Counter(source_words("hebrew")[10000:10000 + N]).most_common():
        inv.setdefault(enc_fit(t), t)
    hid_enc = encoder(hidden)
    correct = sum(1 for x, src in zip(ktoks, kwin) if inv.get(x) == src) / len(ktoks)
    kord = order_test("hebrew", kb[3], klines, random.Random(SEED + 7))
    log(f"[known answer] hidden-table Hebrew: best intersection {kb[2]:.3f}; tokens decoded to the right word {correct:.3f}; "
        f"order z {kord['z']:+.2f} (pairs {kord['pairs']}, decoded share {kord['decoded_share']:.2f})")
    best = {}
    for s in sources:
        b = max((x for x in fits if x[0] == s), key=lambda x: x[2]); best[s] = b
        log(f"[fit] {s:20s} intersection {b[2]:.3f} (restarts {[round(x[2], 3) for x in fits if x[0] == s]}) M={b[3]['M']}")
    fam = max(best[s][2] for s in sources if s in FAMILY); other = max(best[s][2] for s in sources if s not in FAMILY)
    log(f"[specificity] best Hebrew-family {fam:.3f} vs best other source {other:.3f}")
    orders = {}
    for s in sources:
        o = order_test(s, best[s][3], vl, random.Random(SEED + 11)); orders[s] = o
        log(f"[order] {s:20s} decoded share {o['decoded_share']:.3f} pairs {o['pairs']} z {o['z']:+.2f}")
    hb = max((s for s in sources if s in FAMILY), key=lambda s: best[s][2])
    log(f"[decode sample, {hb}]"); [log("   " + x) for x in orders[hb]["sample"][:8]]
    valid = correct >= 0.5 and kord["z"] > 3
    step_spec = fam > other + 0.05
    step_order = orders[hb]["z"] > 3
    if not valid:
        verdict = "VOID (the construction cannot recover a known Hebrew text)"
    elif step_spec and step_order:
        verdict = f"CONSTRUCTION HOLDS ({hb}): next blind reading and LOCKED_TEST prediction"
    elif step_spec:
        verdict = "HEBREW FITS BEST BUT ORDER FAILS"
    elif step_order:
        verdict = "ORDER PASSES BUT FIT NOT HEBREW-SPECIFIC"
    else:
        verdict = "CONSTRUCTION FAILS (fit not Hebrew-specific, order not Hebrew)"
    log(f"VERDICT {verdict} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E083", "seed": SEED, "known_answer": {"intersection": kb[2], "correct_words": correct,
                               "order": kord, "hidden_M": 3}, "fits": {s: {"intersection": best[s][2], "tables": best[s][3],
                               "restarts": [x[2] for x in fits if x[0] == s]} for s in sources}, "orders": orders,
                               "family_best": fam, "other_best": other, "verdict": verdict, "locked_test_excluded": locked,
                               "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
