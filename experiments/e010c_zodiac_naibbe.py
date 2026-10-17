"""E010C: are the zodiac month names written in Naibbe (Greshko's published tables) in their own pages' ring text?

Pre-registered in reports/E010C_PREREG.md (sha256 recorded in the output; read-only). Implements exactly that plan:
primary own-vs-other-month permutation test, descriptive run listing and chance rates on non-zodiac DEV text, and a
positive control (inserted true encryptions) plus a false-positive control (inserted wrong months).

Run: .venv/bin/python experiments/e010c_zodiac_naibbe.py
"""
import hashlib, json, random, sys, time
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.anchors import ZODIAC_FOLIOS, _parsed, locked_leaves, zodiac_pages  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

PREREG = ROOT / "reports/E010C_PREREG.md"
OUT = ROOT / "experiments/results/e010c.json"
SEED = 20261018
N_PERM, N_CTRL, ALPHA = 10_000, 200, 0.01

TAB = NX.load_tables()
UNI = {g for (s, _, _), g in TAB.items() if s == "unigram"}


@lru_cache(maxsize=None)
def opts(unit: str) -> frozenset:
    """All Naibbe outputs for a 1- or 2-letter unit (bigrams exclude unigram glyph strings, as the cipher does)."""
    if len(unit) == 1:
        return frozenset(TAB[("unigram", t, unit)] for t in NX.TABLES)
    return frozenset(g for a in NX.TABLES for b in NX.TABLES
                     if (g := TAB[("prefix", a, unit[0])] + TAB[("suffix", b, unit[1])]) not in UNI)


def clean_tok(t):
    return bool(t) and "?" not in t and "@" not in t


def run_from(words, i, name, j):
    """Longest match starting at word i and letter j: returns letters covered by the best path (DFS)."""
    best = 0
    if i >= len(words) or words[i] is None or j >= len(name):
        return 0
    for L in (1, 2):
        u = name[j:j + L]
        if len(u) == L and words[i] in opts(u):
            best = max(best, L + run_from(words, i + 1, name, j + L))
    return best


def run_words(words, i, name, j):
    """Number of words in the best path from (i, j) (to enforce runs of >= 2 words)."""
    best = (0, 0)
    if i >= len(words) or words[i] is None or j >= len(name):
        return best
    for L in (1, 2):
        u = name[j:j + L]
        if len(u) == L and words[i] in opts(u):
            sub = run_words(words, i + 1, name, j + L)
            best = max(best, (L + sub[0], 1 + sub[1]))
    return best


def score(rings, name):
    """Max letters of `name` covered by one run of >= 2 consecutive matching words, over all rings/start points."""
    best, where = 0, None
    for ri, words in enumerate(rings):
        for i in range(len(words)):
            for j in range(len(name)):
                letters, n_w = run_words(words, i, name, j)
                if n_w >= 2 and letters > best:
                    best, where = letters, (ri, i, j, n_w)
    return best, where


def page_rings(p):
    return [[t if clean_tok(t) else None for t in r["tokens"]] for r in p["text_rings"]]


def primary(S, own):
    """S: pages x months score matrix; own[p] = month index. T = mean(own - mean(other months))."""
    m = S.shape[1]
    d = [S[p, own[p]] - (S[p].sum() - S[p, own[p]]) / (m - 1) for p in range(S.shape[0])]
    return float(np.mean(d))


def perm_test(S, own, rng):
    t = primary(S, own)
    null = np.array([primary(S, rng.permutation(own)) for _ in range(N_PERM)])
    return t, float((1 + (null >= t).sum()) / (N_PERM + 1)), float(null.mean())


def matrix(rings_by_page, months):
    return np.array([[score(r, m)[0] for m in months] for r in rings_by_page], dtype=float)


def insert(rings, name, rng):
    """Replace a random contiguous run in one ring with a true Naibbe encryption of `name` (space removal off)."""
    k = dict(NX.key({}, 0, name), space_removal=0.0)
    enc, _ = NX.encode_tokens(name, k, rng.randrange(2 ** 31))
    rings = [list(r) for r in rings]
    cand = [i for i, r in enumerate(rings) if len(r) >= len(enc)] or [max(range(len(rings)), key=lambda i: len(rings[i]))]
    ri = rng.choice(cand)
    r = rings[ri]
    s = rng.randrange(0, max(1, len(r) - len(enc) + 1))
    r[s:s + len(enc)] = enc
    return rings


def main():
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    pages = [p for p in zodiac_pages() if not p["locked"]]
    names = [NX.clean(p["month_latin_script"]) for p in pages]
    months = sorted(set(names), key=names.index)
    own = np.array([months.index(n) for n in names])
    rings = [page_rings(p) for p in pages]
    rng = np.random.default_rng(SEED)
    pyrng = random.Random(SEED)

    S = matrix(rings, months)
    T, p, null_mean = perm_test(S, own, rng)
    runs = []
    for pg, r, n in zip(pages, rings, names):
        sc, where = score(r, n)
        words = r[where[0]][where[1]:where[1] + where[3]] if where else []
        runs.append({"folio": pg["folio"], "month": n, "own_score": sc, "run_words": words,
                     "letters_start": where[2] if where else None,
                     "best_other_month": months[int(np.argmax([S[pages.index(pg), j] if j != months.index(n) else -1
                                                               for j in range(len(months))]))],
                     "best_other_score": float(max(S[pages.index(pg), j] for j in range(len(months))
                                                   if j != months.index(n)))})
    supported = bool(p < ALPHA and S[np.arange(len(pages)), own].max() >= 4)

    # (b) chance rates on non-zodiac DEV lines (prose + circle), same scoring per month
    locked = locked_leaves()
    lines = {}
    for t in _parsed()[1]:
        if t.folio in ZODIAC_FOLIOS or t.leaf in locked or t.mode not in ("prose", "circle"):
            continue
        lines.setdefault((t.folio, t.line_no), []).append(t.eva if clean_tok(t.eva) else None)
    L = list(lines.values())
    chance = {}
    for m in months:
        sc = [score([l], m)[0] for l in L]
        chance[m] = {"n_lines": len(L), "share_ge2": float(np.mean([s >= 2 for s in sc])),
                     "share_ge3": float(np.mean([s >= 3 for s in sc])), "share_ge4": float(np.mean([s >= 4 for s in sc])),
                     "max": int(max(sc)), "exact_full_name_lines": int(sum(s >= len(m) for s in sc))}

    # positive control and false-positive control
    def ctrl(wrong):
        ps = []
        for _ in range(N_CTRL):
            rr = []
            for i, r in enumerate(rings):
                n = names[i] if not wrong else pyrng.choice([x for x in months if x != names[i]])
                rr.append(insert(r, n, pyrng))
            Sc = matrix(rr, months)
            ps.append(perm_test(Sc, own, np.random.default_rng(pyrng.randrange(2 ** 31)))[1])
        return float(np.mean(np.array(ps) < ALPHA))
    global N_PERM
    N_PERM_MAIN, N_PERM = N_PERM, 1000    # controls use 1,000 permutations each (min p 0.001 < alpha)
    power = ctrl(False)
    fpr = ctrl(True)
    N_PERM = N_PERM_MAIN

    verdict = ("SUPPORTED" if supported else
               ("NEGATIVE" if power >= 0.8 else "UNINFORMATIVE (power < 0.8)"))
    res = {"experiment": "e010c", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha,
           "seed": SEED, "tables_sha256": NX.TABLES_SHA256, "months": months,
           "pages": [p["folio"] for p in pages], "score_matrix": S.tolist(),
           "primary": {"T": T, "p": p, "null_mean": null_mean, "n_perm": N_PERM_MAIN, "alpha": ALPHA,
                       "max_own_score": float(S[np.arange(len(pages)), own].max())},
           "own_month_runs": runs, "chance_on_non_zodiac_DEV_lines": chance,
           "controls": {"power_inserted_true_month": power, "false_positive_inserted_wrong_month": fpr,
                        "n_replicates": N_CTRL, "n_perm_each": 1000},
           "verdict": verdict, "wall_s": round(time.time() - t0)}
    OUT.write_text(json.dumps(res, indent=1, default=str))
    from vcl.eval.ledger import append
    append([dict(experiment="E010C", model="naibbe_exact_month_runs", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split="zodiac_f70v2-f73v", metric=m, value=round(v, 4), command=" ".join(sys.argv),
                 notes=f"pre-registered; verdict {verdict}")
            for m, v in (("T_own_minus_other", T), ("p_perm", p), ("power", power), ("false_positive_rate", fpr))])
    print(json.dumps({k: res[k] for k in ("primary", "controls", "verdict", "wall_s")}, indent=1))
    for r in runs:
        print(r["folio"], r["month"], r["own_score"], r["run_words"], "| best other:", r["best_other_month"],
              r["best_other_score"])


if __name__ == "__main__":
    main()
