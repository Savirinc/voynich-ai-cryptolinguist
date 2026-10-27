"""E072: is ot/ok a detachable front piece? See reports/E072_PREREG.md.

REM(P) = share of target types (start with P, freq >= 2, len >= len(P)+1) whose remainder is a type with freq >= 2.
z against 1,000 matched draws (E071 matching), 10 seeds, median z, 8/10 rule.
Run: caffeinate -ims .venv/bin/python experiments/e072_front_pieces.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, random, re, sys, time, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e071_label_truncation import pools, pool_for as _pool_for  # noqa: E402


def pool_for(P, w, freq):
    """E071 matching; if still fewer than 5 candidates, widen length step by step (same bin +-1 first)."""
    cand = _pool_for(P, w, freq)
    L, b = len(w), int(__import__("math").log2(freq[w]))
    d = 2
    while len(cand) < 5 and d < 15:
        for dl in (d, -d):
            cand += [x for (l, bb), xs in P.items() if l == L + dl and abs(bb - b) <= 1 for x in xs]
        d += 1
    if len(cand) < 5:                        # last resort: the 20 nearest candidates by (length, bin) distance
        allc = sorted(((abs(l - L) + abs(bb - b), x) for (l, bb), xs in P.items() for x in xs))
        cand += [x for _, x in allc[:20]]
    return cand

N, START = 28841, 10000
OUT = ROOT / "experiments/results/e072.json"
SEEDS = list(range(1001, 1011))
DRAWS = 1000
Z_BAR = 3.0
KNOWN = [("arb-vd", ("ال",)), ("hboWLC", ("ה",)), ("hun", ("meg",)), ("indayt", ("ber",))]
GEN_SEEDS = [31, 32, 33]
OG = re.compile(r"^o[tkpf]")


def log(*a):
    print(*a, flush=True)


def targets(freq, pres):
    return sorted(w for w, c in freq.items() if c >= 2 and any(w.startswith(p) and len(w) >= len(p) + 1 for p in pres))


def strip(w, pres):
    for p in sorted(pres, key=len, reverse=True):
        if w.startswith(p):
            return w[len(p):]
    raise ValueError(w)


def rem_share(T, freq, pres):
    return float(np.mean([freq.get(strip(w, pres), 0) >= 2 for w in T]))


def ztest(T, freq, pres, candidates, seeds=SEEDS, draws=DRAWS):
    """T: target types; pres: front pieces; candidates: control types (already excluding targets/forbidden)."""
    k = len(pres[0])
    assert all(len(p) == k for p in pres)
    Tset = set(T)
    cands = [w for w in candidates if w not in Tset and freq[w] >= 2 and len(w) >= k + 1]
    P = pools(freq, cands)
    plist = [pool_for(P, w, freq) for w in T]
    assert all(plist), "empty control pool"
    obs = rem_share(T, freq, pres)
    zs, mus = [], []
    for sd in seeds:
        rng = random.Random(sd)
        vals = [float(np.mean([freq.get(rng.choice(p)[k:], 0) >= 2 for p in plist])) for _ in range(draws)]
        mu, sg = float(np.mean(vals)), float(np.std(vals, ddof=1))
        zs.append((obs - mu) / sg if sg > 0 else 0.0); mus.append(mu)
    return {"n": len(T), "REM": obs, "control_mean": float(np.mean(mus)), "z_median": float(np.median(zs)), "z": zs,
            "above": sum(z > Z_BAR for z in zs), "within": sum(abs(z) <= Z_BAR for z in zs)}


def pseudo(T, freq, candidates, k, rng):
    """Matched non-target types; scored as if their first k glyphs were the front piece."""
    Tset = set(T)
    cands = [w for w in candidates if w not in Tset and freq[w] >= 2 and len(w) >= k + 1]
    P = pools(freq, cands)
    return [rng.choice(pool_for(P, w, freq)) for w in T]


def ztest_pseudo(S, freq, k, candidates, seeds=SEEDS, draws=DRAWS):
    pres = tuple(sorted({w[:k] for w in S}))
    # REM of S with each word stripped of its own first k glyphs; controls exclude S
    Sset = set(S)
    cands = [w for w in candidates if w not in Sset and freq[w] >= 2 and len(w) >= k + 1]
    P = pools(freq, cands)
    plist = [pool_for(P, w, freq) for w in S]
    obs = float(np.mean([freq.get(w[k:], 0) >= 2 for w in S]))
    zs = []
    for sd in seeds:
        rng = random.Random(sd)
        vals = [float(np.mean([freq.get(rng.choice(p)[k:], 0) >= 2 for p in plist])) for _ in range(draws)]
        mu, sg = float(np.mean(vals)), float(np.std(vals, ddof=1))
        zs.append((obs - mu) / sg if sg > 0 else 0.0)
    return {"n": len(S), "REM": obs, "z_median": float(np.median(zs)), "z": zs,
            "within": sum(abs(z) <= Z_BAR for z in zs), "n_first_pieces": len(pres)}


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M").replace("ٱ", "ا")


def known_text(bid):
    from e064_early_audit import tok
    w = tok(bid)[START:START + N]
    if bid in ("arb-vd", "hboWLC"):
        w = [unicodedata.normalize("NFC", cons(x)) for x in w]
        w = [x for x in w if x]
    return Counter(w)


def voynich():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    dev = [t for t in toks if t.leaf not in locked]
    freq = Counter(t.eva for t in dev if t.mode == "prose" and t.is_clean)
    assert sum(freq.values()) == N
    lab = {t.eva for t in dev if t.mode == "label" and t.is_clean}
    return freq, lab, sorted(locked, key=lambda x: (len(x), x))


def voy_cands(freq):
    return [w for w in freq if not w.startswith("q") and not OG.match(w)]


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    rng = random.Random(72072)
    res = {"experiment": "E072", "known": {}, "false": {}, "voynich": {}, "generator": {}}
    ok = []

    log("[known answers]")
    for bid, pres in KNOWN:
        freq = known_text(bid)
        T = targets(freq, pres)
        cands = [w for w in freq if not any(w.startswith(p) for p in pres)]
        r = ztest(T, freq, pres, cands); res["known"][bid] = r; ok.append(("known", bid, r["above"] >= 8))
        log(f"  {bid:8s} {pres[0]:4s} targets {r['n']:4d} REM {r['REM']:.3f} ctrl {r['control_mean']:.3f} z {r['z_median']:+.2f} ({r['above']}/10 > 3)")
        S = pseudo(T, freq, cands, len(pres[0]), rng)
        f = ztest_pseudo(S, freq, len(pres[0]), cands); res["false"][bid] = f; ok.append(("false", bid, f["within"] >= 8))
        log(f"  {bid:8s} pseudo targets {f['n']:4d} REM {f['REM']:.3f} z {f['z_median']:+.2f} ({f['within']}/10 within)")

    log("[VOYNICH]")
    freq, lab, locked = voynich()
    res["locked_test_excluded"] = locked
    C = voy_cands(freq)
    T1 = [w for w in targets(freq, ("q",)) if w.startswith("qo")]
    l1 = ztest(T1, freq, ("q",), C); res["voynich"]["L1_q"] = l1; ok.append(("internal", "q", l1["above"] >= 8))
    log(f"  layer 1 q      targets {l1['n']:4d} REM {l1['REM']:.3f} ctrl {l1['control_mean']:.3f} z {l1['z_median']:+.2f} ({l1['above']}/10 > 3)")
    T2 = targets(freq, ("ot", "ok"))
    l2 = ztest(T2, freq, ("ot", "ok"), C); res["voynich"]["L2_otok"] = l2
    log(f"  layer 2 ot/ok  targets {l2['n']:4d} REM {l2['REM']:.3f} ctrl {l2['control_mean']:.3f} z {l2['z_median']:+.2f} ({l2['above']}/10 > 3)")
    S = pseudo(T2, freq, C, 2, rng)
    f = ztest_pseudo(S, freq, 2, C); res["false"]["voynich"] = f; ok.append(("false", "voynich", f["within"] >= 8))
    log(f"  pseudo         targets {f['n']:4d} REM {f['REM']:.3f} z {f['z_median']:+.2f} ({f['within']}/10 within)")
    rep = {}
    for name, pres, T in [("L3_qotqok", ("qot", "qok"), targets(freq, ("qot", "qok"))),
                          ("opof", ("op", "of"), targets(freq, ("op", "of"))),
                          ("o_on_ogallows", ("o",), [w for w in freq if freq[w] >= 2 and OG.match(w)]),
                          ("L2_labels_only", ("ot", "ok"), [w for w in T2 if w in lab])]:
        r = ztest(T, freq, pres, C); rep[name] = r
        log(f"  {name:14s} targets {r['n']:4d} REM {r['REM']:.3f} ctrl {r['control_mean']:.3f} z {r['z_median']:+.2f} ({r['above']}/10 > 3)")
    res["voynich"].update(rep)

    log("[generator]")
    from e032_copy_generator import generate
    work = ROOT / "data/external/e072_gen_work"
    gz = []
    for s in GEN_SEEDS:
        g = Counter(w for l in generate(gen_dir, java, s, N, work) for w in l)
        Tg = targets(g, ("ot", "ok"))
        r = ztest(Tg, g, ("ot", "ok"), voy_cands(g)); res["generator"][str(s)] = r; gz.append(r)
        log(f"  seed {s} ot/ok targets {r['n']:4d} REM {r['REM']:.3f} ctrl {r['control_mean']:.3f} z {r['z_median']:+.2f} ({r['above']}/10 > 3)")

    valid = all(x[2] for x in ok)
    res["checks"] = ok; res["validated"] = valid
    log(f"[validation] {sum(x[2] for x in ok)}/{len(ok)} checks pass -> {'VALID' if valid else 'VOID'}: {[x for x in ok if not x[2]]}")
    if not valid:
        v, fct = "VOID", "none"
    elif l2["above"] >= 8:
        if all(r["z_median"] <= Z_BAR for r in gz) and all(sum(z <= Z_BAR for z in r["z"]) >= 8 for r in gz):
            v, fct = "DETACHABLE, BEYOND THE GENERATOR", "L x2"
        else:
            v, fct = "DETACHABLE, GENERATOR TOO", "none"
    elif sum(z <= Z_BAR for z in l2["z"]) >= 8:
        v, fct = "NOT DETACHABLE", "none"
    else:
        v, fct = "INCONCLUSIVE (seed rule)", "none"
    res.update(verdict=v, factor=fct, runtime_s=time.time() - t0)
    log(f"VERDICT {v} | factor {fct} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
