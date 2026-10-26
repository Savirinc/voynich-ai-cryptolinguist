"""Label-class programme, step 0 (descriptive, no ledger score): where do o-tall-letter words sit in prose lines?

Recipe fixed before any result was seen (2026-10-26):
  Data: DEV prose lines (LOCKED_TEST leaves excluded), ZL 3b; positions use every token in a line, identities use clean
  tokens only. Three target sets of word types:
    OG   = every clean prose type matching ^o[tkpf] (o + gallows, the "o-tall-letter" class);
    ZL   = DEV zodiac label types (mode label, illustration Z) matching ^o[tkpf], as they occur in prose;
    SH   = label types occurring both as pharma (P) labels and zodiac (Z) labels in DEV, as they occur in prose.
  Measures per set, over prose tokens of those types: share line-initial, line-final, paragraph-initial, mean relative
  position idx/(n-1); previous-word -y share; previous-word concentration = mean over types with >= 10 interior tokens
  of (1 - normalised entropy of the previous-word distribution).
  Control: 500 draws; each target type replaced by a random non-target type from the same log2 prose-frequency bin;
  same measures; 2.5/97.5 percentiles.
  Reading rule: LINE-INITIAL if target line-initial share > control p97.5 + 5 points; NEIGHBOURS if previous-word
  concentration > control p97.5; EVEN otherwise. Reported for ALL and Currier A / B.
Run: .venv/bin/python experiments/label_step0_line_position.py
"""
from __future__ import annotations
import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse
from vcl.corpus.splits import locked_test_leaves

OG = re.compile(r"^o[tkpf]")
OUT = ROOT / "experiments/results/label_step0_line_position.json"
rng = random.Random(710)

_, toks = parse()
locked = set(locked_test_leaves(toks))
dev = [t for t in toks if t.leaf not in locked]
lines = defaultdict(list)
for t in dev:
    if t.mode == "prose":
        lines[(t.folio, t.line_no)].append(t)
# token records: (word or None, idx, n, para_start, currier, prev_word)
recs = []
for k, L in lines.items():
    L = sorted(L, key=lambda t: t.idx); n = len(L)
    for i, t in enumerate(L):
        w = t.eva if t.is_clean else None
        prev = L[i - 1].eva if i > 0 and L[i - 1].is_clean else None
        recs.append(dict(w=w, i=i, n=n, ps=t.para_start, cur=t.currier, prev=prev))
freq = Counter(r["w"] for r in recs if r["w"])
zl = {t.eva for t in dev if t.mode == "label" and t.illustration == "Z" and t.is_clean}
pl = {t.eva for t in dev if t.mode == "label" and t.illustration == "P" and t.is_clean}
sets = {"OG": {w for w in freq if OG.match(w)},
        "ZL": {w for w in zl if OG.match(w) and w in freq},
        "SH": {w for w in zl & pl if w in freq}}
bins = defaultdict(list)
for w, c in freq.items():
    bins[int(math.log2(c))].append(w)

def measures(types, sub):
    R = [r for r in sub if r["w"] in types]
    if not R:
        return None
    N = len(R)
    m = {"tokens": N, "types": len(types & {r["w"] for r in R}),
         "line_initial": sum(r["i"] == 0 for r in R) / N,
         "line_final": sum(r["i"] == r["n"] - 1 for r in R) / N,
         "para_initial": sum(r["i"] == 0 and r["ps"] for r in R) / N,
         "rel_pos": float(np.mean([r["i"] / (r["n"] - 1) for r in R if r["n"] > 1]))}
    inner = [r for r in R if r["i"] > 0 and r["prev"]]
    m["prev_y"] = sum(r["prev"].endswith("y") for r in inner) / max(1, len(inner))
    conc = []
    by = defaultdict(list)
    for r in inner:
        by[r["w"]].append(r["prev"])
    for w, ps in by.items():
        if len(ps) >= 10:
            c = Counter(ps); tot = len(ps)
            H = -sum(v / tot * math.log2(v / tot) for v in c.values())
            conc.append(1 - H / math.log2(tot))
    m["prev_conc"] = float(np.mean(conc)) if conc else float("nan")
    m["n_conc_types"] = len(conc)
    return m

def control(types, sub, draws=500):
    tl = sorted(types)
    out = defaultdict(list)
    for _ in range(draws):
        rep = set()
        for w in tl:
            pool = [x for x in bins[int(math.log2(freq[w]))] if x not in types]
            rep.add(rng.choice(pool))
        m = measures(rep, sub)
        for k, v in m.items():
            out[k].append(v)
    return {k: {"mean": float(np.nanmean(v)), "p2.5": float(np.nanpercentile(v, 2.5)), "p97.5": float(np.nanpercentile(v, 97.5))}
            for k, v in out.items()}

res = {"locked_test_excluded": sorted(locked, key=lambda x: (len(x), x)), "sets": {k: sorted(v) for k, v in sets.items()}, "results": {}}
for name, types in sets.items():
    for scope, sub in (("ALL", recs), ("A", [r for r in recs if r["cur"] == "A"]), ("B", [r for r in recs if r["cur"] == "B"])):
        v = measures(types, sub); c = control(types, sub)
        if v is None:
            continue
        verdict = ("LINE-INITIAL" if v["line_initial"] > c["line_initial"]["p97.5"] + 0.05 else
                   "NEIGHBOURS" if v["prev_conc"] > c["prev_conc"]["p97.5"] else "EVEN")
        res["results"][f"{name}_{scope}"] = {"voynich": v, "control": c, "reading": verdict}
        print(f"{name} {scope:3s} types {v['types']:4d} tokens {v['tokens']:5d} | line-initial {v['line_initial']:.3f} (ctrl {c['line_initial']['mean']:.3f} [{c['line_initial']['p2.5']:.3f},{c['line_initial']['p97.5']:.3f}]) "
              f"| final {v['line_final']:.3f} (ctrl {c['line_final']['mean']:.3f}) | para-init {v['para_initial']:.3f} (ctrl {c['para_initial']['mean']:.3f}) "
              f"| relpos {v['rel_pos']:.3f} (ctrl {c['rel_pos']['mean']:.3f}) | prev-y {v['prev_y']:.3f} (ctrl {c['prev_y']['mean']:.3f}) "
              f"| prev-conc {v['prev_conc']:.3f} n{v['n_conc_types']} (ctrl {c['prev_conc']['mean']:.3f} [{c['prev_conc']['p2.5']:.3f},{c['prev_conc']['p97.5']:.3f}]) -> {verdict}")
# per-type detail for the shared set
det = {}
for w in sets["SH"]:
    R = [r for r in recs if r["w"] == w]
    det[w] = {"n": len(R), "line_initial": round(sum(r["i"] == 0 for r in R) / len(R), 3),
              "top_prev": Counter(r["prev"] for r in R if r["i"] > 0 and r["prev"]).most_common(3)}
res["shared_detail"] = det
OUT.write_text(json.dumps(res, indent=1))
print("sets:", {k: len(v) for k, v in sets.items()})
