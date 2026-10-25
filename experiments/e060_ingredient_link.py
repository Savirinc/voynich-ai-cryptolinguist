"""E060: the ingredient link. Do pharma labels recur in the recipes (stars section)? See reports/E060_PREREG.md.

HIT = share of eligible label types (>= 3 glyphs, DEV count >= 2) found at least once in the target text.
Null: 2,000 draws replacing each label type by a pool type of the same frequency band (DEV count: exact 2-10, bands
11-20, 21-50, 51+), pool = the source section's own non-label text types. p one-sided; excess = HIT - mean(null).
Primary: pharma labels -> stars prose. Secondary (reported): herbal-A first words -> stars prose.
Controls: Culpeper plant-name headings -> first 10,000 words of its Directions section (20 subsamples of 90 names,
500 draws; power >= 0.8); 10 Timm & Schinner samples (seeds 21-30) with pseudo-labels (0/10 at p < 0.01).
Run: caffeinate -ims .venv/bin/python experiments/e060_ingredient_link.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, random, re, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

SEED = 60060
OUT = ROOT / "experiments/results/e060.json"
DRAWS, DRAWS_CUL, DRAWS_GEN = 2000, 500, 1000
MIN_GLYPHS, MIN_COUNT, N_SUB, SUB_SIZE = 3, 2, 20, 90
GEN_SEEDS, GEN_N = range(21, 31), 28841
PH_START, PH_LEN, TG_START, TG_LEN = 20000, 1786, 10041, 9959
CUL_TARGET_WORDS = 10000
STOP = {"the", "and", "its", "with", "for", "from", "common", "great", "small", "wild", "garden", "water", "white",
        "black", "red", "yellow", "sweet", "tree", "herb", "called", "also", "english"}
HEAD = re.compile(r"^ {2,}[A-Z][A-Z ,'’-]+\.? *$")


def log(*a):
    print(*a, flush=True)


def band(c):
    return c if c <= 10 else 11 if c <= 20 else 21 if c <= 50 else 51


def run_test(labels, pool, target_types, counts, rng, draws, exclude_pool_labels=True):
    """labels: list of eligible label types; pool: iterable of candidate types; counts: type -> total count."""
    labels = sorted(set(labels))
    pool_set = set(pool) - (set(labels) if exclude_pool_labels else set())
    bypool = defaultdict(list)
    for w in pool_set:
        if counts.get(w, 0) >= MIN_COUNT:
            bypool[band(counts[w])].append(w)
    for b in bypool:
        bypool[b].sort()
    hit = float(np.mean([w in target_types for w in labels]))
    null = []
    for _ in range(draws):
        used, got = set(), []
        for w in labels:
            b = band(counts[w])
            cand = bypool.get(b) or bypool[min(bypool, key=lambda x: abs(x - b))]
            fresh = [x for x in cand if x not in used] or cand
            x = rng.choice(fresh); used.add(x); got.append(x in target_types)
        null.append(float(np.mean(got)))
    null = np.array(null)
    p = float((1 + np.sum(null >= hit)) / (len(null) + 1))
    found = sorted(w for w in labels if w in target_types)
    return dict(n_labels=len(labels), hit=hit, null_mean=float(null.mean()), null_sd=float(null.std()),
                excess=hit - float(null.mean()), ratio=hit / float(null.mean()) if null.mean() else float("nan"),
                p=p, found=found, pool_types=len(pool_set))


# ------------------------------------------------------------------------------------------------ Voynich
def voynich(rng):
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    D = [t for t in toks if t.leaf not in locked and t.is_clean]
    counts = Counter(t.eva for t in D)
    S = [t for t in D if t.illustration == "S" and t.mode == "prose"]
    target = {t.eva for t in S}
    para = defaultdict(set)
    for t in S:
        para[t.eva].add((t.folio, t.line_no))      # lines, as a proxy for paragraphs when reporting
    # primary
    labels = [t.eva for t in D if t.illustration == "P" and t.mode == "label" and len(t.eva) >= MIN_GLYPHS]
    elig = sorted({w for w in labels if counts[w] >= MIN_COUNT})
    pool = {t.eva for t in D if t.illustration == "P" and t.mode != "label"}
    prim = run_test(elig, pool, target, counts, rng, DRAWS)
    prim["found_detail"] = {w: dict(dev_count=counts[w], stars_lines=len(para[w])) for w in prim["found"]}
    prim["label_tokens"], prim["label_types_all"] = len(labels), len(set(labels))
    log(f"[VOY primary] eligible {prim['n_labels']} of {len(set(labels))} types | HIT {prim['hit']:.3f} null {prim['null_mean']:.3f} "
        f"(sd {prim['null_sd']:.3f}) excess {prim['excess']:+.3f} ratio {prim['ratio']:.2f} p {prim['p']:.4f}")
    log(f"   found: {prim['found_detail']}")
    # secondary: herbal A first words
    H = [t for t in D if t.illustration == "H" and t.mode == "prose" and t.currier == "A"]
    first = {}
    for t in H:
        if t.line_no == 1 and t.idx == 0 and t.folio not in first:
            first[t.folio] = t.eva
    fw = sorted({w for w in first.values() if counts[w] >= MIN_COUNT and len(w) >= MIN_GLYPHS})
    pool2 = {t.eva for t in H if t.eva not in set(first.values())}
    sec = run_test(fw, pool2, target, counts, rng, DRAWS)
    sec["pages"] = len(first)
    log(f"[VOY secondary] herbal-A first words eligible {sec['n_labels']} of {len(set(first.values()))} | HIT {sec['hit']:.3f} "
        f"null {sec['null_mean']:.3f} excess {sec['excess']:+.3f} p {sec['p']:.4f} found {sec['found']}")
    return dict(primary=prim, secondary=sec, target_tokens=len(S), target_types=len(target),
                locked_test_excluded=sorted(locked, key=lambda x: (len(x), x)))


# ------------------------------------------------------------------------------------------------ Culpeper
def words(s):
    return re.findall(r"[a-z]+", s.lower())


def culpeper(rng):
    lines = (ROOT / "data/external/pg_herbal/pg49513.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
    end = next(i for i, l in enumerate(lines) if l.startswith("DIRECTIONS FOR MAKING SYRUPS"))
    start = next(i for i, l in enumerate(lines) if HEAD.match(l) and "AMARA" in l or ("ADDER" in l and HEAD.match(l)))
    names, body = set(), []
    for l in lines[start:end]:
        if HEAD.match(l):
            names |= {w for w in words(l) if len(w) >= MIN_GLYPHS and w not in STOP}
        else:
            body += words(l)
    allw = words("\n".join(lines))
    counts = Counter(allw)
    tail = words("\n".join(lines[end:]))[:CUL_TARGET_WORDS]
    target = set(tail)
    elig = sorted(w for w in names if counts[w] >= MIN_COUNT)
    pool = set(body) - names
    full = run_test(elig, pool, target, counts, rng, DRAWS_CUL)
    log(f"[CUL full] names {len(names)} eligible {len(elig)} | HIT {full['hit']:.3f} null {full['null_mean']:.3f} excess {full['excess']:+.3f} p {full['p']:.4f}")
    subs = []
    for i in range(N_SUB):
        sub = rng.sample(elig, min(SUB_SIZE, len(elig)))
        r = run_test(sub, pool, target, counts, rng, DRAWS_CUL)
        subs.append(dict(hit=r["hit"], null_mean=r["null_mean"], p=r["p"]))
    power = float(np.mean([s["p"] < 0.01 for s in subs]))
    log(f"[CUL power] {sum(s['p'] < 0.01 for s in subs)}/{N_SUB} subsamples of {SUB_SIZE} at p<0.01 -> power {power:.2f} "
        f"{'PASS' if power >= 0.8 else 'FAIL'}; median sub HIT {np.median([s['hit'] for s in subs]):.3f} null {np.median([s['null_mean'] for s in subs]):.3f}")
    return dict(full=full, subsamples=subs, power=power, pass_=power >= 0.8, target_words=len(tail), n_names=len(names))


# ------------------------------------------------------------------------------------------------ generator
def generator(gen_dir, java, voy_labels_counts, rng):
    from e032_copy_generator import generate
    work = ROOT / "data/external/e060_gen_work"
    res, fails = [], 0
    for s in GEN_SEEDS:
        toks = [w for l in generate(gen_dir, java, s, GEN_N, work) for w in l]
        counts = Counter(toks)
        ph = toks[PH_START:PH_START + PH_LEN]
        tg = set(toks[TG_START:TG_START + TG_LEN])
        ph_types = sorted(set(ph))
        byband = defaultdict(list)
        for w in ph_types:
            if counts[w] >= MIN_COUNT and len(w) >= MIN_GLYPHS:
                byband[band(counts[w])].append(w)
        pseudo, used = [], set()
        for c in voy_labels_counts:            # one pseudo-label per real eligible label, same band
            b = band(c)
            cand = byband.get(b) or byband[min(byband, key=lambda x: abs(x - b))]
            fresh = [x for x in cand if x not in used] or cand
            x = rng.choice(fresh); used.add(x); pseudo.append(x)
        r = run_test(sorted(set(pseudo)), set(ph_types), tg, counts, rng, DRAWS_GEN)
        fails += r["p"] < 0.01
        res.append(dict(seed=s, n_labels=r["n_labels"], hit=r["hit"], null_mean=r["null_mean"], excess=r["excess"], p=r["p"]))
        log(f"[GEN seed {s}] pseudo-labels {r['n_labels']} HIT {r['hit']:.3f} null {r['null_mean']:.3f} excess {r['excess']:+.3f} p {r['p']:.4f}")
    log(f"[GEN] {fails}/10 at p<0.01 -> {'PASS' if fails == 0 else 'FAIL'}")
    return dict(samples=res, false_positives=fails, pass_=fails == 0)


# ------------------------------------------------------------------------------------------------ main
def main():
    global SEED, OUT
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    if len(sys.argv) > 3:
        SEED = int(sys.argv[3]); OUT = ROOT / f"experiments/results/e060_seed{SEED}.json"
    t0 = time.time()
    res = {"experiment": "E060", "seed": SEED}
    res["culpeper"] = culpeper(random.Random(SEED + 1))
    V = voynich(random.Random(SEED + 2))
    res["voynich"] = V
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    D = [t for t in toks if t.leaf not in locked and t.is_clean]
    counts = Counter(t.eva for t in D)
    lab_counts = sorted(counts[w] for w in {t.eva for t in D if t.illustration == "P" and t.mode == "label" and len(t.eva) >= MIN_GLYPHS} if counts[w] >= MIN_COUNT)
    res["generator"] = generator(gen_dir, java, lab_counts, random.Random(SEED + 3))
    valid = res["culpeper"]["pass_"] and res["generator"]["pass_"]
    p, ex = V["primary"]["p"], V["primary"]["excess"]
    if not valid:
        v = "VOID"
    elif p < 0.01 and ex > 0:
        v = "FOUND"
    elif p >= 0.05:
        v = "NOT FOUND"
    else:
        v = "INCONCLUSIVE"
    res["verdict"] = v
    res["factors"] = {"FOUND": "L x3, C x3; L-practical x10 within L", "NOT FOUND": "L x0.82, C x0.9; L-practical x0.6 within L"}.get(v, "none")
    res["runtime_s"] = time.time() - t0
    log(f"VERDICT {v} (controls {'valid' if valid else 'FAILED'}; primary p {p:.4f} excess {ex:+.3f}) in {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
