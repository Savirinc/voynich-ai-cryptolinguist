"""E039 (attack step 1c): are the d+-, q+- (and other) alternations SCRIBE habits or LOCATION/topic habits?
See reports/E039_PREREG.md.

Tokens: Voynich DEV prose, clean, hand != '@' (unassigned). For each alternation (E038's minimal pairs, both forms
>= 5 tokens), every token of a pair word gets: pair id p, form f (1 = the longer / q / k / l / ee form, 0 = the other),
hand h (Davis's scribes as given in ZL), quire q.
Statistics (bits; excess = observed - mean of permutations that shuffle f within the conditioning cells; 500 perms):
  E_hand        I(f; h | p)
  E_hand_loc    I(f; h | p, q)        hand effect inside the same quire   (only mixed quires contribute)
  E_loc_hand    I(f; q | p, h)        location effect inside the same hand
  each also as a share of H(f | p); one-sided permutation p-values.
Verdict per alternation (alpha 0.01):
  SCRIBE HABIT       E_hand_loc significant, E_loc_hand not
  LOCATION HABIT     E_loc_hand significant, E_hand_loc not
  BOTH               both significant
  ENTANGLED          neither conditional significant but E_hand significant (hand and location coincide)
  NO PATTERN         none significant
Controls (labels planted on the e/ee pair tokens; must give the expected verdict, else VOID):
  planted scribe     f = 1 for hand 1 tokens, 0 otherwise, each flipped with probability 0.1  -> SCRIBE HABIT
  planted location   f = 1 in quires D-H, 0 otherwise, each flipped with probability 0.1      -> LOCATION HABIT
Run: caffeinate -ims .venv/bin/python experiments/e039_scribe_habits.py
"""
from __future__ import annotations

import json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e038_sign_inventory_v2 import ALTS, keep  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED, PERMS, ALPHA = 39039, 500, 0.01
OUT = ROOT / "experiments/results/e039.json"
LOC_SET = set("DEFGH")


def H(c):
    t = sum(c.values())
    return -sum(v / t * math.log2(v / t) for v in c.values() if v)


def cmi(f, x, z):
    """I(f; x | z) in bits."""
    return H(Counter(zip(f, z))) + H(Counter(zip(x, z))) - H(Counter(zip(f, x, z))) - H(Counter(z))


def perm_within(f, cells, rng):
    idx = defaultdict(list)
    for i, c in enumerate(cells):
        idx[c].append(i)
    g = list(f)
    for ii in idx.values():
        vals = [f[i] for i in ii]; rng.shuffle(vals)
        for i, v in zip(ii, vals):
            g[i] = v
    return g


def stat(f, x, z, cells, rng):
    obs = cmi(f, x, z)
    null = [cmi(perm_within(f, cells, rng), x, z) for _ in range(PERMS)]
    return {"obs": obs, "excess": obs - float(np.mean(null)),
            "p": (1 + sum(n >= obs for n in null)) / (PERMS + 1)}


def analyse(T, rng):
    f = [t["f"] for t in T]; p = [t["p"] for t in T]; h = [t["h"] for t in T]; q = [t["q"] for t in T]
    ph, pq = list(zip(p, h)), list(zip(p, q))
    hf = H(Counter(zip(f, p))) - H(Counter(p))
    r = {"tokens": len(T), "H_f_given_p": hf,
         "E_hand": stat(f, h, p, p, rng),
         "E_hand_loc": stat(f, h, pq, pq, rng),
         "E_loc_hand": stat(f, q, ph, ph, rng)}
    for k in ("E_hand", "E_hand_loc", "E_loc_hand"):
        r[k]["share"] = r[k]["excess"] / hf if hf else float("nan")
    s = {k: r[k]["p"] < ALPHA for k in ("E_hand", "E_hand_loc", "E_loc_hand")}
    if s["E_hand_loc"] and not s["E_loc_hand"]:
        v = "SCRIBE HABIT"
    elif s["E_loc_hand"] and not s["E_hand_loc"]:
        v = "LOCATION HABIT"
    elif s["E_hand_loc"] and s["E_loc_hand"]:
        v = "BOTH"
    elif s["E_hand"]:
        v = "ENTANGLED"
    else:
        v = "NO PATTERN"
    r["verdict"] = v
    # with-form share by hand, pair-weighted (each pair counts once)
    by = defaultdict(list)
    for pid in set(p):
        sub = [t for t in T if t["p"] == pid]
        for hh in set(t["h"] for t in sub):
            ss = [t["f"] for t in sub if t["h"] == hh]
            if len(ss) >= 3:
                by[hh].append(float(np.mean(ss)))
    r["with_share_by_hand"] = {hh: [round(float(np.mean(v_)), 3), len(v_)] for hh, v_ in sorted(by.items())}
    return r


def main():
    rng = random.Random(SEED)
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    D = [t for t in toks if t.mode == "prose" and t.leaf not in locked and t.is_clean and t.hand != "@"]
    wc = Counter(t.eva for t in D)
    res = {"hands": dict(Counter(t.hand for t in D)), "alternations": {}}
    pair_sets = {}
    for name, fn in ALTS.items():
        pairs = keep(fn(wc), wc)
        # a word in several pairs of the same alternation is kept in its first (sorted) pair only
        role, used = {}, set()
        for i, (a, b) in enumerate(pairs):
            if a in used or b in used:
                continue
            used |= {a, b}; role[a] = (i, 0); role[b] = (i, 1)
        pair_sets[name] = role
        T = [{"p": role[t.eva][0], "f": role[t.eva][1], "h": t.hand, "q": t.quire} for t in D if t.eva in role]
        r = analyse(T, rng); r["n_pairs"] = len(set(x["p"] for x in T))
        res["alternations"][name] = r
        print(f"{name:5s} pairs {r['n_pairs']:3d} tokens {r['tokens']:5d} | E_hand {r['E_hand']['share']:.3f} p {r['E_hand']['p']:.3f}"
              f" | hand|loc {r['E_hand_loc']['share']:.3f} p {r['E_hand_loc']['p']:.3f}"
              f" | loc|hand {r['E_loc_hand']['share']:.3f} p {r['E_loc_hand']['p']:.3f} -> {r['verdict']}"
              f" | with-share by hand {r['with_share_by_hand']}", flush=True)
    # controls on the e/ee pair tokens
    role = pair_sets["e/ee"]
    base = [{"p": role[t.eva][0], "h": t.hand, "q": t.quire} for t in D if t.eva in role]
    flip = lambda v: 1 - v if rng.random() < 0.1 else v
    cs = [dict(x, f=flip(int(x["h"] == "1"))) for x in base]
    cl = [dict(x, f=flip(int(x["q"] in LOC_SET))) for x in base]
    rs, rl = analyse(cs, rng), analyse(cl, rng)
    ok = rs["verdict"] == "SCRIBE HABIT" and rl["verdict"] == "LOCATION HABIT"
    res["controls"] = {"planted_scribe": rs, "planted_location": rl, "pass": ok}
    print(f"control scribe -> {rs['verdict']} | control location -> {rl['verdict']} | pass {ok}")
    res["status"] = "VALID" if ok else "VOID"
    res["locked_test_excluded"] = sorted(locked)
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
