"""Independent re-implementation of the key structural effects (no sklearn, no legacy code).

Effects:
  * y->q : P(word is q-initial | previous word in the same line ends in 'y').
  * q->o : share of q-initial words whose 2nd glyph is 'o'.
  * line-final m : odds that an m-final word is line-final vs an iin-final word.
Each is reported as an odds ratio with a leaf-cluster bootstrap 95% CI and, for
held-out validity, as per-fold odds ratios on leaves not used to define anything.
These are descriptive statistics of the glyph stream; they carry no semantic claim.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict


def lines_of(tokens, mode="prose", clean_only=True, exclude_leaves=()):
    """Group tokens into lines; when clean_only, unclean tokens become None placeholders
    so adjacency is never bridged across an unreadable word."""
    out = defaultdict(list)
    for t in tokens:
        if t.mode != mode or t.leaf in exclude_leaves:
            continue
        out[(t.folio, t.line_no)].append(t if (t.is_clean or not clean_only) else None)
    return out


def _or(a, b, c, d):
    """Haldane-corrected odds ratio for table [[a,b],[c,d]]."""
    return ((a + .5) * (d + .5)) / ((b + .5) * (c + .5))


def yq_table(lines):
    """Returns per-leaf counts: [prev_y&q, prev_y&notq, notprev_y&q, notprev_y&notq]."""
    per = defaultdict(lambda: [0, 0, 0, 0])
    for (_, _), ws in lines.items():
        for prev, cur in zip(ws, ws[1:]):
            if prev is None or cur is None:
                continue
            y, q = prev.eva.endswith("y"), cur.eva.startswith("q")
            per[cur.leaf][(0 if y else 2) + (0 if q else 1)] += 1
    return per


def m_table(lines):
    """Per-leaf counts: [m-final&line-final, m-final&not, iin-final&line-final, iin-final&not]."""
    per = defaultdict(lambda: [0, 0, 0, 0])
    for (_, _), ws in lines.items():
        n = len(ws)
        for i, w in enumerate(ws):
            if w is None:
                continue
            if w.eva.endswith("m"):
                row = 0
            elif w.eva.endswith("iin"):
                row = 2
            else:
                continue
            last = i == n - 1
            per[w.leaf][row + (0 if last else 1)] += 1
    return per


def qo_share(lines):
    q = qo = 0
    for ws in lines.values():
        for w in ws:
            if w is not None and w.eva.startswith("q"):
                q += 1
                qo += w.eva[1:2] == "o"
    return qo, q


def pooled_or(per, leaves=None):
    tot = [0, 0, 0, 0]
    for leaf, c in per.items():
        if leaves is None or leaf in leaves:
            tot = [x + y for x, y in zip(tot, c)]
    return _or(*tot), tot


def bootstrap_ci(per, n=2000, seed=0):
    rng = random.Random(seed)
    leaves = list(per)
    vals = []
    for _ in range(n):
        tot = [0, 0, 0, 0]
        for leaf in (rng.choice(leaves) for _ in leaves):
            tot = [x + y for x, y in zip(tot, per[leaf])]
        vals.append(math.log(_or(*tot)))
    vals.sort()
    return math.exp(vals[int(.025 * n)]), math.exp(vals[int(.975 * n)])


def effect_report(tokens, folds: dict[str, int], exclude_leaves=(), seed=0):
    lines = lines_of(tokens, exclude_leaves=set(exclude_leaves))
    rep = {}
    for name, fn in [("y_to_q", yq_table), ("line_final_m_vs_iin", m_table)]:
        per = fn(lines)
        or_, tot = pooled_or(per)
        lo, hi = bootstrap_ci(per, seed=seed)
        k = max(folds.values()) + 1
        fold_or = [round(pooled_or(per, {l for l, f in folds.items() if f == i})[0], 3) for i in range(k)]
        rep[name] = {"odds_ratio": round(or_, 3), "ci95_leaf_bootstrap": [round(lo, 3), round(hi, 3)],
                     "table": tot, "per_fold_odds_ratio": fold_or}
    qo, q = qo_share(lines)
    rep["q_followed_by_o"] = {"qo": qo, "q": q, "share": round(qo / q, 4)}
    return rep
