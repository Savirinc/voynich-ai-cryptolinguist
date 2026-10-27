"""E085: do two herbal pages that show the same plant (by published identifications) share vocabulary? Language-free
bridge test for the crib road. Known answer: Culpeper's entries about the same kind of plant. See reports/E085_PREREG.md.
Run: .venv/bin/python experiments/e085_same_plant_pages.py
"""
from __future__ import annotations

import csv, json, random, re, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
OUT = ROOT / "experiments/results/e085.json"
SEED, DRAWS, TOPK, MAXTOK = 85085, 10000, 100, 200
CULP = ROOT / "data/external/pg_herbal/pg49513.txt"
GENERIC = {"TREE", "BUSH", "GRAS", "WOOD", "FLOWER", "WORT", "TONGUE"}


def log(*a):
    print(*a, flush=True)


def jacc(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


# ---------------------------------------------------------------- Culpeper known answer
def culpeper_entries():
    lines = CULP.read_text(encoding="utf-8").splitlines()
    head = re.compile(r"^    ([A-Z][A-Z’'., -]{2,60})$")
    start = next(i for i, l in enumerate(lines) if l.strip() == "AMARA DULCIS.")
    end = next(i for i, l in enumerate(lines) if i > start and l.strip() == "ENGLISH PHYSICIAN")
    ents, cur, buf = [], None, []
    for l in lines[start:end]:
        m = head.match(l)
        if m:
            if cur and len(buf) > 30:
                ents.append((cur, buf))
            cur, buf = m.group(1), []
        else:
            buf += re.findall(r"[a-z]+", l.lower())
    if cur and len(buf) > 30:
        ents.append((cur, buf))
    return ents


def culp_group(h):
    h = re.split(r",| OR ", h.replace("’", "'"))[0].strip(" .")
    w = [x for x in h.split() if x not in ("THE",)]
    k = w[-1] if w else h
    k = k.replace("-TREE", "")
    return k[:-1] if k.endswith("S") and len(k) > 4 else k


def known_answer(rng):
    ents = culpeper_entries()
    freq = Counter(w for _, b in ents for w in b); stop = {w for w, _ in freq.most_common(TOPK)}
    sets = [{w for w in b[:MAXTOK] if w not in stop} for _, b in ents]
    grp = [culp_group(h) for h, _ in ents]
    by = defaultdict(list)
    for i, g in enumerate(grp):
        by[g].append(i)
    pairs = [p for g, ix in by.items() if len(ix) >= 2 and g not in GENERIC for p in combinations(ix, 2)]
    obs = float(np.mean([jacc(sets[a], sets[b]) for a, b in pairs]))
    n = len(ents); null = []
    for _ in range(DRAWS):
        v = []
        for _p in pairs:
            while True:
                a, b = rng.randrange(n), rng.randrange(n)
                if a != b and grp[a] != grp[b]:
                    break
            v.append(jacc(sets[a], sets[b]))
        null.append(float(np.mean(v)))
    p = (1 + sum(x >= obs for x in null)) / (1 + DRAWS)
    return {"entries": len(ents), "pairs": len(pairs), "groups": {g: [ents[i][0] for i in ix] for g, ix in by.items() if len(ix) >= 2 and g not in GENERIC},
            "obs": obs, "null_mean": float(np.mean(null)), "p": p}


# ---------------------------------------------------------------- Voynich
def voynich_pages():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    pages, meta = defaultdict(list), {}
    for t in toks:
        if t.leaf in locked or t.illustration != "H" or t.mode != "prose":
            continue
        meta[t.folio] = (t.currier, t.quire, t.bifolio_id)
        if t.is_clean:
            pages[t.folio].append(t.eva)
    return pages, meta, sorted(locked, key=lambda x: (len(x), x))


def main():
    rng = random.Random(SEED)
    ka = known_answer(rng)
    log(f"[known answer] Culpeper: {ka['entries']} entries, {ka['pairs']} same-kind pairs; vocabulary overlap {ka['obs']:.4f} vs random {ka['null_mean']:.4f}, p {ka['p']:.4f}")
    valid = ka["p"] < 0.01
    pages, meta, locked = voynich_pages()
    allw = Counter(w for ws in pages.values() for w in ws); stop = {w for w, _ in allw.most_common(TOPK)}
    sets = {f: {w for w in ws[:MAXTOK] if w not in stop} for f, ws in pages.items()}
    first = {f: ws[0] for f, ws in pages.items() if ws}
    ids = {r["folio"]: r["group"] for r in csv.DictReader(open(ROOT / "reports/data/herbal_ids_voynichnu.csv"))}
    ids = {f: g for f, g in ids.items() if f in pages}
    by = defaultdict(list)
    for f, g in ids.items():
        by[g].append(f)
    pairs = [(a, b) for g, fs in by.items() if len(fs) >= 2 for a, b in combinations(sorted(fs), 2) if meta[a][2] != meta[b][2]]
    def sims(a, b):
        return jacc(sets[a], sets[b]), float(first[a] == first[b])
    obs = np.mean([sims(a, b) for a, b in pairs], axis=0)
    herbal = sorted(pages)
    key = lambda a, b: (tuple(sorted((meta[a][0], meta[b][0]))), meta[a][1] == meta[b][1])
    pool = defaultdict(list)
    for a, b in combinations(herbal, 2):
        if meta[a][2] != meta[b][2] and not (a in ids and b in ids and ids[a] == ids[b]):
            pool[key(a, b)].append((a, b))
    null = []
    for _ in range(DRAWS):
        v = [sims(*rng.choice(pool[key(a, b)])) for a, b in pairs]
        null.append(np.mean(v, axis=0))
    null = np.array(null)
    p = [(1 + int((null[:, k] >= obs[k]).sum())) / (1 + DRAWS) for k in range(2)]
    log(f"[VOYNICH] {len(pairs)} same-plant page pairs (different sheets) from {sum(len(v) >= 2 for v in by.values())} plants")
    log(f"  vocabulary overlap {obs[0]:.4f} vs matched random {null[:, 0].mean():.4f} (p {p[0]:.4f}) | identical first word {obs[1]:.3f} vs {null[:, 1].mean():.3f} (p {p[1]:.4f})")
    per = {g: [(a, b, round(jacc(sets[a], sets[b]), 3), first[a], first[b]) for a, b in pairs if ids[a] == g] for g in by if len(by[g]) >= 2}
    for g, v in per.items():
        log(f"  {g}: {v}")
    if not valid:
        verdict, factor = "VOID (known answer failed)", "none"
    elif p[0] < 0.01:
        verdict, factor = "LINK: same-plant pages share vocabulary", "M x1/3; crib attack next"
    else:
        verdict, factor = "NO LINK", "M x1.4"
    log(f"VERDICT {verdict} | {factor}")
    OUT.write_text(json.dumps({"experiment": "E085", "known_answer": ka, "pairs": pairs, "obs": obs.tolist(), "null_mean": null.mean(0).tolist(),
                               "p": p, "per_plant": per, "verdict": verdict, "factor": factor, "locked_test_excluded": locked}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
