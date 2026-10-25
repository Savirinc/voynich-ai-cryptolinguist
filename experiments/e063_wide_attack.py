"""E063 (campaign step 3): the E047/E052 validated letter attack on every remaining Bible language on disk, Voynich A
(primary) and B (secondary). See reports/E063_PREREG.md.

Per language (E052 machinery): LM from OT books (if Genesis exists) else gospels+Acts; plaintext from the complementary
books. 2 cracks (VOY23 ciphers of its own text) + 2 generator controls + 5 pseudo-Voynich-A controls + Voynich A;
5 pseudo-Voynich-B controls + Voynich B. VALIDATED iff both cracks acc >= 0.80, agreement >= 0.95 and min crack lexrate
> max A-control lexrate; T = midpoint. CLAIM iff validated, agreement >= 0.95, lexrate >= T, lexrate > max control + 0.05
(A: A controls; B: B controls). Languages run in batches of 5. --dry builds tasks only.
Run: caffeinate -ims .venv/bin/python experiments/e063_wide_attack.py [--dry] [--workers 3]
"""
from __future__ import annotations

import argparse, glob, json, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from e049_attack_voynich import voynich_seqs  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402
from e052_shortlist_attack import NT_LM, NT_TEST, OT_LM, OT_TEST, book_words  # noqa: E402

SEED = 63063
OUT = ROOT / "experiments/results/e063.json"
BIB = ROOT / "data/external/bibles"
DONE = {"hboWLC", "turytc", "latVUC", "ces1613", "srp1865", "hrv", "slk", "ukr1871", "ron1924", "ita1885", "rmc"}
SKIP = {"cmn-cu89s", "jpn1965", "lit", "vie1934"}
BATCH = 5


def log(*a):
    print(*a, flush=True)


def languages():
    return sorted(d.name for d in BIB.iterdir() if d.is_dir() and d.name not in DONE and d.name not in SKIP)


def build_tasks(bid, VA, VB, sw, rng):
    has_ot = bool(glob.glob(str(BIB / bid / "txt" / "*_GEN_*")))
    lmb, tb, which = (OT_LM, OT_TEST, "OT") if has_ot else (NT_LM, NT_TEST, "NT gospels+Acts")
    K.LMS[bid] = K.SpaceLM(book_words(bid, lmb), bid)
    plain = K.keep_letters(book_words(bid, tb), K.LMS[bid].letters)
    if len(plain) < 2 * len(VA) and has_ot:          # partial translation (e.g. Wycliffe): plaintext from NT instead
        plain = K.keep_letters(book_words(bid, NT_TEST), K.LMS[bid].letters); which += " (plaintext NT)"
    meta = {"lm_books": which, "letters": K.LMS[bid].letters, "plain_words": len(plain)}
    if len(plain) < 2 * len(VA):
        del K.LMS[bid]
        return [], {**meta, "untested": "insufficient plaintext"}
    freq = Counter(c for w in plain for c in w)
    tasks = []
    for k in range(2):
        st = rng.randrange(0, len(plain) - len(VA))
        key = K.make_key(K.LMS[bid].letters, freq, rng)
        seqs, labels = K.encode(plain[st:st + len(VA)], key, sw, rng)
        tasks.append((f"{bid}:crack{k}", bid, seqs, labels, rng.randrange(1 << 30)))
    for k in range(2):
        tasks.append((f"{bid}:control:generator{k}", bid, K.gibberish_streams(len(VA), rng), None, rng.randrange(1 << 30)))
    for k in range(5):
        tasks.append((f"{bid}:control:pseudo{k}", bid, markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
    tasks.append((f"{bid}:VOYNICH_A", bid, VA, None, rng.randrange(1 << 30)))
    for k in range(5):
        tasks.append((f"{bid}:controlB:pseudo{k}", bid, markov_pseudo(VB, len(VB), rng), None, rng.randrange(1 << 30)))
    tasks.append((f"{bid}:VOYNICH_B", bid, VB, None, rng.randrange(1 << 30)))
    return tasks, meta


def judge(bid, R):
    cr = [R["crack0"], R["crack1"]]
    ctA = {k: v for k, v in R.items() if k.startswith("control:")}
    ctB = {k: v for k, v in R.items() if k.startswith("controlB:")}
    cmaxA = max(v["lexrate"] for v in ctA.values()); cmaxB = max(v["lexrate"] for v in ctB.values())
    cmin = min(c["lexrate"] for c in cr)
    valid = all(c["accuracy"] >= K.ACC_CRACK and c["agreement"] >= K.AGREE_MIN for c in cr) and cmin > cmaxA
    T = (cmin + cmaxA) / 2 if valid else None
    out = {"cracks": [(c["accuracy"], c["lexrate"], c["agreement"]) for c in cr], "validated": valid, "threshold": T,
           "controls_A": {k: v["lexrate"] for k, v in ctA.items()}, "controls_B": {k: v["lexrate"] for k, v in ctB.items()},
           "controls_max_A": cmaxA, "controls_max_B": cmaxB}
    for tgt, cmax in (("A", cmaxA), ("B", cmaxB)):
        v = R[f"VOYNICH_{tgt}"]
        out[f"voynich_{tgt}"] = {"lexrate": v["lexrate"], "agreement": v["agreement"],
                                 "claim": bool(valid and v["agreement"] >= K.AGREE_MIN and v["lexrate"] >= T and v["lexrate"] > cmax + 0.05)}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    t0 = time.time()
    rng = random.Random(SEED)
    VA, _, locked = voynich_a_by_folio()
    VB, dB, tB, _ = voynich_seqs("B")
    _, sw = K.voynich_signs()
    langs = languages()
    log(f"Voynich A words {len(VA)}, B words {len(VB)} ({dB}/{tB} rare units dropped); {len(langs)} languages: {langs}")
    out, allres = {}, []
    for i in range(0, len(langs), BATCH):
        batch = langs[i:i + BATCH]
        K.LMS.clear()
        tasks, metas = [], {}
        for bid in batch:
            tk, meta = build_tasks(bid, VA, VB, sw, rng)
            if not tk:
                out[bid] = meta; log(f"  {bid}: UNTESTED ({meta['untested']}, plaintext words {meta['plain_words']})"); continue
            tasks += tk; metas[bid] = meta
            log(f"  built {bid}: {meta['lm_books']}, plaintext words {meta['plain_words']}, letters {len(meta['letters'])}")
        if a.dry:
            continue
        with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
            res = pool.map(decode_task, tasks)
        for r in res:
            r.pop("decoded", None)
        allres += res
        for bid in [b for b in batch if b in metas]:
            R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(bid + ":")}
            j = judge(bid, R); out[bid] = {**metas[bid], **j}
            log(f"{bid:12s} cracks acc/lex {[(round(x, 3), round(y, 3)) for x, y, _ in j['cracks']]} ctrlA max {j['controls_max_A']:.3f} "
                f"-> {'VALIDATED T=%.3f' % j['threshold'] if j['validated'] else 'NOT VALIDATED'} | A lex {j['voynich_A']['lexrate']:.3f} "
                f"agr {j['voynich_A']['agreement']:.2f} {'CLAIM' if j['voynich_A']['claim'] else 'no claim'} | B lex {j['voynich_B']['lexrate']:.3f} "
                f"agr {j['voynich_B']['agreement']:.2f} ctrlB max {j['controls_max_B']:.3f} {'CLAIM' if j['voynich_B']['claim'] else 'no claim'} "
                f"| {time.time() - t0:.0f}s")
        OUT.write_text(json.dumps({"experiment": "E063", "partial": True, "languages": out}, indent=1, ensure_ascii=False, default=str))
    if a.dry:
        log("dry run complete"); return
    tested = {b: o for b, o in out.items() if "validated" in o}
    claims = [(b, t) for b, o in tested.items() for t in ("A", "B") if o[f"voynich_{t}"]["claim"]]
    nval = sum(o["validated"] for o in tested.values())
    share = nval / len(langs)
    if claims:
        verdict, factor = "CLAIM: " + ", ".join(f"{b}/{t}" for b, t in claims) + " (blind reading + LOCKED_TEST next)", "none yet"
    else:
        fL = 1 - share * 0.0756 * 0.8; fC = 1 - share * 0.05 * 0.8
        verdict, factor = f"NO CLAIM ({nval}/{len(langs)} validated)", f"L x{fL:.3f}, C x{fC:.3f}"
    log(f"VERDICT {verdict} | {factor} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E063", "seed": SEED, "languages": out, "results": allres, "verdict": verdict,
                               "factor": factor, "validated": nval, "n_languages": len(langs), "locked_test_excluded": locked,
                               "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
