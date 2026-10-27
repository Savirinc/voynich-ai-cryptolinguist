"""E074: share of the text written as front + middle + ending from short lists. See reports/E074_PREREG.md.
Run: caffeinate -ims .venv/bin/python experiments/e074_slot_coverage.py GEN_DIR JAVA
"""
from __future__ import annotations

import json, sys, time, unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
N, START = 28841, 10000
OUT = ROOT / "experiments/results/e074.json"
SIZES = [(5, 15, 10), (10, 30, 20), (20, 60, 40)]
PRIMARY = (10, 30, 20)
LANGS = ["latVUC", "hboWLC", "turytc", "deu1912", "eng-kjv", "indayt", "hun", "tglulb"]
GEN_SEEDS = [31, 32, 33]


def log(*a):
    print(*a, flush=True)


def lists(types, kF, kM, kE):
    fr, en = Counter(), Counter()
    for w in types:
        for k in range(1, 3):
            if len(w) > k:
                fr[w[:k]] += 1
        for k in range(1, 5):
            if len(w) > k:
                en[w[-k:]] += 1
    F = [""] + [p for p, _ in fr.most_common(kF - 1)]
    E = [""] + [p for p, _ in en.most_common(kE - 1)]
    mid = Counter()
    for w in types:
        seen = set()
        for f in F:
            if not w.startswith(f):
                continue
            for e in E:
                if len(f) + len(e) > len(w) or (e and not w.endswith(e)):
                    continue
                m = w[len(f):len(w) - len(e)]
                if len(m) <= 4:
                    seen.add(m)
        for m in seen:
            if m:
                mid[m] += 1
    M = [""] + [m for m, _ in mid.most_common(kM)]
    return F, M, E


def written(w, F, Ms, E):
    for f in F:
        if not w.startswith(f):
            continue
        for e in E:
            if len(f) + len(e) > len(w) or (e and not w.endswith(e)):
                continue
            if w[len(f):len(w) - len(e)] in Ms:
                return True
    return False


def measure(tokens):
    half = len(tokens) // 2
    build, check = tokens[:half], tokens[half:]
    btypes = sorted(set(build))
    allt = set(tokens)
    out = {}
    for kF, kM, kE in SIZES:
        F, M, E = lists(btypes, kF, kM, kE)
        Ms = set(M)
        cache = {}
        def ok(w):
            if w not in cache:
                cache[w] = written(w, F, Ms, E)
            return cache[w]
        ctypes = set(check)
        combos = {f + m + e for f in F for m in M for e in E}
        r = {"tok_cov": sum(map(ok, check)) / len(check), "type_cov": sum(map(ok, ctypes)) / len(ctypes),
             "build_tok_cov": sum(map(ok, build)) / len(build),
             "fill": len(combos & allt) / (len(F) * len(M) * len(E)), "distinct_strings": len(combos),
             "pieces": len(F) + len(M) + len(E) - 3}
        if (kF, kM, kE) == PRIMARY:
            r["lists"] = {"front": F, "middle": M, "ending": E}
            r["unwritten_top"] = Counter(w for w in check if not ok(w)).most_common(15)
        out[f"{kF}/{kM}/{kE}"] = r
    return out


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    from e011_twin_search import voynich_lines
    from e064_early_audit import tok
    lines, _, _, locked = voynich_lines()
    V = [w for l in lines for w in l if w]
    assert len(V) == N
    texts = {"VOYNICH": V}
    for b in LANGS:
        w = tok(b)[START:START + N]
        if b == "hboWLC":
            w = [x for x in (cons(t) for t in w) if x]
        texts[b] = w
    from e032_copy_generator import generate
    for s in GEN_SEEDS:
        texts[f"generator_{s}"] = [w for l in generate(gen_dir, java, s, N, ROOT / "data/external/e074_gen_work") for w in l][:N]
    res = {"experiment": "E074", "locked_test_excluded": locked, "texts": {}}
    key = "%d/%d/%d" % PRIMARY
    for name, toks in texts.items():
        r = measure(toks); res["texts"][name] = r
        log(f"{name:14s} " + " | ".join(f"{k}: tok {v['tok_cov']:.3f} type {v['type_cov']:.3f} fill {v['fill']:.4f}" for k, v in r.items()))
    v = res["texts"]["VOYNICH"][key]
    lang = [res["texts"][b][key]["tok_cov"] for b in LANGS]
    reading = ("ABOVE EVERY LANGUAGE" if v["tok_cov"] > max(lang) else
               "INSIDE THE LANGUAGE RANGE" if v["tok_cov"] >= min(lang) else "BELOW EVERY LANGUAGE")
    res.update(reading=reading, runtime_s=time.time() - t0)
    log(f"Voynich primary lists: {v['lists']}")
    log(f"Voynich unwritten commonest: {v['unwritten_top']}")
    log(f"READING {reading} (Voynich token coverage {v['tok_cov']:.3f}; languages {min(lang):.3f}-{max(lang):.3f})")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
