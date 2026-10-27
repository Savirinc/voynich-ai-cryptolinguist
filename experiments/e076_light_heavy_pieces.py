"""E076: light pieces (same places, changed meaning: un-, im-, Farsi na-/be-/ba-) versus heavy pieces (different places:
grammar), and which languages have the most Voynich-like mix. See reports/E076_PREREG.md. No generator (Arham).

Machinery from E075 (kit, contexts, swap pairs, consistency). New: LIGHTNESS of a swap a->b on core X = share of the
other frequent words (freq >= 5) whose context is less similar to aX than bX is (cosine); median over cores.
Light >= 0.80, medium 0.65-0.80, heavy < 0.65. Profile = (light, medium, heavy shares; consistent share; front share
among light swaps; front share among heavy swaps). Closeness = Euclidean distance between profiles.
Run: caffeinate -ims .venv/bin/python experiments/e076_light_heavy_pieces.py
"""
from __future__ import annotations

import json, random, sys, time, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e075_piece_effects import kit, contexts, swap_pairs, consistency  # noqa: E402

OUT = ROOT / "experiments/results/e076.json"
BIB = ROOT / "data/external/bibles"
SKIP = {"cmn-cu89s", "jpn1965", "vie1934", "engWycliffe"}
CONS = {"hboWLC", "arb-vd", "pesOPV", "urd", "uigara", "ydd"}
LIGHT, HEAVY, MINF, Z_BAR = 0.80, 0.65, 5, 3.0
SEED = 76076
EN_NOT = {"unto", "unless", "under", "until", "understand", "understood", "understanding", "undertook"}
DE_NOT = {"und", "uns", "unser", "unsre", "unsrer", "unsern", "unsers", "unserm", "unter", "unten", "unsere", "unseren",
          "unserer", "unseres", "unserem", "unterwegs", "untertan", "untertanen"}


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def lightness_fn(ctx, freq):
    W = [w for w, c in freq.items() if c >= MINF and w in ctx]
    idx = {w: i for i, w in enumerate(W)}
    M = np.array([unit(ctx[w]) for w in W])
    def L(a, b):
        with np.errstate(all="ignore"):
            sims = M @ M[idx[a]]
        s_ab = sims[idx[b]]
        mask = np.ones(len(W), bool); mask[idx[a]] = False; mask[idx[b]] = False
        return float((sims[mask] < s_ab).mean())
    return L, W


def profile(lines, seed=SEED, keep=False):
    nrng = np.random.default_rng(seed)
    freq = Counter(w for l in lines for w in l)
    F, E = kit(sorted(freq))
    ctx, _, _ = contexts(lines, F, E)
    L, W = lightness_fn(ctx, freq)
    pairs = swap_pairs(freq, F, E)
    rows = {}
    for key, prs in pairs.items():
        lt = float(np.median([L(a, b) for a, b in prs]))
        c, z = consistency([ctx[b] - ctx[a] for a, b in prs], nrng, draws=300)
        r = {"kind": key[0], "cores": len(prs), "lightness": lt, "z": z,
             "class": "light" if lt >= LIGHT else ("heavy" if lt < HEAVY else "medium")}
        if keep:
            r["examples"] = prs[:6]
        rows[f"{key[0]}:{key[1] or '-'}>{key[2] or '-'}"] = r
    n = len(rows)
    if n == 0:
        return {"eligible": 0}
    cl = Counter(r["class"] for r in rows.values())
    li = [r for r in rows.values() if r["class"] == "light"]; he = [r for r in rows.values() if r["class"] == "heavy"]
    prof = {"light": cl["light"] / n, "medium": cl["medium"] / n, "heavy": cl["heavy"] / n,
            "consistent": sum(r["z"] > Z_BAR for r in rows.values()) / n,
            "front_light": (sum(r["kind"] == "front" for r in li) / len(li)) if li else 0.5,
            "front_heavy": (sum(r["kind"] == "front" for r in he) / len(he)) if he else 0.5}
    rnd = random.Random(seed); ww = [w for w in W]
    rp = [L(*rnd.sample(ww, 2)) for _ in range(300)]
    return {"eligible": n, "profile": prof, "random_pair_median": float(np.median(rp)), "swaps": rows}


def antonym_check(bid, prefix, notset):
    from e064_early_audit import tok
    w = tok(bid)
    lines = [w[i:i + 10] for i in range(0, len(w), 10)]
    freq = Counter(w)
    F, E = kit(sorted(freq))
    ctx, _, _ = contexts(lines, F, E)
    L, W = lightness_fn(ctx, freq)
    Ws = set(W)
    prs = [(x[len(prefix):], x) for x in W if x.startswith(prefix) and x not in notset and len(x) - len(prefix) >= 3
           and x[len(prefix):] in Ws]
    vals = [L(a, b) for a, b in prs]
    rnd = random.Random(SEED); rp = [L(*rnd.sample(W, 2)) for _ in range(500)]
    return {"pairs": len(prs), "median_lightness": float(np.median(vals)) if vals else None, "examples": prs[:12],
            "random_pair_median": float(np.median(rp))}


def main():
    t0 = time.time()
    from e011_twin_search import voynich_lines
    from e064_early_audit import tok
    from e058_word_repeat_individuality_v2 import pseudo
    res = {"experiment": "E076", "known": {}, "texts": {}}
    log("[known answers: antonym prefixes, whole texts]")
    for bid, pre, ns in [("eng-kjv", "un", EN_NOT), ("deu1912", "un", DE_NOT), ("pesOPV", "نا", set())]:
        r = antonym_check(bid, pre, ns); res["known"][f"{bid}:{pre}"] = r
        log(f"  {bid:8s} {pre}- pairs {r['pairs']:3d} median lightness {r['median_lightness']} (random pairs {r['random_pair_median']:.2f}) e.g. {r['examples'][:6]}")
    valid = all(res["known"][k]["median_lightness"] is not None and res["known"][k]["median_lightness"] >= 0.80
                for k in ("eng-kjv:un", "deu1912:un"))
    vl, _, _, locked = voynich_lines()
    vl = [[w for w in l if w] for l in vl]; vl = [l for l in vl if l]
    lens = [len(l) for l in vl]; N = sum(lens)
    res["locked_test_excluded"] = locked
    r = profile(vl, keep=True); res["texts"]["VOYNICH"] = r
    log(f"VOYNICH eligible {r['eligible']} profile { {k: round(v, 3) for k, v in r['profile'].items()} } random {r['random_pair_median']:.2f}")
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        try:
            w = tok(bid)
        except Exception as e:
            log(f"  {bid}: skipped ({e})"); continue
        if bid in CONS:
            w = [x for x in (cons(t) for t in w) if x]
        if len(w) < 10000 + N:
            continue
        r = profile(pseudo(w[10000:10000 + N], lens), keep=bid in ("hboWLC", "latVUC", "pesOPV", "arb-vd"))
        if r["eligible"] < 10:
            log(f"  {bid:10s} eligible {r['eligible']} (<10, not ranked)"); res["texts"][bid] = r; continue
        res["texts"][bid] = r
        log(f"  {bid:10s} eligible {r['eligible']:3d} " + " ".join(f"{k} {v:.2f}" for k, v in r["profile"].items()))
    V = res["texts"]["VOYNICH"]["profile"]; keys = list(V)
    dist = {b: float(np.sqrt(sum((r["profile"][k] - V[k]) ** 2 for k in keys)))
            for b, r in res["texts"].items() if b != "VOYNICH" and r.get("eligible", 0) >= 10}
    rank = sorted(dist.items(), key=lambda x: x[1])
    res.update(validated=valid, ranking=rank, runtime_s=time.time() - t0)
    log(f"[validity] {'VALID' if valid else 'VOID'} (English and German un- median lightness >= 0.80)")
    log("closest to Voynich: " + ", ".join(f"{b} {d:.3f}" for b, d in rank[:12]))
    log("farthest: " + ", ".join(f"{b} {d:.3f}" for b, d in rank[-5:]))
    log("Voynich swaps by class:")
    for cls in ("light", "medium", "heavy"):
        rows = sorted(((k, v) for k, v in res["texts"]["VOYNICH"]["swaps"].items() if v["class"] == cls), key=lambda x: -x[1]["lightness"])
        log(f"  {cls} ({len(rows)}): " + "; ".join(f"{k} {v['lightness']:.2f} {v['examples'][:2]}" for k, v in rows[:14]))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
