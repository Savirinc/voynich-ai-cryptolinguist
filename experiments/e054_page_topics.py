"""E054 (picture route, step 4a): do Voynich herbal pages behave like PAGES ABOUT DIFFERENT THINGS?
See reports/E054_PREREG.md.
For a sequence of pages, each split into first and second half (by tokens), with cosine similarity of word counts:
  within  = mean cos(first half, second half) of the same page
  across  = mean cos(second half of page i, first half of page i+1)       (consecutive pages)
  distant = mean cos(second half of page i, first half of page j), |i-j| >= 5, 500 random pairs (seed 54054)
  D = (within - across) / (within - distant): the share of the topic change that happens AT the page boundary.
Texts: Voynich herbal Currier-A pages (DEV, illustration H, folio order); Culpeper's herbal, one page per plant entry
(entries between 'Of the herbs' start and 'DIRECTIONS FOR MAKING SYRUPS'), each truncated to the Voynich page-size
sequence; the same Culpeper text cut at FAKE boundaries (shifted by half a page); the copy generator (E032 output,
pages of 29 lines, truncated to the same sizes). Secondary: Voynich herbal B pages; Voynich stars-section paragraphs.
Run: .venv/bin/python -I experiments/e054_page_topics.py HERBAL_FILE
"""
from __future__ import annotations

import json, math, random, re, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

SEED = 54054
OUT = ROOT / "experiments/results/e054.json"
HEAD = re.compile(r"^ {2,}[A-Z][A-Z ,'’-]+\.? *$")


def cos(a, b):
    num = sum(v * b[k] for k, v in a.items() if k in b)
    da = math.sqrt(sum(v * v for v in a.values())); db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def D(pages, rng):
    halves = [(Counter(p[:len(p) // 2]), Counter(p[len(p) // 2:])) for p in pages if len(p) >= 10]
    w = float(np.mean([cos(a, b) for a, b in halves]))
    ac = float(np.mean([cos(halves[i][1], halves[i + 1][0]) for i in range(len(halves) - 1)]))
    pairs = [(i, j) for i in range(len(halves)) for j in range(len(halves)) if abs(i - j) >= 5]
    ds = float(np.mean([cos(halves[i][1], halves[j][0]) for i, j in rng.sample(pairs, min(500, len(pairs)))]))
    return {"pages": len(halves), "within": w, "across": ac, "distant": ds,
            "D": (w - ac) / (w - ds) if w != ds else float("nan")}


def words(s):
    return re.findall(r"[a-z]+", s.lower().replace("’", "'"))


def main():
    rng = random.Random(SEED)
    _, toks = parse(); lk = set(locked_test_leaves(toks))
    pages = {"HA": {}, "HB": {}}
    para, cur_p = [], None
    for t in toks:
        if t.mode != "prose" or t.leaf in lk or not t.is_clean:
            continue
        if t.illustration == "H" and t.currier in ("A", "B"):
            pages["H" + t.currier].setdefault(t.folio, []).append(t.eva)
        if t.illustration == "S":
            key = (t.folio, t.para_start and t.n_in_line == 0)
            if t.para_start and (cur_p is None or cur_p[0] != (t.folio, t.line_no)):
                para.append([]); cur_p = ((t.folio, t.line_no),)
            if para:
                para[-1].append(t.eva)
    order = lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f)
    VA = [pages["HA"][f] for f in sorted(pages["HA"], key=order)]
    VB = [pages["HB"][f] for f in sorted(pages["HB"], key=order)]
    sizes = [len(p) for p in VA]
    # Culpeper entries
    lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore").splitlines()
    end = next(i for i, l in enumerate(lines) if l.startswith("DIRECTIONS FOR MAKING SYRUPS"))
    start = next(i for i, l in enumerate(lines) if HEAD.match(l) and "AMARA" in l or ("ADDER" in l and HEAD.match(l)))
    entries, curw = [], None
    for l in lines[start:end]:
        if HEAD.match(l):
            if curw:
                entries.append(curw)
            curw = []
        elif curw is not None:
            curw += words(l)
    if curw:
        entries.append(curw)
    entries = [e for e in entries if len(e) >= max(sizes)]
    cul = [e[:sizes[i % len(sizes)]] for i, e in enumerate(entries)]
    flat = [w for e in entries for w in e[:sizes[0] * 0 + max(sizes)]]
    fake, i, k = [], max(sizes) // 2, 0
    stream = [w for e, s in zip(entries, [sizes[i % len(sizes)] for i in range(len(entries))]) for w in e[:s]]
    i = sizes[0] // 2
    while i < len(stream):
        s = sizes[k % len(sizes)]; fake.append(stream[i:i + s]); i += s; k += 1
    gl = []
    for s in range(1, 11):
        for ln in (ROOT / f"experiments/results/e032_work/seed{s}/generate/generated_text.txt").read_text().splitlines():
            if ln.startswith("#") or not ln.strip():
                continue
            gl.append(ln.split())
    gen = [[w for l in gl[j:j + 29] for w in l] for j in range(0, len(gl), 29)]
    gen = [p[:sizes[i % len(sizes)]] for i, p in enumerate(gen)][:len(VA) * 4]
    R = {"voynich_herbal_A": D(VA, rng), "culpeper_real_pages": D(cul, rng), "culpeper_fake_boundaries": D(fake, rng),
         "copy_generator": D(gen, rng), "voynich_herbal_B": D(VB, rng), "voynich_stars_paragraphs": D(para, rng)}
    for k, v in R.items():
        print(f"{k:26s} pages {v['pages']:4d} within {v['within']:.3f} across {v['across']:.3f} distant {v['distant']:.3f}  D {v['D']:.2f}")
    valid = R["culpeper_real_pages"]["D"] >= 0.5 and R["culpeper_fake_boundaries"]["D"] <= 0.2 and R["copy_generator"]["D"] <= 0.2
    d = R["voynich_herbal_A"]["D"]
    if not valid:
        verdict, bf = "VOID (controls do not behave as required)", {}
    elif d >= 0.5:
        verdict, bf = "PAGES ARE ABOUT DIFFERENT THINGS", {"M": 1 / 3}
    elif d <= 0.2:
        verdict, bf = "NO PAGE STRUCTURE (continuous, like the generator)", {"M": 3.0}
    else:
        verdict, bf = "PARTIAL", {}
    print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E054", "results": R, "culpeper_entries": len(cul), "valid": valid,
                               "verdict": verdict, "bayes_factors": bf, "locked_test_excluded": sorted(lk)}, indent=1))


if __name__ == "__main__":
    main()
