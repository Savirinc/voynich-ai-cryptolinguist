"""E079: skeleton decipherment - match Voynich's fronts and endings one-to-one with each language's by behaviour.
See reports/E079_PREREG.md.

Pieces of a text: its 10 commonest fronts (1-2 characters) and 20 commonest endings (1-4 characters) (E078 lists).
A token carries the longest listed front it starts with and the longest listed ending it ends with (the word must be
longer than the piece). Behaviour fingerprint of a piece p (no letters involved):
  SHARE   log share of tokens carrying p
  FREE    share of p's uses where p stands alone as a whole word
  DETACH  share of word types (freq >= 2) carrying p whose remainder (p removed) is a word (freq >= 2)
  HAPAX   share of word types carrying p that occur once
  TTR     log (types / tokens) of words carrying p
  AGREE   log ratio P(next token carries p | this token carries p) / P(a token carries p)
Each feature is z-scored across the text's 30 pieces. Fronts are matched to fronts (10x10), endings to endings (20x20)
by minimum total Euclidean distance (Hungarian method). Score = mean distance over the 30 matched pairs.
Run: caffeinate -ims .venv/bin/python experiments/e079_skeleton_match.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, math, sys, time, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e078_skeleton_traits import lists  # noqa: E402

OUT = ROOT / "experiments/results/e079.json"
BIB = ROOT / "data/external/bibles"
SKIP = {"cmn-cu89s", "jpn1965", "vie1934", "engWycliffe"}
CONS = {"hboWLC", "arb-vd", "pesOPV", "urd", "uigara", "ydd"}
KNOWN = ["hboWLC", "latVUC", "pesOPV", "arb-vd", "turytc", "deu1912"]
N, A0, B0 = 28841, 10000, 60000
FEATS = ["SHARE", "FREE", "DETACH", "HAPAX", "TTR", "AGREE"]


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def fingerprints(tokens):
    f = Counter(tokens); W2 = {w for w, c in f.items() if c >= 2}
    F, E = lists(sorted(f))
    def front(w):
        return max((p for p in F if w.startswith(p) and len(p) < len(w)), key=len, default=None)
    def end(w):
        return max((p for p in E if w.endswith(p) and len(p) < len(w)), key=len, default=None)
    fo = {w: front(w) for w in f}; en = {w: end(w) for w in f}
    rows = {}
    n = len(tokens)
    for kind, P, get in (("front", F, fo), ("ending", E, en)):
        for p in P:
            toks = [w for w in tokens if get[w] == p]
            types = {w for w in f if get[w] == p}
            k = len(toks)
            if k == 0:
                rows[(kind, p)] = None; continue
            alone = f.get(p, 0)
            rem = [(w[len(p):] if kind == "front" else w[:-len(p)]) for w in types if w in W2]
            nxt = sum(1 for a, b in zip(tokens, tokens[1:]) if get[a] == p and get[b] == p)
            share = k / n
            rows[(kind, p)] = {"SHARE": math.log(share), "FREE": alone / (alone + k),
                               "DETACH": (sum(r in W2 for r in rem) / len(rem)) if rem else 0.0,
                               "HAPAX": sum(f[w] == 1 for w in types) / len(types),
                               "TTR": math.log(len(types) / k),
                               "AGREE": math.log(((nxt + 0.5) / (k + 1)) / share)}
    out = {}
    for kind, P in (("front", F), ("ending", E)):
        keep = [p for p in P if rows[(kind, p)] is not None]
        out[kind] = (keep, np.array([[rows[(kind, p)][x] for x in FEATS] for p in keep]))
    allm = np.vstack([out["front"][1], out["ending"][1]])
    mu, sd = allm.mean(0), allm.std(0) + 1e-9
    for kind in out:
        out[kind] = (out[kind][0], (out[kind][1] - mu) / sd)
    return out


def match(a, b):
    tot, pairs, n = 0.0, [], 0
    for kind in ("front", "ending"):
        pa, Ma = a[kind]; pb, Mb = b[kind]
        D = np.linalg.norm(Ma[:, None, :] - Mb[None, :, :], axis=2)
        ri, ci = linear_sum_assignment(D)
        tot += float(D[ri, ci].sum()); n += len(ri)
        pairs += [(kind, pa[i], pb[j], round(float(D[i, j]), 3)) for i, j in zip(ri, ci)]
    return tot / n, pairs


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    from e011_twin_search import voynich_lines
    from e064_early_audit import tok
    vl, _, _, locked = voynich_lines()
    V = [w for l in vl for w in l if w]
    ref, alt = {}, {}
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        try:
            w = tok(bid)
        except Exception as e:
            log(f"{bid}: skipped ({e})"); continue
        if bid in CONS:
            w = [x for x in (cons(t) for t in w) if x]
        if len(w) < A0 + N:
            continue
        ref[bid] = fingerprints(w[A0:A0 + N])
        if bid in KNOWN:
            assert len(w) >= B0 + N, bid
            alt[bid] = fingerprints(w[B0:B0 + N])
    res = {"experiment": "E079", "locked_test_excluded": locked, "known": {}, "n_languages": len(ref)}
    log(f"{len(ref)} reference languages")
    own_d, ok_rank, accs = [], [], []
    for bid, fp in alt.items():
        sc = sorted(((b, *match(fp, r)) for b, r in ref.items()), key=lambda x: x[1])
        rank = [b for b, _, _ in sc].index(bid) + 1
        d_own = next(d for b, d, _ in sc if b == bid)
        pairs = next(p for b, _, p in sc if b == bid)
        acc = sum(x == y for _, x, y, _ in pairs) / len(pairs)
        own_d.append(d_own); ok_rank.append(rank == 1); accs.append(acc)
        res["known"][bid] = {"rank_of_own_language": rank, "own_distance": d_own, "best": sc[0][:2], "top5": [(b, round(d, 3)) for b, d, _ in sc[:5]],
                             "mapping_accuracy": acc}
        log(f"[known] second {bid} window: own language rank {rank}, distance {d_own:.3f}; best {sc[0][0]} {sc[0][1]:.3f}; "
            f"pieces paired correctly {acc:.2f}; top5 {[(b, round(d, 2)) for b, d, _ in sc[:5]]}")
    valid = sum(ok_rank) >= 5 and float(np.median(accs)) >= 0.5
    band = max(own_d)
    vfp = fingerprints(V)
    vs = sorted(((b, *match(vfp, r)) for b, r in ref.items()), key=lambda x: x[1])
    res["voynich"] = {"ranking": [(b, round(d, 3)) for b, d, _ in vs], "best_pairs": vs[0][2], "second_pairs": vs[1][2],
                      "pieces": {k: vfp[k][0] for k in vfp}}
    log(f"[VOYNICH] closest: {[(b, round(d, 3)) for b, d, _ in vs[:10]]}")
    log(f"  farthest: {[(b, round(d, 3)) for b, d, _ in vs[-5:]]}")
    from e032_copy_generator import generate
    gd = {}
    for s in (31, 32, 33):
        g = [w for l in generate(gen_dir, java, s, N, ROOT / "data/external/e079_gen_work") for w in l][:N]
        gs = sorted(((b, *match(fingerprints(g), r)) for b, r in ref.items()), key=lambda x: x[1])
        gd[s] = (gs[0][0], gs[0][1]); log(f"[generator {s}] closest {gs[0][0]} {gs[0][1]:.3f}")
    res["generator"] = gd
    vbest = vs[0][1]
    within = vbest <= band
    gen_within = [d <= band for _, d in gd.values()]
    if not valid:
        verdict, factor = "VOID", "none"
    elif within and not any(gen_within):
        verdict, factor = f"SKELETON MATCH: {vs[0][0]}", "M x1/2"
    elif within:
        verdict, factor = f"SKELETON MATCH, GENERATOR TOO: {vs[0][0]}", "none"
    else:
        verdict, factor = "NO LANGUAGE MATCHES LIKE ITSELF", "none"
    res.update(validated=valid, same_language_band=band, verdict=verdict, factor=factor, runtime_s=time.time() - t0)
    log(f"[validity] own language first in {sum(ok_rank)}/{len(ok_rank)}; median pairing accuracy {np.median(accs):.2f} -> {'VALID' if valid else 'VOID'}")
    log(f"same-language band (largest own distance) {band:.3f}; Voynich best {vs[0][0]} {vbest:.3f}; generator best {[round(d, 3) for _, d in gd.values()]}")
    log("Voynich pieces paired with " + vs[0][0] + ": " + ", ".join(f"{a}->{b}" for _, a, b, _ in vs[0][2]))
    log(f"VERDICT {verdict} | factor {factor} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
