"""E069: do Voynich words have partners that persist across the book? See reports/E069_PREREG.md.

Per text: lines (Voynich own lines in manuscript order; generator own lines; languages in pseudo-lines of Voynich DEV
line lengths). K = 200 most frequent words. The text is cut into two halves by token count (first half / second half).
In each half h, for each unordered pair (a, b) of the K words (both present in both halves): c_h = lines containing
both, e_h = n_lines_h * p_h(a) * p_h(b) with p_h(a) = share of lines containing a; association s_h = log((c_h + 0.5) /
(e_h + 0.5)). RAW = Spearman correlation of s_1 and s_2 over pairs. The same is computed after shuffling the words of
each half across its lines (3 shuffles; frequencies and line lengths kept), giving the frequency-driven baseline.
STAB = RAW - mean(shuffled RAW): do partners in one half stay partners in the other, beyond what frequencies alone give?
Also reported: PART = share of pairs with s > log 3 in both halves, minus its shuffled baseline; n_pairs.
Texts: Voynich DEV all prose (primary); Voynich A-only and B-only (secondary, at their own sizes, with size-matched
language windows); 60 Bibles (E064 TOK, words from 2,000); 10 generator stretches.
Known-answer gate: >= 8 of 10 generator stretches below the 10th percentile of the 60 languages (the measure separates
languages from the generator), else VOID.
Verdict (primary): LANGUAGE-LIKE iff Voynich STAB >= language 10th percentile and > max generator -> L x3;
GENERATOR-LIKE iff Voynich STAB <= generator median -> M x3; else INCONCLUSIVE. The primary verdict stands only if the
within-A secondary agrees in direction (A >= its language 10th percentile for LANGUAGE-LIKE; A <= its generator median
for GENERATOR-LIKE); otherwise INCONCLUSIVE (dialect shift between halves is a possible cause).
Seed rule: Voynich STAB within 0.05 of a boundary -> language windows and generator stretches re-drawn with 10 seeds.
Run: caffeinate -ims .venv/bin/python experiments/e069_word_partners.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time, zlib
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e058_word_repeat_individuality_v2 import pseudo  # noqa: E402
from e064_early_audit import tok  # noqa: E402

SEED, K = 69069, 200
OUT = ROOT / "experiments/results/e069.json"
BIB = ROOT / "data/external/bibles"
SKIP = {"cmn-cu89s", "jpn1965", "vie1934", "lit", "engWycliffe"}
LEDGER = {"M": 0.0739, "L": 0.8938, "C": 0.0281, "O": 0.0041}


def log(*a):
    print(*a, flush=True)


def halves(lines):
    tot = sum(map(len, lines)); acc = 0
    for i, l in enumerate(lines):
        acc += len(l)
        if acc >= tot / 2:
            return lines[:i + 1], lines[i + 1:]
    return lines, []


def assoc(lines, words):
    n = len(lines)
    present = [set(l) & words for l in lines]
    pw = Counter(w for s in present for w in s)
    cc = Counter()
    for s in present:
        for a, b in combinations(sorted(s), 2):
            cc[(a, b)] += 1
    s, e = {}, {}
    for a, b in combinations(sorted(words), 2):
        eab = n * (pw[a] / n) * (pw[b] / n)
        e[(a, b)] = eab; s[(a, b)] = math.log((cc[(a, b)] + 0.5) / (eab + 0.5))
    return s, e


def shuffle_half(lines, rng):
    flat = [w for l in lines for w in l]; rng.shuffle(flat)
    out, i = [], 0
    for l in lines:
        out.append(flat[i:i + len(l)]); i += len(l)
    return out


def raw_stab(h1, h2, words):
    s1, _ = assoc(h1, words); s2, _ = assoc(h2, words)
    pairs = list(s1)
    x = np.array([s1[p] for p in pairs]); y = np.array([s2[p] for p in pairs])
    rho = float(spearmanr(x, y).correlation) if len(pairs) > 10 else float("nan")
    part = float(np.mean((x > math.log(3)) & (y > math.log(3)))) if len(pairs) else float("nan")
    return rho, part, len(pairs)


def stability(lines, seed=0):
    rng = random.Random(seed)
    cnt = Counter(w for l in lines for w in l)
    h1, h2 = halves(lines)
    in1 = {w for l in h1 for w in l}; in2 = {w for l in h2 for w in l}
    words = {w for w, _ in cnt.most_common(K) if w in in1 and w in in2}
    rho, part, npairs = raw_stab(h1, h2, words)
    sh = [raw_stab(shuffle_half(h1, rng), shuffle_half(h2, rng), words) for _ in range(3)]
    return {"STAB": rho - float(np.mean([x[0] for x in sh])), "RAW": rho, "RAW_shuffled": float(np.mean([x[0] for x in sh])),
            "PART": part - float(np.mean([x[1] for x in sh])), "n_pairs": npairs, "n_words": len(words),
            "n_lines": len(lines), "n_tokens": sum(map(len, lines))}


def task(args):
    kind, name, lines = args
    return kind, name, stability(lines, zlib.crc32(f"{kind}:{name}".encode()) & 0xFFFF)


def build_jobs(seed, vl, cur):
    rng = random.Random(seed)
    lens = [len(l) for l in vl]
    jobs = [("voynich", "ALL", vl)]
    for t in "AB":
        sub = [l for l, c in zip(vl, cur) if c == t]
        jobs.append(("voynich", t, sub))
    sizes = {"ALL": sum(lens), "A": sum(len(l) for l, c in zip(vl, cur) if c == "A"), "B": sum(len(l) for l, c in zip(vl, cur) if c == "B")}
    gl = gen_lines()
    for k in range(10):
        st = rng.randrange(len(gl) - 4000); chunk, n = [], 0
        for l in gl[st:]:
            chunk.append(l); n += len(l)
            if n >= sizes["ALL"]:
                break
        jobs.append(("generator", f"gen{k}", chunk))
        for t in "AB":
            chunk2, n = [], 0
            for l in gl[st:]:
                chunk2.append(l); n += len(l)
                if n >= sizes[t]:
                    break
            jobs.append((f"generator_{t}", f"gen{k}", chunk2))
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        w = tok(bid)
        if len(w) < 2000 + sizes["ALL"]:
            continue
        st = rng.randrange(2000, len(w) - sizes["ALL"] + 1)
        jobs.append(("language", bid, pseudo(w[st:st + sizes["ALL"]], lens)))
        for t in "AB":
            jobs.append((f"language_{t}", bid, pseudo(w[st:st + sizes[t]], lens)))
    return jobs


def collect(out):
    R = {}
    for kind, name, r in out:
        R.setdefault(kind, {})[name] = r
    return R


def judge(R):
    v = R["voynich"]["ALL"]["STAB"]
    L = np.array([r["STAB"] for r in R["language"].values()]); G = np.array([r["STAB"] for r in R["generator"].values()])
    p10 = float(np.percentile(L, 10)); gmax = float(G.max()); gmed = float(np.median(G))
    gate = int((G < p10).sum()) >= 8
    if not gate:
        verdict, f = "VOID (generator not separated from languages)", {}
    elif v >= p10 and v > gmax:
        verdict, f = "LANGUAGE-LIKE", {"L": 3.0}
    elif v <= gmed:
        verdict, f = "GENERATOR-LIKE", {"M": 3.0}
    else:
        verdict, f = "INCONCLUSIVE", {}
    sec = {}
    for t in "AB":
        vt = R["voynich"][t]["STAB"]
        Lt = np.array([r["STAB"] for r in R[f"language_{t}"].values()]); Gt = np.array([r["STAB"] for r in R[f"generator_{t}"].values()])
        sec[t] = {"STAB": vt, "lang_p10": float(np.percentile(Lt, 10)), "lang_median": float(np.median(Lt)), "gen_max": float(Gt.max()),
                  "gen_median": float(np.median(Gt)), "language_like": bool(vt >= np.percentile(Lt, 10) and vt > Gt.max()), "generator_like": bool(vt <= np.median(Gt))}
    if verdict == "LANGUAGE-LIKE" and not sec["A"]["language_like"]:
        verdict, f = "INCONCLUSIVE (A-only does not agree)", {}
    if verdict == "GENERATOR-LIKE" and not sec["A"]["generator_like"]:
        verdict, f = "INCONCLUSIVE (A-only does not agree)", {}
    border = gate and (abs(v - p10) < 0.05 or abs(v - gmax) < 0.05 or abs(v - gmed) < 0.05)
    return {"voynich_STAB": v, "lang_p10": p10, "lang_median": float(np.median(L)), "lang_min": float(L.min()), "lang_max": float(L.max()),
            "gen_max": gmax, "gen_median": gmed, "gen_below_p10": int((G < p10).sum()), "gate": gate, "secondary": sec,
            "verdict": verdict, "factors": f, "borderline": border}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time()
    lines, cur, _, locked = E.voynich_lines()
    keep = [i for i, l in enumerate(lines) if any(l)]
    vl = [[w for w in lines[i] if w] for i in keep]; cur = [cur[i] for i in keep]
    jobs = build_jobs(SEED, vl, cur)
    log(f"jobs {len(jobs)}: Voynich ALL/A/B, 30 generator, {sum(j[0] == 'language' for j in jobs)} languages x3")
    with Pool(a.workers) as pool:
        R = collect(pool.map(task, jobs))
    J = judge(R)
    for t in ("ALL", "A", "B"):
        r = R["voynich"][t]; log(f"Voynich {t:3s} STAB {r['STAB']:.3f} PART {r['PART']:.3f} pairs {r['n_pairs']} tokens {r['n_tokens']}")
    log(f"languages (ALL size): min {J['lang_min']:.3f} p10 {J['lang_p10']:.3f} median {J['lang_median']:.3f} max {J['lang_max']:.3f}")
    log(f"generator (ALL size): median {J['gen_median']:.3f} max {J['gen_max']:.3f}; below language p10: {J['gen_below_p10']}/10 -> gate {'PASS' if J['gate'] else 'FAIL'}")
    for t in "AB":
        s = J["secondary"][t]; log(f"  secondary {t}: Voynich {s['STAB']:.3f} | lang p10 {s['lang_p10']:.3f} median {s['lang_median']:.3f} | gen median {s['gen_median']:.3f} max {s['gen_max']:.3f} | {'language-like' if s['language_like'] else ''}{'generator-like' if s['generator_like'] else ''}")
    top = sorted(R["language"].items(), key=lambda x: -x[1]["STAB"]); log("languages: " + ", ".join(f"{b} {r['STAB']:.2f}" for b, r in top[:6]) + " ... " + ", ".join(f"{b} {r['STAB']:.2f}" for b, r in top[-4:]))
    verdict, f = J["verdict"], J["factors"]
    seed_rule = None
    if J["borderline"]:
        votes = []
        for s in range(1, 11):
            with Pool(a.workers) as pool:
                R2 = collect(pool.map(task, build_jobs(SEED + s, vl, cur)))
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
    OUT.write_text(json.dumps({"experiment": "E069", "seed": SEED, "K": K, "results": R, "judge": J, "seed_rule": seed_rule, "verdict": verdict,
                               "factors": f, "ledger": {"before": LEDGER, "after": new}, "locked_test_excluded": locked,
                               "runtime_s": time.time() - t0}, indent=1, default=str))


if __name__ == "__main__":
    main()
