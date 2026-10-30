"""E099 (Arham, Reddit idea R3): does the Voynich reuse multi-word phrases? See reports/E099_PREREG.md.

Every text is cut to 28,841 tokens (seeded offset) and poured into the Voynich DEV line lengths; n-grams are counted
within lines only. An n-gram is "phrasal" iff no two adjacent words in it are identical (so back-to-back repeats,
C9, do not count as phrases). RP_n = number of phrasal n-gram tokens whose n-gram occurs >= 2 times.
Q_n = (RP_n(text) + 1) / (mean RP_n + 1) over 20 shuffles of the same tokens (whole-text word-order shuffle, re-poured): phrase
reuse beyond what the word frequencies give. Primary n = 3; n = 4, 5 reported.
Meaningful texts: 61 eBible translations (E067 set) + 8 technical/other texts (Pliny, Pliny abbreviated, Avicenna,
Quran, Mahabharata, Lojban Alice, Culpeper, Latin farming prose Cato+Varro+Columella). Meaningless: the copy
generator, 10 disjoint stretches. Voynich: DEV clean prose tokens.
Validity: meaningful 10th percentile of Q3 > generator maximum. Verdict:
  PHRASES LIKE LANGUAGE  Voynich Q3 >= meaningful p10 and > generator max   -> M x 1/3
  NO PHRASES (GENERATOR) Voynich Q3 <= generator max and < meaningful min   -> M x 3
  BETWEEN                otherwise                                         -> none
Rule 8: if Voynich Q3 is within 0.5 shuffle-sd of a boundary, 10 fresh shuffle seeds must agree.
Run: caffeinate -ims .venv/bin/python experiments/e099_phrase_repeats.py [--smoke]
"""
from __future__ import annotations

import argparse, glob, json, random, sys, time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e064_early_audit import tok  # noqa: E402
from e067_gibberish_vocabulary import BIB, GB, SKIP, clean_tokens  # noqa: E402

SEED = 99099
OUT = ROOT / "experiments/results/e099.json"
NS, N_SHUF, N_GEN = (3, 4, 5), 20, 10
OTHER = {"pliny": GB / "mean/texts/Historical - Latin - Technical - Pliny's Natural History.txt",
         "pliny_abbrev": GB / "mean/texts/Historical - Latin (Abbreviated) - Technical - Pliny's Natural History.txt",
         "avicenna": GB / "mean/texts/Historical - Arabic - Technical - Avicenna.txt",
         "quran": GB / "mean/texts/Historical - Arabic - Literary - Quran.txt",
         "mahabharata": GB / "mean/texts/Historical - Sanskrit - Literary - Mahabharata.txt",
         "lojban_alice": GB / "mean/texts/Conlangs - Lojban - Literary - Alice in Wonderland.txt",
         "culpeper": ROOT / "data/external/pg_herbal/pg49513.txt"}
FARM = ["cato", "varro.rr1.txt", "varro.rr2.txt", "columella"]


def log(*a):
    print(*a, flush=True)


def farm_tokens():
    out = []
    for f in FARM:
        p = ROOT / "data/external/latin_library_e043" / f
        for q in sorted([p] if p.is_file() else p.rglob("*")):
            if q.is_file():
                out += clean_tokens(q)
    return out


def pour(toks, lens):
    out, i = [], 0
    for L in lens:
        out.append(toks[i:i + L]); i += L
    return out


def rp(lines, n):
    grams = []
    for l in lines:
        for i in range(len(l) - n + 1):
            g = tuple(l[i:i + n])
            if all(a != b for a, b in zip(g, g[1:])):
                grams.append(g)
    c = Counter(grams)
    return sum(v for v in c.values() if v >= 2), len(grams)


def measure(toks, lens, rng, n_shuf=N_SHUF):
    obs = {n: rp(pour(toks, lens), n) for n in NS}
    sh = {n: [] for n in NS}
    for _ in range(n_shuf):
        x = list(toks); rng.shuffle(x); L = pour(x, lens)
        for n in NS:
            sh[n].append(rp(L, n)[0])
    res = {}
    for n in NS:
        m, s = float(np.mean(sh[n])), float(np.std(sh[n], ddof=1))
        res[n] = {"RP": obs[n][0], "grams": obs[n][1], "shuffle_mean": m, "shuffle_sd": s,
                  "Q": (obs[n][0] + 1) / (m + 1), "Q_sd": s / (m + 1) * (obs[n][0] + 1) / (m + 1)}
    return res


def cut(toks, N, rng):
    if len(toks) < N:
        return None
    s = rng.randrange(len(toks) - N + 1)
    return toks[s:s + N]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, dev_words, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]; N = sum(lens)
    log(f"Voynich DEV lines {len(vl)} tokens {N}")
    texts = {}
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        texts["bible:" + bid] = tok(bid)
    for k, p in OTHER.items():
        texts["other:" + k] = clean_tokens(p)
    texts["other:latin_farming"] = farm_tokens()
    if a.smoke:
        texts = dict(list(texts.items())[:6] + [(k, v) for k, v in texts.items() if k.startswith("other:")])
    R = {"meaningful": {}, "generator": {}}
    for k, t in texts.items():
        c = cut(t, N, rng)
        if c is None:
            log(f"skip {k} ({len(t)} tokens)"); continue
        R["meaningful"][k] = measure(c, lens, rng)
        log(f"{k:28s} Q3 {R['meaningful'][k][3]['Q']:.2f}  Q4 {R['meaningful'][k][4]['Q']:.2f}  Q5 {R['meaningful'][k][5]['Q']:.2f}")
    gflat = [w for l in gen_lines() for w in l]
    for g in range(N_GEN):
        R["generator"][f"gen{g}"] = measure(gflat[g * N:(g + 1) * N], lens, rng)
        log(f"gen{g} Q3 {R['generator'][f'gen{g}'][3]['Q']:.2f}")
    mq = np.array([v[3]["Q"] for v in R["meaningful"].values()]); gq = np.array([v[3]["Q"] for v in R["generator"].values()])
    p10, mmin, gmax = float(np.percentile(mq, 10)), float(mq.min()), float(gq.max())
    valid = p10 > gmax
    log(f"meaningful Q3 p10 {p10:.3f} min {mmin:.3f} (n {len(mq)}) | generator max {gmax:.3f} | VALID {valid} | {time.time() - t0:.0f}s")
    res = {"experiment": "E099", "seed": SEED, "N": N, "results": R, "p10": p10, "meaningful_min": mmin, "generator_max": gmax,
           "valid": bool(valid), "locked_test_excluded": locked}
    if not a.smoke:
        vt = [w for l in vl for w in l]
        V = measure(vt, lens, rng); res["voynich"] = V
        q, sd = V[3]["Q"], V[3]["Q_sd"]
        log("VOYNICH " + " ".join(f"Q{n} {V[n]['Q']:.3f} (RP {V[n]['RP']}, shuffle {V[n]['shuffle_mean']:.1f})" for n in NS))

        def verdict(q):
            if q >= p10 and q > gmax:
                return "PHRASES LIKE LANGUAGE"
            if q <= gmax and q < mmin:
                return "NO PHRASES (GENERATOR-LIKE)"
            return "BETWEEN"
        v = verdict(q) if valid else "VOID"
        near = min(abs(q - b) for b in (p10, gmax, mmin)) < 0.5 * sd
        if valid and near:
                reps = [verdict(measure(vt, lens, random.Random(SEED + 100 + s))[3]["Q"]) for s in range(10)]
            res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "BETWEEN"
        fM = {"PHRASES LIKE LANGUAGE": 1 / 3, "NO PHRASES (GENERATOR-LIKE)": 3.0}.get(v, 1.0)
        res.update(verdict=v, factor_M=fM)
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e099_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
