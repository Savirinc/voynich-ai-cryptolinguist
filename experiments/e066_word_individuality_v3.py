"""E066 (= E058 v3, reopened by the tokenizer defect): do individual WORDS differ in back-to-back self-repetition beyond
their FAMILY? See reports/E066_PREREG.md.

Statistic unchanged from E058: words with count >= 10; E_w = sum over lines n_wl (n_wl - 1) / L_l (expected back-to-back
pairs if the line's words were in random order); O_w observed; family = (first unit [E024 S3 for EVA, first character
otherwise], last two characters), families with >= 2 words; H0: O_w ~ Poisson(A_fam E_w); G = family-model deviance;
parametric bootstrap (2,000 draws); z, one-sided p.
Texts: Voynich DEV (own lines); 20 copy-generator stretches (10 decide, 10 reserve for the seed rule); every Bible on
disk except cmn-cu89s, jpn1965, vie1934 (syllable-spaced), lit (too small), engWycliffe (partial), tokenized with E064's
TOK, words [2000:2000+N] in Voynich-length pseudo-lines.
Power gate: a language is MEASURABLE iff >= 20 kept words and total E >= 30 (E depends on counts and line lengths only,
not on the outcome). VALID iff >= 3 measurable languages separate from the generator (z > max generator z, p < 0.01).
Run: caffeinate -ims .venv/bin/python experiments/e066_word_individuality_v3.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e058_word_repeat_individuality_v2 import pseudo, stats  # noqa: E402
from e064_early_audit import tok  # noqa: E402

SEED, N = 66066, 28841
OUT = ROOT / "experiments/results/e066.json"
BIB = ROOT / "data/external/bibles"
SKIP = {"cmn-cu89s", "jpn1965", "vie1934", "lit", "engWycliffe"}
MIN_WORDS, MIN_E = 20, 30.0
LEDGER = {"M": 0.0259, "L": 0.9401, "C": 0.0296, "O": 0.0043}


def log(*a):
    print(*a, flush=True)


def languages():
    return sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP)


def task(args):
    kind, name, lines, eva, seed = args
    r = stats(lines, eva, random.Random(seed))
    r["measurable"] = r["kept_words"] >= MIN_WORDS and r["total_E"] >= MIN_E
    return kind, name, r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]
    jobs = [("voynich", "Voynich DEV", vl, True, rng.randrange(1 << 30))]
    gl = gen_lines()
    for k in range(20):
        st = rng.randrange(len(gl) - 4000); chunk, n = [], 0
        for l in gl[st:]:
            chunk.append(l); n += len(l)
            if n >= N:
                break
        jobs.append(("generator", f"gen{k}", chunk, True, rng.randrange(1 << 30)))
    short = []
    for bid in languages():
        w = tok(bid)
        if len(w) < 2000 + N:
            short.append(bid); continue
        jobs.append(("language", bid, pseudo(w[2000:2000 + N], lens), False, rng.randrange(1 << 30)))
    log(f"jobs: 1 Voynich, 20 generator, {sum(j[0] == 'language' for j in jobs)} languages (too short: {short})")
    with Pool(a.workers) as pool:
        out = pool.map(task, jobs)
    R = {"voynich": None, "generator": {}, "languages": {}}
    for kind, name, r in out:
        if kind == "voynich":
            R["voynich"] = r
        else:
            R[kind][name] = r
    v = R["voynich"]
    gz10 = [R["generator"][f"gen{k}"]["z"] for k in range(10)]
    gz20 = [R["generator"][f"gen{k}"]["z"] for k in range(20)]
    log(f"Voynich: words {v['kept_words']} fam {v['families']} O {v['total_O']} E {v['total_E']:.0f} z {v['z']:+.1f} p {v['p']:.4f}")
    log("   watch (O, E):", v["watch"])
    log(f"generator z (10) {[round(x, 1) for x in gz10]} | reserve {[round(x, 1) for x in gz20[10:]]}")
    meas = {b: r for b, r in R["languages"].items() if r["measurable"]}
    sep = [b for b, r in meas.items() if r["z"] > max(gz10) and r["p"] < 0.01]
    for b, r in sorted(R["languages"].items(), key=lambda x: -x[1]["z"] if x[1]["measurable"] and not np.isnan(x[1]["z"]) else 99):
        log(f"  {b:10s} words {r['kept_words']:4d} fam {r['families']:3d} O {r['total_O']:4d} E {r['total_E']:6.1f} z {r['z']:+5.1f} p {r['p']:.4f}"
            f" {'MEASURABLE' if r['measurable'] else 'not measurable'}{' SEPARATES' if b in sep else ''}")
    log(f"measurable {len(meas)}/{len(R['languages'])}; separating from generator: {len(sep)} {sep}")
    valid = len(sep) >= 3

    def judge(gz):
        if v["z"] > max(gz) and v["p"] < 0.01:
            return "WORD-SPECIFIC (vocabulary-like)", 1 / 3
        if v["z"] <= float(np.median(gz)):
            return "FAMILY-LEVEL (generator-like)", 3.0
        return "INCONCLUSIVE", 1.0

    verdict, fM = judge(gz10)
    border = abs(v["z"] - max(gz10)) < 0.5 or abs(v["z"] - float(np.median(gz10))) < 0.5
    seed_rule = None
    if border:
        r2 = random.Random(SEED + 1)
        votes = [judge(r2.sample(gz20, 10))[0] for _ in range(10)]
        top = max(set(votes), key=votes.count)
        seed_rule = {"votes": votes, "decided": votes.count(top) >= 8}
        verdict, fM = (top, {"WORD-SPECIFIC (vocabulary-like)": 1 / 3, "FAMILY-LEVEL (generator-like)": 3.0}.get(top, 1.0)) if votes.count(top) >= 8 else ("INCONCLUSIVE (seed rule undecided)", 1.0)
    if not valid:
        verdict, fM = f"VOID ({len(sep)} of {len(meas)} measurable languages separate; need 3) | unscored Voynich: {verdict}", 1.0
    new = {"M": LEDGER["M"] * fM, "L": LEDGER["L"], "C": LEDGER["C"], "O": LEDGER["O"]}
    s = sum(new.values()); new = {k: round(x / s, 4) for k, x in new.items()}
    log(f"VERDICT {verdict} | M x{fM:.3g} | ledger {new} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E066", "seed": SEED, "results": R, "measurable": sorted(meas), "separating": sep,
                               "valid": valid, "borderline": border, "seed_rule": seed_rule, "verdict": verdict, "factor_M": fM,
                               "ledger": {"before": LEDGER, "after": new}, "too_short": short, "locked_test_excluded": locked,
                               "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
