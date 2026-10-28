"""E089: spaceless line-by-line attack with mixed-language models (E088 decoding and yardstick selection, E084 mixture
streams). See reports/E089_PREREG.md.
Run: caffeinate -ims .venv/bin/python experiments/e089_spaceless_mixtures.py GEN_DIR JAVA [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
import e087_spaceless_attack_v3 as S  # noqa: E402
import e084_mixed_sources as MX  # noqa: E402
from e088_spaceless_hebrew_family import cover_min, pair_score, RULERS  # noqa: E402
from e050_hebrew_nearmiss import decode_task  # noqa: E402

SEED = 89089
OUT = ROOT / "experiments/results/e089.json"
DEC = ROOT / "experiments/results/e089_decoded.json"
HEBREW_MIX = ["heb+aram", "heb+jarab", "heb+aram+jarab", "hebtr+latin", "hebtr+turkish"]
OTHER_MIX = ["latin+german", "latin+turkish"]
MIXES = HEBREW_MIX + OTHER_MIX


def log(*a):
    print(*a, flush=True)


def stream(name):
    if name == "heb+aram+jarab":
        a, b, c = MX.base("heb"), MX.base("aram"), MX.base("jarab"); out, i, k = [], 0, MX.CHUNK
        while i + k <= min(len(a), len(b), len(c)):
            out += a[i:i + k] + b[i:i + k] + c[i:i + k]; i += k
        return out
    return MX.stream(name)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("gen_dir"); ap.add_argument("java"); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    V, sw, locked = S.voynich_lines_units()
    signs, _ = K.voynich_signs(); sidx = {s: i + 1 for i, s in enumerate(signs)}
    lensA = [len(l) for l in V["A"]]
    mixes = MIXES[:1] if a.smoke else MIXES
    K.LMS.clear(); tasks, models = [], {}
    gen = [S.generator_lines(a.gen_dir, a.java, s, len(V["A"]), sidx) for s in (31, 32)]
    for name in mixes:
        w = stream(name); cut = int(len(w) * 0.6); lmw, tew = w[:cut], w[cut:]
        chunks = ["".join(lmw[i:i + 10]) for i in range(0, len(lmw), 10)]
        K.LMS[name] = K.SpaceLM(chunks, name); letters = set(K.LMS[name].letters)
        mw = ["".join(ch for ch in y if ch in letters) for y in lmw]; mw = [x for x in mw if x]
        uni = Counter(mw); big = Counter(zip(mw, mw[1:]))
        models[name] = {"vocab": {x for x, c in uni.items() if c >= 2 and len(x) >= 3}, "uni": uni, "big": big, "total": len(mw)}
        stream_l = "".join(ch for y in tew for ch in y if ch in letters); need = sum(lensA)
        assert len(stream_l) >= 2 * need, (name, len(stream_l), need)
        freq = Counter(stream_l)
        log(f"{name}: stream words {len(w)}, letters {''.join(K.LMS[name].letters)}, plaintext letters {len(stream_l)}")
        for k in range(2):
            st = rng.randrange(0, len(stream_l) - need); pl, i = [], st
            for L in lensA:
                pl.append(stream_l[i:i + L]); i += L
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
    DEC.write_text(json.dumps({r["name"]: r["decoded"] for r in res}, ensure_ascii=False))
    R = {}
    for r in res:
        name, part = r["name"].split(":", 1); m = models[name]; d = r.pop("decoded")
        r["scores"] = {"COVER4": cover_min(d, m["vocab"], 4), "COVER5": cover_min(d, m["vocab"], 5), "PAIR": pair_score(d, m["uni"], m["big"], m["total"])}
        R.setdefault(name, {})[part] = r
    sel = {}
    for ru in RULERS:
        val, gaps = 0, []
        for name in mixes:
            X = R[name]; cr = [X["crack0"]["scores"][ru], X["crack1"]["scores"][ru]]
            ct = [v["scores"][ru] for k, v in X.items() if k.startswith("control:")]
            ok = min(cr) > max(ct) and all(X[f"crack{k}"]["accuracy"] >= K.ACC_CRACK and X[f"crack{k}"]["agreement"] >= K.AGREE_MIN for k in (0, 1))
            val += ok; gaps.append((min(cr) - max(ct)) / (max(cr) - min(ct) + 1e-12))
        sel[ru] = {"validated": val, "mean_gap": sum(gaps) / len(gaps)}
        log(f"[yardstick] {ru}: validates {val}/{len(mixes)}, mean normalised gap {sel[ru]['mean_gap']:+.3f}")
    chosen = max(RULERS, key=lambda ru: (sel[ru]["validated"], sel[ru]["mean_gap"]))
    log(f"[yardstick] chosen: {chosen}")
    out, claims = {}, []
    for name in mixes:
        X = R[name]; cr = [X["crack0"], X["crack1"]]; c = lambda r: r["scores"][chosen]
        cA = max(c(v) for k, v in X.items() if k.startswith("control:")); cB = max(c(v) for k, v in X.items() if k.startswith("controlB:"))
        valid = all(x["accuracy"] >= K.ACC_CRACK and x["agreement"] >= K.AGREE_MIN for x in cr) and min(c(x) for x in cr) > cA
        T = (min(c(x) for x in cr) + cA) / 2 if valid else None
        o = {"hebrew_mixture": name in HEBREW_MIX, "validated": valid, "threshold": T, "cracks": [(x["accuracy"], c(x), x["agreement"]) for x in cr],
             "controls_max_A": cA, "controls_max_B": cB, "all_scores": {k: v["scores"] for k, v in X.items()}}
        for t in "AB":
            v = X[f"VOYNICH_{t}"]
            cl = bool(valid and v["agreement"] >= K.AGREE_MIN and c(v) >= T and (t == "A" or c(v) > cB))
            o[t] = {"score": c(v), "agreement": v["agreement"], "claim": cl}
            if cl:
                claims.append((name, t))
        out[name] = o
        log(f"{name:16s} cracks {[(round(x, 3), round(y, 3)) for x, y, _ in o['cracks']]} ctrlA {cA:.3f} -> {'VALIDATED T=%.3f' % T if valid else 'NOT VALIDATED'} "
            f"| A {o['A']['score']:.3f} agr {o['A']['agreement']:.2f} {'CLAIM' if o['A']['claim'] else 'no claim'} | B {o['B']['score']:.3f} "
            f"agr {o['B']['agreement']:.2f} ctrlB {cB:.3f} {'CLAIM' if o['B']['claim'] else 'no claim'}")
    verdict = ("CLAIM: " + ", ".join(f"{n}/{t}" for n, t in claims)) if claims else (
        "NO CLAIM, validated" if all(o["validated"] for o in out.values()) else "NO CLAIM, partly validated")
    log(f"VERDICT {verdict} | yardstick {chosen} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E089", "smoke": a.smoke, "seed": SEED, "selection": sel, "chosen": chosen, "mixtures": out,
                               "verdict": verdict, "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
