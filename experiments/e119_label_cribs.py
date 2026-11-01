"""E119 (Arham, move 5): labels as name-cribs in the high-information slot. See reports/E119_PREREG.md.

Crib: a label beside a drawing is a name; in a herbal or picture book, names are introduced at the start of a paragraph
(X117: the Voynich's surprise sits in paragraph-first lines). So label words should be over-represented in
paragraph-first lines of the prose, beyond words of the same shape and frequency.
For each text: LABELS = label word types with prose frequency 2..50. For each, up to 5 MATCHED non-label prose types with
the same first two letters and the nearest prose frequency (no reuse within a label; ties by a fixed shuffle).
s(w) = share of w's prose tokens that stand in paragraph-first lines.
ENRICH = mean over labels of [s(label) - mean s(its matches)] (labels with >= 1 match).
Texts:
  Voynich: DEV prose (para_start flags from the transcription); labels = DEV tokens in mode 'label' (not circle/radial).
  Culpeper (positive, real): paragraph-first lines = first line after a blank line; labels = words (>= 4 letters) of the
    herb headings.
  Planted (positive, 10): E032 copy-generator seeds; 150 rare words (generator frequency 2..20) are 'names', one per
    page; each paragraph-first line of the page gets its name at a random slot with p 0.6, and one other line of the
    page with p 0.6; labels = the names.
  Null (70): 10 E032 + 50 E100 generator runs (paragraph = line after a line shorter than 40 characters) and 10 dice
    books (E114 best set, Voynich page shapes and paragraph flags); labels = the Voynich's own label types.
Validity: Culpeper ENRICH and every planted ENRICH > null max.
  ENRICHED      Voynich > null max                                 -> M x 1/3
  NOT ENRICHED  Voynich <= null p90                                -> M x 1.5 (weak absence: labels need not be names)
  BETWEEN / VOID                                                    -> none
Rule 8: Voynich within 0.5 bootstrap-sd (over label types) of null max or null p90 -> 10 bootstrap replicates must
give the same verdict >= 8 times, else BETWEEN.
Unscored: ENRICH by section of the label; own-sheet variant (label words in first lines of pages on the label's own
sheet vs other sheets).
Run: caffeinate -ims .venv/bin/python experiments/e119_label_cribs.py [--dev]   (--dev: controls only)
"""
from __future__ import annotations

import argparse, json, math, random, re, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e093_explanation_model as E93  # noqa: E402
import e114_dice_generator as D  # noqa: E402
from e117_surprise_map import words  # noqa: E402

SEED = 119119
OUT = ROOT / "experiments/results/e119.json"
CULP = ROOT / "data/external/pg_herbal/pg49513.txt"
E032W, E100W = ROOT / "experiments/results/e032_work", ROOT / "experiments/results/e100_work"
DICE_SET = ("2d6", "page", (20, 60, 40))
FMIN, FMAX, NMATCH = 2, 50, 5


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ statistic
def enrich(lines, labels, rng, by=None):
    """lines: list of (tokens, is_para_first). labels: set of label types. by: optional {label: group}"""
    tot, head = Counter(), Counter()
    for l, f in lines:
        for w in l:
            tot[w] += 1; head[w] += f
    s = {w: head[w] / tot[w] for w in tot}
    L = sorted(w for w in labels if FMIN <= tot[w] <= FMAX)
    pool = defaultdict(list)
    for w in sorted(tot):
        if w not in labels:
            pool[w[:2]].append(w)
    for k in pool:
        rng.shuffle(pool[k])
    diffs, used = {}, set()
    for w in L:
        cand = sorted((c for c in pool[w[:2]] if c not in used), key=lambda c: abs(math.log(tot[c] / tot[w])))[:NMATCH]
        if not cand:
            continue
        used.update(cand)
        diffs[w] = s[w] - float(np.mean([s[c] for c in cand]))
    v = list(diffs.values())
    out = {"ENRICH": float(np.mean(v)) if v else float("nan"), "n_labels": len(v),
           "base_head_share": sum(head.values()) / sum(tot.values())}
    if by is not None:
        g = defaultdict(list)
        for w, d in diffs.items():
            g[by.get(w, "?")].append(d)
        out["by_group"] = {k: [float(np.mean(x)), len(x)] for k, x in sorted(g.items())}
    out["_diffs"] = diffs
    return out


def boot(diffs, rng, n=1000):
    v = np.array(list(diffs.values())); r = np.random.default_rng(rng.randrange(1 << 30))
    return [float(v[r.integers(0, len(v), len(v))].mean()) for _ in range(n)]


# ------------------------------------------------------------------ texts
def voynich():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    L, F, meta = defaultdict(list), {}, {}
    lab, labsec, labsheet = set(), {}, defaultdict(set)
    for t in toks:
        if t.leaf in locked:
            continue
        if t.mode == "prose":
            k = (t.folio, t.line_no); F[k] = F.get(k, False) or bool(t.para_start)
            if t.is_clean:
                L[k].append(t.eva)
            meta[t.folio] = t.bifolio_id
        elif t.mode == "label" and t.is_clean:
            lab.add(t.eva); labsec.setdefault(t.eva, t.illustration); labsheet[t.eva].add(t.bifolio_id)
    key = lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f)
    order = sorted(L, key=lambda k: (key(k[0]), k))
    lines = [(L[k], F[k]) for k in order if L[k]]
    sheets = [meta[k[0]] for k in order if L[k]]
    return lines, lab, labsec, labsheet, sheets, [F[k] for k in order]


def culpeper():
    raw = CULP.read_text(encoding="utf-8", errors="ignore")
    raw = raw[raw.find("    AMARA DULCIS."):raw.find("*** END")]
    heads, lines, prev_blank = set(), [], True
    for ln in raw.splitlines():
        if re.match(r"^ {4}[A-Z][A-Z' ,.-]+\.\s*$", ln):
            heads.update(w for w in words(ln) if len(w) >= 4); prev_blank = True; continue
        if not ln.strip():
            prev_blank = True; continue
        ws = words(ln)
        if ws:
            lines.append((ws, prev_blank)); prev_blank = False
    return lines, heads


def gen_lines(path):
    out, prev_short = [], True
    for ln in path.read_text().splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        out.append((ln.split(), prev_short)); prev_short = len(ln.strip()) < 40
    return out


def planted(path, rng):
    ls = gen_lines(path)
    tot = Counter(w for l, _ in ls for w in l)
    rare = sorted(w for w, c in tot.items() if 2 <= c <= 20); rng.shuffle(rare)
    names = rare[:150]; out = []
    for p in range(0, len(ls), 29):
        page = [(list(l), f) for l, f in ls[p:p + 29]]
        name = names[(p // 29) % len(names)]
        for l, f in page:
            if f and rng.random() < 0.6:
                l[rng.randrange(len(l))] = name
        others = [l for l, f in page if not f]
        if others and rng.random() < 0.6:
            l = rng.choice(others); l[rng.randrange(len(l))] = name
        out += page
    return out, set(names)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dev", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    vlines, vlab, labsec, labsheet, sheets, vflags = voynich()
    log(f"Voynich prose lines {len(vlines)} tokens {sum(len(l) for l, _ in vlines)} para-first {sum(f for _, f in vlines)} | label types {len(vlab)}")
    R = {"positive": {}, "null": {}}
    cl, ch = culpeper(); m = enrich(cl, ch, rng); m.pop("_diffs"); R["positive"]["culpeper"] = m
    log(f"pos culpeper ENRICH {m['ENRICH']:+.4f} n {m['n_labels']} base {m['base_head_share']:.3f}")
    gfiles = [d / "generate/generated_text.txt" for d in sorted(E032W.iterdir()) if (d / "generate/generated_text.txt").exists()]
    for f in gfiles:
        pl, nm = planted(f, rng); m = enrich(pl, nm, rng); m.pop("_diffs"); R["positive"]["planted_" + f.parts[-3]] = m
        log(f"pos planted {f.parts[-3]:10s} ENRICH {m['ENRICH']:+.4f} n {m['n_labels']}")
    gfiles += [d / "generate/generated_text.txt" for d in sorted(E100W.iterdir())]
    for f in gfiles:
        m = enrich(gen_lines(f), vlab, rng); m.pop("_diffs"); R["null"][f.parts[-3]] = m
        log(f"null {f.parts[-3]:24s} ENRICH {m['ENRICH']:+.4f} n {m['n_labels']} base {m['base_head_share']:.3f}")
    pages, meta, _ = E93.voynich(); shape = [[len(l) for l in p] for p in pages]; ms = D.masters(pages, DICE_SET[2])
    assert sum(map(len, shape)) == len(vlines)
    for s in range(1, 11):
        bk = [l for p in D.book(DICE_SET, ms, shape, s) for l in p]
        m = enrich([(l, f) for l, (_, f) in zip(bk, vlines)], vlab, rng); m.pop("_diffs"); R["null"][f"dice_seed{s}"] = m
        log(f"null dice_seed{s:<15d} ENRICH {m['ENRICH']:+.4f} n {m['n_labels']}")
    nv = np.array([v["ENRICH"] for v in R["null"].values()])
    nmax, np90 = float(nv.max()), float(np.percentile(nv, 90))
    pos = [v["ENRICH"] for v in R["positive"].values()]
    valid = all(x > nmax for x in pos)
    log(f"null max {nmax:+.4f} p90 {np90:+.4f} | positives min {min(pos):+.4f} | VALID {valid}")
    res = {"experiment": "E119", "seed": SEED, "results": R, "null_max": nmax, "null_p90": np90, "valid": bool(valid)}
    if not a.dev:
        V = enrich(vlines, vlab, rng, by=labsec); d = V.pop("_diffs")
        bs = boot(d, rng); V["sd"] = float(np.std(bs, ddof=1))

        def verdict(x):
            return "ENRICHED" if x > nmax else "NOT ENRICHED" if x <= np90 else "BETWEEN"
        v = verdict(V["ENRICH"]) if valid else "VOID"
        if valid and min(abs(V["ENRICH"] - b) for b in (nmax, np90)) < 0.5 * V["sd"]:
            rv = [verdict(x) for x in bs[:10]]; res["seed_check"] = rv
            if sum(r == v for r in rv) < 8:
                v = "BETWEEN"
        fM = {"ENRICHED": 1 / 3, "NOT ENRICHED": 1.5}.get(v, 1.0)
        # unscored own-sheet variant: label words in first lines of their own sheet vs other sheets
        own = oth = no = nt = 0
        for (l, f), sh in zip(vlines, sheets):
            if not f:
                continue
            for w in l:
                if w in vlab:
                    if sh in labsheet[w]:
                        own += 1
                    else:
                        oth += 1
        for (l, f), sh in zip(vlines, sheets):
            for w in l:
                if w in vlab:
                    if sh in labsheet[w]:
                        no += 1
                    else:
                        nt += 1
        V["own_sheet_head_share"] = own / max(1, no); V["other_sheet_head_share"] = oth / max(1, nt)
        res.update(voynich=V, verdict=v, factor_M=fM)
        log(f"VOYNICH ENRICH {V['ENRICH']:+.4f} (sd {V['sd']:.4f}, n {V['n_labels']}, base {V['base_head_share']:.3f}) | by section {V['by_group']}")
        log(f"own-sheet head share {V['own_sheet_head_share']:.3f} vs other {V['other_sheet_head_share']:.3f}")
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e119_dev.json" if a.dev else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
