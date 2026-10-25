"""E070 v2 script (E070_AMENDMENT.md): the rank-correlation statistic is replaced by partner-set overlap, after a toy
language showed the artifact described in the amendment. Band, texts, gate, bar and decision rules are unchanged.

PSO: in each half h a pair (a, b) of the band words (ranks 51-250, present in both halves) is a PARTNER iff c_h >= 2 and
c_h >= 3 e_h (co-occur in at least two lines and at least three times chance). PSO = |P1 & P2| / |P1 | P2| (0 if the
union is empty), minus the mean over 3 within-half shuffles. Reported under the key "STAB" so E070's judge applies
unchanged, plus explicit fields.
Run: caffeinate -ims .venv/bin/python experiments/e070_content_partners_v2.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time, zlib
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e069_word_partners as P  # noqa: E402
import e070_content_partners as X  # noqa: E402

SEED, LO, HI = X.SEED, X.LO, X.HI
OUT = ROOT / "experiments/results/e070.json"
LEDGER = X.LEDGER


def log(*a):
    print(*a, flush=True)


def partners(lines, words):
    n = len(lines)
    present = [set(l) & words for l in lines]
    pw = Counter(w for s in present for w in s)
    cc = Counter()
    for s in present:
        for a, b in combinations(sorted(s), 2):
            cc[(a, b)] += 1
    return {p for p, c in cc.items() if c >= 2 and c >= 3 * n * (pw[p[0]] / n) * (pw[p[1]] / n)}


def pso(h1, h2, words):
    p1, p2 = partners(h1, words), partners(h2, words)
    u = p1 | p2
    return (len(p1 & p2) / len(u) if u else 0.0), len(p1), len(p2), len(p1 & p2)


def stability_pso(lines, seed=0):
    rng = random.Random(seed)
    cnt = Counter(w for l in lines for w in l)
    h1, h2 = P.halves(lines)
    in1 = {w for l in h1 for w in l}; in2 = {w for l in h2 for w in l}
    words = {w for w in [w for w, _ in cnt.most_common(HI)][LO:HI] if w in in1 and w in in2}
    raw, n1, n2, both = pso(h1, h2, words)
    sh = [pso(P.shuffle_half(h1, rng), P.shuffle_half(h2, rng), words) for _ in range(3)]
    base = float(np.mean([x[0] for x in sh]))
    return {"STAB": raw - base, "PSO": raw - base, "RAW": raw, "RAW_shuffled": base, "partners_h1": n1, "partners_h2": n2,
            "partners_both": both, "shuffled_partners": float(np.mean([x[1] + x[2] for x in sh]) / 2),
            "n_words": len(words), "n_lines": len(lines), "n_tokens": sum(map(len, lines))}


def task(args):
    kind, name, lines = args
    return kind, name, stability_pso(lines, zlib.crc32(f"{kind}:{name}".encode()) & 0xFFFF)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time()
    lines, cur, _, locked = E.voynich_lines()
    keep = [i for i, l in enumerate(lines) if any(l)]
    vl = [[w for w in lines[i] if w] for i in keep]; cur = [cur[i] for i in keep]
    jobs = P.build_jobs(SEED, vl, cur)
    log(f"jobs {len(jobs)} (statistic: partner-set overlap PSO, band ranks {LO + 1}-{HI})")
    with Pool(a.workers) as pool:
        R = P.collect(pool.map(task, jobs))
    J = X.judge(R)
    for t in ("ALL", "A", "B"):
        r = R["voynich"][t]; log(f"Voynich {t:3s} PSO {r['PSO']:.3f} (raw {r['RAW']:.3f}, shuffled {r['RAW_shuffled']:.3f}) partners h1 {r['partners_h1']} h2 {r['partners_h2']} both {r['partners_both']} (shuffled ~{r['shuffled_partners']:.0f}) words {r['n_words']}")
    log(f"languages (ALL): min {J['lang_min']:.3f} p10 {J['lang_p10']:.3f} median {J['lang_median']:.3f} max {J['lang_max']:.3f} | grammar-heavy {{{', '.join(f'{b}: {v:.3f}' for b, v in J['grammar_heavy'].items() if v is not None)}}} median {J['grammar_heavy_median']:.3f} | bar {J['bar']:.3f}")
    log(f"generator (ALL): median {J['gen_median']:.3f} max {J['gen_max']:.3f}; below p10 {J['gen_below_p10']}/10 -> gate {'PASS' if J['gate'] else 'FAIL'}")
    for t in "AB":
        s = J["secondary"][t]; log(f"  secondary {t}: Voynich {s['STAB']:.3f} | bar {s['bar']:.3f} (lang p10 {s['lang_p10']:.3f}, median {s['lang_median']:.3f}) | gen median {s['gen_median']:.3f} max {s['gen_max']:.3f} | {'language-like ' if s['language_like'] else ''}{'generator-like' if s['generator_like'] else ''}")
    top = sorted(R["language"].items(), key=lambda x: -x[1]["PSO"]); log("languages: " + ", ".join(f"{b} {r['PSO']:.2f}" for b, r in top[:6]) + " ... " + ", ".join(f"{b} {r['PSO']:.2f}" for b, r in top[-4:]))
    verdict, f = J["verdict"], J["factors"]
    seed_rule = None
    if J["borderline"]:
        votes = []
        for s in range(1, 11):
            with Pool(a.workers) as pool:
                R2 = P.collect(pool.map(task, P.build_jobs(SEED + s, vl, cur)))
            votes.append(X.judge(R2)["verdict"].split(" (")[0])
        top_v = max(set(votes), key=votes.count); seed_rule = {"votes": votes, "decided": votes.count(top_v) >= 8}
        if votes.count(top_v) >= 8:
            verdict = top_v; f = {"LANGUAGE-LIKE": {"L": 3.0}, "GENERATOR-LIKE": {"M": 3.0}}.get(top_v, {})
        else:
            verdict, f = "INCONCLUSIVE (seed rule undecided)", {}
        log(f"seed rule: {votes}")
    new = {k: LEDGER[k] * f.get(k, 1.0) for k in LEDGER}
    s = sum(new.values()); new = {k: round(x / s, 4) for k, x in new.items()}
    log(f"VERDICT {verdict} | factors {f} | ledger {new} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E070", "script": "v2 (PSO)", "seed": SEED, "ranks": [LO + 1, HI], "results": R, "judge": J,
                               "seed_rule": seed_rule, "verdict": verdict, "factors": f, "ledger": {"before": LEDGER, "after": new},
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
