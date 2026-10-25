"""E064: pre-registered re-audit of the early ledger factors E030-E032, plus the E051 re-measurement forced by the
tokenizer defect found while preparing it. See reports/E064_PREREG.md.

Tokenizer (TOK): lowercase NFC text; a word is a maximal run of letters (Unicode L*), combining marks (M*) and
  apostrophes. The old loaders (e030.tokens, e042.words) split words at combining marks, which cut abugida scripts
  (Tamil, Malayalam, Assamese, Panjabi, Devanagari) into single-letter fragments.
Part A (E031 on fresh data): R and NR (E031's statistics, 10 windows of 28,841 tokens, 5 shuffles) for the 30 E051
  languages. "Does both" iff R >= 1.5 and NR >= max(1.5, 0.67 x Voynich NR). Seed rule: a text within 0.1 of either bar
  is re-measured with 10 fresh window draws (>= 8 of 10 agree).
Part B (E032 with five scribes): Timm & Schinner generator, authors' defaults, one run per scribe (seed 100*sample+hand),
  consumed line by line along the DEV hand runs in manuscript order (E062's construction); 10 samples; E032's 13
  features and rule (|z| > 3 fails; <= 1 fail REPRODUCES, 2-4 PARTIAL, >= 5 FAILS). Seed rule: a feature within 0.5 of
  |z| = 3 is re-judged on samples 11-20 with 10 bootstrap draws of 10 from the 20 (>= 8 of 10 agree); an undecided
  feature forces PARTIAL if the verdict depends on it.
Part C (E051 Part 1 re-measured): AS = sum O / sum E on pseudo-lines with Voynich DEV line lengths, words [2000:2000+N]
  with TOK, for the same 30 languages; exclusion and generator values (seeds 11-20, unaffected) as in E051; E051's
  k / p / BF(M:L) rule and band table.
Run: caffeinate -ims .venv/bin/python experiments/e064_early_audit.py GEN_DIR JAVA [--dry] [--workers 3]   (GEN_DIR absolute)
"""
from __future__ import annotations

import argparse, json, random, sys, time, unicodedata
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e030_reduplication import bible_text  # noqa: E402
from e031_copy_pairs import stats as pair_stats, text_stats  # noqa: E402
from e032_copy_generator import FEATS, Z_OK, features, generate  # noqa: E402
from e051_missing_evidence import OE, THR, bands, pseudo  # noqa: E402
from e062_scribe_tables import dev_lines  # noqa: E402

SEED, N = 64064, 28841
OUT = ROOT / "experiments/results/e064.json"
LANGS = (ROOT / "experiments/e051_ids.txt").read_text().split()
SAMPLES, EXTRA = list(range(1, 11)), list(range(11, 21))
HANDS = "12345"
LEDGER = {"M": 0.0083, "L": 0.9808, "C": 0.0095, "O": 0.0014}


def log(*a):
    print(*a, flush=True)


def tok(bid):
    t = unicodedata.normalize("NFC", bible_text(bid).lower()).replace("’", "'").replace("ʻ", "'")
    return "".join(c if (unicodedata.category(c)[0] in "LM" or c == "'") else " " for c in t).split()


# ------------------------------------------------------------------------------------------------ Part A
def voynich_lines_clean():
    from e011_twin_search import voynich_lines
    vl, cur, _, _ = voynich_lines()
    keep = [i for i, l in enumerate(vl) if any(l)]
    return [[w for w in vl[i] if w] for i in keep], [cur[i] for i in keep]


def does_both(r, nr, nr_bar):
    return r >= 1.5 and nr >= nr_bar


def part_a(words, nr_bar, dry):
    out = {}
    for i, bid in enumerate(LANGS):
        w = words[bid]
        if dry:
            out[bid] = {"tokens": len(w)}; log(f"  {bid:9s} tokens {len(w)}"); continue
        st = text_stats(w, random.Random(SEED + i))
        st["does_both"] = does_both(st["R"], st["NR"], nr_bar)
        st["borderline"] = abs(st["R"] - 1.5) < 0.1 or abs(st["NR"] - nr_bar) < 0.1
        if st["borderline"]:
            votes = []
            for k in range(10):
                s2 = text_stats(w, random.Random(SEED + 1000 * (k + 1) + i))
                votes.append(does_both(s2["R"], s2["NR"], nr_bar))
            st["seed_votes"] = votes
            agree = max(votes.count(True), votes.count(False))
            st["does_both"] = (votes.count(True) >= 8) if agree >= 8 else st["does_both"]
            st["seed_rule"] = "decided" if agree >= 8 else "undecided (first measurement kept)"
        out[bid] = st
        log(f"  {bid:9s} tokens {st['tokens']:7d} R {st['R']:.2f} NR {st['NR']:.2f} raw {st['raw']:.4f} near {st['near']:.4f}"
            f" {'DOES BOTH' if st['does_both'] else ''}{' borderline' if st['borderline'] else ''}")
    return out


# ------------------------------------------------------------------------------------------------ Part B
def hand_runs(lines):
    runs = []
    for h, n in lines:
        if runs and runs[-1][0] == h:
            runs[-1][1] += n
        else:
            runs.append([h, n])
    return runs


def five_scribe_sample(sample, lines, gen_dir, java, work):
    need = Counter()
    for h, n in lines:
        need[h] += n
    streams = {h: generate(gen_dir, java, 100 * sample + int(h), need[h], work) for h in HANDS}
    pos = {h: [0, 0] for h in HANDS}
    out = []
    for h, k in hand_runs(lines):
        got = 0
        while got < k:
            li, off = pos[h]
            line = streams[h][li]
            take = line[off:off + (k - got)]
            out.append(take); got += len(take)
            pos[h] = [li + 1, 0] if off + len(take) >= len(line) else [li, off + len(take)]
    assert sum(map(len, out)) == N, sum(map(len, out))
    return out


def task_b(args):
    sample, lines, gen_dir, java, work = args
    ml = five_scribe_sample(sample, lines, Path(gen_dir), java, Path(work))
    f = features(ml, SEED + sample)
    f["n_lines"] = len(ml)
    return sample, f


def judge(V, G):
    M = {k: float(np.mean([g[k] for g in G])) for k in FEATS}
    S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in FEATS}
    Z = {k: round((V[k] - M[k]) / S[k], 2) for k in FEATS}
    fail = [k for k in FEATS if abs(Z[k]) > Z_OK]
    border = [k for k in FEATS if abs(abs(Z[k]) - Z_OK) < 0.5]
    return {"mean": M, "sd": S, "z": Z, "fail": fail, "n_fail": len(fail), "borderline": border}


def verdict_b(n_fail):
    if n_fail <= 1:
        return "M REPRODUCES", "M x9 (E032's x1/3 withdrawn, x3 for the untuned reproduction)", 9.0
    if n_fail <= 4:
        return "PARTIAL", "M x3 (E032's x1/3 withdrawn)", 3.0
    return "FIVE-SCRIBE GENERATOR FAILS", "none (E032 stands)", 1.0


# ------------------------------------------------------------------------------------------------ Part C
def part_c(words, lens):
    e051 = json.loads((ROOT / "experiments/results/e051.json").read_text())
    G = e051["generator"]
    L, excluded = {}, []
    for b in LANGS:
        w = words[b][2000:2000 + N]
        if len(w) < N or np.mean([len(x) for x in w]) > 15:
            excluded.append(b); continue
        o, e = OE(pseudo(w, lens)); L[b] = o / e
    kL = sum(v >= THR for v in L.values()); kM = sum(v >= THR for v in G.values())
    pL = (kL + 0.5) / (len(L) + 1); pM = (kM + 0.5) / (len(G) + 1)
    bf = pM / pL; f = bands(bf)
    return {"AS": L, "excluded": excluded, "generator": G, "kL": kL, "kM": kM, "pL": pL, "pM": pM, "BF_M_L": bf,
            "factor_M": f, "old_AS": e051["meaningful"], "caution_E045": "REINSTATED" if kL == 0 else "stays withdrawn"}


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("gen_dir"); ap.add_argument("java")
    ap.add_argument("--dry", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    t0 = time.time()
    gen_dir = Path(a.gen_dir).resolve(); work = ROOT / "data/external/e064_gen_work"
    res = {"experiment": "E064", "seed": SEED}
    words = {b: tok(b) for b in LANGS}
    res["token_counts"] = {b: len(w) for b, w in words.items()}

    vl, cur = voynich_lines_clean()
    vst = pair_stats(vl, random.Random(SEED))
    nr_bar = max(1.5, 0.67 * vst["NR"])
    res["voynich_pairs"] = vst; res["nr_bar"] = nr_bar
    log(f"[Part A] E031 on the 30 E051 languages | Voynich R {vst['R']:.2f} NR {vst['NR']:.2f} -> NR bar {nr_bar:.2f}")
    A = part_a(words, nr_bar, a.dry); res["part_a"] = A

    lines, locked = dev_lines(); res["locked_test_excluded"] = locked
    need = Counter()
    for h, n in lines:
        need[h] += n
    log(f"[Part B] DEV {len(lines)} lines, {len(hand_runs(lines))} hand runs, tokens per hand {dict(sorted(need.items()))}")
    if a.dry:
        log("dry run complete"); return

    V = features(vl, SEED); res["voynich"] = V
    log("  Voynich:", {k: round(V[k], 4) for k in FEATS})
    with Pool(a.workers) as pool:
        rows = dict(pool.map(task_b, [(s, lines, str(gen_dir), a.java, str(work)) for s in SAMPLES]))
    J = judge(V, [rows[s] for s in SAMPLES])
    log(f"  five-scribe generator: fails {J['n_fail']} {J['fail']} | borderline {J['borderline']} | z " +
        " ".join(f"{k} {J['z'][k]:+.1f}" for k in FEATS))
    undecided = []
    if J["borderline"]:
        with Pool(a.workers) as pool:
            rows.update(dict(pool.map(task_b, [(s, lines, str(gen_dir), a.java, str(work)) for s in EXTRA])))
        all20 = [rows[s] for s in SAMPLES + EXTRA]
        rng = random.Random(SEED)
        draws = [judge(V, rng.sample(all20, 10)) for _ in range(10)]
        J["seed_rule"] = {}
        for k in J["borderline"]:
            fails = sum(k in d["fail"] for d in draws)
            decided = True if fails >= 8 else False if fails <= 2 else None
            if decided is None:
                undecided.append(k)
            J["seed_rule"][k] = {"fail_votes": fails, "decided_fail": decided}
            if decided is True and k not in J["fail"]:
                J["fail"].append(k)
            if decided is False and k in J["fail"]:
                J["fail"].remove(k)
        J["n_fail"] = len(J["fail"]); J["judge_20"] = judge(V, all20)
        log(f"  seed rule: {J['seed_rule']} -> fails {J['n_fail']} {J['fail']}")
    lo = len([k for k in J["fail"] if k not in undecided]); hi = lo + len(undecided)
    vb, fb, fM_b = verdict_b(J["n_fail"])
    if verdict_b(lo)[0] != verdict_b(hi)[0]:
        vb, fb, fM_b = "PARTIAL (undecided borderline feature)", "M x3 (E032's x1/3 withdrawn)", 3.0
    res["part_b"] = {**J, "samples": rows, "verdict": vb, "factor": fb, "undecided": undecided}

    both = [b for b, s in A.items() if s["does_both"]]
    va = "E031 CONFIRMED (a fresh language does both)" if both else "E031 WITHDRAWN (0 of 30 fresh languages do both)"
    fL = 1.0 if both else 1 / 3
    r15 = [b for b, s in A.items() if s["R"] >= 1.5]
    res["part_a_verdict"] = {"verdict": va, "factor": "none" if both else "L x1/3", "does_both": both, "R_ge_1.5": r15}

    lens = [len(l) for l in vl]
    C = part_c(words, lens); res["part_c"] = C
    fM_c = C["factor_M"] or 1.0
    top = sorted(C["AS"].items(), key=lambda x: -x[1])[:6]
    log(f"[Part C] E051 re-measured: k_L(AS>=0.85) {C['kL']}/{len(C['AS'])} (was 2), k_M {C['kM']}, BF(M:L) {C['BF_M_L']:.2f} -> factor on M "
        f"{C['factor_M']} | top {[(b, round(v, 2)) for b, v in top]} | excluded {C['excluded']} | E045 caution {C['caution_E045']}")

    log(f"[Part A] {va} | does both: {both} | R >= 1.5: {r15}")
    log(f"[Part B] VERDICT {vb} | {fb}")
    new = {"M": LEDGER["M"] * fM_b * fM_c, "L": LEDGER["L"] * fL, "C": LEDGER["C"], "O": LEDGER["O"]}
    s = sum(new.values()); new = {k: round(v / s, 4) for k, v in new.items()}
    res["ledger"] = {"before": LEDGER, "factors": {"L_partA": fL, "M_partB": fM_b, "M_partC": fM_c}, "after": new}
    res["runtime_s"] = time.time() - t0
    log(f"LEDGER before {LEDGER} -> after {new} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
