"""E091 (approach check 2): ledger audit. See reports/E091_PREREG.md. Pure arithmetic on the ledger's factors.

Recomputes the ledger exactly (R0: no intermediate rounding) from the starting point with every factor still in force,
reports the drift from the current written values, then applies the four pre-registered audit rules one at a time and together, from the point values and from
the two range-edge starting points used since E030.
Run: .venv/bin/python experiments/e091_ledger_audit.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/results/e091.json"
STARTS = {"point": (0.45, 0.30, 0.20, 0.05), "edge_M_high": (0.60, 0.15, 0.20, 0.05), "edge_L_high": (0.30, 0.45, 0.20, 0.05)}
CURRENT = (0.0887, 0.8824, 0.0254, 0.0035)
# (entry, M, L, C) factors in force, after withdrawals (E031 by E064, E035 by E035b) and the E090 correction
FACTORS = [
    ("E030", 1, 3, 1), ("E032", 1 / 3, 1, 1), ("E036", 1, 10, 3),
    ("E049-E050", 1, 0.9428, 0.9533), ("E052", 1, 0.9329, 1), ("E053", 1, 0.9755, 1), ("E062", 1, 1, 1 / 3),
    ("E063", 1, 0.965, 0.9767), ("E065", 1, 0.921, 1), ("E066", 3, 1, 1), ("E067", 3, 1, 1), ("E068", 1 / 3, 1, 1),
    ("E085", 1.4, 1, 1),
]
# R1 superseded basis: earlier factor withdrawn, later one kept (precedent: E064 withdrew E031)
R1_WITHDRAW = {"E030": "doubling languages explain Voynich's back-to-back repeats; E066 (and E064 Part C) show Voynich repeats "
                       "family-level, unlike the doubling languages, which repeat word-specifically",
               "E036": "Indonesian + free invented spellings reproduces Voynich word features; E066 shows Indonesian's repeats "
                       "are word-specific (+4.8) where Voynich's are not (-1.2); E067/E068 show human gibberish also makes "
                       "the one-off richness and near-copies E036 credited to invention"}
# R2 overlap: same-direction factors on the same Voynich measurement -> keep the larger only (candidate list)
R2_GROUPS = []          # none found when the candidate list was drawn up; stated in the prereg
# R3 measured ratio replaces pre-registered ratio where the test itself reported one
R3_REPLACE = {"E066": (1.4, 1, 1)}
# R4 within-L shares after E090 (searched-language share of L-alpha-known 0.946, of L-abbrev 0.35; m 0.2 -> 0.533)
FORMS = {"unattested": 0.35, "syll": 0.21, "abbrev": 0.12, "other": 0.17, "alpha_known": 0.15}
R4_MULT = {"alpha_known": (0.054 + 0.946 * 0.533) / (0.054 + 0.946 * 0.2), "abbrev": (0.65 + 0.35 * 0.533) / (0.65 + 0.35 * 0.2)}


def run(start, factors):
    v = list(start)
    for _, fm, fl, fc in factors:
        v = [v[0] * fm, v[1] * fl, v[2] * fc, v[3]]
    s = sum(v)
    return [round(x / s, 4) for x in v]


def apply(rules):
    f = list(FACTORS)
    if "R1" in rules:
        f = [x for x in f if x[0] not in R1_WITHDRAW]
    if "R3" in rules:
        f = [(e, *R3_REPLACE[e]) if e in R3_REPLACE else (e, m, l, c) for e, m, l, c in f]
    return f


def main():
    repro = run(STARTS["point"], FACTORS)
    ok = all(abs(a - b) <= 0.002 for a, b in zip(repro, CURRENT))
    print("R0 exact recomputation:", repro, "vs written", CURRENT, "within 0.002" if ok else "ROUNDING DRIFT")
    table = {}
    for name, rules in (("R0 exact", ()), ("R1 only", ("R1",)), ("R3 only", ("R3",)), ("R1+R2+R3", ("R1", "R3"))):
        table[name] = {k: run(s, apply(rules)) for k, s in STARTS.items()}
        print(f"{name:10s}", "  ".join(f"{k}: M {v[0]:.4f} L {v[1]:.4f} C {v[2]:.4f} O {v[3]:.4f}" for k, v in table[name].items()))
    forms = {k: v * R4_MULT.get(k, 1) for k, v in FORMS.items()}
    s = sum(forms.values()); forms = {k: round(v / s, 3) for k, v in forms.items()}
    print("R4 forms of L:", forms)
    fin = table["R1+R2+R3"]
    lead = {k: ("M" if v[0] > v[1] else "L") for k, v in fin.items()}
    verdict = "AUDITED: " + ", ".join(f"{k} {lead[k]} leads" for k in fin)
    print("VERDICT", verdict)
    OUT.write_text(json.dumps({"experiment": "E091", "reproduced": repro, "reproduces": ok, "table": table, "forms_of_L": forms,
                               "R1": R1_WITHDRAW, "R2": R2_GROUPS, "R3": {k: v for k, v in R3_REPLACE.items()},
                               "verdict": verdict}, indent=1))


if __name__ == "__main__":
    main()
