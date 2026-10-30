"""E100 (Arham): E099's phrase-reuse test redone against controls matched in vocabulary richness. See reports/E100_PREREG.md.

E099's Q3 = (RP3 + 1) / (shuffle RP3 + 1) rises with vocabulary richness, and no E099 control was as rich as the Voynich
(6,077 types in 28,841 tokens). Here the copy generator is run on a declared grid of 10 settings x 5 fresh seeds
(50 stretches, about 3,800-10,000 types); meaningful texts are E099's 69. Richness = distinct word types in the
28,841-token stretch. Matched band: Voynich types +-15%. G* = generator stretches in band, L* = meaningful texts in band.
Validity: |G*| >= 10, |L*| >= 8, and L* Q3 p10 > G* Q3 max. Verdict (supersedes E099's scoring):
  PHRASES LIKE LANGUAGE  Voynich Q3 >= L* p10 and > G* max      -> E099's M x 1/3 kept (no new factor)
  NO PHRASES             Voynich Q3 <= G* max and < L* min      -> E099 replaced by M x 3 (net M x 9 now)
  BETWEEN                otherwise                              -> E099 withdrawn (net M x 3 now)
  VOID                   validity fails                         -> E099 withdrawn (net M x 3 now)
Rule 8: if Voynich Q3 is within 0.5 shuffle-sd of a boundary, 10 fresh shuffle seeds must agree (>= 8).
Run: caffeinate -ims .venv/bin/python experiments/e100_matched_phrases.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e099_phrase_repeats_v2 as P  # noqa: E402

SEED = 100100
OUT = ROOT / "experiments/results/e100.json"
WORK = ROOT / "experiments/results/e100_work"
GEN = ROOT / "data/external/timm_schinner_generator/sct"
JAVA = "/opt/homebrew/opt/openjdk/bin/java"
BAND = 0.15
GSEEDS = (11, 12, 13, 14, 15)
GRID = {
    "default": {},
    "err10": {"method.canFollow.error_rate": "10"},
    "err10_reuse0_pos0": {"method.canFollow.error_rate": "10", "method.morph.reuse_last.probability": "0",
                          "method.sourceChooser.same_position_probability": "0"},
    "err10_position": {"method.canFollow.error_rate": "10", "method.sourceChooser": "position"},
    "random_morphhi": {"method.sourceChooser": "random", "method.morph.add_remove.probability": "40",
                       "method.morph.combine_split.probability": "40"},
    "err2_random": {"method.canFollow.error_rate": "2", "method.sourceChooser": "random"},
    "random": {"method.sourceChooser": "random"},
    "err5_random": {"method.canFollow.error_rate": "5", "method.sourceChooser": "random"},
    "none": {"method.canFollow": "none"},
    "err10_none": {"method.canFollow": "none", "method.canFollow.error_rate": "10"},
}
log = P.log


def generate(job):
    name, seed, n = job
    d = WORK / f"{name}_s{seed}"; (d / "generate").mkdir(parents=True, exist_ok=True)
    c = (GEN / "executable/conf.properties").read_text()
    c = re.sub(r"(?m)^text\.lines_to_create=.*$", "text.lines_to_create=4200", c)
    c = re.sub(r"(?m)^method\.random\.pseudo\.seed=.*$", f"method.random.pseudo.seed={seed}", c)
    for k, v in GRID[name].items():
        c, m = re.subn(rf"(?m)^{re.escape(k)}=.*$", f"{k}={v}", c)
        assert m == 1, k
    (d / "conf.properties").write_text(c)
    subprocess.run([JAVA, "-jar", str(GEN / "executable/text-generator.jar")], cwd=d, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = [w for ln in (d / "generate/generated_text.txt").read_text().splitlines()
         if ln.strip() and not ln.startswith("#") for w in ln.split()]
    assert len(t) >= n, f"{name} s{seed}: {len(t)} tokens"
    return name, seed, t[:n]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    lines, _, _, locked = P.E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    lens = [len(l) for l in vl]; N = sum(lens); vt = [w for l in vl for w in l]
    vtypes = len(set(vt)); lo, hi = vtypes * (1 - BAND), vtypes * (1 + BAND)
    log(f"Voynich tokens {N} types {vtypes} | band {lo:.0f}-{hi:.0f}")
    texts = {}
    for bid in sorted(d.name for d in P.BIB.iterdir() if d.is_dir() and d.name not in P.SKIP):
        texts["bible:" + bid] = P.tok(bid)
    for k, p in P.OTHER.items():
        texts["other:" + k] = P.clean_tokens(p)
    texts["other:latin_farming"] = P.farm_tokens()
    grid = list(GRID)
    if a.smoke:
        texts = {k: v for k, v in texts.items() if k in ("bible:hrv", "bible:slk", "bible:eng-kjv", "other:culpeper")}
        grid = ["err10_position", "random_morphhi"]
    R = {"meaningful": {}, "generator": {}}
    for k, t in texts.items():
        c = P.cut(t, N, rng)
        if c is None:
            log(f"skip {k} ({len(t)} tokens)"); continue
        m = P.measure(c, lens, rng); m["types"] = len(set(c)); R["meaningful"][k] = m
        log(f"{k:28s} types {m['types']:6d} Q3 {m[3]['Q']:.2f}")
    jobs = [(g, s, N) for g in grid for s in (GSEEDS[:1] if a.smoke else GSEEDS)]
    with ProcessPoolExecutor(4) as ex:
        gens = list(ex.map(generate, jobs))
    for name, seed, t in gens:
        m = P.measure(t, lens, rng); m["types"] = len(set(t)); m["setting"] = name
        R["generator"][f"{name}_s{seed}"] = m
        log(f"gen {name}_s{seed:<3d} types {m['types']:6d} Q3 {m[3]['Q']:.2f}")
    inb = lambda d: {k: v for k, v in d.items() if lo <= v["types"] <= hi}
    Ls, Gs = inb(R["meaningful"]), inb(R["generator"])
    lq = np.array([v[3]["Q"] for v in Ls.values()]); gq = np.array([v[3]["Q"] for v in Gs.values()])
    p10 = float(np.percentile(lq, 10)) if len(lq) else float("nan")
    lmin = float(lq.min()) if len(lq) else float("nan"); gmax = float(gq.max()) if len(gq) else float("nan")
    valid = len(Gs) >= 10 and len(Ls) >= 8 and p10 > gmax
    log(f"matched: L* {len(Ls)} {sorted(Ls)} | G* {len(Gs)} | L* p10 {p10:.3f} min {lmin:.3f} | G* max {gmax:.3f} | VALID {valid}")
    res = {"experiment": "E100", "seed": SEED, "N": N, "voynich_types": vtypes, "band": [lo, hi], "results": R,
           "L_star": sorted(Ls), "G_star": sorted(Gs), "p10": p10, "L_min": lmin, "G_max": gmax, "valid": bool(valid),
           "locked_test_excluded": locked}
    if not a.smoke:
        V = P.measure(vt, lens, rng); res["voynich"] = V
        q, sd = V[3]["Q"], V[3]["Q_sd"]
        log(f"VOYNICH Q3 {q:.3f} (RP {V[3]['RP']}, shuffle {V[3]['shuffle_mean']:.1f})")

        def verdict(q):
            if q >= p10 and q > gmax:
                return "PHRASES LIKE LANGUAGE"
            if q <= gmax and q < lmin:
                return "NO PHRASES (GENERATOR-LIKE)"
            return "BETWEEN"
        v = verdict(q) if valid else "VOID"
        if valid and min(abs(q - b) for b in (p10, gmax, lmin)) < 0.5 * sd:
            reps = [verdict(P.measure(vt, lens, random.Random(SEED + 100 + s))[3]["Q"]) for s in range(10)]
            res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "BETWEEN"
        net = {"PHRASES LIKE LANGUAGE": 1.0, "NO PHRASES (GENERATOR-LIKE)": 9.0}.get(v, 3.0)
        res.update(verdict=v, net_factor_M_now=net)
        log(f"VERDICT {v} | net M x {net:g} relative to the post-E099 ledger")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e100_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
