"""E067: does human-written gibberish grow vocabulary the way Voynich does? See reports/E067_PREREG.md.

Window length W = 150 tokens (34+ of the 38 Gaskell & Bowern gibberish texts are that long). Per window: T (distinct
words), H (share of tokens whose word occurs once in the window), BETA (vocabulary growth exponent log2(T_150 / T_75)).
Groups: GIB = first 150 tokens of each gibberish text of >= 150 tokens; VOY = 200 random windows of DEV reading order;
LANG = 60 Bibles x 20 random windows (E064 TOK); GBM = Gaskell & Bowern meaningful texts x 10 random windows (cleaned the
same way); GEN = 20 copy-generator stretches x 10 windows.
d(X) = (mean_X - mean_VOY) / sd_VOY (effect size in Voynich-window sd units), on T (primary) and H (secondary).
Gate: |d(LANG)| on T >= 1, else VOID. LIKE: |d_T(GIB)| <= 0.5 and |d_H(GIB)| <= 1 -> M x3. LANGUAGE-SIDE: same sign as
d_T(LANG), |d_T(GIB)| >= |d_T(LANG)|/2 and > 0.5 -> M x1/3. BEYOND: opposite side, |d_T(GIB)| >= 1.5 -> none. Else
INCONCLUSIVE. Seed rule: a d within 0.1 of a boundary -> reference windows re-drawn with 10 seeds, >= 8/10 agree.
Run: caffeinate -ims .venv/bin/python experiments/e067_gibberish_vocabulary.py [--dry]
"""
from __future__ import annotations

import argparse, glob, json, random, sys, time, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e064_early_audit import tok  # noqa: E402

SEED, W = 67067, 150
OUT = ROOT / "experiments/results/e067.json"
GB = ROOT / "data/external/gaskell_bowern_unzipped"
BIB = ROOT / "data/external/bibles"
SKIP = {"cmn-cu89s", "jpn1965", "vie1934", "lit", "engWycliffe"}
N_VOY, N_LANG, N_GBM, N_GEN = 200, 20, 10, 10
LEDGER = {"M": 0.0739, "L": 0.8939, "C": 0.0281, "O": 0.0041}


def log(*a):
    print(*a, flush=True)


def clean_tokens(path):
    t = unicodedata.normalize("NFC", Path(path).read_text(encoding="utf-8", errors="ignore").lower())
    out = []
    for l in t.splitlines():
        if set(l.strip()) <= set("_- "):
            continue
        out += "".join(c if (unicodedata.category(c)[0] in "LM" or c == "'") else " " for c in l).split()
    return out


def measure(win):
    assert len(win) == W
    c = Counter(win); c75 = Counter(win[:W // 2])
    T = len(c); H = sum(1 for w in win if c[w] == 1) / W
    return {"T": float(T), "H": H, "BETA": float(np.log2(T / len(c75)))}


def windows(tokens, n, rng):
    if len(tokens) < W:
        return []
    return [measure(tokens[s:s + W]) for s in (rng.randrange(0, len(tokens) - W + 1) for _ in range(n))]


def group_mean(ms, k):
    return float(np.mean([m[k] for m in ms]))


def references(seed):
    rng = random.Random(seed)
    lines, _, _, locked = E.voynich_lines()
    vt = [w for l in lines for w in l if w]
    VOY = windows(vt, N_VOY, rng)
    LANG = {}
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        LANG[bid] = windows(tok(bid), N_LANG, rng)
    GBM = {Path(f).name: windows(clean_tokens(f), N_GBM, rng) for f in sorted(glob.glob(str(GB / "mean/texts/*.txt")))}
    gl = gen_lines(); GEN = []
    for _ in range(20):
        st = rng.randrange(len(gl) - 4000)
        toks = [w for l in gl[st:st + 4000] for w in l]
        GEN += windows(toks, N_GEN, rng)
    return VOY, LANG, GBM, GEN, locked


def judge(VOY, LANG, GIB):
    mv = {k: group_mean(VOY, k) for k in ("T", "H", "BETA")}
    sv = {k: float(np.std([m[k] for m in VOY], ddof=1)) for k in ("T", "H", "BETA")}
    lang_means = {b: {k: group_mean(ms, k) for k in ("T", "H", "BETA")} for b, ms in LANG.items() if ms}
    d = lambda X, k: (float(np.mean([x[k] for x in X])) - mv[k]) / sv[k]
    dL = {k: (float(np.mean([m[k] for m in lang_means.values()])) - mv[k]) / sv[k] for k in ("T", "H", "BETA")}
    dG = {k: d(GIB, k) for k in ("T", "H", "BETA")}
    if abs(dL["T"]) < 1:
        v, f = "VOID (languages not separated from Voynich at this length)", 1.0
    elif abs(dG["T"]) <= 0.5 and abs(dG["H"]) <= 1:
        v, f = "GIBBERISH LIKE VOYNICH", 3.0
    elif np.sign(dG["T"]) == np.sign(dL["T"]) and abs(dG["T"]) >= abs(dL["T"]) / 2 and abs(dG["T"]) > 0.5:
        v, f = "GIBBERISH ON THE LANGUAGE SIDE (unlike Voynich)", 1 / 3
    elif np.sign(dG["T"]) != np.sign(dL["T"]) and abs(dG["T"]) >= 1.5:
        v, f = "GIBBERISH BEYOND VOYNICH (richer still)", 1.0
    else:
        v, f = "INCONCLUSIVE", 1.0
    border = any(abs(abs(x) - b) < 0.1 for x, b in ((dG["T"], 0.5), (dG["T"], 1.5), (dG["T"], abs(dL["T"]) / 2), (dL["T"], 1.0), (dG["H"], 1.0)))
    return {"voy_mean": mv, "voy_sd": sv, "d_lang": dL, "d_gib": dG, "verdict": v, "factor_M": f, "borderline": border,
            "lang_means": lang_means}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    gib_files = sorted(glob.glob(str(GB / "gib/*.txt")))
    gib = {Path(f).name: clean_tokens(f) for f in gib_files}
    kept = {n: t for n, t in gib.items() if len(t) >= W}
    log(f"gibberish texts {len(gib)}, with >= {W} tokens: {len(kept)}; dropped {[n for n in gib if n not in kept]}")
    if a.dry:
        log("dry run complete"); return
    GIB = [measure(t[:W]) for t in kept.values()]
    VOY, LANG, GBM, GEN, locked = references(SEED)
    J = judge(VOY, LANG, GIB)
    gbm_all = [m for ms in GBM.values() for m in ms]
    extra = {g: {k: (group_mean(X, k) - J["voy_mean"][k]) / J["voy_sd"][k] for k in ("T", "H", "BETA")}
             for g, X in (("GBM", gbm_all), ("GEN", GEN))}
    log(f"Voynich windows: T {J['voy_mean']['T']:.1f} ± {J['voy_sd']['T']:.1f}, H {J['voy_mean']['H']:.3f} ± {J['voy_sd']['H']:.3f}, BETA {J['voy_mean']['BETA']:.3f}")
    log(f"languages (60, mean of language means): d_T {J['d_lang']['T']:+.2f} d_H {J['d_lang']['H']:+.2f} | T {group_mean(list(J['lang_means'].values()), 'T'):.1f} H {group_mean(list(J['lang_means'].values()), 'H'):.3f}")
    log(f"gibberish ({len(GIB)} writers): d_T {J['d_gib']['T']:+.2f} d_H {J['d_gib']['H']:+.2f} d_BETA {J['d_gib']['BETA']:+.2f} | T {group_mean(GIB, 'T'):.1f} H {group_mean(GIB, 'H'):.3f}")
    log(f"G&B meaningful (71 texts): d_T {extra['GBM']['T']:+.2f} d_H {extra['GBM']['H']:+.2f} | T {group_mean(gbm_all, 'T'):.1f}")
    log(f"generator (200 windows): d_T {extra['GEN']['T']:+.2f} d_H {extra['GEN']['H']:+.2f} | T {group_mean(GEN, 'T'):.1f} H {group_mean(GEN, 'H'):.3f}")
    top = sorted(J["lang_means"].items(), key=lambda x: -x[1]["T"])[:8]
    log("richest languages at 150: " + ", ".join(f"{b} {m['T']:.0f}" for b, m in top))
    log("gibberish writers T: " + " ".join(f"{m['T']:.0f}" for m in GIB))
    verdict, f = J["verdict"], J["factor_M"]
    seed_rule = None
    if J["borderline"]:
        votes = []
        for s in range(1, 11):
            V2, L2, _, _, _ = references(SEED + s); votes.append(judge(V2, L2, GIB)["verdict"])
        top_v = max(set(votes), key=votes.count); seed_rule = {"votes": votes, "decided": votes.count(top_v) >= 8}
        if votes.count(top_v) >= 8:
            verdict = top_v; f = {"GIBBERISH LIKE VOYNICH": 3.0, "GIBBERISH ON THE LANGUAGE SIDE (unlike Voynich)": 1 / 3}.get(top_v, 1.0)
        else:
            verdict, f = "INCONCLUSIVE (seed rule undecided)", 1.0
        log(f"seed rule: {votes}")
    new = {"M": LEDGER["M"] * f, "L": LEDGER["L"], "C": LEDGER["C"], "O": LEDGER["O"]}
    s = sum(new.values()); new = {k: round(x / s, 4) for k, x in new.items()}
    log(f"VERDICT {verdict} | M x{f:.3g} | ledger {new} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E067", "seed": SEED, "W": W, "judge": J, "extra_d": extra, "gib": {n: m for n, m in zip(kept, GIB)},
                               "gib_dropped": [n for n in gib if n not in kept], "voy_windows": VOY, "gen_windows": GEN,
                               "gbm_means": {n: {k: group_mean(ms, k) for k in ("T", "H", "BETA")} for n, ms in GBM.items() if ms},
                               "seed_rule": seed_rule, "verdict": verdict, "factor_M": f, "ledger": {"before": LEDGER, "after": new},
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
