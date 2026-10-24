"""E057: do individual WORDS differ in how often they stand next to themselves, beyond what their FORM (family)
predicts? A generator that works with word families cannot do this; a real vocabulary can. See reports/E057_PREREG.md.

Per text (28,841 tokens, lines as given; references cut into Voynich-length pseudo-lines):
  per word w and line l: E_wl = n_wl (n_wl - 1) / L_l  (expected identical neighbours if the line's words were shuffled)
  O_w = observed identical neighbour pairs of w;  E_w = sum_l E_wl
  eligible words: E_w >= 1;  family(w) = (first unit, last two characters)   [first unit = E024 S3 segment for EVA,
  first letter otherwise]; families with >= 2 eligible words are kept
  lambda_w = A_fam * E_w with A_fam = sum O / sum E over the family's eligible words
  PHI = mean over kept words of (O_w - lambda_w)^2 / lambda_w; parametric null: O_w ~ Poisson(lambda_w), 2,000 draws
  (refitting A_fam each draw); z = (PHI - mean null) / sd null.
Also reported: share of kept words that never self-repeat although E_w >= 3; share with O_w/E_w >= 3.
Run: caffeinate -ims .venv/bin/python experiments/e057_word_repeat_individuality.py
"""
from __future__ import annotations

import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e024_atoms as A24  # noqa: E402
from e030_reduplication import tokens as e030_tokens  # noqa: E402
from e042_language_shortlist import words as bwords  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED, N, NSIM = 57057, 28841, 2000
OUT = ROOT / "experiments/results/e057.json"
LANGS = {"Indonesian": "indayt", "Malay": "zlmKSZI", "Tamil": "tam2017", "Assamese": "asmfb", "Malayalam": "mal"}


def first_unit(w, eva):
    return A24.segment(w, A24.SEGS["S3"])[0] if eva else w[0]


def stats(lines, eva, rng):
    O, Ew = Counter(), defaultdict(float)
    for l in lines:
        if len(l) < 2:
            continue
        c = Counter(l)
        for w, n in c.items():
            if n > 1:
                Ew[w] += n * (n - 1) / len(l)
        for a, b in zip(l, l[1:]):
            if a == b:
                O[a] += 1
    elig = [w for w, e in Ew.items() if e >= 1.0]
    fam = defaultdict(list)
    for w in elig:
        fam[(first_unit(w, eva), w[-2:])].append(w)
    kept = [w for f, ws in fam.items() if len(ws) >= 2 for w in ws]
    fams = [ws for ws in fam.values() if len(ws) >= 2]

    def phi(Ov):
        tot = []
        for ws in fams:
            o = sum(Ov[w] for w in ws); e = sum(Ew[w] for w in ws); A = o / e
            for w in ws:
                lam = A * Ew[w]
                if lam > 0:
                    tot.append((Ov[w] - lam) ** 2 / lam)
        return float(np.mean(tot)) if tot else float("nan")

    obs = phi(O)
    nrng = np.random.default_rng(rng.randrange(1 << 30))
    lam0 = {}
    for ws in fams:
        o = sum(O[w] for w in ws); e = sum(Ew[w] for w in ws)
        for w in ws:
            lam0[w] = o / e * Ew[w]
    sims = []
    for _ in range(NSIM):
        Ov = {w: int(nrng.poisson(lam0[w])) for w in kept}
        sims.append(phi(Ov))
    sims = np.array([s for s in sims if s == s])
    z = (obs - sims.mean()) / sims.std() if len(sims) and sims.std() > 0 else float("nan")
    av = [w for w in kept if Ew[w] >= 3 and O[w] == 0]
    rp = [w for w in kept if O[w] / Ew[w] >= 3]
    return {"kept_words": len(kept), "families": len(fams), "PHI": obs, "null_mean": float(sims.mean()),
            "null_sd": float(sims.std()), "z": float(z), "p": float((1 + (sims >= obs).sum()) / (1 + len(sims))),
            "share_never_repeat_E3": len(av) / max(1, sum(Ew[w] >= 3 for w in kept)), "share_ratio_ge3": len(rp) / max(1, len(kept)),
            "examples_never": sorted(av, key=lambda w: -Ew[w])[:8], "examples_high": sorted(rp, key=lambda w: -O[w] / Ew[w])[:8]}


def pseudo(words, lens):
    out, i, j = [], 0, 0
    while i < len(words):
        L = lens[j % len(lens)]; out.append(words[i:i + L]); i += L; j += 1
    return out


def main():
    rng = random.Random(SEED)
    lines, cur, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]
    R = {"Voynich DEV": stats(vl, True, rng)}
    gl = gen_lines(); gens = []
    for k in range(10):
        chunk, n = [], 0
        start = rng.randrange(len(gl) - 4000)
        for l in gl[start:]:
            chunk.append(l); n += len(l)
            if n >= N:
                break
        gens.append(stats(chunk, True, rng))
    R["generator (10 samples)"] = {"PHI": [g["PHI"] for g in gens], "z": [g["z"] for g in gens],
                                   "never": [g["share_never_repeat_E3"] for g in gens]}
    for name, bid in LANGS.items():
        w = (e030_tokens(bid) if bid in ("indayt", "zlmKSZI") else bwords(bid))[2000:2000 + N]
        R[name] = stats(pseudo(w, lens), False, rng)
    v = R["Voynich DEV"]; gphi = R["generator (10 samples)"]["PHI"]
    langs_above = sum(R[n]["PHI"] > max(gphi) for n in LANGS)
    valid = langs_above >= 3
    if not valid:
        verdict, bf = "VOID (reference languages do not exceed the generator)", {}
    elif v["PHI"] > max(gphi) and v["p"] < 0.01:
        verdict, bf = "WORD-SPECIFIC (vocabulary-like)", {"M": 1 / 3}
    elif v["PHI"] <= float(np.median(gphi)):
        verdict, bf = "FAMILY-LEVEL (generator-like)", {"M": 3.0}
    else:
        verdict, bf = "INCONCLUSIVE", {}
    print(f"Voynich: PHI {v['PHI']:.2f} (null {v['null_mean']:.2f}±{v['null_sd']:.2f}, z {v['z']:.1f}, p {v['p']:.4f}); kept {v['kept_words']} words in {v['families']} families; never-repeat share {v['share_never_repeat_E3']:.2f}, ratio>=3 share {v['share_ratio_ge3']:.2f}")
    print("   never:", v["examples_never"], "| high:", v["examples_high"])
    print(f"generator PHI {[round(x, 2) for x in gphi]} | z {[round(x, 1) for x in R['generator (10 samples)']['z']]} | never {[round(x, 2) for x in R['generator (10 samples)']['never']]}")
    for n in LANGS:
        r = R[n]; print(f"{n:11s} PHI {r['PHI']:.2f} z {r['z']:.1f} p {r['p']:.4f} kept {r['kept_words']} never {r['share_never_repeat_E3']:.2f} high {r['share_ratio_ge3']:.2f}")
    print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E057", "results": R, "languages_above_generator": langs_above,
                               "valid": valid, "verdict": verdict, "bayes_factors": bf, "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
