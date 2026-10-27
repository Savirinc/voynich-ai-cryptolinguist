"""E080 (Hebrew campaign H1/H2): the E047/E063 validated letter attack with Hebrew on Voynich B (never attacked with
Hebrew) and A, for Hebrew written forwards (H1) and with every word's letters reversed (H2). See reports/E080_PREREG.md.
Machinery and rules exactly E063 (VOY23 cracks of the language's own text, 2 generator + 5 pseudo-A controls,
5 pseudo-B controls; 32 restarts x 30,000 iterations; 4-gram KN LM with spaces).
Run: caffeinate -ims .venv/bin/python experiments/e080_hebrew_letters_b.py [--workers 3]
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
from e049_attack_voynich import voynich_seqs  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402
from e052_shortlist_attack import OT_LM, OT_TEST, book_words  # noqa: E402
from e063_wide_attack import judge  # noqa: E402

SEED = 80080
OUT = ROOT / "experiments/results/e080.json"
VARIANTS = {"hebrew_forward": lambda w: w, "hebrew_reversed": lambda w: w[::-1]}


def log(*a):
    print(*a, flush=True)


def tasks_for(name, fn, VA, VB, sw, rng):
    lm_words = [fn(w) for w in book_words("hboWLC", OT_LM)]
    K.LMS[name] = K.SpaceLM(lm_words, name)
    plain = K.keep_letters([fn(w) for w in book_words("hboWLC", OT_TEST)], K.LMS[name].letters)
    assert len(plain) >= 2 * len(VA)
    freq = Counter(c for w in plain for c in w)
    T = []
    for k in range(2):
        st = rng.randrange(0, len(plain) - len(VA))
        key = K.make_key(K.LMS[name].letters, freq, rng)
        seqs, labels = K.encode(plain[st:st + len(VA)], key, sw, rng)
        T.append((f"{name}:crack{k}", name, seqs, labels, rng.randrange(1 << 30)))
    for k in range(2):
        T.append((f"{name}:control:generator{k}", name, K.gibberish_streams(len(VA), rng), None, rng.randrange(1 << 30)))
    for k in range(5):
        T.append((f"{name}:control:pseudo{k}", name, markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
    T.append((f"{name}:VOYNICH_A", name, VA, None, rng.randrange(1 << 30)))
    for k in range(5):
        T.append((f"{name}:controlB:pseudo{k}", name, markov_pseudo(VB, len(VB), rng), None, rng.randrange(1 << 30)))
    T.append((f"{name}:VOYNICH_B", name, VB, None, rng.randrange(1 << 30)))
    return T, {"letters": K.LMS[name].letters, "plain_words": len(plain)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    VA, _, locked = voynich_a_by_folio()
    VB, dB, tB, _ = voynich_seqs("B")
    _, sw = K.voynich_signs()
    log(f"Voynich A words {len(VA)}, B words {len(VB)}")
    K.LMS.clear(); tasks, metas = [], {}
    for name, fn in VARIANTS.items():
        t, m = tasks_for(name, fn, VA, VB, sw, rng); tasks += t; metas[name] = m
    with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    decoded = {r["name"]: r.pop("decoded", None) for r in res}
    out = {}
    for name in VARIANTS:
        R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(name + ":")}
        j = judge(name, R); out[name] = {**metas[name], **j}
        log(f"{name:16s} cracks acc/lex {[(round(x, 3), round(y, 3)) for x, y, _ in j['cracks']]} ctrlA max {j['controls_max_A']:.3f} "
            f"-> {'VALIDATED T=%.3f' % j['threshold'] if j['validated'] else 'NOT VALIDATED'} | A lex {j['voynich_A']['lexrate']:.3f} "
            f"agr {j['voynich_A']['agreement']:.2f} {'CLAIM' if j['voynich_A']['claim'] else 'no claim'} | B lex {j['voynich_B']['lexrate']:.3f} "
            f"agr {j['voynich_B']['agreement']:.2f} ctrlB max {j['controls_max_B']:.3f} {'CLAIM' if j['voynich_B']['claim'] else 'no claim'}")
    claims = [(n, t) for n, o in out.items() for t in ("A", "B") if o[f"voynich_{t}"]["claim"]]
    allval = all(o["validated"] for o in out.values())
    verdict = ("CLAIM: " + ", ".join(f"{n}/{t}" for n, t in claims)) if claims else ("NO CLAIM, validated" if allval else "NO CLAIM, partly validated")
    sample = {k: (v[:60] if isinstance(v, list) else v) for k, v in decoded.items() if "VOYNICH" in k}
    OUT.write_text(json.dumps({"experiment": "E080", "seed": SEED, "variants": out, "verdict": verdict, "locked_test_excluded": locked,
                               "decoded_sample": sample, "results": res, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))
    log(f"VERDICT {verdict} | {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
