"""E087: the validated letter attack with spaces removed and each line decoded as one record. See reports/E087_PREREG.md.
Cipher units: Voynich S3 units (23 commonest), spaces removed, one sequence per DEV prose line (Currier A, B).
Plaintext: each language with spaces removed, cut into chunks of the Voynich lines' sign counts. Model: 4-gram KN over
continuous letters with line breaks as the only separator. Score of a decode: COVER = share of decoded letters that fall
inside dictionary words (>= 3 letters, frequency >= 2 in the model text) in the best segmentation of each line.
Run: caffeinate -ims .venv/bin/python experiments/e087_spaceless_attack.py GEN_DIR JAVA [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time, unicodedata
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from e050_hebrew_nearmiss import decode_task  # noqa: E402

SEED = 87087
OUT = ROOT / "experiments/results/e087.json"
LANGS = ["hboWLC", "aramaic_onkelos", "judeoarabic_saadia", "talmud", "latVUC", "turytc", "deu1912", "arb-vd"]
MAXW = 12


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def lang_words(name):
    from e052_shortlist_attack import norm
    if name in ("aramaic_onkelos", "judeoarabic_saadia", "talmud"):
        fn = {"aramaic_onkelos": "onkelos.txt", "judeoarabic_saadia": "rasag.txt", "talmud": "talmud.txt"}[name]
        return [w for l in (ROOT / "data/external/hebrew_script" / fn).read_text(encoding="utf-8").splitlines() for w in norm(l)]
    from e064_early_audit import tok
    w = tok(name)
    return [x for x in (cons(t) for t in w) if x] if name in ("hboWLC", "arb-vd") else w


def voynich_lines_units():
    signs, sw = K.voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    L, cur, _, locked = K.E.voynich_lines()
    out = {"A": [], "B": []}
    for l, c in zip(L, cur):
        if c not in out:
            continue
        u = [idx[x] for w in l if w for x in K.A24.segment(K.n1(w), K.A24.SEGS["S3"]) if x in idx]
        if u:
            out[c].append(u)
    return out, sw, locked


def markov_lines(lines, rng, n):
    tr = defaultdict(Counter)
    for l in lines:
        s = ["^", "^"] + l + ["$"]
        for a, b, c in zip(s, s[1:], s[2:]):
            tr[(a, b)][c] += 1
    out = []
    while len(out) < n:
        a, b, l = "^", "^", []
        while len(l) < 200:
            ch = tr[(a, b)]; c = rng.choices(list(ch), list(ch.values()))[0]
            if c == "$":
                break
            l.append(c); a, b = b, c
        if l:
            out.append(l)
    return out


def generator_lines(gen_dir, java, seed, n_lines, sw_idx):
    from e032_copy_generator import generate
    g = generate(gen_dir, java, seed, 40000, ROOT / f"data/external/e087_gen_work")
    out = []
    for l in g:
        u = [sw_idx[x] for w in l for x in K.A24.segment(K.n1(w), K.A24.SEGS["S3"]) if x in sw_idx]
        if u:
            out.append(u)
        if len(out) >= n_lines:
            break
    return out


def cover(lines, vocab):
    tot = cov = 0
    segs = []
    for s in lines:
        n = len(s); best = [0] * (n + 1); back = [None] * (n + 1)
        for i in range(1, n + 1):
            best[i], back[i] = best[i - 1], (i - 1, False)
            for j in range(max(0, i - MAXW), i - 2):
                if s[j:i] in vocab and best[j] + (i - j) > best[i]:
                    best[i], back[i] = best[j] + (i - j), (j, True)
        tot += n; cov += best[n]
        parts, i = [], n
        while i > 0:
            j, isw = back[i]; parts.append(s[j:i] if isw else "·" + s[j:i]); i = j
        segs.append(" ".join(reversed(parts)))
    return cov / tot if tot else 0.0, segs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("gen_dir"); ap.add_argument("java"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    V, sw, locked = voynich_lines_units()
    signs, _ = K.voynich_signs(); sidx = {s: i + 1 for i, s in enumerate(signs)}
    lensA = [len(l) for l in V["A"]]
    K.LMS.clear(); tasks, meta, vocabs = [], {}, {}
    gen = [generator_lines(a.gen_dir, a.java, s, len(V["A"]), sidx) for s in (31, 32)]
    for name in LANGS:
        w = lang_words(name); cut = int(len(w) * 0.6)
        lmw, tew = w[:cut], w[cut:]
        # model text: verses/chunks of ~10 words joined without spaces
        chunks = ["".join(lmw[i:i + 10]) for i in range(0, len(lmw), 10)]
        K.LMS[name] = K.SpaceLM(chunks, name)
        letters = set(K.LMS[name].letters)
        vocabs[name] = {x for x, c in Counter("".join(ch for ch in y if ch in letters) for y in lmw).items() if c >= 2 and len(x) >= 3}
        stream = "".join(ch for y in tew for ch in y if ch in letters)
        need = sum(lensA)
        assert len(stream) >= 2 * need, (name, len(stream), need)
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
        for k in range(5):
            tasks.append((f"{name}:control:pseudo{k}", name, markov_lines(V["A"], rng, len(V["A"])), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_A", name, V["A"], None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{name}:controlB:pseudo{k}", name, markov_lines(V["B"], rng, len(V["B"])), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_B", name, V["B"], None, rng.randrange(1 << 30)))
        meta[name] = {"letters": "".join(K.LMS[name].letters), "vocab": len(vocabs[name])}
        log(f"{name}: model chunks {len(chunks)}, vocab {len(vocabs[name])}, plaintext letters {len(stream)}")
    with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    R = {}
    for r in res:
        name, part = r["name"].split(":", 1)
        c, segs = cover(r.pop("decoded"), vocabs[name])
        r["cover"] = c; r["sample"] = segs[:15]
        R.setdefault(name, {})[part] = r
    out, claims = {}, []
    for name in LANGS:
        X = R[name]; cr = [X["crack0"], X["crack1"]]
        cA = max(v["cover"] for k, v in X.items() if k.startswith("control:")); cB = max(v["cover"] for k, v in X.items() if k.startswith("controlB:"))
        cmin = min(c["cover"] for c in cr)
        valid = all(c["accuracy"] >= K.ACC_CRACK and c["agreement"] >= K.AGREE_MIN for c in cr) and cmin > cA
        T = (cmin + cA) / 2 if valid else None
        o = {"validated": valid, "threshold": T, "cracks": [(c["accuracy"], c["cover"], c["agreement"]) for c in cr], "controls_max_A": cA, "controls_max_B": cB}
        for t, cm in (("A", cA), ("B", cB)):
            v = X[f"VOYNICH_{t}"]
            cl = bool(valid and v["agreement"] >= K.AGREE_MIN and v["cover"] >= T and v["cover"] > cm + 0.05)
            o[t] = {"cover": v["cover"], "agreement": v["agreement"], "claim": cl, "sample": v["sample"]}
            if cl:
                claims.append((name, t))
        out[name] = {**meta[name], **o}
        log(f"{name:20s} cracks {[(round(x, 3), round(y, 3)) for x, y, _ in o['cracks']]} ctrlA {cA:.3f} -> {'VALIDATED T=%.3f' % T if valid else 'NOT VALIDATED'} "
            f"| A {o['A']['cover']:.3f} agr {o['A']['agreement']:.2f} {'CLAIM' if o['A']['claim'] else 'no claim'} | B {o['B']['cover']:.3f} "
            f"agr {o['B']['agreement']:.2f} ctrlB {cB:.3f} {'CLAIM' if o['B']['claim'] else 'no claim'}")
        log(f"   A sample: {o['A']['sample'][0][:150]}")
    verdict = ("CLAIM: " + ", ".join(f"{n}/{t}" for n, t in claims)) if claims else (
        "NO CLAIM, validated" if all(o["validated"] for o in out.values()) else "NO CLAIM, partly validated")
    log(f"VERDICT {verdict} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E087", "seed": SEED, "languages": out, "verdict": verdict, "locked_test_excluded": locked,
                               "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
