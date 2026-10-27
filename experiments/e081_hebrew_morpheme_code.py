"""E081 (Hebrew campaign H3): morpheme-code attack. Voynich words cut into front + bridge glyphs + ending; Hebrew words
cut into prefix + root letters + suffix; the E047 annealer searches a many-to-one map from Voynich units to Hebrew units
under a 4-gram KN model of Hebrew unit sequences. See reports/E081_PREREG.md.
Run: caffeinate -ims .venv/bin/python experiments/e081_hebrew_morpheme_code.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo  # noqa: E402
from e052_shortlist_attack import OT_LM, OT_TEST, book_words  # noqa: E402

SEED, NS = 81081, 40
ITERS = 60_000
OUT = ROOT / "experiments/results/e081.json"
HE_PRE = ["וה", "וב", "ול", "ומ", "וכ", "וש", "ה", "ו", "ב", "ל", "מ", "כ", "ש"]
HE_SUF = ["ים", "ות", "יו", "יה", "הם", "הן", "כם", "נו", "תי", "תם", "ו", "ה", "י", "ך", "ם", "ן", "ת"]
V_FRONT = ["qo", "q", "o", "d", "y", "s", "l"]
V_END = ["aiin", "ain", "iin", "in", "edy", "eey", "ey", "dy", "y", "ol", "or", "al", "ar", "am", "m", "r", "l", "s", "o", "d"]


def log(*a):
    print(*a, flush=True)


def he_units(w):
    p = next((x for x in HE_PRE if w.startswith(x) and len(w) - len(x) >= 2), "")
    r = w[len(p):]
    s = next((x for x in HE_SUF if r.endswith(x) and len(r) - len(x) >= 2), "")
    core = r[:len(r) - len(s)] if s else r
    return ([("P", p)] if p else []) + [("L", c) for c in core] + ([("S", s)] if s else [])


def v_units(w):
    w = K.n1(w)
    f = next((x for x in V_FRONT if w.startswith(x) and len(w) > len(x)), "")
    r = w[len(f):]
    e = next((x for x in V_END if r.endswith(x) and len(r) >= len(x)), "")
    mid = r[:len(r) - len(e)] if e else r
    return ([("F", f)] if f else []) + [("B", g) for g in (K.A24.segment(mid, K.A24.SEGS["S3"]) if mid else [])] + ([("E", e)] if e else [])


def _init(state, ns):
    K.NSIGN = ns
    K.LMS.update(state)


def run_task(task):
    import e047_known_answer_script as KK
    KK.ITERS = ITERS
    return decode_task(task)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    K.NSIGN = NS
    # Hebrew units -> single private-use characters
    lm_w = [he_units(w) for w in book_words("hboWLC", OT_LM)]
    te_w = [he_units(w) for w in book_words("hboWLC", OT_TEST)]
    hu = Counter(u for w in lm_w for u in w)
    hch = {u: chr(0xE000 + i) for i, (u, _) in enumerate(hu.most_common())}
    lm_words = ["".join(hch[u] for u in w) for w in lm_w]
    K.LMS["hebunits"] = K.SpaceLM(lm_words, "hebunits")
    lm = K.LMS["hebunits"]
    plain = K.keep_letters(["".join(hch[u] for u in w if u in hch) for w in te_w], lm.letters)
    inv = {c: u for u, c in hch.items()}
    # Voynich units
    from e011_twin_search import voynich_lines
    from vcl.corpus.splits import locked_test_leaves  # noqa: F401
    L, cur, _, locked = voynich_lines()
    vw = {t: [v_units(w) for l, c in zip(L, cur) if c == t for w in l if w] for t in "AB"}
    vu = Counter(u for t in "AB" for w in vw[t] for u in w)
    top = [u for u, _ in vu.most_common(NS)]; idx = {u: i + 1 for i, u in enumerate(top)}
    sw = np.array([vu[u] for u in top], float)
    seqs = {t: [s for s in ([idx[u] for u in w if u in idx] for w in vw[t]) if s] for t in "AB"}
    dropped = sum(1 for t in "AB" for w in vw[t] for u in w if u not in idx)
    total = sum(len(w) for t in "AB" for w in vw[t])
    log(f"Hebrew unit types {len(hu)} (top {NS} kept: {[inv[c] for c in lm.letters][:12]}...), plaintext words {len(plain)}")
    log(f"Voynich unit types {len(vu)}, top {NS} kept, dropped {dropped}/{total} units; A words {len(seqs['A'])}, B words {len(seqs['B'])}")
    log(f"Voynich units: {top}")
    VA, VB = seqs["A"], seqs["B"]
    freq = Counter(c for w in plain for c in w)
    tasks = []
    for k in range(2):
        st = rng.randrange(0, len(plain) - len(VA)); key = K.make_key(lm.letters, freq, rng)
        s, lab = K.encode(plain[st:st + len(VA)], key, sw, rng)
        tasks.append((f"crack{k}", "hebunits", s, lab, rng.randrange(1 << 30)))
    from e032_copy_generator import generate  # generator text cut the same way
    for k in range(2):
        g = [w for l in generate(Path(sys.argv[sys.argv.index("--gen") + 1]) if "--gen" in sys.argv else ROOT / "data/external/timm_schinner_generator/sct",
                                 "/opt/homebrew/opt/openjdk/bin/java", 31 + k, len(VA), ROOT / "data/external/e081_gen_work") for w in l]
        gs = [s for s in ([idx[u] for u in v_units(w) if u in idx] for w in g) if s][:len(VA)]
        tasks.append((f"control:generator{k}", "hebunits", gs, None, rng.randrange(1 << 30)))
    for k in range(5):
        tasks.append((f"control:pseudo{k}", "hebunits", markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
    tasks.append(("VOYNICH_A", "hebunits", VA, None, rng.randrange(1 << 30)))
    for k in range(5):
        tasks.append((f"controlB:pseudo{k}", "hebunits", markov_pseudo(VB, len(VB), rng), None, rng.randrange(1 << 30)))
    tasks.append(("VOYNICH_B", "hebunits", VB, None, rng.randrange(1 << 30)))
    if a.dry:
        log("dry run: tasks built", [t[0] for t in tasks]); return
    with Pool(a.workers, initializer=_init, initargs=(dict(K.LMS), NS)) as pool:
        res = pool.map(run_task, tasks)
    R = {r["name"]: r for r in res}
    cr = [R["crack0"], R["crack1"]]
    cmaxA = max(v["lexrate"] for k, v in R.items() if k.startswith("control:"))
    cmaxB = max(v["lexrate"] for k, v in R.items() if k.startswith("controlB:"))
    cmin = min(c["lexrate"] for c in cr)
    valid = all(c["accuracy"] >= K.ACC_CRACK and c["agreement"] >= K.AGREE_MIN for c in cr) and cmin > cmaxA
    T = (cmin + cmaxA) / 2 if valid else None
    out = {}
    for t, cm in (("A", cmaxA), ("B", cmaxB)):
        v = R[f"VOYNICH_{t}"]
        out[t] = {"lexrate": v["lexrate"], "agreement": v["agreement"],
                  "claim": bool(valid and v["agreement"] >= K.AGREE_MIN and v["lexrate"] >= T and v["lexrate"] > cm + 0.05)}
        out[t]["decoded_sample"] = [" ".join("".join(inv.get(c, ("?", "?"))[1] for c in d) for d in v["decoded"][:40])]
    for r in res:
        r.pop("decoded", None)
    verdict = ("CLAIM: " + ",".join(t for t in "AB" if out[t]["claim"])) if any(out[t]["claim"] for t in "AB") else (
        "NO CLAIM, validated" if valid else "NOT VALIDATED (H3 untested at this setting)")
    log(f"cracks {[(round(c['accuracy'], 3), round(c['lexrate'], 3), round(c['agreement'], 2)) for c in cr]} controls A max {cmaxA:.3f} B max {cmaxB:.3f} "
        f"-> {'VALIDATED T=%.3f' % T if valid else 'NOT VALIDATED'}")
    for t in "AB":
        log(f"Voynich {t}: lexrate {out[t]['lexrate']:.3f} agreement {out[t]['agreement']:.2f} {'CLAIM' if out[t]['claim'] else 'no claim'} | {out[t]['decoded_sample'][0][:200]}")
    log(f"VERDICT {verdict} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E081", "seed": SEED, "nsign": NS, "iters": ITERS, "validated": valid, "threshold": T,
                               "controls_max_A": cmaxA, "controls_max_B": cmaxB, "voynich": out, "verdict": verdict,
                               "voynich_units": [list(u) for u in top], "dropped_units": [dropped, total], "results": res,
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
