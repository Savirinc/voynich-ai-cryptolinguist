"""E084: mixed-language sources (Hebrew with Aramaic, Judeo-Arabic, Latin, Turkish, Greek; real Talmud) against
non-Hebrew mixtures, with the E083 construction and the E063 letter attack. See reports/E084_PREREG.md.
Run: caffeinate -ims .venv/bin/python experiments/e084_mixed_sources.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time, unicodedata
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e083_hebrew_construction as C  # noqa: E402

SEED, N, CHUNK = 84084, 28841, 10
OUT = ROOT / "experiments/results/e084.json"
SRC = ROOT / "data/external/hebrew_script"
HEB_TR = dict(zip("אבגדהוזחטיכךלמםנןסעפףצץקרשת", list("abgdhuzxticclmmnnsoppqqyref")))
HEBREW_SET = {"talmud", "heb+aram", "heb+jarab", "heb+latin", "heb+turkish", "heb+greek"}
OTHER_SET = {"latin+german", "turkish+greek", "latin+greek"}
NULL_SET = {"scrheb+scrlat"}
CONSTRUCTION = sorted(HEBREW_SET | OTHER_SET | NULL_SET)
LETTER = {"talmud": None, "heb+aram": None, "heb+jarab": None, "hebtr+latin": None, "hebtr+turkish": None,
          "latin+german": None, "latin+turkish": None}


def log(*a):
    print(*a, flush=True)


def cons(w):
    return "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c)[0] != "M")


def base(name):
    from e064_early_audit import tok
    from e052_shortlist_attack import norm
    if name in ("aram", "jarab", "talmud"):
        fn = {"aram": "onkelos.txt", "jarab": "rasag.txt", "talmud": "talmud.txt"}[name]
        return [w for l in (SRC / fn).read_text(encoding="utf-8").splitlines() for w in norm(l)
                if all("א" <= c <= "ת" for c in w)]
    if name == "hebtr":
        return [t for t in ("".join(HEB_TR.get(c, "") for c in w) for w in base("heb")) if t]
    bid = {"heb": "hboWLC", "latin": "latVUC", "turkish": "turytc", "greek": "grcbyz", "german": "deu1912"}[name]
    w = tok(bid)
    if bid == "hboWLC":
        w = [x for x in (cons(t) for t in w) if x and all("א" <= c <= "ת" for c in x)]
    else:
        w = [x for x in (cons(t) for t in w) if x]
    return w


def mix(a, b):
    out, i = [], 0
    while i + CHUNK <= min(len(a), len(b)):
        out += a[i:i + CHUNK] + b[i:i + CHUNK]; i += CHUNK
    return out


def stream(name):
    if name == "talmud":
        return base("talmud")
    if name == "scrheb+scrlat":
        rng = random.Random(SEED)
        sc = lambda ws: ["".join(rng.sample(x, len(x))) for x in ws]
        return mix(sc(base("heb")), sc(base("latin")))
    a, b = name.split("+")
    key = {"heb": "heb", "aram": "aram", "jarab": "jarab", "latin": "latin", "turkish": "turkish", "greek": "greek",
           "german": "german", "hebtr": "hebtr"}
    return mix(base(key[a]), base(key[b]))


C.source_words = stream          # the E083 construction now reads mixed streams (same code otherwise)


def known_answer(rng):
    w = stream("talmud"); win = w[60000:60000 + N]
    PRE, SUF = C.affix_lists("talmud", sorted(set(w[10000:10000 + N])))
    letters = sorted({c for x in win for c in C.decompose(x, PRE, SUF)[1]})
    hidden = {"PT": {p: rng.choice(C.FRONTS) for p in [""] + PRE}, "ST": {s: rng.choice(C.ENDS) for s in [""] + SUF},
              "RT": {c: rng.choice(C.CHUNKS[1:]) for c in letters}, "M": 3, "PRE": PRE, "SUF": SUF}
    enc = C.encoder(hidden)
    return [enc(x) for x in win], win


def letter_attack(workers, rng):
    import e047_known_answer_script as K
    from e049_attack_voynich import voynich_seqs
    from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio
    from e063_wide_attack import judge
    VA, _, locked = voynich_a_by_folio(); VB, _, _, _ = voynich_seqs("B"); _, sw = K.voynich_signs()
    K.LMS.clear(); tasks, metas = [], {}
    for name in LETTER:
        s = stream(name); cut = int(len(s) * 0.6)
        K.LMS[name] = K.SpaceLM(s[:cut], name)
        plain = K.keep_letters(s[cut:], K.LMS[name].letters)
        assert len(plain) >= 2 * len(VA), (name, len(plain))
        freq = Counter(c for w in plain for c in w)
        for k in range(2):
            st = rng.randrange(0, len(plain) - len(VA)); key = K.make_key(K.LMS[name].letters, freq, rng)
            sq, lab = K.encode(plain[st:st + len(VA)], key, sw, rng)
            tasks.append((f"{name}:crack{k}", name, sq, lab, rng.randrange(1 << 30)))
        for k in range(2):
            tasks.append((f"{name}:control:generator{k}", name, K.gibberish_streams(len(VA), rng), None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{name}:control:pseudo{k}", name, markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_A", name, VA, None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{name}:controlB:pseudo{k}", name, markov_pseudo(VB, len(VB), rng), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_B", name, VB, None, rng.randrange(1 << 30)))
        metas[name] = {"stream_words": len(s), "letters": "".join(K.LMS[name].letters)}
    with Pool(workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    dec = {r["name"]: r.pop("decoded", None) for r in res}
    out = {}
    for name in LETTER:
        R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(name + ":")}
        j = judge(name, R); out[name] = {**metas[name], **j, "decoded_A": dec[f"{name}:VOYNICH_A"][:30], "decoded_B": dec[f"{name}:VOYNICH_B"][:30]}
        log(f"[letters] {name:14s} cracks {[(round(x, 3), round(y, 3)) for x, y, _ in j['cracks']]} ctrlA {j['controls_max_A']:.3f} "
            f"-> {'VALIDATED T=%.3f' % j['threshold'] if j['validated'] else 'NOT VALIDATED'} | A {j['voynich_A']['lexrate']:.3f} "
            f"{'CLAIM' if j['voynich_A']['claim'] else 'no claim'} | B {j['voynich_B']['lexrate']:.3f} agr {j['voynich_B']['agreement']:.2f} "
            f"ctrlB {j['controls_max_B']:.3f} {'CLAIM' if j['voynich_B']['claim'] else 'no claim'}")
    return out, locked


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    for n in CONSTRUCTION + list(LETTER):
        log(f"stream {n}: {len(stream(n))} words")
    from e011_twin_search import voynich_lines
    vl, _, _, _ = voynich_lines()
    vl = [[x for x in l if x] for l in vl]; vl = [l for l in vl if l]
    V = Counter(x for l in vl for x in l); tot = sum(V.values()); voy = {k: v / tot for k, v in V.items()}
    ktoks, kwin = known_answer(rng)
    KC = Counter(ktoks); kt = sum(KC.values()); kvoy = {k: v / kt for k, v in KC.items()}
    jobs = [("talmud", r, kvoy) for r in range(C.RESTARTS)] + [(s, r, voy) for s in CONSTRUCTION for r in range(C.RESTARTS)]
    with Pool(a.workers) as pool:
        res = pool.map(C.fit_task, jobs)
    known, fits = res[:C.RESTARTS], res[C.RESTARTS:]
    kb = max(known, key=lambda x: x[2])
    enc = C.encoder(kb[3]); inv = {}
    for t, _ in Counter(stream("talmud")[10000:10000 + N]).most_common():
        inv.setdefault(enc(t), t)
    correct = sum(1 for x, s in zip(ktoks, kwin) if inv.get(x) == s) / len(ktoks)
    klines, i = [], 0
    for l in vl:
        if i >= len(ktoks):
            break
        klines.append(ktoks[i:i + len(l)]); i += len(l)
    kord = C.order_test("talmud", kb[3], klines, random.Random(SEED + 7))
    log(f"[known answer] hidden-table Talmud: intersection {kb[2]:.3f}, exact words {correct:.3f}, order z {kord['z']:+.2f}")
    best = {s: max((x for x in fits if x[0] == s), key=lambda x: x[2]) for s in CONSTRUCTION}
    orders = {s: C.order_test(s, best[s][3], vl, random.Random(SEED + 11)) for s in CONSTRUCTION}
    for s in CONSTRUCTION:
        tag = "HEB" if s in HEBREW_SET else ("NON" if s in OTHER_SET else "NULL")
        log(f"[construction] {tag:4s} {s:14s} fit {best[s][2]:.3f} M={best[s][3]['M']} | order z {orders[s]['z']:+.2f} decoded {orders[s]['decoded_share']:.2f}")
    hb = max(HEBREW_SET, key=lambda s: best[s][2])
    fit_h, fit_o = best[hb][2], max(best[s][2] for s in OTHER_SET)
    ord_h = max(orders[s]["z"] for s in HEBREW_SET)
    ord_hb = max(HEBREW_SET, key=lambda s: orders[s]["z"])
    ord_ctrl = max(orders[s]["z"] for s in OTHER_SET | NULL_SET)
    valid = correct >= 0.5 and kord["z"] > 3
    spec = fit_h > fit_o + 0.05
    order_ok = ord_h > 3 and ord_h > ord_ctrl
    log(f"[decode sample, {ord_hb}]"); [log("   " + x) for x in orders[ord_hb]["sample"][:8]]
    letters, locked = letter_attack(a.workers, rng)
    claims = [(n, t) for n, o in letters.items() for t in "AB" if o[f"voynich_{t}"]["claim"]]
    if not valid:
        cverdict = "VOID"
    elif spec and order_ok:
        cverdict = f"CONSTRUCTION HOLDS ({hb} fit; {ord_hb} order)"
    elif spec:
        cverdict = "HEBREW MIXTURE FITS BEST BUT ORDER FAILS"
    elif order_ok:
        cverdict = f"ORDER PASSES ({ord_hb}) BUT FIT NOT HEBREW-SPECIFIC"
    else:
        cverdict = "CONSTRUCTION FAILS"
    lverdict = ("CLAIM: " + ", ".join(f"{n}/{t}" for n, t in claims)) if claims else (
        "NO CLAIM, validated" if all(o["validated"] for o in letters.values()) else "NO CLAIM, partly validated")
    log(f"[specificity] best Hebrew mixture {hb} {fit_h:.3f} vs best non-Hebrew {fit_o:.3f}; order best Hebrew {ord_hb} {ord_h:+.2f} vs best control {ord_ctrl:+.2f}")
    log(f"VERDICT construction: {cverdict} | letters: {lverdict} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E084", "seed": SEED, "known_answer": {"intersection": kb[2], "exact_words": correct, "order": kord},
                               "construction": {s: {"fit": best[s][2], "tables": best[s][3], "order": orders[s]} for s in CONSTRUCTION},
                               "letters": letters, "construction_verdict": cverdict, "letter_verdict": lverdict,
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
