"""E043: Voynich's words recur within a LINE (not specifically back to back). Which kind of text does that?
Sacred/liturgical vs practical/medical vs other (secular verse, prose) vs the copy generator. See reports/E043_PREREG.md.

Statistics per text (exact repeats of word tokens; chance = sum_w p_w^2 over the sample):
  SL  same-line recurrence: repeat rate of neighbouring words AFTER shuffling the words within each line
      (mean of 5 shuffles) / chance   -> how often a word meets a copy of itself somewhere in its line
  AS  adjacency specificity: observed back-to-back repeat rate / (SL x chance)
      (~1: back to back is not special; >> 1: real doubling, as Indonesian)
  also reported: observed repeat rate at distance 1, 2, 3 / chance
Lines: references are cut into pseudo-lines that follow Voynich DEV's own sequence of line lengths (from a random
start, cycled). The generator keeps its own lines. Natural lines (verse lines, Bible verses) reported secondarily.
Windows: non-overlapping windows of Currier A's token count (8,806), up to 10 at random (seed 43043).
z = (V - mean) / max(own window sd if >= 3 windows, median window sd of all references with >= 3 windows,
2%|V|, 0.01). A text MATCHES Voynich DEV if |z| <= 3 on both SL and AS.
Run: caffeinate -ims .venv/bin/python experiments/e043_line_recurrence.py LL_DIR HERBAL_FILE
"""
from __future__ import annotations

import glob, hashlib, json, random, re, sys, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e030_reduplication import tokens as e030_tokens  # noqa: E402

SEED, SHUF, KMAX, Z_OK = 43043, 5, 10, 3.0
OUT = ROOT / "experiments/results/e043.json"
BIB = ROOT / "data/external/bibles"
STATS = ["SL", "AS"]


def norm_words(text):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[^\W\d_]+", unicodedata.normalize("NFC", t))


def bible_books(bid, books):
    fs = sorted(f for f in glob.glob(str(BIB / bid / "txt" / "*_read.txt")) if any(f"_{b}_" in f for b in books))
    vs = []
    for f in fs:
        for ln in Path(f).read_text(encoding="utf-8-sig").splitlines()[1:]:
            w = norm_words(ln)
            if w:
                vs.append(w)
    return vs                                              # natural lines = verses


def ll_files(d, files):
    lines = []
    for f in files:
        for ln in (Path(d) / f).read_text(encoding="utf-8", errors="ignore").splitlines():
            w = norm_words(ln)
            if w:
                lines.append(w)
    return lines                                           # natural lines = the file's lines (verse lines)


def gen_lines():
    out = []
    for s in range(1, 11):
        for ln in (ROOT / f"experiments/results/e032_work/seed{s}/generate/generated_text.txt").read_text().splitlines():
            if ln.startswith("#") or not ln.strip():
                continue
            out.append(ln.split())
    return out


def rate(d, lines):
    a = b = 0
    for l in lines:
        for i in range(len(l) - d):
            a += 1; b += l[i] == l[i + d]
    return b / a if a else 0.0


def stats(lines, rng):
    toks = [w for l in lines for w in l]
    wc = Counter(toks); n = len(toks)
    p2 = sum((c / n) ** 2 for c in wc.values())
    sh = []
    for _ in range(SHUF):
        o = []
        for l in lines:
            m = l[:]; rng.shuffle(m); o.append(m)
        sh.append(rate(1, o))
    sl = float(np.mean(sh)) / p2
    d1 = rate(1, lines) / p2
    return {"SL": sl, "AS": d1 / sl if sl else float("nan"), "d1": d1, "d2": rate(2, lines) / p2, "d3": rate(3, lines) / p2}


def pseudo(words, lens, rng):
    out, i, j = [], 0, rng.randrange(len(lens))
    while i < len(words):
        L = lens[j % len(lens)]; out.append(words[i:i + L]); i += L; j += 1
    return out


def windows(lines, n, rng):
    """split a list of lines into consecutive chunks of ~n tokens; up to KMAX at random."""
    ch, cur, k = [], [], 0
    for l in lines:
        cur.append(l); k += len(l)
        if k >= n:
            ch.append(cur); cur, k = [], 0
    if not ch and cur:
        ch = [cur]
    return [ch[i] for i in sorted(rng.sample(range(len(ch)), min(KMAX, len(ch))))]


def main():
    lld, herbal = sys.argv[1], Path(sys.argv[2])
    rng = random.Random(SEED)
    lines, cur, _, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines]
    lens = [len(l) for l in vl if l]
    DEV = [l for l in vl if l]
    VA = [l for l, c in zip(vl, cur) if l and c == "A"]; VB = [l for l, c in zip(vl, cur) if l and c == "B"]
    nA = sum(len(l) for l in VA)
    V = {"DEV": stats(DEV, random.Random(SEED)), "A": stats(VA, random.Random(SEED)), "B": stats(VB, random.Random(SEED))}
    print("Voynich", {k: {s: round(x, 2) for s, x in v.items()} for k, v in V.items()}, flush=True)
    hb = herbal.read_text(encoding="utf-8", errors="ignore"); hb = hb[hb.index("*** START"):hb.index("*** END")]
    herb_lines = [norm_words(ln) for ln in hb.splitlines()[1:]]
    TEXTS = {   # name: (group, natural lines)
        "Latin hymns (Hymni, Ambrose, Prudentius)": ("SACRED", ll_files(lld, ["hymni.txt", "ambrose/hymns.txt"] + [f"prudentius/prud{i}.txt" for i in range(1, 15)])),
        "Latin Psalms (Vulgate)": ("SACRED", bible_books("latVUC", ["PSA"])),
        "Hebrew Psalms": ("SACRED", bible_books("hboWLC", ["PSA"])),
        "Latin Genesis-Exodus (Vulgate)": ("SACRED", bible_books("latVUC", ["GEN", "EXO"])),
        "Hebrew Genesis-Exodus": ("SACRED", bible_books("hboWLC", ["GEN", "EXO"])),
        "Apicius + Cato + Varro (recipes, farming)": ("PRACTICAL", ll_files(lld, [f"apicius/apicius{i}.txt" for i in range(1, 6)] + ["cato/cato.agri.txt", "varro.rr1.txt", "varro.rr2.txt", "varro.rr3.txt"])),
        "Columella (farming)": ("PRACTICAL", ll_files(lld, [f"columella/columella.rr{i}.txt" for i in range(1, 13)] + ["columella/columella.arbor.txt"])),
        "Culpeper herbal (English)": ("PRACTICAL", [l for l in herb_lines if l]),
        "Vergil Aeneid": ("OTHER", ll_files(lld, [f"vergil/aen{i}.txt" for i in range(1, 13)])),
        "Ovid Metamorphoses": ("OTHER", ll_files(lld, [f"ovid/ovid.met{i}.txt" for i in range(1, 16)])),
        "Caesar Gallic War": ("OTHER", ll_files(lld, [f"caesar/gall{i}.txt" for i in range(1, 9)])),
        "Indonesian Bible (doubling reference)": ("REFERENCE", [e030_tokens("indayt")]),
        "Copy generator (Timm & Schinner)": ("GENERATOR", gen_lines()),
    }
    shas = {k: hashlib.sha256(" ".join(" ".join(l) for l in v[1]).encode()).hexdigest() for k, v in TEXTS.items()}
    R = {}
    for name, (grp, nat) in TEXTS.items():
        if grp == "GENERATOR":
            prim = nat
        else:
            prim = pseudo([w for l in nat for w in l], lens, rng)
        W = windows(prim, nA, rng)
        G = [stats(w, rng) for w in W]
        natw = windows(nat, nA, rng) if grp not in ("GENERATOR", "REFERENCE") else []
        natS = [stats(w, rng) for w in natw]
        R[name] = {"group": grp, "tokens": sum(len(l) for l in nat), "n_windows": len(G),
                   "mean": {k: float(np.mean([g[k] for g in G])) for k in ["SL", "AS", "d1", "d2", "d3"]},
                   "own_sd": {k: float(np.std([g[k] for g in G], ddof=1)) if len(G) >= 3 else None for k in STATS},
                   "natural_lines": {k: float(np.mean([g[k] for g in natS])) for k in ["SL", "AS", "d1", "d2", "d3"]} if natS else None}
    med = {k: float(np.median([r["own_sd"][k] for r in R.values() if r["own_sd"][k] is not None])) for k in STATS}
    for name, r in R.items():
        S = {k: max(r["own_sd"][k] or 0.0, med[k], 0.02 * abs(V["DEV"][k]), 0.01) for k in STATS}
        r["sd"] = S
        r["z"] = {k: round((V["DEV"][k] - r["mean"][k]) / S[k], 2) for k in STATS}
        r["match"] = all(abs(r["z"][k]) <= Z_OK for k in STATS)
        m = r["mean"]
        print(f"{r['group']:9s} {name:44s} n={r['n_windows']:2d} SL {m['SL']:.2f} AS {m['AS']:.2f} | d1 {m['d1']:.2f} d2 {m['d2']:.2f} d3 {m['d3']:.2f}"
              f" | z SL {r['z']['SL']:+.1f} AS {r['z']['AS']:+.1f} -> {'MATCH' if r['match'] else '-'}"
              + (f" | natural lines SL {r['natural_lines']['SL']:.2f} AS {r['natural_lines']['AS']:.2f}" if r["natural_lines"] else ""), flush=True)
    groups = {g: [n for n, r in R.items() if r["group"] == g and r["match"]] for g in ("SACRED", "PRACTICAL", "OTHER", "GENERATOR")}
    lang = [g for g in ("SACRED", "PRACTICAL", "OTHER") if groups[g]]
    if len(lang) == 1:
        bf = {{"SACRED": "L-sacred", "PRACTICAL": "L-practical", "OTHER": "L-other"}[lang[0]]: 3.0}
        verdict = f"ONLY {lang[0]} MATCHES"
    elif groups["GENERATOR"] and not lang:
        bf, verdict = {"M": 3.0}, "ONLY THE GENERATOR MATCHES"
    elif not lang and not groups["GENERATOR"]:
        bf, verdict = {}, "NOTHING MATCHES"
    else:
        bf, verdict = {}, "MIXED (" + ", ".join(lang + (["GENERATOR"] if groups["GENERATOR"] else [])) + ")"
    print("matches by group:", groups); print("VERDICT:", verdict, bf)
    OUT.write_text(json.dumps({"experiment": "E043", "voynich": V, "median_sd": med, "texts": R, "groups": groups,
                               "verdict": verdict, "bayes_factors": bf, "text_sha256": shas,
                               "locked_test_excluded": locked}, indent=1))


if __name__ == "__main__":
    main()
