"""E065: the syllable route, go/no-go. See reports/E065_PREREG.md.

Half 1 (syllabary): for 11 Latin/Greek-script Bibles, syllabify words (crude rule, declared) in two renderings: FULL
  syllables and CV-reduced (coda dropped, Linear-B-like). F95 = final syllables covering 95% of word tokens. A language
  passes iff F95 <= 2 x E95 in either rendering, where E95 = Voynich final-group classes (E026 suffix incl. the empty
  class) covering 95% of DEV word tokens. Also reported: I95 (initial), S95 (all syllables), syllables per word.
Half 2 (pfeaster, each Voynich word = one syllable): the syllable stream of each language (28,841 syllables): types,
  hapax share, Zipf slope, R, NR. Passes iff 4,860 <= types <= 7,290 and hapax >= 0.55. Vietnamese (syllable-spaced) is
  a reference row.
Syllabifier gate: syllables per word within 0.4 of the declared typical value, else the language is UNRELIABLE.
Seed rule: a language within 10% of a bar is re-measured on 10 random windows (>= 8 of 10 agree).
Run: caffeinate -ims .venv/bin/python experiments/e065_syllable_gonogo.py [--dry]
"""
from __future__ import annotations

import argparse, json, random, sys, time, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from e031_copy_pairs import stats as pair_stats  # noqa: E402
from e064_early_audit import tok  # noqa: E402
from vcl.solvers.segment import segment_types  # noqa: E402

SEED, N, START = 65065, 28841, 10000
OUT = ROOT / "experiments/results/e065.json"
SEG = dict(max_suf=4, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, smooth=0.01)   # = E026/E061
# language: (vowels after mark stripping, y-is-vowel rule, typical syllables per word)
LANGS = {"latVUC": ("aeiou", True, 2.4), "ita1885": ("aeiou", True, 2.3), "deu1912": ("aeiou", True, 1.8),
         "ces1613": ("aeiou", True, 2.0), "hun": ("aeiou", True, 2.3), "grcbyz": ("αεηιουω", False, 2.5),
         "turytc": ("aeıiou", False, 2.5), "fraLSG": ("aeiou", True, 1.7), "eng-kjv": ("aeiou", True, 1.4),
         "polubg": ("aeiou", True, 2.1), "nld": ("aeiou", True, 1.7)}
REF = "vie1934"
TYPES_LO, TYPES_HI, HAPAX_MIN, SLACK = 4860, 7290, 0.55, 2.0


def log(*a):
    print(*a, flush=True)


def strip_marks(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn" and c != "'")


def syllabify(w, vowels, y_vowel):
    """Nuclei = maximal vowel runs (y counts as a vowel only when not next to another vowel, if y_vowel). A consonant
    cluster between nuclei gives one consonant to the coda and the rest to the next onset (V.CV, VC.CV, VC.CCV)."""
    isv = []
    for i, c in enumerate(w):
        if c in vowels:
            isv.append(True)
        elif y_vowel and c == "y":
            nb = (w[i - 1] if i else "") + (w[i + 1] if i + 1 < len(w) else "")
            isv.append(not any(x in vowels for x in nb))
        else:
            isv.append(False)
    if not any(isv):
        return [w]
    nuclei = []
    i = 0
    while i < len(w):
        if isv[i]:
            j = i
            while j < len(w) and isv[j]:
                j += 1
            nuclei.append((i, j)); i = j
        else:
            i += 1
    cuts = [0]
    for (a1, b1), (a2, b2) in zip(nuclei, nuclei[1:]):
        ncons = a2 - b1                  # consonants between the two nuclei
        cuts.append(b1 if ncons <= 1 else b1 + 1)
    cuts.append(len(w))
    return [w[a:b] for a, b in zip(cuts, cuts[1:]) if b > a]


def cv_reduce(s, vowels, y_vowel):
    """Drop the coda: trailing consonants after the last vowel of the syllable."""
    j = len(s)
    while j > 0 and not (s[j - 1] in vowels or (y_vowel and s[j - 1] == "y")):
        j -= 1
    return s[:j] if j > 0 else s


def n95(counter):
    tot = sum(counter.values()); acc = k = 0
    for _, c in counter.most_common():
        if acc >= 0.95 * tot:
            break
        acc += c; k += 1
    return k


def inventories(words, vowels, y_vowel):
    syl = [syllabify(w, vowels, y_vowel) for w in words]
    out = {"syl_per_word": float(np.mean([len(s) for s in syl]))}
    for name, f in (("FULL", lambda s: s), ("CV", lambda s: cv_reduce(s, vowels, y_vowel))):
        fin = Counter(f(s[-1]) for s in syl); ini = Counter(f(s[0]) for s in syl); al = Counter(f(x) for s in syl for x in s)
        out[name] = {"F95": n95(fin), "I95": n95(ini), "S95": n95(al), "n_final_types": len(fin), "n_syl_types": len(al),
                     "top_final": fin.most_common(10)}
    return out, syl


def stream_stats(stream, rng):
    wc = Counter(stream)
    fr = np.array(sorted(wc.values(), reverse=True)[:100], float)
    ps = pair_stats([stream], rng)
    return {"types": len(wc), "hapax": sum(v == 1 for v in wc.values()) / len(wc),
            "zipf": float(np.polyfit(np.log(np.arange(1, len(fr) + 1)), np.log(fr), 1)[0]),
            "R": ps["R"], "NR": ps["NR"], "mean_len": float(np.mean([len(s) for s in stream]))}


def voynich_e95():
    from e011_twin_search import voynich_lines
    vl, _, _, locked = voynich_lines()
    toks = [w for l in vl for w in l if w]
    assert len(toks) == N
    split = segment_types(Counter(toks), seed=SEED, **SEG)
    ends = Counter(w[split[w]:] for w in toks)             # "" = no suffix, its own class
    last_unit = Counter()
    from vcl.corpus.units import collapsed_units
    for w in toks:
        u = collapsed_units(w); last_unit[u[-1] if u else w] += 1
    return {"E95": n95(ends), "n_end_classes": len(ends), "share_empty": ends[""] / N, "top_endings": ends.most_common(12),
            "U95_last_unit": n95(last_unit)}, locked


def half2_pass(st):
    return TYPES_LO <= st["types"] <= TYPES_HI and st["hapax"] >= HAPAX_MIN


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    if a.dry:
        for bid, (vow, yv, _) in LANGS.items():
            w = [strip_marks(x) for x in tok(bid)[START:START + 12]]
            log(f"  {bid:8s}", [("-".join(syllabify(x, vow, yv)), "-".join(cv_reduce(s, vow, yv) for s in syllabify(x, vow, yv))) for x in w[:6]])
        log("dry run complete"); return
    res = {"experiment": "E065", "seed": SEED}
    V, locked = voynich_e95(); res["voynich"] = V; res["locked_test_excluded"] = locked
    bar = SLACK * V["E95"]
    log(f"[Voynich] E95 {V['E95']} final-group classes cover 95% (empty class {V['share_empty']:.2f}); last-unit U95 {V['U95_last_unit']}; bar F95 <= {bar:.0f}")
    log(f"  top endings {V['top_endings']}")
    H1, H2 = {}, {}
    for bid, (vow, yv, typ) in LANGS.items():
        allw = [strip_marks(x) for x in tok(bid)]
        words = allw[START:START + N]
        inv, syl = inventories(words, vow, yv)
        inv["typical_spw"] = typ; inv["reliable"] = abs(inv["syl_per_word"] - typ) <= 0.4
        inv["pass"] = inv["reliable"] and (inv["FULL"]["F95"] <= bar or inv["CV"]["F95"] <= bar)
        inv["borderline"] = any(abs(inv[r]["F95"] - bar) <= 0.1 * bar for r in ("FULL", "CV"))
        if inv["borderline"]:
            rng = random.Random(SEED); votes = []
            for _ in range(10):
                st = rng.randrange(0, len(allw) - N); i2, _ = inventories(allw[st:st + N], vow, yv)
                votes.append(i2["FULL"]["F95"] <= bar or i2["CV"]["F95"] <= bar)
            inv["seed_votes"] = votes
            if max(votes.count(True), votes.count(False)) >= 8:
                inv["pass"] = inv["reliable"] and votes.count(True) >= 8
        H1[bid] = inv
        log(f"  [H1] {bid:8s} syl/word {inv['syl_per_word']:.2f} (typ {typ}) {'' if inv['reliable'] else 'UNRELIABLE '}| FULL F95 {inv['FULL']['F95']:4d} I95 {inv['FULL']['I95']:4d} S95 {inv['FULL']['S95']:5d} "
            f"| CV F95 {inv['CV']['F95']:4d} S95 {inv['CV']['S95']:5d} | {'PASS' if inv['pass'] else 'no'}{' borderline' if inv['borderline'] else ''}")
        # half 2: syllable stream
        allsyl = [x for w in allw for x in syllabify(w, vow, yv)]
        stream = allsyl[2 * START:2 * START + N]
        st = stream_stats(stream, random.Random(SEED)); st["pass"] = half2_pass(st) and inv["reliable"]
        st["borderline"] = abs(st["types"] - TYPES_LO) <= 0.1 * TYPES_LO or abs(st["types"] - TYPES_HI) <= 0.1 * TYPES_HI or abs(st["hapax"] - HAPAX_MIN) <= 0.055
        if st["borderline"]:
            rng = random.Random(SEED); votes = []
            for _ in range(10):
                s0 = rng.randrange(0, len(allsyl) - N); votes.append(half2_pass(stream_stats(allsyl[s0:s0 + N], rng)))
            st["seed_votes"] = votes
            if max(votes.count(True), votes.count(False)) >= 8:
                st["pass"] = inv["reliable"] and votes.count(True) >= 8
        H2[bid] = st
        log(f"  [H2] {bid:8s} syllable stream: types {st['types']:5d} hapax {st['hapax']:.2f} zipf {st['zipf']:+.2f} R {st['R']:.2f} NR {st['NR']:.2f} len {st['mean_len']:.2f} | {'PASS' if st['pass'] else 'no'}{' borderline' if st['borderline'] else ''}")
    ref = tok(REF)[START:START + N]
    H2[REF] = {**stream_stats(ref, random.Random(SEED)), "reference": True}
    log(f"  [H2] {REF:8s} (reference, syllable-spaced): types {H2[REF]['types']} hapax {H2[REF]['hapax']:.2f} R {H2[REF]['R']:.2f} NR {H2[REF]['NR']:.2f}")
    res["half1"] = H1; res["half2"] = H2
    p1 = [b for b, v in H1.items() if v["pass"]]; p2 = [b for b, v in H2.items() if v.get("pass")]
    unrel = [b for b, v in H1.items() if not v["reliable"]]
    if p1 or p2:
        verdict, factor = f"GO: syllabary {p1}, syllable-per-word {p2} (validated attack next, own prereg)", "none"
    else:
        cov = 0.6 * (len(LANGS) - len(unrel)) / len(LANGS)
        fL = 1 - 0.20 * cov * 0.8
        verdict, factor = f"NO GO (unreliable: {unrel})", f"L x{fL:.3f} (absence rule on L-syll: share 0.20, coverage {cov:.2f}, m 0.2)"
    res.update(verdict=verdict, factor=factor, runtime_s=time.time() - t0)
    log(f"VERDICT {verdict} | {factor} | {res['runtime_s']:.0f}s")
    OUT.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
