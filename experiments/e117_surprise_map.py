"""X117 (Arham, move 3; EXPLORATORY, unscored): where does the surprise sit? See reports/SURPRISE_MAP.md.
Not locked: in development (controls only) the L and G bands overlapped (Bible chapter openings are LESS surprising
than the rest; several generator settings are positive), so the verdict below is VOID by construction.

Each text is cut into its own real entries: Voynich pages (folio sides), Bible chapters, Culpeper herb entries
(heading line dropped), copy-generator pages (29 lines, the generator's own page unit, which its source chooser
prefers), dice-generator pages (E114 best set, refilled per page, Voynich page shapes).
Surprisal of a token = -log2 p(w) under a unigram model built from every OTHER entry of the same stretch
(add-0.5 smoothing over the stretch vocabulary + 1 unseen slot): high where a word is rare outside its own entry.
HEAD = mean over entries (>= 30 tokens) of [mean surprisal of tokens 2-11] - [mean surprisal of tokens 12..end].
Token 1 is skipped everywhere (Voynich paragraph-initial gallows, E106; 'And'/'In' in Bibles).
Stretches: meaningful texts and generators are cut to whole consecutive entries from a random start until >= N tokens
(N = Voynich DEV tokens).
L band = meaningful HEAD [p10, p90]; G band = generator HEAD [p10, p90]. Validity: bands do not overlap.
  LANGUAGE-LIKE   Voynich in L band, outside G band -> M x 1/3
  GENERATOR-LIKE  Voynich in G band, outside L band -> M x 3
  NEITHER / VOID                                   -> none
Rule 8: Voynich within 0.5 jackknife-sd of a band edge -> 10 jackknife replicates (drop every 10th page) must agree >= 8.
Unscored map: surprisal by word position in line (first / middle / last), by line of page (1, 2, 3, 4+), by section;
label words scored under the prose model; the same HEAD with the five spelling families merged (E116 mu) and gallows
unified (k, t, p, f -> t).
Run: caffeinate -ims .venv/bin/python experiments/e117_surprise_map.py [--dev]
--dev measures controls only (development; no Voynich).
"""
from __future__ import annotations

import argparse, glob, json, math, random, re, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e093_explanation_model as E93  # noqa: E402
import e099_phrase_repeats_v2 as P  # noqa: E402
import e114_dice_generator as D  # noqa: E402
from e116_merged_phrases import mu  # noqa: E402

SEED = 117117
OUT = ROOT / "experiments/results/e117.json"
CULP = ROOT / "data/external/pg_herbal/pg49513.txt"
E032W, E100W = ROOT / "experiments/results/e032_work", ROOT / "experiments/results/e100_work"
DICE_SET = ("2d6", "page", (20, 60, 40))
H0, H1, MINLEN = 1, 11, 30
log = P.log


def words(s):
    s = s.lower().replace("’", "'").replace("ʻ", "'")
    import unicodedata
    s = unicodedata.normalize("NFC", s)
    return "".join(c if (unicodedata.category(c)[0] in "LM" or c == "'") else " " for c in s).split()


def bible_entries(bid):
    out = []
    for f in sorted(glob.glob(str(P.BIB / bid / "txt" / "*_read.txt"))):
        if "_000_000_000_" in f:
            continue
        ls = Path(f).read_text(encoding="utf-8-sig").splitlines()[2:]     # book title, chapter number
        e = [words(l) for l in ls]; e = [l for l in e if l]
        if e:
            out.append(e)
    return out


def culpeper_entries():
    t = CULP.read_text(encoding="utf-8", errors="ignore")
    t = t[t.find("    AMARA DULCIS."):t.find("*** END")]
    parts = re.split(r"(?m)^ {4}[A-Z][A-Z' ,.-]+\.\s*$", t)
    return [e for e in ([words(l) for l in p.splitlines() if words(l)] for p in parts) if e]


def gen_entries(path):
    ls = [ln.split() for ln in path.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    return [ls[i:i + 29] for i in range(0, len(ls), 29)]


def take(entries, N, rng):
    """whole consecutive entries from a random start until >= N tokens (wrapping); None if the text is too short"""
    if sum(len(w) for e in entries for w in e) < N:
        return None
    s = rng.randrange(len(entries)); out, n, i = [], 0, s
    while n < N:
        out.append(entries[i % len(entries)]); n += sum(map(len, entries[i % len(entries)])); i += 1
    return out


def surprisal(entries):
    """per entry, per line: list of surprisal values (leave-entry-out unigram)"""
    tot = Counter(w for e in entries for l in e for w in l); V = len(tot) + 1; N = sum(tot.values())
    out = []
    for e in entries:
        own = Counter(w for l in e for w in l); n = N - sum(own.values()); den = n + 0.5 * V
        out.append([[-math.log2((tot[w] - own[w] + 0.5) / den) for w in l] for l in e])
    return out


def head(S):
    d = []
    for e in S:
        f = [x for l in e for x in l]
        if len(f) >= MINLEN:
            d.append(np.mean(f[H0:H1]) - np.mean(f[H1:]))
    return float(np.mean(d)), d


def measure(entries):
    S = surprisal(entries); h, d = head(S)
    return {"HEAD": h, "n_entries": len(d), "tokens": sum(len(w) for e in entries for w in e)}


def mapped(entries, f):
    return [[[f(w) for w in l] for l in e] for e in entries]


def gall(w):
    return re.sub(r"[kpf]", "t", mu(w))


def vmap(pages, meta):
    S = surprisal(pages); pos, row, sec = defaultdict(list), defaultdict(list), defaultdict(list)
    for e, m in zip(S, meta):
        for i, l in enumerate(e):
            for j, x in enumerate(l):
                k = "first" if j == 0 else "last" if j == len(l) - 1 else "middle"
                pos[k].append(x); row[str(min(i + 1, 4))].append(x); sec[m["section"]].append(x)
    f = lambda D: {k: [float(np.mean(v)), len(v)] for k, v in sorted(D.items())}
    return {"position_in_line": f(pos), "line_of_page": f(row), "section": f(sec)}


def labels(pages):
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    lab = [t.eva for t in toks if t.mode != "prose" and t.is_clean and t.leaf not in locked]
    tot = Counter(w for e in pages for l in e for w in l); V = len(tot) + 1; N = sum(tot.values())
    s = lambda w: -math.log2((tot[w] + 0.5) / (N + 0.5 * V))
    prose = [s(w) for e in pages for l in e for w in l]
    return {"labels_mean": float(np.mean([s(w) for w in lab])), "n_labels": len(lab), "prose_mean": float(np.mean(prose)),
            "labels_unseen_in_prose": float(np.mean([tot[w] == 0 for w in lab]))}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dev", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    pages, meta, locked = E93.voynich()
    N = sum(len(w) for p in pages for w in p)
    log(f"Voynich pages {len(pages)} tokens {N}")
    texts = {"bible:" + b: bible_entries(b) for b in sorted(d.name for d in P.BIB.iterdir() if d.is_dir() and d.name not in P.SKIP)}
    texts["other:culpeper"] = culpeper_entries()
    gens = {}
    for d in sorted(E032W.iterdir()):
        if d.is_dir() and (d / "generate/generated_text.txt").exists():
            gens["e032_" + d.name] = gen_entries(d / "generate/generated_text.txt")
    for d in sorted(E100W.iterdir()):
        gens["e100_" + d.name] = gen_entries(d / "generate/generated_text.txt")
    shape = [[len(l) for l in p] for p in pages]; ms = D.masters(pages, DICE_SET[2])
    for s in range(1, 11):
        gens[f"dice_seed{s}"] = D.book(DICE_SET, ms, shape, s)
    R = {"meaningful": {}, "generator": {}}
    for grp, src in (("meaningful", texts), ("generator", gens)):
        for k, ent in src.items():
            c = ent if k.startswith("dice") else take(ent, N, rng)
            if c is None:
                log(f"skip {k}"); continue
            R[grp][k] = m = measure(c); log(f"{grp[:4]} {k:28s} entries {m['n_entries']:4d} HEAD {m['HEAD']:+.3f}")
    le = np.array([v["HEAD"] for v in R["meaningful"].values()]); ge = np.array([v["HEAD"] for v in R["generator"].values()])
    Lb = (float(np.percentile(le, 10)), float(np.percentile(le, 90))); Gb = (float(np.percentile(ge, 10)), float(np.percentile(ge, 90)))
    valid = Lb[1] < Gb[0] or Gb[1] < Lb[0]
    log(f"L band {Lb[0]:+.3f}..{Lb[1]:+.3f} (n {len(le)}) | G band {Gb[0]:+.3f}..{Gb[1]:+.3f} (n {len(ge)}) | VALID {valid}")
    res = {"experiment": "E117", "seed": SEED, "N": N, "results": R, "L_band": Lb, "G_band": Gb, "valid": bool(valid),
           "locked_test_excluded": locked}
    if not a.dev:
        V = measure(pages)
        reps = [measure([p for i, p in enumerate(pages) if i % 10 != j])["HEAD"] for j in range(10)]
        V["sd"] = float(np.std(reps, ddof=1)) * math.sqrt(9); V["jackknife"] = reps
        inL = lambda x: Lb[0] <= x <= Lb[1]; inG = lambda x: Gb[0] <= x <= Gb[1]

        def verdict(x):
            if inL(x) and not inG(x):
                return "LANGUAGE-LIKE"
            if inG(x) and not inL(x):
                return "GENERATOR-LIKE"
            return "NEITHER"
        v = verdict(V["HEAD"]) if valid else "VOID"
        if valid and min(abs(V["HEAD"] - b) for b in (*Lb, *Gb)) < 0.5 * V["sd"]:
            rv = [verdict(x) for x in reps]; res["seed_check"] = rv
            if sum(r == v for r in rv) < 8:
                v = "NEITHER"
        fM = {"LANGUAGE-LIKE": 1 / 3, "GENERATOR-LIKE": 3.0}.get(v, 1.0)
        V["map"] = vmap(pages, meta); V["labels"] = labels(pages)
        V["HEAD_merged_gallows"] = measure(mapped(pages, gall))["HEAD"]
        V["HEAD_by_section"] = {s: measure([p for p, m in zip(pages, meta) if m["section"] == s])["HEAD"]
                                for s in sorted({m["section"] for m in meta}) if sum(m["section"] == s for m in meta) >= 10}
        res.update(voynich=V, verdict=v, factor_M=fM)
        log(f"VOYNICH HEAD {V['HEAD']:+.3f} (sd {V['sd']:.3f}) | merged+gallows {V['HEAD_merged_gallows']:+.3f} | by section {V['HEAD_by_section']}")
        log(f"map {V['map']} | labels {V['labels']}")
        log(f"VERDICT {v} | M x {fM:.3g}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e117_dev.json" if a.dev else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
