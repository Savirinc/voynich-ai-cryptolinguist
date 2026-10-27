"""E078: Voynich's word skeleton counted, and which languages share it. See reports/E078_PREREG.md.

Per text (28,841 tokens): lists = 10 commonest fronts (1-2 characters) and 20 commonest endings (1-4 characters) by
word types (E074). Six traits:
 PFRONT  number of productive fronts: >= 15 front-words (freq >= 2) and >= 30% of them leave a word (freq >= 2) when the
         front is removed;
 PEND    number of productive endings: >= 15 bridges X with X+e a word and X+e2 a word for another listed ending e2;
 BOUND   share of tokens whose bridge (after removing the longest listed front and ending) is not itself a word;
 FREEEND share of productive endings that are also words on their own (freq >= 10);
 BARE    share of tokens that are a listed ending standing alone;
 FILL    E074 fill rate at 10/30/20.
Closeness to Voynich: Euclidean distance after scaling each trait by its standard deviation across the languages.
Run: caffeinate -ims .venv/bin/python experiments/e078_skeleton_traits.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, sys, time, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e074_slot_coverage import lists as e074_lists  # noqa: E402

OUT = ROOT / "experiments/results/e078.json"
BIB = ROOT / "data/external/bibles"
SKIP = {"cmn-cu89s", "jpn1965", "vie1934", "engWycliffe"}
CONS = {"hboWLC", "arb-vd", "pesOPV", "urd", "uigara", "ydd"}
N, START = 28841, 10000
TRAITS = ["PFRONT", "PEND", "BOUND", "FREEEND", "BARE", "FILL"]


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def lists(types):
    fr, en = Counter(), Counter()
    for w in types:
        for k in (1, 2):
            if len(w) > k:
                fr[w[:k]] += 1
        for k in (1, 2, 3, 4):
            if len(w) > k:
                en[w[-k:]] += 1
    return [p for p, _ in fr.most_common(10)], [p for p, _ in en.most_common(20)]


def traits(tokens):
    f = Counter(tokens); types = sorted(f)
    W2 = {w for w, c in f.items() if c >= 2}
    F, E = lists(types)
    pf = 0
    for p in F:
        ws = [w for w in W2 if w.startswith(p) and len(w) > len(p)]
        if len(ws) >= 15 and sum(w[len(p):] in W2 for w in ws) / len(ws) >= 0.30:
            pf += 1
    prod = []
    for e in E:
        X = {w[:-len(e)] for w in W2 if w.endswith(e) and len(w) > len(e)}
        k = sum(1 for x in X if any(e2 != e and (x + e2) in W2 for e2 in E))
        if k >= 15:
            prod.append(e)
    bound = tot = 0
    for w, c in f.items():
        fr = max((p for p in F if w.startswith(p) and len(p) < len(w)), key=len, default="")
        rest = w[len(fr):]
        en = max((p for p in E if rest.endswith(p) and len(p) < len(rest)), key=len, default="")
        b = rest[:len(rest) - len(en)]
        if b:
            tot += c
            if b not in W2:
                bound += c
    Fe, Me, Ee = e074_lists(types, 10, 30, 20)
    combos = {a + b + c for a in Fe for b in Me for c in Ee}
    return {"PFRONT": float(pf), "PEND": float(len(prod)), "BOUND": bound / tot if tot else 0.0,
            "FREEEND": (sum(f.get(e, 0) >= 10 for e in prod) / len(prod)) if prod else 0.0,
            "BARE": sum(f.get(e, 0) for e in E) / len(tokens),
            "FILL": len(combos & set(types)) / (len(Fe) * len(Me) * len(Ee)),
            "fronts": F, "endings": E, "productive_endings": prod}


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    from e011_twin_search import voynich_lines
    from e064_early_audit import tok
    vl, _, _, locked = voynich_lines()
    V = [w for l in vl for w in l if w]
    res = {"experiment": "E078", "locked_test_excluded": locked, "texts": {}, "generator": {}}
    res["texts"]["VOYNICH"] = traits(V)
    for bid in sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in SKIP):
        try:
            w = tok(bid)
        except Exception as e:
            log(f"{bid}: skipped ({e})"); continue
        if bid in CONS:
            w = [x for x in (cons(t) for t in w) if x]
        if len(w) < START + N:
            continue
        res["texts"][bid] = traits(w[START:START + N])
    from e032_copy_generator import generate
    for s in (31, 32, 33):
        res["generator"][str(s)] = traits([w for l in generate(gen_dir, java, s, N, ROOT / "data/external/e078_gen_work") for w in l][:N])
    langs = [b for b in res["texts"] if b != "VOYNICH"]
    sd = {t: float(np.std([res["texts"][b][t] for b in langs], ddof=1)) or 1.0 for t in TRAITS}
    v = res["texts"]["VOYNICH"]
    dist = lambda r: float(np.sqrt(sum(((r[t] - v[t]) / sd[t]) ** 2 for t in TRAITS)))
    rank = sorted(((b, dist(res["texts"][b])) for b in langs), key=lambda x: x[1])
    res.update(scale=sd, ranking=rank, generator_distance={s: dist(r) for s, r in res["generator"].items()}, runtime_s=time.time() - t0)
    hdr = "text        " + " ".join(f"{t:>8s}" for t in TRAITS)
    log(hdr)
    for name, r in [("VOYNICH", v)] + [(b, res["texts"][b]) for b, _ in rank] + [(f"gen{s}", r) for s, r in res["generator"].items()]:
        log(f"{name:11s} " + " ".join(f"{r[t]:8.3f}" for t in TRAITS) + (f"   d {dist(r):.2f}" if name != "VOYNICH" else ""))
    log(f"Voynich productive endings: {v['productive_endings']}")
    for t in TRAITS:
        vals = [res["texts"][b][t] for b in langs]
        log(f"  {t}: Voynich {v[t]:.3f}; languages {min(vals):.3f}-{max(vals):.3f}; Voynich above {sum(x < v[t] for x in vals)}/{len(vals)}")
    log("closest: " + ", ".join(f"{b} {d:.2f}" for b, d in rank[:10]))
    log("generator distances: " + ", ".join(f"{s} {d:.2f}" for s, d in res["generator_distance"].items()))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
