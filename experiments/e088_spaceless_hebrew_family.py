"""E088: spaceless line-by-line attack for the Hebrew family and Arabic with a yardstick chosen on known answers only.
Decoding exactly E087 (v3 functions, new seed); all decoded lines saved. Three candidate yardsticks:
  COVER4  share of decoded letters inside dictionary words of >= 4 letters (best segmentation)
  COVER5  the same with >= 5 letters
  PAIR    unigram-best segmentation into model words, then mean over adjacent known-word pairs of
          log P(b | a) - log P(b) (word-bigram association; add-0.1)
Selection (known answers only): a yardstick validates a language if min(crack scores) > max(A-control scores); the
yardstick validating the most languages is chosen, ties by the larger mean normalised gap
(min crack - max control) / (max crack - min control). Voynich is scored only with the chosen yardstick.
CLAIM iff validated, agreement >= 0.95 and score >= T = (min crack + max A control) / 2 (for B: also > max B control).
Run: caffeinate -ims .venv/bin/python experiments/e088_spaceless_hebrew_family.py GEN_DIR JAVA [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
import e087_spaceless_attack_v3 as S  # noqa: E402
from e050_hebrew_nearmiss import decode_task  # noqa: E402

SEED = 88088
OUT = ROOT / "experiments/results/e088.json"
DEC = ROOT / "experiments/results/e088_decoded.json"
LANGS = ["hboWLC", "aramaic_onkelos", "judeoarabic_saadia", "talmud", "arb-vd"]
RULERS = ["COVER4", "COVER5", "PAIR"]


def log(*a):
    print(*a, flush=True)


def cover_min(lines, vocab, minlen):
    v = {w for w in vocab if len(w) >= minlen}
    tot = cov = 0
    for s in lines:
        n = len(s); best = [0] * (n + 1)
        for i in range(1, n + 1):
            best[i] = best[i - 1]
            for j in range(max(0, i - 12), i - minlen + 1):
                if s[j:i] in v and best[j] + (i - j) > best[i]:
                    best[i] = best[j] + (i - j)
        tot += n; cov += best[n]
    return cov / tot if tot else 0.0


def pair_score(lines, uni, big, total):
    V = len(uni) + 1
    lp1 = lambda w: math.log((uni.get(w, 0) + 0.1) / (total + 0.1 * V))
    vals = []
    for s in lines:
        n = len(s); best = [-1e18] * (n + 1); back = [0] * (n + 1); best[0] = 0.0
        for i in range(1, n + 1):
            for j in range(max(0, i - 12), i):
                w = s[j:i]
                sc = best[j] + (lp1(w) if w in uni else -14.0 * (i - j))
                if sc > best[i]:
                    best[i], back[i] = sc, j
        words, i = [], n
        while i > 0:
            words.append(s[back[i]:i]); i = back[i]
        words.reverse()
        for a, b in zip(words, words[1:]):
            if a in uni and b in uni:
                vals.append(math.log((big.get((a, b), 0) + 0.1) / (uni[a] + 0.1 * V)) - lp1(b))
    return sum(vals) / len(vals) if vals else -10.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("gen_dir"); ap.add_argument("java"); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    V, sw, locked = S.voynich_lines_units()
    signs, _ = K.voynich_signs(); sidx = {s: i + 1 for i, s in enumerate(signs)}
    lensA = [len(l) for l in V["A"]]
    langs = LANGS[:1] if a.smoke else LANGS
    K.LMS.clear(); tasks, models = [], {}
    gen = [S.generator_lines(a.gen_dir, a.java, s, len(V["A"]), sidx) for s in (31, 32)]
    for name in langs:
        w = S.lang_words(name); cut = int(len(w) * 0.6); lmw, tew = w[:cut], w[cut:]
        chunks = ["".join(lmw[i:i + 10]) for i in range(0, len(lmw), 10)]
        K.LMS[name] = K.SpaceLM(chunks, name); letters = set(K.LMS[name].letters)
        mw = ["".join(ch for ch in y if ch in letters) for y in lmw]; mw = [x for x in mw if x]
        uni = Counter(mw); big = Counter(zip(mw, mw[1:]))
        models[name] = {"vocab": {x for x, c in uni.items() if c >= 2 and len(x) >= 3}, "uni": uni, "big": big, "total": len(mw)}
        stream = "".join(ch for y in tew for ch in y if ch in letters); need = sum(lensA)
        assert len(stream) >= 2 * need, name
        freq = Counter(stream)
        for k in range(2):
            st = rng.randrange(0, len(stream) - need); pl, i = [], st
            for L in lensA:
                pl.append(stream[i:i + L]); i += L
            key = K.make_key(K.LMS[name].letters, freq, rng)
            s, lab = K.encode(pl, key, sw, rng)
            tasks.append((f"{name}:crack{k}", name, s, lab, rng.randrange(1 << 30)))
        for k in range(2):
            tasks.append((f"{name}:control:generator{k}", name, gen[k], None, rng.randrange(1 << 30)))
        for k in range(1 if a.smoke else 5):
            tasks.append((f"{name}:control:pseudo{k}", name, S.markov_lines(V["A"], rng, len(V["A"])), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_A", name, V["A"], None, rng.randrange(1 << 30)))
        for k in range(1 if a.smoke else 5):
            tasks.append((f"{name}:controlB:pseudo{k}", name, S.markov_lines(V["B"], rng, len(V["B"])), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_B", name, V["B"], None, rng.randrange(1 << 30)))
    if a.smoke:
        K.ITERS, K.RESTARTS = 200, 2
        K._init(K.LMS); res = [decode_task(t) for t in tasks]
    else:
        with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
            res = pool.map(decode_task, tasks)
    decoded = {r["name"]: r["decoded"] for r in res}
    DEC.write_text(json.dumps(decoded, ensure_ascii=False))
    R = {}
    for r in res:
        name, part = r["name"].split(":", 1); m = models[name]; d = r["decoded"]
        r["scores"] = {"COVER4": cover_min(d, m["vocab"], 4), "COVER5": cover_min(d, m["vocab"], 5),
                       "PAIR": pair_score(d, m["uni"], m["big"], m["total"])}
        r.pop("decoded"); R.setdefault(name, {})[part] = r
    # yardstick selection on known answers only
    sel = {}
    for ru in RULERS:
        val, gaps = 0, []
        for name in langs:
            X = R[name]; cr = [X["crack0"]["scores"][ru], X["crack1"]["scores"][ru]]
            ct = [v["scores"][ru] for k, v in X.items() if k.startswith("control:")]
            ok = min(cr) > max(ct) and all(X[f"crack{k}"]["accuracy"] >= K.ACC_CRACK and X[f"crack{k}"]["agreement"] >= K.AGREE_MIN for k in (0, 1))
            val += ok; gaps.append((min(cr) - max(ct)) / (max(cr) - min(ct) + 1e-12))
        sel[ru] = {"validated": val, "mean_gap": sum(gaps) / len(gaps)}
        log(f"[yardstick] {ru}: validates {val}/{len(langs)}, mean normalised gap {sel[ru]['mean_gap']:+.3f}")
    chosen = max(RULERS, key=lambda ru: (sel[ru]["validated"], sel[ru]["mean_gap"]))
    log(f"[yardstick] chosen: {chosen}")
    out, claims = {}, []
    for name in langs:
        X = R[name]; cr = [X["crack0"], X["crack1"]]
        c = lambda r: r["scores"][chosen]
        cA = max(c(v) for k, v in X.items() if k.startswith("control:")); cB = max(c(v) for k, v in X.items() if k.startswith("controlB:"))
        valid = all(x["accuracy"] >= K.ACC_CRACK and x["agreement"] >= K.AGREE_MIN for x in cr) and min(c(x) for x in cr) > cA
        T = (min(c(x) for x in cr) + cA) / 2 if valid else None
        o = {"validated": valid, "threshold": T, "cracks": [(x["accuracy"], c(x), x["agreement"]) for x in cr], "controls_max_A": cA, "controls_max_B": cB,
             "all_scores": {k: v["scores"] for k, v in X.items()}}
        for t in "AB":
            v = X[f"VOYNICH_{t}"]
            cl = bool(valid and v["agreement"] >= K.AGREE_MIN and c(v) >= T and (t == "A" or c(v) > cB))
            o[t] = {"score": c(v), "agreement": v["agreement"], "claim": cl}
            if cl:
                claims.append((name, t))
        out[name] = o
        log(f"{name:20s} cracks {[(round(x, 3), round(y, 3)) for x, y, _ in o['cracks']]} ctrlA {cA:.3f} -> {'VALIDATED T=%.3f' % T if valid else 'NOT VALIDATED'} "
            f"| A {o['A']['score']:.3f} agr {o['A']['agreement']:.2f} {'CLAIM' if o['A']['claim'] else 'no claim'} | B {o['B']['score']:.3f} "
            f"agr {o['B']['agreement']:.2f} ctrlB {cB:.3f} {'CLAIM' if o['B']['claim'] else 'no claim'}")
    verdict = ("CLAIM: " + ", ".join(f"{n}/{t}" for n, t in claims)) if claims else (
        "NO CLAIM, validated" if all(o["validated"] for o in out.values()) else "NO CLAIM, partly validated")
    log(f"VERDICT {verdict} | yardstick {chosen} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E088", "smoke": a.smoke, "seed": SEED, "selection": sel, "chosen": chosen, "languages": out,
                               "verdict": verdict, "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
