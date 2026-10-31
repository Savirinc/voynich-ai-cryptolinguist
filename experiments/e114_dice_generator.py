"""E114 (Arham, Reddit R10): can a dice word generator (one roll per slot, no copying) make the Voynich's fingerprint?
See reports/E114_PREREG.md. Yardstick: E032's 13 features, judged as in E098.

A word = front + middle + ending, each slot chosen by a dice roll from a table. Tables are filled from master piece
lists taken from the target itself (generous to M), weighted by how often the target uses each piece.
Dice: d6 (6 entries, uniform), 2d6 (11 entries, triangular, sum 2..12), d66 (36 cells, two dice as row/column,
cells shared out by piece weight). Tables are re-filled every k lines, every page, or never.
Run: caffeinate -ims .venv/bin/python experiments/e114_dice_generator.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e086_spaces_and_lines as E86  # noqa: E402
import e093_explanation_model as E93  # noqa: E402
from e032_copy_generator import FEATS, Z_OK, features  # noqa: E402
from e074_slot_coverage import lists  # noqa: E402
from e098_cipher_classes import generator_target, judge, pour  # noqa: E402

SEED = 114114
OUT = ROOT / "experiments/results/e114.json"
SEEDS, CHECK_SEEDS = list(range(1, 11)), list(range(11, 21))
DICE = ["d6", "2d6", "d66"]
REFILL = ["book", "page", 64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1]   # lines between re-fills
MASTER = [(8, 24, 16), (10, 30, 20), (13, 39, 26), (17, 51, 34), (20, 60, 40), (25, 75, 50)]   # front / middle / ending list sizes (E074 scale)
GRID = [(d, r, m) for d in DICE for r in REFILL for m in MASTER]
PLANT, PLANT_SEED = ("d66", 10, (15, 45, 30)), 777
SHARE = 0.15                                               # share of M for dice/table generators, fixed in the prereg
TWO_D6 = [min(s - 1, 13 - s) for s in range(2, 13)]        # 1,2,3,4,5,6,5,4,3,2,1


def log(*a):
    print(*a, flush=True)


def masters(pages, size):
    """master piece lists from the target and token-level weights from a longest-front, longest-ending parse"""
    toks = [w for p in pages for l in p for w in l]
    F, M, E = lists(sorted(set(toks)), *size)
    Fs, Ms, Es = sorted(F, key=len, reverse=True), set(M), sorted(E, key=len, reverse=True)
    wf, wm, we, n_ok = Counter(), Counter(), Counter(), 0
    cache = {}
    for w in toks:
        if w not in cache:
            cache[w] = None
            for f in Fs:
                if w.startswith(f):
                    for e in Es:
                        if len(f) + len(e) <= len(w) and (not e or w.endswith(e)) and w[len(f):len(w) - len(e)] in Ms:
                            cache[w] = (f, w[len(f):len(w) - len(e)], e); break
                if cache[w]:
                    break
        if cache[w]:
            f, m, e = cache[w]; wf[f] += 1; wm[m] += 1; we[e] += 1; n_ok += 1
    rank = lambda P, W: [(p, W[p]) for p in sorted(P, key=lambda p: (-W[p], p)) if W[p] > 0]
    return {"F": rank(F, wf), "M": rank(M, wm), "E": rank(E, we), "written_share": n_ok / len(toks)}


def fill(master, dice, rng):
    """one table for one slot: list of (piece, roll weight)"""
    pieces, w = [p for p, _ in master], np.array([c for _, c in master], float)
    if dice == "d66":
        cells = rng.choices(pieces, weights=w, k=36)
        return list(Counter(cells).items())
    k = 6 if dice == "d6" else 11
    k = min(k, len(pieces))
    picked, avail, aw = [], list(pieces), list(w)
    for _ in range(k):                                      # weighted draw without replacement
        i = rng.choices(range(len(avail)), weights=aw, k=1)[0]
        picked.append(avail.pop(i)); aw.pop(i)
    if dice == "d6":
        return [(p, 1.0) for p in picked]
    order = sorted(range(11), key=lambda s: -TWO_D6[s])     # first drawn piece sits on 7, the likeliest sum
    return [(picked[j], float(TWO_D6[order[j]])) for j in range(k)]


def book(setting, ms, shape, seed):
    dice, refill, _ = setting
    rng = random.Random(SEED * 1000 + seed)
    tabs, out, since = None, [], 0
    for lens in shape:
        page = []
        if refill == "page":
            tabs = None
        for L in lens:
            if tabs is None or (isinstance(refill, int) and since >= refill):
                tabs = [fill(ms[s], dice, rng) for s in ("F", "M", "E")]; since = 0
            line = []
            while len(line) < L:
                w = "".join(rng.choices([p for p, _ in t], weights=[x for _, x in t], k=1)[0] for t in tabs)
                if w:                                       # an empty word is re-rolled
                    line.append(w)
            page.append(line); since += 1
        out.append(page)
    return out


_T = {}


def init(T):
    _T.update(T)


def task(a):
    tname, setting, seed = a
    shape, ms = _T[tname]["shape"], _T[tname]["ms"][setting[2]]
    pages = book(setting, ms, shape, seed)
    f = features([l for p in pages for l in p if l], SEED + seed)
    if seed in (1, 11):
        f["lines_z"] = E86.continuity(pages, random.Random(E86.SEED))["z"]
    if seed == 1:
        f["sample"] = [" ".join(l) for l in pages[0][:3]]
    return a, f


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    global SEEDS, GRID
    vpages, _, locked = E93.voynich()
    shape = [[len(l) for l in p] for p in vpages]
    log(f"Voynich DEV pages {len(vpages)}, tokens {sum(map(sum, shape))}")
    targets = {"generator": generator_target(shape)}
    vms = {m: masters(vpages, m) for m in MASTER + [PLANT[2]]}
    targets["plant"] = book(PLANT, vms[PLANT[2]], shape, PLANT_SEED)
    if a.smoke:
        SEEDS = [1, 2, 3]
        GRID = [g for g in GRID if g[1] in ("book", "page", 12, 8, 2) and g[0] != "d6"]
    else:
        targets["VOYNICH"] = vpages
    T = {t: {"shape": shape, "ms": {m: (vms[m] if t == "VOYNICH" else masters(pp, m)) for m in MASTER}} for t, pp in targets.items()}
    for t in T:
        log(f"{t}: written share " + " ".join(f"{m} {T[t]['ms'][m]['written_share']:.3f}" for m in MASTER))
    V = {t: features([l for p in pp for l in p if l], SEED) for t, pp in targets.items()}
    for t in V:
        log(f"target {t:10s} " + " ".join(f"{k} {V[t][k]:.3g}" for k in FEATS))
    jobs = [(t, g, sd) for t in T for g in GRID for sd in SEEDS]
    log(f"jobs {len(jobs)} | {time.time() - t0:.0f}s")
    res = {"experiment": "E114", "seed": SEED, "targets": V, "locked_test_excluded": locked,
           "voynich_masters": {str(m): vms[m] for m in MASTER}}
    with Pool(a.workers, initializer=init, initargs=(T,)) as pool:
        rows = pool.map(task, jobs, chunksize=2)
        R = {}
        for (t, g, sd), f in rows:
            R.setdefault((t, g), []).append(f)
        J = {k: judge(V[k[0]], v) for k, v in R.items()}
        log(f"main pass done | {time.time() - t0:.0f}s")
        best = lambda t: min((k for k in J if k[0] == t), key=lambda k: (J[k]["n_fail"], str(k[1])))
        bp, bg = best("plant"), best("generator")
        res["plant_best"] = [str(bp[1]), J[bp]["n_fail"], J[bp]["fail"]]
        res["generator_best"] = [str(bg[1]), J[bg]["n_fail"], J[bg]["fail"]]
        res["valid"] = J[bp]["n_fail"] <= 1 and J[bg]["n_fail"] >= 2
        log(f"valid {res['valid']} plant {res['plant_best']} generator {res['generator_best']}")
        res["all_sets"] = {f"{k[0]}|{k[1]}": [J[k]["n_fail"], J[k]["fail"]] for k in J}
        if "VOYNICH" in T:
            bv = best("VOYNICH"); nf = J[bv]["n_fail"]
            res["voynich_best"] = [str(bv[1]), nf, J[bv]["fail"], J[bv]["z"]]
            res["voynich_best_mean"] = J[bv]["mean"]
            res["voynich_best_lines_z"] = [f.get("lines_z") for f in R[bv] if "lines_z" in f]
            res["voynich_sample"] = next((f["sample"] for f in R[bv] if "sample" in f), None)
            raw = "REPRODUCES" if nf <= 1 else ("CLASS FAILS" if nf >= 5 else "PARTIAL")
            res["raw"] = raw
            log(f"VOYNICH best {bv[1]} fails {nf} {J[bv]['fail']} -> {raw}")
            log("z " + " ".join(f"{k} {J[bv]['z'][k]:+.1f}" for k in FEATS))
            if res["valid"] and raw != "PARTIAL":
                cr = pool.map(task, [("VOYNICH", bv[1], sd) for sd in CHECK_SEEDS])
                jc = judge(V["VOYNICH"], [f for _, f in cr])
                res["seed_check"] = [jc["n_fail"], jc["fail"]]
                log(f"seed check fails {jc['n_fail']} {jc['fail']}")
    if "VOYNICH" in T:
        if not res["valid"]:
            v, f = "VOID", 1.0
        elif res["raw"] == "PARTIAL":
            v, f = "PARTIAL", 1.0
        else:
            nf = res["seed_check"][0]
            same = (nf <= 1) if res["raw"] == "REPRODUCES" else (nf >= 5)
            v, f = (res["raw"], 3.0 if res["raw"] == "REPRODUCES" else 1 / 3) if same else ("PARTIAL", 1.0)
        res["verdict"], res["share_factor"] = v, f
        res["M_factor"] = 1 + SHARE * (f - 1)
        log(f"VERDICT {v} | M x {res['M_factor']:.4f}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e114_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
