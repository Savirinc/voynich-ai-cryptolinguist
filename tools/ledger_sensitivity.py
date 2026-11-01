"""Sensitivity of the post-audit ledger to the judgement-call factors (publication step 2).
Base = E091 audited ledger; factors applied after it, as pre-registered (see reports/LEDGER.md)."""
import itertools
BASE = {"M": 0.4631, "L": 0.3604, "C": 0.0978, "O": 0.0788}
EDGES = {"E091 edge, M-favoured": {"M": 0.63, "L": 0.18, "C": 0.10, "O": 0.09},
         "E091 edge, L-favoured": {"M": 0.30, "L": 0.53, "C": 0.10, "O": 0.07}}
F = [("E097", "L", 0.943), ("E098", "C", 0.653), ("E104", "M", 3.0), ("E114", "M", 0.9), ("E116", "M", 3.0),
     ("E119", "M", 1.5), ("E120", "M", 0.9)]


def run(base, fs, power=1.0, cap3=None):
    p = dict(base)
    for _, h, f in fs:
        if cap3 is not None and f == 3.0:
            f = cap3
        p[h] *= f ** power
    t = sum(p.values())
    return {k: round(v / t, 3) for k, v in p.items()}


rows = [("As pre-registered", run(BASE, F)),
        ("Every factor halved in strength (f^0.5)", run(BASE, F, 0.5)),
        ("Every x3 replaced by x1.4 (E091's measured ratio for E066)", run(BASE, F, cap3=1.4)),
        ("Without E104", run(BASE, [x for x in F if x[0] != "E104"])),
        ("Without E116", run(BASE, [x for x in F if x[0] != "E116"])),
        ("Without E104 and E116", run(BASE, [x for x in F if x[0] not in ("E104", "E116")]))]
for name, b in EDGES.items():
    rows.append((f"Start at {name}", run(b, F)))
    rows.append((f"Start at {name}, factors halved", run(b, F, 0.5)))
for n, r in rows:
    print(f"| {n} | {r['M']} | {r['L']} | {r['C']} | {r['O']} |")
