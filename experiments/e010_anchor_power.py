"""E010 part 2: known-answer power analysis for semantic anchors.

Question: with N anchors (cipher word <-> proposed meaning) of which a fraction r are correct, can an
anchor-consistency score tell the TRUE key from (i) random keys, (ii) near-miss keys (true key + k swaps) and,
crucially, (iii) wrong keys OPTIMISED to fit anchors (the flexible-method failure of past 'solutions')?

Setup (all known-answer, synthetic; no Voynich text is used here):
- plaintext words: word types (len 4-10, freq>=3) of TUNE-role books of one train-family language per family
  (de germanic, fr romance, pl slavic; data/derived/benchmark_v1/book_roles.json); month-name scenario uses
  the 12 month names of the same languages.
- mechanisms / analyst freedom:
    mono_strict      vcl.synthetic.encoders.mono; analyst key = injective unit->letter; score = edit similarity
    verbose_strict   encoders.homophonic + local verbose layer (fixed null modifier glyph after 1/3 of letters);
                     analyst key = unit -> letter or '' (many-to-one); score = edit similarity
    flexible_anagram same cipher; analyst key = unit -> letter, '' or one of the 30 commonest bigrams; score =
                     multiset (anagram-allowed) Dice similarity
- anchor-consistency score S(K) = mean over anchors of max over the anchor's candidate cipher words of
  sim(decode(word, K), meaning). Wrong anchors pair the cipher word with another lexicon word of similar length
  (a misidentified plant) or another month (month scenario).
Tests (one-sided, alpha = 0.01):
  T1  S(true key; A)            vs null of max_K S(K; A0) over anchor sets A0 with r = 0 (optimised wrong keys)
  T2  max_K S(K; A)             vs the same null  (does fitting to the real anchors reveal real signal?)
  T3  held-out: fit K on half of A, score the other half; null = same procedure on r = 0 sets
  plus random keys and near-miss keys (k swaps) around the true key.
Identifiability frontier: smallest N (per r, mechanism) with power (fraction of trials p < 0.01) >= 0.8.
Finally the REAL anchor set (data/derived/anchors_v1, usable word-level rows; tier reliabilities stated as
assumptions) is simulated directly at its own N and r.

Run: .venv/bin/python experiments/e010_anchor_power.py [--workers 3] [--trials 30] [--nulls 200]
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
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.eval.ledger import append  # noqa: E402
from vcl.synthetic import encoders as E  # noqa: E402
from vcl.synthetic.schema import BOUNDARY  # noqa: E402

OUT = ROOT / "experiments/results/e010.json"
SEED = 20261010
ALPHA = 0.01
LANG_BOOKS = {"de": "58520", "fr": "70746", "pl": "27178"}  # tune-role books, one per train family
MONTHS = {
    "de": "januar februar märz april mai juni juli august september oktober november dezember".split(),
    "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(),
    "pl": "styczeń luty marzec kwiecień maj czerwiec lipiec sierpień wrzesień październik listopad grudzień".split(),
}
MECHS = ["mono_strict", "verbose_strict", "flexible_anagram"]
NS = [3, 5, 10, 20, 40]
RS = [1.0, 0.8, 0.5, 0.3, 0.1]
_LANG = {}


def lang_data(lang):
    if lang not in _LANG:
        from vcl.synthetic.corpora import load_books
        book = [b for b in load_books() if b["id"] == LANG_BOOKS[lang]][0]
        words = book["text"].split()
        c = Counter(words)
        lex = sorted(w for w, n in c.items() if 4 <= len(w) <= 10 and n >= 3)
        alpha = sorted({ch for w in lex for ch in w} | {ch for w in MONTHS[lang] for ch in w})
        bg = Counter(w[i:i + 2] for w in words[:200000] for i in range(len(w) - 1))
        _LANG[lang] = {"lex": lex, "alpha": alpha, "bigrams": [b for b, _ in bg.most_common(30)],
                       "context": words[:20000], "by_len": {}}
        for w in lex:
            _LANG[lang]["by_len"].setdefault(len(w), []).append(w)
    return _LANG[lang]


# ------------------------------------------------------------------ similarity
def lev(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if not la or not lb:
        return la or lb
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ai = a[i - 1]
        for j in range(1, lb + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ai != b[j - 1]))
        prev = cur
    return prev[lb]


def sim_strict(dec, tgt, _tc=None):
    m = max(len(dec), len(tgt))
    return 1.0 - lev(dec, tgt) / m if m else 1.0


def sim_anagram(dec, tgt, tc):
    if not dec:
        return 0.0
    dc = Counter(dec)
    return 2 * sum(min(v, tc.get(k, 0)) for k, v in dc.items()) / (len(dec) + len(tgt))


# ------------------------------------------------------------------ encoding
def encode(words, mech, rng, lang):
    """Encode `words` (with book context so homophone counts follow real frequencies); return cipher words
    (tuples of glyphs) and the true decoding map glyph -> string."""
    ctx = lang_data(lang)["context"]
    start = rng.randrange(0, len(ctx) - 400)
    plain = " ".join(list(words) + ctx[start:start + 300])
    if mech == "mono_strict":
        syms, key, *_ = E.mono(plain, rng)
        true = {g: c for c, g in key.items()}
    else:
        syms, key, *_ = E.homophonic(plain, rng)
        true = {g: c for c, gs in key.items() for g in gs}
        alpha = sorted({ch for ch in plain if ch != " "})
        heavy = set(rng.sample(alpha, max(1, len(alpha) // 3)))
        mods = [g for g in E.GLYPHS if g not in set(syms)][:3]
        modmap = {ch: rng.choice(mods) for ch in heavy}
        out = []
        for ch, s in zip(plain, syms):
            out.append(s)
            if ch in modmap:
                out.append(modmap[ch])
        syms = out
        for m in mods:
            true[m] = ""
    cw, cur = [], []
    for s in syms + [BOUNDARY]:
        if s == BOUNDARY:
            cw.append(tuple(cur)); cur = []
        else:
            cur.append(s)
    return cw[:len(words)], true


# ------------------------------------------------------------------ anchor sets
def make_anchors(rng, lang, mech, N, r, scenario="lexicon", M=1, r_list=None):
    """Return dict with candidates (list of list of cipher words), meanings, correct flags, true map."""
    L = lang_data(lang)
    if scenario == "months":
        idx = rng.sample(range(12), N)
        true_words = [MONTHS[lang][i] for i in idx]
    else:
        true_words = rng.sample(L["lex"], N)
    if r_list is None:
        n_ok = int(round(r * N))
        correct = [True] * n_ok + [False] * (N - n_ok)
        rng.shuffle(correct)
    else:
        correct = [rng.random() < ri for ri in r_list]
    meanings = []
    for w, ok in zip(true_words, correct):
        if ok:
            meanings.append(w)
        elif scenario == "months":
            meanings.append(rng.choice([m for m in MONTHS[lang] if m != w]))
        else:
            pool = [x for d in (-1, 0, 1) for x in L["by_len"].get(len(w) + d, []) if x != w]
            meanings.append(rng.choice(pool))
    # candidate lists: anchor i holds its true cipher word (if the word is 'present') plus M-1 distractors
    distract = [rng.choice(L["lex"]) for _ in range(N * (M - 1))]
    cw, true = encode(true_words + distract, mech, rng, lang)
    cands = []
    for i in range(N):
        c = [cw[i]] + list(cw[N + i * (M - 1): N + (i + 1) * (M - 1)])
        rng.shuffle(c)
        cands.append(c)
    return {"cands": cands, "meanings": meanings, "correct": correct, "true": true, "lang": lang}


class Scorer:
    def __init__(self, A, mech, lang, idx=None):
        L = lang_data(lang)
        self.idx = list(range(len(A["meanings"]))) if idx is None else list(idx)
        self.cands = [A["cands"][i] for i in self.idx]
        self.mean = [A["meanings"][i] for i in self.idx]
        self.tc = [Counter(m) for m in self.mean]
        self.sim = sim_anagram if mech == "flexible_anagram" else sim_strict
        units = sorted({u for c in A["cands"] for w in c for u in w})
        self.units = units
        self.uid = {u: i for i, u in enumerate(units)}
        self.cand_ids = [[[self.uid[u] for u in w] for w in c] for c in self.cands]
        if mech == "mono_strict":
            self.values = list(L["alpha"]); self.injective = True
        elif mech == "verbose_strict":
            self.values = list(L["alpha"]) + [""]; self.injective = False
        else:
            self.values = list(L["alpha"]) + [""] + L["bigrams"]; self.injective = False
        self.vid = {v: i for i, v in enumerate(self.values)}
        self.touch = [[] for _ in units]
        for a, c in enumerate(self.cand_ids):
            for u in {u for w in c for u in w}:
                self.touch[u].append(a)

    def key_from_map(self, m):
        return [self.vid[m[u]] for u in self.units]

    def anchor_score(self, a, K):
        V = self.values
        return max(self.sim("".join(V[K[u]] for u in w), self.mean[a], self.tc[a]) for w in self.cand_ids[a])

    def score(self, K):
        return sum(self.anchor_score(a, K) for a in range(len(self.cands))) / max(1, len(self.cands))

    def random_key(self, rng):
        if self.injective:
            return rng.sample(range(len(self.values)), len(self.units))
        return [rng.randrange(len(self.values)) for _ in self.units]

    def optimise(self, rng, iters=None, restarts=3):
        n = len(self.cands)
        iters = iters or 2000 + 60 * len(self.units)
        best_K, best = None, -1.0
        for _ in range(restarts):
            K = self.random_key(rng)
            sc = [self.anchor_score(a, K) for a in range(n)]
            tot = sum(sc)
            T0, T1 = 0.5, 0.005
            for it in range(iters):
                T = T0 * (T1 / T0) ** (it / iters)
                if rng.random() < 0.6:
                    # targeted move (what a flexible analyst does): make one glyph of an anchor word decode to
                    # the letter(s) at the aligned position of its proposed meaning
                    a0 = rng.randrange(n)
                    w = rng.choice(self.cand_ids[a0]); tgt = self.mean[a0]
                    if not w:
                        continue
                    j = rng.randrange(len(w)); u = w[j]
                    pos = min(len(tgt) - 1, int(j * len(tgt) / len(w)) + rng.choice((-1, 0, 0, 1)))
                    pos = max(0, pos)
                    opts = [tgt[pos]]
                    if not self.injective:
                        opts += ["", tgt[pos:pos + 2]]
                    v = self.vid.get(rng.choice(opts))
                    if v is None:
                        continue
                else:
                    u = rng.randrange(len(self.units))
                    v = rng.randrange(len(self.values))
                if v == K[u]:
                    continue
                other = None
                if self.injective and v in K:
                    other = K.index(v)
                old_u = K[u]
                K[u] = v
                if other is not None:
                    K[other] = old_u
                aff = set(self.touch[u]) | (set(self.touch[other]) if other is not None else set())
                new = {a: self.anchor_score(a, K) for a in aff}
                d = sum(new[a] - sc[a] for a in aff)
                if d >= 0 or rng.random() < math.exp(d / T):
                    for a in aff:
                        sc[a] = new[a]
                    tot += d
                    if tot > best + 1e-12:
                        best, best_K = tot, list(K)
                else:
                    K[u] = old_u
                    if other is not None:
                        K[other] = v
        return best_K, best / max(1, n)


def true_key(S, A):
    m = dict(A["true"])
    for u in S.units:
        if m.get(u) not in S.vid:
            m[u] = S.values[0]
    K = S.key_from_map(m)
    if S.injective:
        assert len(set(K)) == len(K)
    return K


def near_miss(S, K, k, rng):
    K = list(K)
    for _ in range(k):
        a, b = rng.sample(range(len(K)), 2)
        if S.injective or rng.random() < 0.5:
            K[a], K[b] = K[b], K[a]
        else:
            K[a] = rng.randrange(len(S.values))
    return K


def seed_of(*parts):
    return SEED + int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest(), 16) % 10**8


# ------------------------------------------------------------------ jobs
def job(spec):
    kind, mech, N, r, rep, scen, M, r_list = spec
    rng = random.Random(seed_of(*spec[:7], tuple(r_list) if r_list else None))
    lang = rng.choice(sorted(LANG_BOOKS))
    A = make_anchors(rng, lang, mech, N, r, scen, M, r_list)
    S = Scorer(A, mech, lang)
    half = list(range(N)); rng.shuffle(half)
    fit_idx, ho_idx = sorted(half[:max(1, N - N // 2)]), sorted(half[max(1, N - N // 2):])
    out = {"kind": kind, "mech": mech, "N": N, "r": r, "rep": rep, "scen": scen, "M": M, "lang": lang,
           "n_correct": sum(A["correct"]), "n_units": len(S.units)}
    _, out["S_fit"] = S.optimise(rng)
    if ho_idx:
        Sf, Sh = Scorer(A, mech, lang, fit_idx), Scorer(A, mech, lang, ho_idx)
        Kf, _ = Sf.optimise(rng)
        # held-out units unseen in fit get random values (the fitted key says nothing about them)
        m = {u: Sf.values[Kf[i]] for i, u in enumerate(Sf.units)}
        Kh = [Sh.vid.get(m.get(u), rng.randrange(len(Sh.values))) if u in m else rng.randrange(len(Sh.values))
              for u in Sh.units]
        if Sh.injective and len(set(Kh)) < len(Kh):  # repair collisions with unused letters
            used, free = set(), [v for v in range(len(Sh.values)) if v not in set(Kh)]
            for i, v in enumerate(Kh):
                if v in used:
                    Kh[i] = free.pop()
                used.add(Kh[i])
        out["S_heldout"] = Sh.score(Kh)
    if kind == "trial":
        Kt = true_key(S, A)
        out["S_true"] = S.score(Kt)
        out["S_random"] = [S.score(S.random_key(rng)) for _ in range(200)]
        out["S_near"] = {k: float(np.mean([S.score(near_miss(S, Kt, k, rng)) for _ in range(20)]))
                         for k in (1, 2, 4, 8)}
    return out


def pv(obs, null):
    null = np.asarray(null)
    return float((1 + (null >= obs - 1e-9).sum()) / (1 + len(null)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--nulls", type=int, default=200); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    anchors = [json.loads(l) for l in open(ROOT / "data/derived/anchors_v1/anchors.jsonl")]
    word_level = [r for r in anchors if r["word_level"]]
    nB = sum(r["tier"] == "B" for r in word_level); nC = sum(r["tier"] == "C" for r in word_level)
    nA_pages = sum(r["tier"] == "A" and r["anchor_type"] == "zodiac_month" and r["usable"] for r in anchors)
    Ns, Rs, mechs = (NS, RS, MECHS) if not a.quick else ([3, 10], [1.0, 0.3], MECHS)
    specs = []
    for mech in mechs:
        for N in Ns + [nB + nC]:
            specs += [("null", mech, N, 0.0, i, "lexicon", 1, None) for i in range(a.nulls)]
        for N in Ns:
            for r in Rs:
                specs += [("trial", mech, N, r, i, "lexicon", 1, None) for i in range(a.trials)]
        # zodiac/month scenario: 12 page-level anchors, ambiguity M candidates per page
        for M in (1, 15):
            specs += [("null", mech, 12, 0.0, i, "months", M, None) for i in range(a.nulls // 2)]
            for r in (1.0, 0.5, 0.25):
                specs += [("trial", mech, 12, r, i, "months", M, None) for i in range(a.trials)]
        # real anchor set: B rows at r_B, C rows at r_C (assumption grid)
        for rB, rC in [(0.4, 0.15), (0.2, 0.05), (0.05, 0.01)]:
            rl = [rB] * nB + [rC] * nC
            specs += [("trial", mech, nB + nC, round((rB * nB + rC * nC) / (nB + nC), 4), i, "lexicon", 1, rl)
                      for i in range(a.trials)]
        for rB in (0.4,):  # tier B alone (r=0.8 at N=nB is already in the main grid when nB in NS)
            specs += [("trial", mech, nB, rB, i, "lexicon", 1, None) for i in range(a.trials)]
        specs += [("null", mech, nB, 0.0, i, "lexicon", 1, None) for i in range(a.nulls)] if nB not in Ns else []
    print(len(specs), "jobs", flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=min(3, a.workers)) as ex:
        for i, r in enumerate(ex.map(job, specs, chunksize=8)):
            rows.append(r)
            if i % 500 == 0:
                print(i, round(time.time() - t0), flush=True)
    (ROOT / "experiments/results/e010_rows.jsonl").write_text(
        "\n".join(json.dumps({k: v for k, v in r.items() if k != "S_random"}) for r in rows))

    def nulls(mech, N, scen="lexicon", M=1):
        sel = [r for r in rows if r["kind"] == "null" and (r["mech"], r["N"], r["scen"], r["M"]) == (mech, N, scen, M)]
        return np.array([r["S_fit"] for r in sel]), np.array([r["S_heldout"] for r in sel if "S_heldout" in r])

    def cell(mech, N, r, scen="lexicon", M=1, real=None):
        tr = [x for x in rows if x["kind"] == "trial" and (x["mech"], x["N"], x["scen"], x["M"]) == (mech, N, scen, M)
              and abs(x["r"] - r) < 1e-9]
        nf, nh = nulls(mech, N, scen, M)
        if not tr or not len(nf):
            return None
        p1 = [pv(x["S_true"], nf) for x in tr]; p2 = [pv(x["S_fit"], nf) for x in tr]
        p3 = [pv(x["S_heldout"], nh) for x in tr if "S_heldout" in x and len(nh)]
        prand = [pv(x["S_true"], x["S_random"]) for x in tr]
        return {"n_trials": len(tr), "n_null": len(nf),
                "S_true_mean": float(np.mean([x["S_true"] for x in tr])),
                "S_fit_real_mean": float(np.mean([x["S_fit"] for x in tr])),
                "S_fit_null_mean": float(nf.mean()), "S_fit_null_q99": float(np.quantile(nf, 0.99)),
                "S_random_mean": float(np.mean([np.mean(x["S_random"]) for x in tr])),
                "S_near_mean": {k: float(np.mean([x["S_near"][k] for x in tr])) for k in tr[0]["S_near"]},
                "inflation_fit_minus_true": float(np.mean([x["S_fit"] - x["S_true"] for x in tr])),
                "power_T1_true_vs_optimised_wrong": float(np.mean([p < ALPHA for p in p1])),
                "power_T2_fit_real_vs_fit_wrong": float(np.mean([p < ALPHA for p in p2])),
                "power_T3_heldout": float(np.mean([p < ALPHA for p in p3])) if p3 else None,
                "power_vs_random_keys": float(np.mean([p < ALPHA for p in prand]))}

    res = {"experiment": "E010", "seed": SEED, "alpha": ALPHA, "command": " ".join(["experiments/e010_anchor_power.py"] + sys.argv[1:]),
           "languages": LANG_BOOKS, "mechanisms": mechs, "N": Ns, "r": Rs, "trials": a.trials, "nulls": a.nulls,
           "grid": {}, "frontier": {}, "months_scenario": {}, "real_set": {}}
    for mech in mechs:
        res["grid"][mech] = {f"N={N}|r={r}": cell(mech, N, r) for N in Ns for r in Rs}
        fr = {}
        for test in ("power_T1_true_vs_optimised_wrong", "power_T2_fit_real_vs_fit_wrong", "power_T3_heldout"):
            fr[test] = {}
            for r in Rs:
                ok = [N for N in Ns if (res["grid"][mech][f"N={N}|r={r}"] or {}).get(test) is not None
                      and res["grid"][mech][f"N={N}|r={r}"][test] >= 0.8]
                fr[test][str(r)] = min(ok) if ok else f">{max(Ns)}"
        res["frontier"][mech] = fr
        res["months_scenario"][mech] = {f"M={M}|r={r}": cell(mech, 12, r, "months", M) for M in (1, 15)
                                        for r in (1.0, 0.5, 0.25)}
        rs = {}
        for rB, rC in [(0.4, 0.15), (0.2, 0.05), (0.05, 0.01)]:
            rmix = round((rB * nB + rC * nC) / (nB + nC), 4)
            rs[f"B+C rB={rB} rC={rC}"] = cell(mech, nB + nC, rmix)
        for rB in (0.4, 0.8):
            rs[f"B only rB={rB}"] = cell(mech, nB, rB)
        res["real_set"][mech] = rs
    res["real_counts"] = {"word_level_usable_B": nB, "word_level_usable_C": nC, "zodiac_pages_tierA": nA_pages,
                          "tier_D_usable": sum(r["tier"] == "D" and r["usable"] for r in anchors),
                          "locked_rows_excluded": sum(r["locked"] for r in anchors)}
    res["wall_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    led = []
    for mech in mechs:
        for r, n in res["frontier"][mech]["power_T1_true_vs_optimised_wrong"].items():
            led.append({"experiment": "E010", "model": f"anchor_power|{mech}", "split": "synthetic(tune books)",
                        "metric": f"min_N_power0.8_T1_r={r}", "value": n, "command": res["command"]})
        for k, v in res["real_set"][mech].items():
            if v:
                led.append({"experiment": "E010", "model": f"anchor_power|{mech}", "split": "synthetic(real-set sizes)",
                            "metric": f"power_T1|{k}", "value": v["power_T1_true_vs_optimised_wrong"],
                            "command": res["command"]})
    append(led)
    print(json.dumps(res["frontier"], indent=1), res["wall_s"])


if __name__ == "__main__":
    main()
