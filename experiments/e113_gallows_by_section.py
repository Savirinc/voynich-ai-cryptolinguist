"""E113 (Arham, Reddit idea R12): do gallows letters change by section, within the same scribe? See reports/E113_PREREG.md.

Tokens: DEV clean tokens of all modes, page order, excluding paragraph-first lines (para_start). For each scribe with
>= 2 sections of >= 3 pages each (sections with < 3 pages of that scribe are dropped), a section x gallows (t, k, p, f
glyph counts) table; G = likelihood-ratio statistic. TOTAL = sum over those scribes.
Null (keeps drift/sheet clustering): for each scribe, its page sequence keeps its order and its section-label sequence
is rotated by a random offset (all offsets equally likely, independently per scribe); 2,000 draws. p = share >= observed.
Known answers: 10 copy-generator stretches poured token-for-token into the same token slots (same pages, scribes,
sections): UNPLANTED, and PLANTED where in each eligible scribe's smallest section 30% of k glyphs become t.
Validity: unplanted p < 0.01 in <= 2 of 10; planted p < 0.01 in >= 8 of 10.
  SECTION-SPECIFIC  Voynich p < 0.01;  WEAK  0.01 <= p < 0.05;  NOT SECTION-SPECIFIC  p >= 0.05;  VOID if invalid.
Rule 8: if 0.005 <= p <= 0.02 or 0.035 <= p <= 0.07, 10 fresh seeds (2,000 draws each) must give the same verdict (>= 8).
No Bayes factor. Unscored: per-scribe G and p; p and f merged (E110: one letter); paragraph-first lines included.
Run: caffeinate -ims .venv/bin/python experiments/e113_gallows_by_section.py [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402

SEED = 113113
OUT = ROOT / "experiments/results/e113.json"


def load(include_para=False):
    _, toks = parse(); L = set(locked_test_leaves(toks))
    order, meta, slots = [], {}, []
    for t in toks:
        if t.leaf in L or not t.is_clean or not t.eva or (t.para_start and not include_para):
            continue
        if t.folio not in meta:
            meta[t.folio] = (str(t.hand), str(t.illustration)); order.append(t.folio)
        slots.append((t.folio, t.eva))
    order.sort(key=lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f))
    return order, meta, slots, sorted(L)


def page_counts(slots, glyphs):
    pc = defaultdict(Counter)
    for f, w in slots:
        for g in glyphs:
            pc[f][g] += w.count(g)
    return pc


def eligible(order, meta):
    out = {}
    for h in sorted({v[0] for v in meta.values()}):
        pages = [f for f in order if meta[f][0] == h]
        secs = Counter(meta[f][1] for f in pages)
        keep = {s for s, n in secs.items() if n >= 3}
        if len(keep) >= 2:
            out[h] = [f for f in pages if meta[f][1] in keep]
    return out


def G_of(pages, labels, pc, glyphs):
    tab = defaultdict(Counter)
    for f, s in zip(pages, labels):
        tab[s].update({g: pc[f][g] for g in glyphs})
    secs = list(tab); tot = Counter()
    for s in secs:
        tot.update(tab[s])
    n = sum(tot.values()); G = 0.0
    for s in secs:
        ns = sum(tab[s].values())
        for g in glyphs:
            o = tab[s][g]; e = ns * tot[g] / n if n else 0
            if o > 0 and e > 0:
                G += 2 * o * np.log(o / e)
    return G


def test(order, meta, pc, glyphs, rng, ndraw):
    el = eligible(order, meta); obs, per, lab = 0.0, {}, {}
    for h, pages in el.items():
        lab[h] = [meta[f][1] for f in pages]
        per[h] = G_of(pages, lab[h], pc, glyphs); obs += per[h]
    ge = 0
    for _ in range(ndraw):
        tot = 0.0
        for h, pages in el.items():
            k = rng.randrange(len(pages)); l = lab[h][k:] + lab[h][:k]
            tot += G_of(pages, l, pc, glyphs)
        ge += tot >= obs - 1e-9
    return obs, (ge + 1) / (ndraw + 1), per, {h: len(p) for h, p in el.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    rng = random.Random(SEED)
    order, meta, slots, locked = load()
    el = eligible(order, meta)
    print("eligible scribes:", {h: Counter(meta[f][1] for f in p) for h, p in el.items()}, "tokens", len(slots), flush=True)
    G4 = "tkpf"; nd = 300 if a.smoke else 2000
    gflat = [w for l in gen_lines() for w in l]; N = len(slots)
    KA = {"unplanted": [], "planted": []}
    for s in range(3 if a.smoke else 10):
        gt = gflat[s * N:(s + 1) * N]
        gs = [(f, w) for (f, _), w in zip(slots, gt)]
        KA["unplanted"].append(test(order, meta, page_counts(gs, G4), G4, rng, nd)[1])
        small = {h: min(Counter(meta[f][1] for f in p).items(), key=lambda x: x[1])[0] for h, p in el.items()}
        gp = []
        for f, w in gs:
            h, sec = meta[f]
            if h in small and sec == small[h]:
                w = "".join(("t" if (c == "k" and rng.random() < 0.3) else c) for c in w)
            gp.append((f, w))
        KA["planted"].append(test(order, meta, page_counts(gp, G4), G4, rng, nd)[1])
        print(f"gen{s}: unplanted p {KA['unplanted'][-1]:.4f} | planted p {KA['planted'][-1]:.4f}", flush=True)
    need = (2, 8) if not a.smoke else (1, 2)
    valid = sum(p < 0.01 for p in KA["unplanted"]) <= need[0] and sum(p < 0.01 for p in KA["planted"]) >= need[1]
    res = {"experiment": "E113", "seed": SEED, "eligible": {h: dict(Counter(meta[f][1] for f in p)) for h, p in el.items()},
           "known_answers": KA, "valid": bool(valid), "locked_test_excluded": locked}
    print("VALID", valid, flush=True)
    if not a.smoke:
        pc = page_counts(slots, G4)
        obs, p, per, npg = test(order, meta, pc, G4, rng, 2000)
        verdict = lambda p: "SECTION-SPECIFIC" if p < 0.01 else ("WEAK" if p < 0.05 else "NOT SECTION-SPECIFIC")
        v = verdict(p) if valid else "VOID"
        if valid and (0.005 <= p <= 0.02 or 0.035 <= p <= 0.07):
            reps = [verdict(test(order, meta, pc, G4, random.Random(SEED + 900 + s), 2000)[1]) for s in range(10)]
            res["seed_check"] = reps
            if sum(r == v for r in reps) < 8:
                v = "WEAK"
        # unscored
        per_p = {}
        for h, pages in el.items():
            m1 = {f: meta[f] for f in pages}
            per_p[h] = test(pages, m1, pc, G4, random.Random(SEED + 5), 2000)[:2]
        tables = {h: {s: dict(sum((Counter({g: pc[f][g] for g in G4}) for f in pages if meta[f][1] == s), Counter())) for s in sorted({meta[f][1] for f in pages})} for h, pages in el.items()}
        merged = {f: Counter({"t": c["t"], "k": c["k"], "P": c["p"] + c["f"]}) for f, c in pc.items()}
        pm = test(order, meta, merged, "tkP", random.Random(SEED + 6), 2000)[:2]
        o2, m2, s2, _ = load(include_para=True)
        pinc = test(o2, m2, page_counts(s2, G4), G4, random.Random(SEED + 7), 2000)[:2]
        res.update(G=obs, p=p, verdict=v, per_scribe_G=per, per_scribe_G_p=per_p, tables=tables, pf_merged=pm, with_para_lines=pinc)
        print(f"VOYNICH G {obs:.1f} p {p:.4f} -> {v}\nper scribe (G, p) {per_p}\ntables {tables}\np+f merged {pm} | with paragraph lines {pinc}")
    OUT.with_name("e113_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
