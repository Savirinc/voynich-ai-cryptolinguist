"""Descriptive (Arham, 2026-10-27): the full front/middle/ending kit for Voynich, and how much of the script it writes.

Recipe fixed before running: all DEV prose word types (clean tokens, LOCKED_TEST excluded). Fronts are word beginnings
of 0-3 EVA letters, endings word endings of 0-4 letters, middles 0-6 letters; lists ranked as in E074 (fronts/endings by
number of word types, middles by number of types they complete). Kit sizes grow (front, middle, ending):
(10,30,20) (15,60,30) (20,120,40) (25,250,50) (30,500,60) (40,1000,80). At each size: share of running words and of word
types the kit writes. Then the words the largest kit cannot write are listed: they are what a complete kit would still
have to add. Also: every combination of the 10/30/20 kit is built and compared with the real vocabulary.
Run: .venv/bin/python experiments/kit_build_voynich.py
"""
from __future__ import annotations
import json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from e011_twin_search import voynich_lines
OUT = ROOT / "experiments/results/kit_build_voynich.json"
SIZES = [(10, 30, 20), (15, 60, 30), (20, 120, 40), (25, 250, 50), (30, 500, 60), (40, 1000, 80)]
FL, EL, ML = 3, 4, 6

def lists(types, wt, kF, kM, kE):
    fr, en = Counter(), Counter()
    for w in types:
        for k in range(1, FL + 1):
            if len(w) > k: fr[w[:k]] += 1
        for k in range(1, EL + 1):
            if len(w) > k: en[w[-k:]] += 1
    F = [""] + [p for p, _ in fr.most_common(kF - 1)]
    E = [""] + [p for p, _ in en.most_common(kE - 1)]
    mid = Counter()
    for w in types:
        seen = set()
        for f in F:
            if not w.startswith(f): continue
            for e in E:
                if len(f) + len(e) > len(w) or (e and not w.endswith(e)): continue
                m = w[len(f):len(w) - len(e)]
                if 0 < len(m) <= ML: seen.add(m)
        for m in seen: mid[m] += 1
    return F, [""] + [m for m, _ in mid.most_common(kM)], E

def split(w, F, Ms, E):
    best = None
    for f in sorted(F, key=len, reverse=True):
        if not w.startswith(f): continue
        for e in sorted(E, key=len, reverse=True):
            if len(f) + len(e) > len(w) or (e and not w.endswith(e)): continue
            m = w[len(f):len(w) - len(e)]
            if m in Ms:
                return (f, m, e)
    return best

lines, _, _, locked = voynich_lines()
toks = [w for l in lines for w in l if w]
F_ = Counter(toks); types = sorted(F_); N = len(toks)
res = {"tokens": N, "types": len(types), "locked_test_excluded": locked, "sizes": {}}
for kF, kM, kE in SIZES:
    F, M, E = lists(types, F_, kF, kM, kE); Ms = set(M)
    sp = {w: split(w, F, Ms, E) for w in types}
    tc = sum(F_[w] for w in types if sp[w]) / N; yc = sum(1 for w in types if sp[w]) / len(types)
    key = f"{kF}/{kM}/{kE}"
    res["sizes"][key] = {"pieces": len(F) + len(M) + len(E) - 3, "token_cov": tc, "type_cov": yc,
                         "front": F, "middle": M, "ending": E}
    print(f"{key:12s} pieces {len(F)+len(M)+len(E)-3:5d}  running text {tc:.3f}  vocabulary {yc:.3f}")
    last = (F, M, E, sp)
F, M, E, sp = last
miss = sorted((w for w in types if not sp[w]), key=lambda w: -F_[w])
res["unwritten"] = {"types": len(miss), "tokens": sum(F_[w] for w in miss), "top": [(w, F_[w]) for w in miss[:60]],
                    "hapax_share": sum(F_[w] == 1 for w in miss) / max(1, len(miss)),
                    "length": Counter(len(w) for w in miss).most_common(), "with_rare_glyph": sum(any(c in "gjbuvxz" for c in w) for w in miss)}
print("unwritten by largest kit:", res["unwritten"]["types"], "types,", res["unwritten"]["tokens"], "tokens; hapax share",
      round(res["unwritten"]["hapax_share"], 2), "| top", res["unwritten"]["top"][:25])
# complete kit: add each unwritten word's leftover middle (after the longest front/ending in the kit) to the middle list
extra = Counter()
for w in miss:
    f = max((x for x in F if w.startswith(x)), key=len); rest = w[len(f):]
    e = max((x for x in E if rest.endswith(x) and len(x) < len(rest)), key=len, default="")
    extra[rest[:len(rest) - len(e)]] += 1
res["complete_kit"] = {"front": len(F) - 1, "middle": len(M) - 1 + len(extra), "ending": len(E) - 1, "extra_middles": len(extra),
                       "extra_examples": extra.most_common(20)}
print("complete kit (writes 100%):", res["complete_kit"]["front"], "fronts,", res["complete_kit"]["middle"], "middles,",
      res["complete_kit"]["ending"], "endings; extra middles needed", len(extra), extra.most_common(12))
# build every word of the small kit
F0, M0, E0 = (res["sizes"]["10/30/20"][k] for k in ("front", "middle", "ending"))
built = {f + m + e for f in F0 for m in M0 for e in E0}
real = built & set(types)
res["small_kit_built"] = {"combinations": len(F0) * len(M0) * len(E0), "distinct": len(built), "real": len(real),
                          "real_tokens": sum(F_[w] for w in real) / N,
                          "never_seen_examples": sorted(built - set(types), key=lambda w: (len(w), w))[:40]}
print("small kit builds", len(built), "distinct strings;", len(real), "are real words, covering", round(res["small_kit_built"]["real_tokens"], 3), "of the text")
# grid: for middle 'k' (and 't'), fronts x endings with counts
grids = {}
for mid in ("k", "t", "ke", "ch"):
    grids[mid] = {f or "-": {e or "-": F_.get(f + mid + e, 0) for e in E0} for f in F0}
res["grids"] = grids
OUT.write_text(json.dumps(res, indent=1))
