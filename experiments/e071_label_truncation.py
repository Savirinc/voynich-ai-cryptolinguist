"""E071: are the Voynich label words truncations of longer words? See reports/E071_PREREG.md.

Prefix score S(T) = mean log2(1 + EXT(w)) over a target set T, EXT = distinct prose types extending w by >= 1 glyph.
z against 1,000 length- and frequency-matched control draws, 10 seeds, median z, 8/10 rule.
Known answers: G&B abbreviated Pliny (3 windows, truncation types) and planted truncations (latVUC, deu1912, turytc);
false claims: matched pseudo-labels in each known-answer text, generator seeds 31-33.
Voynich: T1 = o-gallows label types (general and class-internal controls), T2 = all label types.
Run: caffeinate -ims .venv/bin/python experiments/e071_label_truncation.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, math, random, re, sys, time, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

N, START = 28841, 10000
OUT = ROOT / "experiments/results/e071.json"
GB = ROOT / "data/external/gaskell_bowern_unzipped/mean/texts"
PLINY_ABBR = GB / "Historical - Latin (Abbreviated) - Technical - Pliny's Natural History.txt"
PLINY_FULL = GB / "Historical - Latin - Technical - Pliny's Natural History.txt"
PLANT_LANGS = ["latVUC", "deu1912", "turytc"]
GEN_SEEDS = [31, 32, 33]
SEEDS = list(range(1001, 1011))
DRAWS = 1000
Z_BAR = 3.0
OG = re.compile(r"^o[tkpf]")


def log(*a):
    print(*a, flush=True)


def tok_line(s):
    t = unicodedata.normalize("NFC", s.lower()).replace("’", "'").replace("ʻ", "'")
    return "".join(c if (unicodedata.category(c)[0] in "LM" or c == "'") else " " for c in t).split()


# ------------------------------------------------------------------------------------------------ measure
def ext_counts(freq):
    """EXT(w) for every type: number of distinct types having w as a proper prefix."""
    types = sorted(freq)
    ext = Counter()
    # for each type v, count every proper prefix that is itself a type
    S = set(types)
    for v in types:
        for k in range(1, len(v)):
            p = v[:k]
            if p in S:
                ext[p] += 1
    return ext


def top_ext_share(freq, w):
    e = [(v, c) for v, c in freq.items() if v != w and v.startswith(w)]
    tot = sum(c for _, c in e)
    return max(c for _, c in e) / tot if tot else float("nan")


def score(T, ext):
    return float(np.mean([math.log2(1 + ext[w]) for w in T]))


def pools(freq, candidates):
    """(length, fbin) -> candidate list; thin bins merged upward."""
    P = defaultdict(list)
    for w in candidates:
        P[(len(w), int(math.log2(freq[w])))].append(w)
    return P


def pool_for(P, w, freq):
    L, b = len(w), int(math.log2(freq[w]))
    cand = list(P.get((L, b), []))
    step = 1
    while len(cand) < 5 and step < 12:
        cand += P.get((L, b + step), []) + P.get((L, b - step), [])
        step += 1
    if len(cand) < 5:                       # no words of this length at all: neighbouring lengths, same bin first
        for dL in (1, -1):
            cand += [w for (l, bb), ws in P.items() if l == L + dL and abs(bb - b) <= 1 for w in ws]
    return cand


def ztest(T, freq, candidates, ext, seeds=SEEDS, draws=DRAWS):
    T = [w for w in T if w in freq and freq[w] >= 2]
    cands = [w for w in candidates if w not in set(T) and freq[w] >= 2]
    P = pools(freq, cands)
    plist = [pool_for(P, w, freq) for w in T]
    assert all(plist), "empty control pool"
    merged = sum(len(P.get((len(w), int(math.log2(freq[w]))), [])) < 5 for w in T)
    s_obs = score(T, ext)
    zs = []
    for sd in seeds:
        rng = random.Random(sd)
        vals = [score([rng.choice(p) for p in plist], ext) for _ in range(draws)]
        mu, sg = float(np.mean(vals)), float(np.std(vals, ddof=1))
        zs.append((s_obs - mu) / sg if sg > 0 else 0.0)
    return {"n": len(T), "S": s_obs, "merged_bins": merged, "z_median": float(np.median(zs)), "z": zs,
            "above": sum(z > Z_BAR for z in zs), "within": sum(abs(z) <= Z_BAR for z in zs),
            "top_ext_share": float(np.nanmean([top_ext_share(freq, w) for w in T]))}


def pseudo_labels(T, freq, candidates, rng):
    cands = [w for w in candidates if w not in set(T) and freq[w] >= 2]
    P = pools(freq, cands)
    return [rng.choice(pool_for(P, w, freq)) for w in T if w in freq and freq[w] >= 2]


# ------------------------------------------------------------------------------------------------ texts
def pliny_windows():
    A = PLINY_ABBR.read_text(encoding="utf-8", errors="replace").splitlines()
    F = PLINY_FULL.read_text(encoding="utf-8", errors="replace").splitlines()
    pairs = []
    for a, f in zip(A, F):
        ta, tf = tok_line(a), tok_line(f)
        if len(ta) == len(tf):
            pairs += list(zip(ta, tf))
    out = []
    for st in (0, 100000, 200000):
        win = pairs[st:st + N]
        freq = Counter(a for a, _ in win)
        trunc = {a for a, f in win if a != f and len(a) >= 2 and f.startswith(a)}
        T = sorted(w for w in trunc if freq[w] >= 2)
        out.append((f"pliny_abbr_{st}", freq, T))
    return out, len(pairs)


def planted(bid, rng):
    from e064_early_audit import tok
    w = tok(bid)[START:START + N]
    freq = Counter(w)
    pool = sorted(t for t, c in freq.items() if len(t) >= 6 and c >= 4)
    chosen = rng.sample(pool, min(150, len(pool)))
    cut = {t: t[:rng.randint(3, 5)] for t in chosen}
    out = []
    for t in w:
        out.append(cut[t] if t in cut and rng.random() < 0.5 else t)
    freq2 = Counter(out)
    T = sorted({c for c in cut.values() if freq2[c] >= 2})
    return freq2, T, len(chosen)


def generator_text(seed, gen_dir, java):
    from e032_copy_generator import generate
    work = ROOT / "data/external/e071_gen_work"
    return Counter(w for l in generate(gen_dir, java, seed, N, work) for w in l)


def voynich():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    dev = [t for t in toks if t.leaf not in locked]
    freq = Counter(t.eva for t in dev if t.mode == "prose" and t.is_clean)
    assert sum(freq.values()) == N
    lab = {t.eva for t in dev if t.mode == "label" and t.is_clean}
    T1 = sorted(w for w in lab if OG.match(w) and freq.get(w, 0) >= 2)
    T2 = sorted(w for w in lab if freq.get(w, 0) >= 2)
    general = [w for w in freq if w not in lab]
    cls = [w for w in freq if w not in lab and OG.match(w)]
    return freq, T1, T2, general, cls, sorted(locked, key=lambda x: (len(x), x))


# ------------------------------------------------------------------------------------------------ main
def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    rng = random.Random(71071)
    res = {"experiment": "E071", "known": {}, "false": {}, "voynich": {}}
    ok_known, ok_false = [], []

    log("[known answers: G&B abbreviated Pliny]")
    wins, npairs = pliny_windows()
    res["pliny_aligned_pairs"] = npairs
    for name, freq, T in wins:
        ext = ext_counts(freq); cands = [w for w in freq if w not in set(T)]
        r = ztest(T, freq, cands, ext); res["known"][name] = r; ok_known.append(r["above"] >= 8)
        log(f"  {name:18s} targets {r['n']:4d} S {r['S']:.3f} z {r['z_median']:+.2f} ({r['above']}/10 > 3) top-ext {r['top_ext_share']:.2f}")
        pl = pseudo_labels(T, freq, cands, rng)
        f = ztest(pl, freq, [w for w in cands if w not in set(pl)], ext); res["false"][name] = f; ok_false.append(f["within"] >= 8)
        log(f"  {name:18s} pseudo   {f['n']:4d} S {f['S']:.3f} z {f['z_median']:+.2f} ({f['within']}/10 within)")
    log("[known answers: planted truncations]")
    for bid in PLANT_LANGS:
        freq, T, nch = planted(bid, rng)
        ext = ext_counts(freq); cands = [w for w in freq if w not in set(T)]
        r = ztest(T, freq, cands, ext); r["planted_types"] = nch; res["known"][bid] = r; ok_known.append(r["above"] >= 8)
        log(f"  {bid:18s} targets {r['n']:4d} S {r['S']:.3f} z {r['z_median']:+.2f} ({r['above']}/10 > 3) top-ext {r['top_ext_share']:.2f}")
        pl = pseudo_labels(T, freq, cands, rng)
        f = ztest(pl, freq, [w for w in cands if w not in set(pl)], ext); res["false"][bid] = f; ok_false.append(f["within"] >= 8)
        log(f"  {bid:18s} pseudo   {f['n']:4d} S {f['S']:.3f} z {f['z_median']:+.2f} ({f['within']}/10 within)")
    log("[false claims: generator]")
    for s in GEN_SEEDS:
        freq = generator_text(s, gen_dir, java)
        ext = ext_counts(freq)
        pool = [w for w, c in freq.items() if 3 <= len(w) <= 6 and c >= 2]
        pl = rng.sample(pool, 95)
        f = ztest(pl, freq, [w for w in freq if w not in set(pl)], ext); res["false"][f"generator_{s}"] = f; ok_false.append(f["within"] >= 8)
        log(f"  generator_{s:<9d} pseudo   {f['n']:4d} S {f['S']:.3f} z {f['z_median']:+.2f} ({f['within']}/10 within)")
    valid = all(ok_known) and all(ok_false)
    res["validated"] = valid
    log(f"[validation] known {sum(ok_known)}/{len(ok_known)} pass, false-claim {sum(ok_false)}/{len(ok_false)} pass -> {'VALID' if valid else 'VOID'}")

    log("[VOYNICH]")
    freq, T1, T2, general, cls, locked = voynich()
    ext = ext_counts(freq)
    g1 = ztest(T1, freq, general, ext); c1 = ztest(T1, freq, cls, ext); g2 = ztest(T2, freq, general, ext)
    res["voynich"] = {"T1_general": g1, "T1_class": c1, "T2_general": g2, "T1": T1, "locked_test_excluded": locked,
                      "T1_ext": {w: ext[w] for w in T1}}
    log(f"  T1 general  n {g1['n']} S {g1['S']:.3f} z {g1['z_median']:+.2f} ({g1['above']}/10 > 3) top-ext {g1['top_ext_share']:.2f}")
    log(f"  T1 class    n {c1['n']} S {c1['S']:.3f} z {c1['z_median']:+.2f} ({c1['above']}/10 > 3)")
    log(f"  T2 general  n {g2['n']} S {g2['S']:.3f} z {g2['z_median']:+.2f} ({g2['above']}/10 > 3) top-ext {g2['top_ext_share']:.2f}")
    if not valid:
        v, f = "VOID", "none"
    elif g1["above"] >= 8 and c1["above"] >= 8 and g2["z_median"] > 0:
        v, f = "ABBREVIATION-LIKE", "L-abbrev x3"
    elif g1["above"] >= 8:
        v, f = "CLASS MORPHOLOGY (INCONCLUSIVE)", "none"
    elif sum(z <= Z_BAR for z in g1["z"]) >= 8:
        v, f = "NOT ABBREVIATION-LIKE", "L-abbrev x0.6"
    else:
        v, f = "INCONCLUSIVE (seed rule)", "none"
    res.update(verdict=v, factor=f, runtime_s=time.time() - t0)
    log(f"VERDICT {v} | factor {f} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
