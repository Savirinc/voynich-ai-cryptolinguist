"""E058 (= E057 v2): do individual WORDS differ in back-to-back self-repetition beyond their FAMILY?
See reports/E058_PREREG.md. Same texts as E057 (Voynich DEV own lines; 10 copy-generator stretches; Indonesian,
Malay, Tamil, Assamese, Malayalam in Voynich-length pseudo-lines; 28,841 tokens each).
Words: every word with count >= 10. E_w = sum over lines n_wl (n_wl - 1) / L_l; O_w = observed back-to-back pairs.
Family = (first unit [E024 S3 for EVA; first letter otherwise], last two characters); families with >= 2 words.
H0: O_w ~ Poisson(A_fam * E_w) (one rate per family). G = 2 * sum_w [O ln(O/lam) - (O - lam)] (deviance of the family
model). Parametric bootstrap under H0 (2,000 draws, rates refitted): z = (G - mean) / sd, one-sided p.
Run: caffeinate -ims .venv/bin/python experiments/e058_word_repeat_individuality_v2.py
"""
from __future__ import annotations

import json, math, random, sys
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

SEED, N, NSIM, MINC = 58058, 28841, 2000, 10
OUT = ROOT / "experiments/results/e058.json"
LANGS = {"Indonesian": "indayt", "Malay": "zlmKSZI", "Tamil": "tam2017", "Assamese": "asmfb", "Malayalam": "mal"}
WATCH = ["dal", "shey", "saiin", "okaiin", "daiin", "chol", "qokeedy", "qokeey", "chedy", "shedy", "dy", "ol", "aiin"]


def dev(O, lam):
    s = 0.0
    for o, l in zip(O, lam):
        if l <= 0:
            continue
        s += (o * math.log(o / l) if o > 0 else 0.0) - (o - l)
    return 2 * s


def stats(lines, eva, rng):
    cnt = Counter(w for l in lines for w in l)
    O, Ew = Counter(), defaultdict(float)
    for l in lines:
        if len(l) < 2:
            continue
        for w, n in Counter(l).items():
            if n > 1:
                Ew[w] += n * (n - 1) / len(l)
        for a, b in zip(l, l[1:]):
            if a == b:
                O[a] += 1
    words = [w for w, c in cnt.items() if c >= MINC and Ew[w] > 0]
    fam = defaultdict(list)
    for w in words:
        fam[((A24.segment(w, A24.SEGS["S3"])[0] if eva else w[0]), w[-2:])].append(w)
    fams = [ws for ws in fam.values() if len(ws) >= 2]
    kept = [w for ws in fams for w in ws]

    def G_of(Ov):
        o_list, l_list = [], []
        for ws in fams:
            o = sum(Ov[w] for w in ws); e = sum(Ew[w] for w in ws); A = o / e if e else 0.0
            for w in ws:
                o_list.append(Ov[w]); l_list.append(A * Ew[w])
        return dev(o_list, l_list)

    obs = G_of(O)
    lam = {}
    for ws in fams:
        o = sum(O[w] for w in ws); e = sum(Ew[w] for w in ws)
        for w in ws:
            lam[w] = (o / e if e else 0.0) * Ew[w]
    nrng = np.random.default_rng(rng.randrange(1 << 30))
    sims = np.array([G_of({w: int(nrng.poisson(lam[w])) for w in kept}) for _ in range(NSIM)])
    z = float((obs - sims.mean()) / sims.std()) if sims.std() > 0 else float("nan")
    watch = {w: [O[w], round(Ew[w], 1)] for w in WATCH if w in cnt}
    return {"kept_words": len(kept), "families": len(fams), "G": obs, "null_mean": float(sims.mean()), "null_sd": float(sims.std()),
            "z": z, "p": float((1 + (sims >= obs).sum()) / (1 + NSIM)), "total_O": int(sum(O[w] for w in kept)),
            "total_E": float(sum(Ew[w] for w in kept)), "watch": watch}


def pseudo(words, lens):
    out, i, j = [], 0, 0
    while i < len(words):
        L = lens[j % len(lens)]; out.append(words[i:i + L]); i += L; j += 1
    return out


def main():
    rng = random.Random(SEED)
    lines, _, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]
    R = {"Voynich DEV": stats(vl, True, rng)}
    gl = gen_lines(); G = []
    for _ in range(10):
        st = rng.randrange(len(gl) - 4000); chunk, n = [], 0
        for l in gl[st:]:
            chunk.append(l); n += len(l)
            if n >= N:
                break
        G.append(stats(chunk, True, rng))
    for name, bid in LANGS.items():
        w = (e030_tokens(bid) if bid in ("indayt", "zlmKSZI") else bwords(bid))[2000:2000 + N]
        R[name] = stats(pseudo(w, lens), False, rng)
    gz = [g["z"] for g in G]
    R["generator"] = {"z": gz, "kept": [g["kept_words"] for g in G], "p": [g["p"] for g in G]}
    ok = [n for n in LANGS if R[n]["z"] > max(gz) and R[n]["p"] < 0.01]
    valid = len(ok) >= 3
    v = R["Voynich DEV"]
    if not valid:
        verdict, bf = "VOID (fewer than 3 reference languages separate from the generator)", {}
    elif v["z"] > max(gz) and v["p"] < 0.01:
        verdict, bf = "WORD-SPECIFIC (vocabulary-like)", {"M": 1 / 3}
    elif v["z"] <= float(np.median(gz)):
        verdict, bf = "FAMILY-LEVEL (generator-like)", {"M": 3.0}
    else:
        verdict, bf = "INCONCLUSIVE", {}
    print(f"Voynich: words {v['kept_words']} in {v['families']} families, O {v['total_O']} E {v['total_E']:.0f}; G {v['G']:.1f} null {v['null_mean']:.1f}±{v['null_sd']:.1f} z {v['z']:.1f} p {v['p']:.4f}")
    print("   watch (O, E):", v["watch"])
    print(f"generator z {[round(x, 1) for x in gz]} words {R['generator']['kept']}")
    for n in LANGS:
        r = R[n]; print(f"{n:11s} words {r['kept_words']:4d} fam {r['families']:3d} O {r['total_O']:4d} E {r['total_E']:6.1f} z {r['z']:.1f} p {r['p']:.4f}")
    print("languages separating from generator:", ok); print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E058", "results": R, "languages_separating": ok, "valid": valid,
                               "verdict": verdict, "bayes_factors": bf, "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
