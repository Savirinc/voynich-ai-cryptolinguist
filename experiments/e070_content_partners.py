"""E070: do Voynich's content-like words (ranks 51-250) have partners that persist across the book? See E070_PREREG.md.
E069's statistic (STAB = Spearman of pair associations between halves minus within-half shuffle baseline) on the words
ranked 51-250 by frequency (the 50 commonest, grammar-like words excluded), present in both halves.
Texts, sizes, pseudo-lines, generator stretches: exactly E069 (seed 70070).
Gate: >= 8/10 generator stretches below the languages' 10th percentile (ALL size), else VOID.
Verdict: LANGUAGE-LIKE iff Voynich > every generator stretch and Voynich >= min(language p10, median of the four
grammar-heavy languages hboWLC, polubg, slk, azb) -> L x3; GENERATOR-LIKE iff Voynich <= generator median -> M x3; else
INCONCLUSIVE. A-only must agree in direction (same rule at A size), else INCONCLUSIVE. Seed rule as E069 (0.05, 10 seeds).
Run: caffeinate -ims .venv/bin/python experiments/e070_content_partners.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time, zlib
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e069_word_partners as P  # noqa: E402

SEED, LO, HI = 70070, 50, 250
OUT = ROOT / "experiments/results/e070.json"
GRAMMAR_HEAVY = ["hboWLC", "polubg", "slk", "azb"]
LEDGER = {"M": 0.0739, "L": 0.8939, "C": 0.0281, "O": 0.0041}


def log(*a):
    print(*a, flush=True)


def stability_content(lines, seed=0):
    rng = random.Random(seed)
    cnt = Counter(w for l in lines for w in l)
    h1, h2 = P.halves(lines)
    in1 = {w for l in h1 for w in l}; in2 = {w for l in h2 for w in l}
    ranked = [w for w, _ in cnt.most_common(HI)][LO:HI]
    words = {w for w in ranked if w in in1 and w in in2}
    rho, part, npairs = P.raw_stab(h1, h2, words)
    sh = [P.raw_stab(P.shuffle_half(h1, rng), P.shuffle_half(h2, rng), words) for _ in range(3)]
    return {"STAB": rho - float(np.mean([x[0] for x in sh])), "RAW": rho, "RAW_shuffled": float(np.mean([x[0] for x in sh])),
            "PART": part - float(np.mean([x[1] for x in sh])), "n_pairs": npairs, "n_words": len(words),
            "n_lines": len(lines), "n_tokens": sum(map(len, lines))}


def task(args):
    kind, name, lines = args
    return kind, name, stability_content(lines, zlib.crc32(f"{kind}:{name}".encode()) & 0xFFFF)


def judge(R):
    v = R["voynich"]["ALL"]["STAB"]
    L = {b: r["STAB"] for b, r in R["language"].items()}; La = np.array(list(L.values()))
    G = np.array([r["STAB"] for r in R["generator"].values()])
    p10 = float(np.percentile(La, 10)); gh = float(np.median([L[b] for b in GRAMMAR_HEAVY if b in L]))
    bar = min(p10, gh); gmax = float(G.max()); gmed = float(np.median(G))
    gate = int((G < p10).sum()) >= 8
    if not gate:
        verdict, f = "VOID (generator not separated from languages)", {}
    elif v > gmax and v >= bar:
        verdict, f = "LANGUAGE-LIKE", {"L": 3.0}
    elif v <= gmed:
        verdict, f = "GENERATOR-LIKE", {"M": 3.0}
    else:
        verdict, f = "INCONCLUSIVE", {}
    sec = {}
    for t in "AB":
        vt = R["voynich"][t]["STAB"]
        Lt = {b: r["STAB"] for b, r in R[f"language_{t}"].items()}; Lta = np.array(list(Lt.values()))
        Gt = np.array([r["STAB"] for r in R[f"generator_{t}"].values()])
        bart = min(float(np.percentile(Lta, 10)), float(np.median([Lt[b] for b in GRAMMAR_HEAVY if b in Lt])))
        sec[t] = {"STAB": vt, "bar": bart, "lang_p10": float(np.percentile(Lta, 10)), "lang_median": float(np.median(Lta)),
                  "gen_max": float(Gt.max()), "gen_median": float(np.median(Gt)),
                  "language_like": bool(vt > Gt.max() and vt >= bart), "generator_like": bool(vt <= np.median(Gt))}
    if verdict == "LANGUAGE-LIKE" and not sec["A"]["language_like"]:
        verdict, f = "INCONCLUSIVE (A-only does not agree)", {}
    if verdict == "GENERATOR-LIKE" and not sec["A"]["generator_like"]:
        verdict, f = "INCONCLUSIVE (A-only does not agree)", {}
    border = gate and (abs(v - bar) < 0.05 or abs(v - gmax) < 0.05 or abs(v - gmed) < 0.05)
    return {"voynich_STAB": v, "lang_p10": p10, "grammar_heavy_median": gh, "bar": bar, "lang_median": float(np.median(La)),
            "lang_min": float(La.min()), "lang_max": float(La.max()), "grammar_heavy": {b: L.get(b) for b in GRAMMAR_HEAVY},
            "gen_max": gmax, "gen_median": gmed, "gen_below_p10": int((G < p10).sum()), "gate": gate, "secondary": sec,
            "verdict": verdict, "factors": f, "borderline": border}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time()
    lines, cur, _, locked = E.voynich_lines()
    keep = [i for i, l in enumerate(lines) if any(l)]
    vl = [[w for w in lines[i] if w] for i in keep]; cur = [cur[i] for i in keep]
    jobs = P.build_jobs(SEED, vl, cur)
    log(f"jobs {len(jobs)}")
    with Pool(a.workers) as pool:
        R = P.collect(pool.map(task, jobs))
    J = judge(R)
    for t in ("ALL", "A", "B"):
        r = R["voynich"][t]; log(f"Voynich {t:3s} STAB {r['STAB']:.3f} (RAW {r['RAW']:.3f}) PART {r['PART']:.3f} words {r['n_words']} tokens {r['n_tokens']}")
    log(f"languages (ALL): min {J['lang_min']:.3f} p10 {J['lang_p10']:.3f} median {J['lang_median']:.3f} max {J['lang_max']:.3f} | grammar-heavy {J['grammar_heavy']} median {J['grammar_heavy_median']:.3f} | bar {J['bar']:.3f}")
    log(f"generator (ALL): median {J['gen_median']:.3f} max {J['gen_max']:.3f}; below p10 {J['gen_below_p10']}/10 -> gate {'PASS' if J['gate'] else 'FAIL'}")
    for t in "AB":
        s = J["secondary"][t]; log(f"  secondary {t}: Voynich {s['STAB']:.3f} | bar {s['bar']:.3f} (lang p10 {s['lang_p10']:.3f}, median {s['lang_median']:.3f}) | gen median {s['gen_median']:.3f} max {s['gen_max']:.3f} | {'language-like ' if s['language_like'] else ''}{'generator-like' if s['generator_like'] else ''}")
    verdict, f = J["verdict"], J["factors"]
    seed_rule = None
    if J["borderline"]:
        votes = []
        for s in range(1, 11):
            with Pool(a.workers) as pool:
                R2 = P.collect(pool.map(task, P.build_jobs(SEED + s, vl, cur)))
            votes.append(judge(R2)["verdict"].split(" (")[0])
        top_v = max(set(votes), key=votes.count); seed_rule = {"votes": votes, "decided": votes.count(top_v) >= 8}
        if votes.count(top_v) >= 8:
            verdict = top_v; f = {"LANGUAGE-LIKE": {"L": 3.0}, "GENERATOR-LIKE": {"M": 3.0}}.get(top_v, {})
        else:
            verdict, f = "INCONCLUSIVE (seed rule undecided)", {}
        log(f"seed rule: {votes}")
    new = {k: LEDGER[k] * f.get(k, 1.0) for k in LEDGER}
    s = sum(new.values()); new = {k: round(x / s, 4) for k, x in new.items()}
    log(f"VERDICT {verdict} | factors {f} | ledger {new} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E070", "seed": SEED, "ranks": [LO + 1, HI], "results": R, "judge": J, "seed_rule": seed_rule,
                               "verdict": verdict, "factors": f, "ledger": {"before": LEDGER, "after": new},
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
