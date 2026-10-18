"""E022 (methodology A2b): do plants that look alike have pages with alike words?

Pre-registered in reports/E022_PREREG.md. Inputs: locked visual codes (data/derived/e022_visual_codes_A.json; its
sha256 is recorded in the results) and the Voynich herbal DEV prose. Refuses to run unless the codes file is
read-only (locked).

Run: .venv/bin/python experiments/e022_plant_text_link.py [--codes data/derived/e022_visual_codes_A.json]
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, random, re, stat, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402

PREREG = ROOT / "reports/E022_PREREG.md"
OUT = ROOT / "experiments/results/e022.json"
FEATS = ["root", "stems", "leaf_arrangement", "leaf_shape", "leaf_margin", "leaf_count", "flower", "flower_color",
         "fruit_or_pods", "leaf_color", "symmetry", "height", "thorns_hairs"]
N_PERM, MIN_GAP, DF_MAX, ALPHA, SEED = 10_000, 4, 15, 0.01, 22022


def folio_num(f):
    return int(re.match(r"f(\d+)", f).group(1))


def vis_sim(a, b):
    ks = [k for k in FEATS if a[k] != "unclear" and b[k] != "unclear"]
    return sum(a[k] == b[k] for k in ks) / len(ks) if ks else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes", default=str(ROOT / "data/derived/e022_visual_codes_A.json"))
    a = ap.parse_args()
    codes_path = Path(a.codes)
    if os.stat(codes_path).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
        sys.exit("visual codes file must be locked read-only before analysis")
    codes = json.loads(codes_path.read_text())
    codes_sha = hashlib.sha256(codes_path.read_bytes()).hexdigest()
    _, toks = E.parse()
    locked = set(E.locked_test_leaves(toks))
    words, stratum, first = defaultdict(list), {}, {}
    for t in toks:
        if t.folio in codes and t.mode == "prose" and t.is_clean and t.leaf not in locked:
            words[t.folio].append(t.eva)
            stratum[t.folio] = (t.currier, t.hand)
            first.setdefault(t.folio, t.eva)
    pages = sorted(p for p in codes if p in words)
    n = len(pages)
    df = Counter(w for p in pages for w in set(words[p]))
    vocab = sorted(w for w, d in df.items() if 2 <= d <= DF_MAX)
    vi = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((n, len(vocab)))
    for i, p in enumerate(pages):
        for w, c in Counter(words[p]).items():
            if w in vi:
                M[i, vi[w]] = c * math.log(n / df[w])
    nr = np.linalg.norm(M, axis=1); nr[nr == 0] = 1
    Tm = (M / nr[:, None]) @ (M / nr[:, None]).T
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    far = [(i, j) for i, j in pairs if abs(folio_num(pages[i]) - folio_num(pages[j])) >= MIN_GAP]

    Vm = np.array([[vis_sim(codes[p], codes[q]) for q in pages] for p in pages])
    from scipy.stats import rankdata

    def stat_r(order, prs):
        I, J = np.array([x for x, _ in prs]), np.array([y for _, y in prs])
        o = np.asarray(order)
        return float(np.corrcoef(rankdata(Vm[o[I], o[J]]), rankdata(Tm[I, J]))[0, 1])

    strata = defaultdict(list)
    for i, p in enumerate(pages):
        strata[stratum[p]].append(i)
    rng = random.Random(SEED)

    def perm_p(prs, obs):
        ge = 0
        for _ in range(N_PERM):
            order = list(range(n))
            for idx in strata.values():
                sh = idx[:]; rng.shuffle(sh)
                for a_, b_ in zip(idx, sh):
                    order[a_] = b_
            ge += stat_r(order, prs) >= obs
        return (ge + 1) / (N_PERM + 1)

    ident = list(range(n))
    r_far = stat_r(ident, far); p_far = perm_p(far, r_far)
    r_all = stat_r(ident, pairs); p_all = perm_p(pairs, r_all)
    a1 = [i for i in range(n) if stratum[pages[i]] == ("A", "1")]
    a1_far = [(i, j) for i, j in far if i in a1 and j in a1]
    r_a1 = stat_r(ident, a1_far)
    V = np.array([vis_sim(codes[pages[i]], codes[pages[j]]) for i, j in far])
    cut = np.quantile(V, 0.9)
    same_first = np.array([first[pages[i]] == first[pages[j]] for i, j in far])
    res = {"experiment": "e022", "prereg_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest(),
           "codes_file": str(codes_path.relative_to(ROOT)), "codes_sha256": codes_sha, "n_pages": n,
           "n_vocab": len(vocab), "n_pairs_far": len(far),
           "primary": {"r": r_far, "p": p_far, "verdict": "MEANING LINK DETECTED" if p_far < ALPHA else "NOT DETECTED"},
           "all_pairs": {"r": r_all, "p": p_all},
           "currier_A_hand1_far": {"r": r_a1, "n_pairs": len(a1_far)},
           "first_word": {"top10_rate": float(same_first[V >= cut].mean()), "rest_rate": float(same_first[V < cut].mean()),
                          "n_top": int((V >= cut).sum())},
           "strata": {f"{k[0]}{k[1]}": len(v) for k, v in strata.items()}}
    OUT.write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("n_pages", "n_vocab", "n_pairs_far", "primary", "all_pairs",
                                          "currier_A_hand1_far", "first_word", "strata")}, indent=1, default=str))
    from vcl.eval.ledger import append
    append([dict(experiment="E022", model="plant_visual_vs_text", checkpoint_sha256=f"codes={codes_sha[:12]}",
                 split="voynich_DEV_herbal", metric=m, value=round(v, 4), command=" ".join(sys.argv),
                 notes=res["primary"]["verdict"]) for m, v in (("spearman_r_far", r_far), ("perm_p_far", p_far))])


if __name__ == "__main__":
    main()
