"""E031 (ledger test 2): does any real language show BOTH of Voynich's neighbour habits -- exact copies above chance
AND near-copies (one letter different) above chance -- in the same text? See reports/E031_PREREG.md. No key, no search.

Per text: R  = exact-repeat rate of neighbouring words / sum p_w^2 (as E030);
          NR = near-copy rate of neighbouring words / the same rate after shuffling the words (mean of 5 shuffles).
Voynich: DEV prose, within-line pairs; shuffles permute all clean tokens and refill the same line lengths.
Reference: the 14 E030 Bibles (incl. anchors) + every PG file (34+ languages) with >= 10,000 words.
Run: caffeinate -ims .venv/bin/python experiments/e031_copy_pairs.py
"""
from __future__ import annotations

import json, random, re, sys, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from e011_twin_search import voynich_lines  # noqa: E402
from e030_reduplication import ANCHORS, PRIMARY, SECONDARY, ed1, tokens  # noqa: E402

N, K, SHUF, SEED, MIN_PG = 28841, 10, 5, 31031, 10000


def pair_rates(seqs):
    rep = near = n = 0
    for s in seqs:
        for a, b in zip(s, s[1:]):
            n += 1; rep += a == b; near += ed1(a, b)
    return rep / n, near / n


def stats(seqs, rng):
    wc = Counter(w for s in seqs for w in s); tot = sum(wc.values())
    p2 = sum((c / tot) ** 2 for c in wc.values())
    raw, near = pair_rates(seqs)
    flat = [w for s in seqs for w in s]; lens = [len(s) for s in seqs]
    sh = []
    for _ in range(SHUF):
        rng.shuffle(flat); out, i = [], 0
        for L in lens:
            out.append(flat[i:i + L]); i += L
        sh.append(pair_rates(out)[1])
    return {"R": raw / p2, "NR": near / max(1e-12, float(np.mean(sh))), "raw": raw, "near": near}


def text_stats(w, rng):
    if len(w) > N:
        wins = [stats([w[s:s + N]], rng) for s in (rng.randrange(0, len(w) - N) for _ in range(K))]
    else:
        wins = [stats([w], rng)]
    return {"tokens": len(w), **{k: float(np.mean([x[k] for x in wins])) for k in ("R", "NR", "raw", "near")}}


def pg_tokens(p):
    t = unicodedata.normalize("NFC", p.read_text(encoding="utf-8", errors="ignore").lower())
    return re.findall(r"[^\W\d_]+", t)


def main():
    rng = random.Random(SEED)
    V = stats([[x for x in l if x] for l in voynich_lines()[0]], rng)
    T = {}
    for b in ANCHORS + PRIMARY + SECONDARY:
        T["bible:" + b] = text_stats(tokens(b), rng)
    for p in sorted((ROOT / "data/raw/corpora/pg").glob("*.txt")):
        w = pg_tokens(p)
        if len(w) >= MIN_PG:
            T["pg:" + p.name] = text_stats(w, rng)
    thr_nr = max(1.5, 0.67 * V["NR"])
    both = [k for k, x in T.items() if x["R"] >= 1.5 and x["NR"] >= thr_nr]
    if V["NR"] < 1.5:
        verdict, bf = "PREMISE FAILS", {}
    elif both:
        verdict, bf = "A LANGUAGE DOES BOTH", {"L": 3.0}
    else:
        verdict, bf = "NO LANGUAGE DOES BOTH", {"M": 3.0}
    out = {"experiment": "E031", "voynich_dev": V, "thr_NR": thr_nr, "both": both, "texts": T,
           "max_NR_text": max(T, key=lambda k: T[k]["NR"]), "max_NR": max(x["NR"] for x in T.values()),
           "n_R_ge_1.5": sum(x["R"] >= 1.5 for x in T.values()), "verdict": verdict, "bayes_factors": bf}
    (ROOT / "experiments/results/e031.json").write_text(json.dumps(out, indent=1))
    print(f"Voynich R {V['R']:.2f} NR {V['NR']:.2f} (raw {100*V['raw']:.2f}% near {100*V['near']:.2f}%)  thr_NR {thr_nr:.2f}")
    for k, x in sorted(T.items(), key=lambda kv: -kv[1]["NR"])[:12]:
        print(f"  top NR {k:24s} R {x['R']:.2f} NR {x['NR']:.2f}")
    for k, x in sorted(T.items(), key=lambda kv: -kv[1]["R"])[:6]:
        print(f"  top R  {k:24s} R {x['R']:.2f} NR {x['NR']:.2f}")
    print(len(T), "texts | both:", both, "|", verdict, bf)


if __name__ == "__main__":
    main()
