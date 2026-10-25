"""E068: human gibberish against Voynich's small-scale habits (beyond vocabulary). See reports/E068_PREREG.md.

Same windows as E067 (W = 150 tokens): GIB = first 150 tokens of 36 Gaskell & Bowern gibberish texts; VOY = 200 random
DEV windows; LANG = 60 Bibles x 20 windows (group value = mean of language means); GEN = 20 generator stretches x 10.
Voynich is measured in EVA letters (S0), the project's convention for cross-script comparison (E031-E036); the E027
caveat (glyph groups) is declared in the prereg.
Features (6): WL mean word length; WLSD sd of word length; H2 conditional letter entropy within words (start symbol);
END5 share of tokens whose final letter is among the window's 5 commonest final letters; R pooled back-to-back repeats /
chance (sum O / sum E over windows, E = sum_w n_w(n_w-1)/W per window); NR pooled near-copies (edit distance 1) / mean
of 5 within-window shuffles.
Per feature: v (Voynich), l (languages), g (gibberish), m (generator); sd_v = sd over Voynich windows (for pooled R, NR:
sd of the pooled value over 200 bootstrap resamples of 36 Voynich windows). DIAGNOSTIC iff |v - l| >= sd_v. On a
diagnostic feature gibberish is VOYNICH-LIKE iff |g - v| < |g - l|.
Verdict over D diagnostic features (D >= 3 else VOID): all Voynich-like -> M FULL CASE, M x3; <= 1 Voynich-like -> M
RULED DOWN, M x1/3; otherwise TWO-WAY STREET, none. Seed rule: if any diagnostic feature has |g-v| within 10% of |g-l|,
or |v-l| within 10% of sd_v, the reference windows are re-drawn with 10 seeds (>= 8/10 agree).
Run: caffeinate -ims .venv/bin/python experiments/e068_gibberish_battery.py [--dry]
"""
from __future__ import annotations

import argparse, glob, json, math, random, sys, time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e030_reduplication import ed1  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e064_early_audit import tok  # noqa: E402
from e067_gibberish_vocabulary import GB, BIB, SKIP, clean_tokens  # noqa: E402

SEED, W = 68068, 150
OUT = ROOT / "experiments/results/e068.json"
N_VOY, N_LANG, N_GEN, N_BOOT = 200, 20, 10, 200
PER_WINDOW = ["WL", "WLSD", "H2", "END5"]
POOLED = ["R", "NR"]
FEATS = PER_WINDOW + POOLED
LEDGER = {"M": 0.1932, "L": 0.7788, "C": 0.0245, "O": 0.0036}


def log(*a):
    print(*a, flush=True)


def h2(words):
    big, uni = Counter(), Counter()
    for w in words:
        s = "^" + w
        for a, b in zip(s, s[1:]):
            big[(a, b)] += 1; uni[a] += 1
    tot = sum(big.values())
    return -sum(c / tot * math.log2(c / uni[a]) for (a, _), c in big.items())


def window_stats(win, rng):
    """Per-window features plus the raw counts needed for the pooled ones."""
    L = [len(w) for w in win]
    fin = Counter(w[-1] for w in win)
    o = sum(a == b for a, b in zip(win, win[1:]))
    e = sum(n * (n - 1) for n in Counter(win).values()) / len(win)
    near = sum(ed1(a, b) for a, b in zip(win, win[1:]))
    sh = []
    for _ in range(5):
        x = list(win); rng.shuffle(x); sh.append(sum(ed1(a, b) for a, b in zip(x, x[1:])))
    return {"WL": float(np.mean(L)), "WLSD": float(np.std(L)), "H2": h2(win),
            "END5": sum(c for _, c in fin.most_common(5)) / len(win),
            "o": o, "e": e, "near": near, "near_sh": float(np.mean(sh))}


def pooled(ws):
    return {"R": sum(x["o"] for x in ws) / max(1e-9, sum(x["e"] for x in ws)),
            "NR": sum(x["near"] for x in ws) / max(1e-9, sum(x["near_sh"] for x in ws))}


def group_value(ws):
    return {**{k: float(np.mean([x[k] for x in ws])) for k in PER_WINDOW}, **pooled(ws)}


def windows(tokens, n, rng):
    if len(tokens) < W:
        return []
    return [window_stats(tokens[s:s + W], rng) for s in (rng.randrange(0, len(tokens) - W + 1) for _ in range(n))]


def references(seed):
    rng = random.Random(seed)
    lines, _, _, locked = E.voynich_lines()
    vt = [w for l in lines for w in l if w]
    VOY = windows(vt, N_VOY, rng)
    LANG = {}
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        ws = windows(tok(bid), N_LANG, rng)
        if ws:
            LANG[bid] = group_value(ws)
    gl = gen_lines(); GEN = []
    for _ in range(20):
        st = rng.randrange(len(gl) - 4000)
        GEN += windows([w for l in gl[st:st + 4000] for w in l], N_GEN, rng)
    return VOY, LANG, GEN, locked


def judge(VOY, LANG, GIB, GEN, seed):
    rng = random.Random(seed)
    v = group_value(VOY); g = group_value(GIB); m = group_value(GEN)
    l = {k: float(np.mean([x[k] for x in LANG.values()])) for k in FEATS}
    sd = {k: float(np.std([x[k] for x in VOY], ddof=1)) for k in PER_WINDOW}
    for k in POOLED:
        boots = [pooled(rng.sample(VOY, len(GIB)))[k] for _ in range(N_BOOT)]
        sd[k] = float(np.std(boots, ddof=1))
    rows = {}
    for k in FEATS:
        diag = abs(v[k] - l[k]) >= sd[k]
        like = abs(g[k] - v[k]) < abs(g[k] - l[k])
        rows[k] = {"voynich": v[k], "languages": l[k], "gibberish": g[k], "generator": m[k], "sd_v": sd[k],
                   "diagnostic": diag, "voynich_like": like if diag else None,
                   "border": (abs(abs(g[k] - v[k]) - abs(g[k] - l[k])) < 0.1 * abs(g[k] - l[k])) or (abs(abs(v[k] - l[k]) - sd[k]) < 0.1 * sd[k])}
    D = [k for k in FEATS if rows[k]["diagnostic"]]
    kk = sum(rows[k]["voynich_like"] for k in D)
    if len(D) < 3:
        verdict, f = "VOID (fewer than 3 diagnostic features)", 1.0
    elif kk == len(D):
        verdict, f = "M FULL CASE (gibberish Voynich-like on every diagnostic feature)", 3.0
    elif kk <= 1:
        verdict, f = "M RULED DOWN (gibberish Voynich-like on at most one diagnostic feature)", 1 / 3
    else:
        verdict, f = "TWO-WAY STREET", 1.0
    return {"rows": rows, "diagnostic": D, "voynich_like_count": kk, "verdict": verdict, "factor_M": f,
            "borderline": any(rows[k]["border"] for k in D)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    gib = {Path(f).name: clean_tokens(f) for f in sorted(glob.glob(str(GB / "gib/*.txt")))}
    kept = {n: t for n, t in gib.items() if len(t) >= W}
    log(f"gibberish texts with >= {W} tokens: {len(kept)}")
    if a.dry:
        log("dry run complete"); return
    GIB = [window_stats(t[:W], rng) for t in kept.values()]
    VOY, LANG, GEN, locked = references(SEED)
    J = judge(VOY, LANG, GIB, GEN, SEED)
    for k in FEATS:
        r = J["rows"][k]
        log(f"  {k:5s} Voynich {r['voynich']:7.3f} (sd {r['sd_v']:.3f}) | languages {r['languages']:7.3f} | gibberish {r['gibberish']:7.3f} | generator {r['generator']:7.3f} "
            f"| {'DIAGNOSTIC' if r['diagnostic'] else 'not diagnostic'} {'' if r['voynich_like'] is None else ('VOYNICH-LIKE' if r['voynich_like'] else 'language-like')}{' border' if r['border'] else ''}")
    verdict, f = J["verdict"], J["factor_M"]
    seed_rule = None
    if J["borderline"] and len(J["diagnostic"]) >= 3:
        votes = []
        for s in range(1, 11):
            V2, L2, G2, _ = references(SEED + s); votes.append(judge(V2, L2, GIB, G2, SEED + s)["verdict"])
        top = max(set(votes), key=votes.count); seed_rule = {"votes": votes, "decided": votes.count(top) >= 8}
        if votes.count(top) >= 8:
            verdict = top; f = 3.0 if top.startswith("M FULL") else 1 / 3 if top.startswith("M RULED") else 1.0
        else:
            verdict, f = "TWO-WAY STREET (seed rule undecided)", 1.0
        log(f"seed rule: {votes}")
    new = {"M": LEDGER["M"] * f, "L": LEDGER["L"], "C": LEDGER["C"], "O": LEDGER["O"]}
    s = sum(new.values()); new = {k: round(x / s, 4) for k, x in new.items()}
    log(f"diagnostic {J['diagnostic']} | Voynich-like {J['voynich_like_count']}/{len(J['diagnostic'])}")
    log(f"VERDICT {verdict} | M x{f:.3g} | ledger {new} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E068", "seed": SEED, "W": W, "judge": J, "language_values": LANG,
                               "gib_values": {n: {k: x[k] for k in PER_WINDOW} for n, x in zip(kept, GIB)}, "seed_rule": seed_rule,
                               "verdict": verdict, "factor_M": f, "ledger": {"before": LEDGER, "after": new},
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
