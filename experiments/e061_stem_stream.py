"""E061 (campaign step 1): stems versus padding. See reports/E061_PREREG.md.

Every text (Voynich DEV prose; 22 Bible windows; Caesar; 10 generator samples; 10 padding-cipher controls) is
segmented into stem + suffix by E026's unsupervised segmenter, and the stem stream is measured:
  NSTEM95 (stems covering 95% of tokens), COLLAPSE (stem types / word types), STEM_HAPAX, STEM_ZIPF (top-100 slope).
Verdict for Voynich from z-scores against the languages and against the padding controls (see prereg table).
Controls: padding controls leave-one-out PADDING-LIKE >= 8/10; Caesar WORD-LIKE.
Run: caffeinate -ims .venv/bin/python experiments/e061_stem_stream.py GEN_DIR JAVA   (GEN_DIR absolute)
"""
from __future__ import annotations

import json, math, random, sys, time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from vcl.solvers.segment import segment_types, ending_features  # noqa: E402

SEED, N, START = 61061, 28841, 10000
OUT = ROOT / "experiments/results/e061.json"
SEG = dict(max_suf=4, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, smooth=0.01)
LANGS = ["latVUC", "eng-kjv", "indayt", "zlmKSZI", "tglulb", "cebulb", "swhulb", "yor", "hausa", "haw1868", "ton",
         "mri2012", "hboWLC", "turytc", "ces1613", "deu1912", "ita1885", "fraLSG", "hun", "grcbyz", "arb-vd", "tam2017"]
PAD_LANGS = ["latVUC", "deu1912", "ita1885", "hboWLC", "turytc"]
GEN_SEEDS = range(31, 41)
MEASURES = ["NSTEM95", "COLLAPSE", "STEM_HAPAX", "STEM_ZIPF"]
ENDINGS = {"": .19, "y": .18, "dy": .10, "ol": .06, "aiin": .05, "edy": .05, "ar": .04, "or": .04, "al": .04,
           "ey": .03, "ain": .03, "in": .03, "o": .02, "s": .01, "am": .01}
Z_BAR = 3.0


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------------------------------------ measures
def zipf(counter):
    fr = np.array(sorted(counter.values(), reverse=True)[:100], float)
    return float(np.polyfit(np.log(np.arange(1, len(fr) + 1)), np.log(fr), 1)[0]) if len(fr) >= 10 else float("nan")


def n95(counter):
    tot = sum(counter.values()); acc = k = 0
    for _, c in counter.most_common():
        if acc >= 0.95 * tot:
            break
        acc += c; k += 1
    return float(k)


def h2(words):
    """Conditional glyph entropy (bits) inside words, with a start symbol."""
    big, uni = Counter(), Counter()
    for w in words:
        s = "^" + w
        for a, b in zip(s, s[1:]):
            big[(a, b)] += 1; uni[a] += 1
    tot = sum(big.values())
    return -sum(c / tot * math.log2(c / uni[a]) for (a, _), c in big.items())


def measure(tokens, seed):
    wc = Counter(tokens)
    split = segment_types(wc, seed=seed, **SEG)
    stems = [w[:split[w]] for w in tokens]
    sc = Counter(stems)
    m = {"NSTEM95": n95(sc), "COLLAPSE": len(sc) / len(wc), "STEM_HAPAX": sum(v == 1 for v in sc.values()) / len(sc),
         "STEM_ZIPF": zipf(sc),
         "word_types": float(len(wc)), "stem_types": float(len(sc)), "NWORD95": n95(wc),
         "WORD_HAPAX": sum(v == 1 for v in wc.values()) / len(wc), "WORD_ZIPF": zipf(wc),
         "h2_words": h2(list(wc.elements())), "h2_stems": h2(stems)}
    m.update(ending_features(tokens, split))
    m["top_stems"] = sc.most_common(12)
    m["top_suffixes"] = Counter(w[split[w]:] for w in tokens).most_common(12)
    return m


def zs(v, ref):
    out = {}
    for k in MEASURES:
        vals = [r[k] for r in ref]
        mu, sd = float(np.mean(vals)), max(float(np.std(vals, ddof=1)), 0.02 * abs(float(np.mean(vals))), 1e-9)
        out[k] = (v[k] - mu) / sd
    return out


def verdict(v, langs, pads, gens=None):
    zl, zp = zs(v, langs), zs(v, pads)
    in_pad = all(abs(zp[k]) <= Z_BAR for k in MEASURES)
    out_lang = sum(abs(zl[k]) > Z_BAR for k in MEASURES)
    in_lang = sum(abs(zl[k]) <= Z_BAR for k in MEASURES)
    if in_pad and out_lang >= 3:
        vd = "PADDING-LIKE"
    elif in_lang >= 3:
        vd = "WORD-LIKE"
    elif gens and all(abs(zs(v, gens)[k]) <= Z_BAR for k in MEASURES):
        vd = "GENERATOR-LIKE"
    else:
        vd = "MIXED"
    border = [k for k in MEASURES if abs(abs(zl[k]) - Z_BAR) < 0.5 or abs(abs(zp[k]) - Z_BAR) < 0.5]
    return dict(verdict=vd, z_lang=zl, z_pad=zp, z_gen=zs(v, gens) if gens else None, borderline=border)


# ------------------------------------------------------------------------------------------------ texts
def bible_window(bid):
    from e042_language_shortlist import words
    w = words(bid)
    assert len(w) >= START + N, bid
    return w[START:START + N]


def caesar():
    from e043_line_recurrence import ll_files
    d = ROOT / "data/external/latin_library_e043/caesar"
    files = sorted(p.name for p in d.iterdir() if p.is_file())
    toks = [w for l in ll_files(d, files) for w in l]
    assert len(toks) >= N
    return toks[:N]


def padding_cipher(plain_tokens, glyph_freq, rng):
    """Letters of the plaintext cut into 1-2 letter units; each unit -> fixed 2-4 glyph code; + independent ending."""
    letters = "".join(plain_tokens)
    units, i = [], 0
    while i < len(letters) and len(units) < N:
        k = 2 if rng.random() < 0.5 and i + 1 < len(letters) else 1
        units.append(letters[i:i + k]); i += k
    glyphs, weights = zip(*sorted(glyph_freq.items()))
    key, used = {}, set()
    for u in sorted(set(units)):
        while True:
            code = "".join(rng.choices(glyphs, weights, k=rng.choice((2, 3, 4))))
            if code not in used:
                used.add(code); key[u] = code; break
    ends, ew = zip(*ENDINGS.items())
    return [key[u] + rng.choices(ends, ew)[0] for u in units[:N]]


def generator_samples(gen_dir, java):
    from e032_copy_generator import generate
    work = ROOT / "data/external/e061_gen_work"
    return {s: [w for l in generate(gen_dir, java, s, N, work) for w in l] for s in GEN_SEEDS}


# ------------------------------------------------------------------------------------------------ main
def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    t0 = time.time()
    rng = random.Random(SEED)
    from e011_twin_search import voynich_lines
    lines, _, dev_words, locked = voynich_lines()
    vtoks = [w for l in lines for w in l if w]
    assert len(vtoks) == N, len(vtoks)
    glyph_freq = Counter(g for w in vtoks for g in w)
    res = {"experiment": "E061", "seed": SEED, "locked_test_excluded": locked, "languages": {}, "padding": {}, "generator": {}}

    log("[languages]")
    for bid in LANGS:
        m = measure(bible_window(bid), SEED); res["languages"][bid] = m
        log(f"  {bid:9s} words {int(m['word_types']):6d} stems {int(m['stem_types']):6d} NSTEM95 {m['NSTEM95']:6.0f} COLLAPSE {m['COLLAPSE']:.3f} "
            f"HAPAX {m['STEM_HAPAX']:.3f} ZIPF {m['STEM_ZIPF']:+.2f} | SPLIT {m['SPLIT']:.2f} NSUF95 {m['NSUF95']:.0f}")
    log("[padding controls]")
    for i, bid in enumerate(PAD_LANGS):
        plain = bible_window(bid)
        for j in range(2):
            toks = padding_cipher(plain, glyph_freq, random.Random(SEED + 100 * j + i))
            m = measure(toks, SEED); res["padding"][f"{bid}_{j}"] = m
            log(f"  {bid}_{j:<6} words {int(m['word_types']):6d} stems {int(m['stem_types']):6d} NSTEM95 {m['NSTEM95']:6.0f} COLLAPSE {m['COLLAPSE']:.3f} "
                f"HAPAX {m['STEM_HAPAX']:.3f} ZIPF {m['STEM_ZIPF']:+.2f} | SPLIT {m['SPLIT']:.2f} NSUF95 {m['NSUF95']:.0f}")
    log("[generator]")
    for s, toks in generator_samples(gen_dir, java).items():
        m = measure(toks, SEED); res["generator"][str(s)] = m
        log(f"  seed {s} words {int(m['word_types']):6d} stems {int(m['stem_types']):6d} NSTEM95 {m['NSTEM95']:6.0f} COLLAPSE {m['COLLAPSE']:.3f} "
            f"HAPAX {m['STEM_HAPAX']:.3f} ZIPF {m['STEM_ZIPF']:+.2f}")
    L, P, G = list(res["languages"].values()), list(res["padding"].values()), list(res["generator"].values())

    # controls
    loo = []
    for k, m in res["padding"].items():
        others = [x for kk, x in res["padding"].items() if kk != k]
        loo.append(verdict(m, L, others)["verdict"])
    cm = measure(caesar(), SEED); res["caesar"] = cm
    cv = verdict(cm, L, P, G); res["caesar_verdict"] = cv
    pad_ok = sum(v == "PADDING-LIKE" for v in loo) >= 8
    res["controls"] = dict(padding_loo=loo, padding_pass=pad_ok, caesar=cv["verdict"], caesar_pass=cv["verdict"] == "WORD-LIKE")
    valid = pad_ok and cv["verdict"] == "WORD-LIKE"
    log(f"[controls] padding leave-one-out {loo.count('PADDING-LIKE')}/10 PADDING-LIKE | Caesar -> {cv['verdict']} (z_lang {cv['z_lang']}) | {'VALID' if valid else 'VOID'}")

    # Voynich
    vm = measure(vtoks, SEED); res["voynich"] = vm
    vv = verdict(vm, L, P, G); res["voynich_verdict"] = vv
    log(f"[VOYNICH] words {int(vm['word_types'])} stems {int(vm['stem_types'])} NSTEM95 {vm['NSTEM95']:.0f} COLLAPSE {vm['COLLAPSE']:.3f} "
        f"HAPAX {vm['STEM_HAPAX']:.3f} ZIPF {vm['STEM_ZIPF']:+.2f} | SPLIT {vm['SPLIT']:.2f} NSUF95 {vm['NSUF95']:.0f} | h2 words {vm['h2_words']:.2f} stems {vm['h2_stems']:.2f}")
    log(f"  z vs languages {vv['z_lang']}")
    log(f"  z vs padding   {vv['z_pad']}")
    log(f"  z vs generator {vv['z_gen']}")
    log(f"  top stems {vm['top_stems']}")
    log(f"  top suffixes {vm['top_suffixes']}")
    final = vv["verdict"] if valid else "VOID"
    res["verdict"] = final
    res["factor"] = {"PADDING-LIKE": "C x3", "WORD-LIKE": "C x0.8 (absence rule)"}.get(final, "none")
    res["borderline"] = vv["borderline"]
    res["runtime_s"] = time.time() - t0
    log(f"VERDICT {final} | factor {res['factor']} | borderline {vv['borderline']} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
