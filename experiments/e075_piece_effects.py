"""E075: does swapping a word piece change the word's job the same way across cores? See reports/E075_PREREG.md.

Per text (lines): kit = E074 recipe (10 fronts of 0-2 chars, 20 endings of 0-4 chars) on the whole text.
Swap pairs: FRONT (a, b): words a+X and b+X; ENDING (a, b): X+a and X+b; X non-empty; both forms frequency >= 5.
Context of a word = 4 blocks of probabilities over the neighbours' pieces: previous word's front, previous word's ending,
next word's front, next word's ending (longest kit piece that matches; a neighbour outside the line counts as BOUNDARY).
Shift d_X = ctx(form b) - ctx(form a). Consistency C = mean over X of cosine(d_X, mean of the other d's).
Null: random sign flips of the d_X (1,000 draws); z = (C - mean) / sd. Eligible pair: >= 8 cores.
Run: caffeinate -ims .venv/bin/python experiments/e075_piece_effects.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, random, sys, time, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
OUT = ROOT / "experiments/results/e075.json"
LANGS = ["hboWLC", "latVUC", "deu1912", "turytc", "eng-kjv", "indayt"]
KNOWN = ["hboWLC", "latVUC"]
GEN_SEEDS = [31, 32, 33]
MINF, MINCORES, DRAWS, Z_BAR = 5, 8, 1000, 3.0
SEED = 75075


def log(*a):
    print(*a, flush=True)


def kit(types):
    fr, en = Counter(), Counter()
    for w in types:
        for k in (1, 2):
            if len(w) > k:
                fr[w[:k]] += 1
        for k in range(1, 5):
            if len(w) > k:
                en[w[-k:]] += 1
    return [""] + [p for p, _ in fr.most_common(9)], [""] + [p for p, _ in en.most_common(19)]


def pieces_of(w, F, E):
    f = max((p for p in F if w.startswith(p) and len(p) < len(w)), key=len, default="")
    e = max((p for p in E if w.endswith(p) and len(p) < len(w)), key=len, default="")
    return f, e


def contexts(lines, F, E):
    fi = {p: i for i, p in enumerate(F + ["#"])}; ei = {p: i for i, p in enumerate(E + ["#"])}
    nf, ne = len(fi), len(ei)
    C = defaultdict(lambda: np.zeros(2 * nf + 2 * ne))
    pc = {}
    for l in lines:
        for i, w in enumerate(l):
            v = C[w]
            if i > 0:
                p = l[i - 1]; pc.setdefault(p, pieces_of(p, F, E)); f, e = pc[p]
                v[fi[f]] += 1; v[nf + ei[e]] += 1
            else:
                v[fi["#"]] += 1; v[nf + ei["#"]] += 1
            if i < len(l) - 1:
                n = l[i + 1]; pc.setdefault(n, pieces_of(n, F, E)); f, e = pc[n]
                v[nf + ne + fi[f]] += 1; v[2 * nf + ne + ei[e]] += 1
            else:
                v[nf + ne + fi["#"]] += 1; v[2 * nf + ne + ei["#"]] += 1
    blocks = [(0, nf), (nf, nf + ne), (nf + ne, 2 * nf + ne), (2 * nf + ne, 2 * nf + 2 * ne)]
    out = {}
    for w, v in C.items():
        u = v.copy()
        for a, b in blocks:
            s = u[a:b].sum()
            if s > 0:
                u[a:b] /= s
        out[w] = u
    return out, list(fi), list(ei)


def consistency(D, rng, draws=DRAWS):
    D = np.array(D)
    n = len(D)
    def C(M):
        tot = M.sum(0); vals = []
        for i in range(n):
            o = (tot - M[i]) / (n - 1)
            a, b = np.linalg.norm(M[i]), np.linalg.norm(o)
            vals.append(float(M[i] @ o / (a * b)) if a > 0 and b > 0 else 0.0)
        return float(np.mean(vals))
    obs = C(D)
    null = [C(D * rng.choice([-1.0, 1.0], size=(n, 1))) for _ in range(draws)]
    mu, sd = float(np.mean(null)), float(np.std(null, ddof=1))
    return obs, (obs - mu) / sd if sd > 0 else 0.0


def swap_pairs(freq, F, E):
    """(kind, a, b) -> list of (form_a, form_b)."""
    P = defaultdict(list)
    common = {w for w, c in freq.items() if c >= MINF}
    for w in common:
        for a in F:
            if not w.startswith(a) or len(w) <= len(a):
                continue
            X = w[len(a):]
            for b in F:
                if b > a and b + X in common and len(X) > 0:
                    P[("front", a, b)].append((w, b + X))
        for a in E:
            if not w.endswith(a) or len(w) <= len(a):
                continue
            X = w[:len(w) - len(a)]
            for b in E:
                if b > a and X + b in common and len(X) > 0:
                    P[("ending", a, b)].append((w, X + b))
    return {k: sorted(set(v)) for k, v in P.items() if len(set(v)) >= MINCORES}


def analyse(lines, seed=SEED, keep_examples=False):
    rng = random.Random(seed); nrng = np.random.default_rng(seed)
    freq = Counter(w for l in lines for w in l)
    F, E = kit(sorted(freq))
    ctx, fl, el = contexts(lines, F, E)
    pairs = swap_pairs(freq, F, E)
    res = {}
    names = [f"prev-front:{p}" for p in fl] + [f"prev-end:{p}" for p in el] + [f"next-front:{p}" for p in fl] + [f"next-end:{p}" for p in el]
    for key, prs in pairs.items():
        D = [ctx[b] - ctx[a] for a, b in prs]
        c, z = consistency(D, nrng)
        r = {"cores": len(prs), "C": c, "z": z}
        if keep_examples:
            m = np.mean(D, 0); top = np.argsort(-np.abs(m))[:4]
            r["shift"] = [(names[i], round(float(m[i]), 3)) for i in top]
            r["examples"] = prs[:6]
        res[f"{key[0]}:{key[1] or '-'}>{key[2] or '-'}"] = r
    n = len(res); k = sum(r["z"] > Z_BAR for r in res.values())
    return {"kit": {"front": F, "ending": E}, "eligible": n, "consistent": k, "share": k / n if n else float("nan"),
            "median_z": float(np.median([r["z"] for r in res.values()])) if n else float("nan"), "pairs": res}


def shuffled(lines, seed):
    rng = random.Random(seed); w = [x for l in lines for x in l]; rng.shuffle(w); out, i = [], 0
    for l in lines:
        out.append(w[i:i + len(l)]); i += len(l)
    return out


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    from e011_twin_search import voynich_lines
    from e064_early_audit import tok
    from e058_word_repeat_individuality_v2 import pseudo
    vl, _, _, locked = voynich_lines()
    vl = [[w for w in l if w] for l in vl]; vl = [l for l in vl if l]
    lens = [len(l) for l in vl]; N = sum(lens)
    texts = {"VOYNICH": vl}
    for b in LANGS:
        w = tok(b)[10000:]
        if b == "hboWLC":
            w = [x for x in (cons(t) for t in w) if x]
        texts[b] = pseudo(w[:N], lens)
    from e032_copy_generator import generate
    for s in GEN_SEEDS:
        texts[f"generator_{s}"] = generate(gen_dir, java, s, N, ROOT / "data/external/e075_gen_work")
    res = {"experiment": "E075", "locked_test_excluded": locked, "texts": {}, "shuffled": {}}
    for name, L in texts.items():
        r = analyse(L, keep_examples=(name in ("VOYNICH", "hboWLC", "latVUC")))
        res["texts"][name] = r
        log(f"{name:14s} eligible pairs {r['eligible']:4d} consistent {r['consistent']:4d} share {r['share']:.3f} median z {r['median_z']:+.2f}")
    for name in ["VOYNICH", "hboWLC", "latVUC"]:
        r = analyse(shuffled(texts[name], SEED)); res["shuffled"][name] = {k: r[k] for k in ("eligible", "consistent", "share", "median_z")}
        log(f"shuffled {name:9s} eligible {r['eligible']:4d} consistent {r['consistent']:4d} share {r['share']:.3f}")
    T = res["texts"]
    valid = all(T[k]["consistent"] >= 5 for k in KNOWN) and all(v["share"] <= 0.05 for v in res["shuffled"].values())
    SV = T["VOYNICH"]["share"]; SL = [T[b]["share"] for b in LANGS]; SG = [T[f"generator_{s}"]["share"] for s in GEN_SEEDS]
    if not valid:
        v, f = "VOID", "none"
    elif SV >= min(SL) and SV > max(SG) + 0.05:
        v, f = "LANGUAGE-LIKE", "M x1/2"
    elif SV <= max(SG) and SV < min(SL):
        v, f = "GENERATOR-LIKE", "M x2"
    else:
        v, f = "BETWEEN", "none"
    res.update(validated=valid, verdict=v, factor=f, runtime_s=time.time() - t0)
    log(f"[validity] {'VALID' if valid else 'VOID'} | Voynich {SV:.3f} languages {min(SL):.3f}-{max(SL):.3f} generator {min(SG):.3f}-{max(SG):.3f}")
    log("Voynich consistent pairs (z > 3), strongest first:")
    for k, r in sorted(T["VOYNICH"]["pairs"].items(), key=lambda x: -x[1]["z"]):
        if r["z"] > Z_BAR:
            log(f"  {k:18s} cores {r['cores']:3d} z {r['z']:+6.2f} shift {r['shift']} e.g. {r['examples'][:3]}")
    log(f"VERDICT {v} | factor {f} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
