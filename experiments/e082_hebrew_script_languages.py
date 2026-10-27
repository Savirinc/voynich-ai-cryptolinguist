"""E082 (Hebrew campaign H5): the E063/E080 validated letter attack with two other languages written in Hebrew letters:
Aramaic (Targum Onkelos) and Judeo-Arabic (Saadia Gaon's Tafsir), on Voynich A and B. See reports/E082_PREREG.md.
Texts: data/external/hebrew_script/{onkelos,rasag}.txt (Sefaria API, one line per verse, Torah order). Model from
Genesis-Leviticus (lines before the first line of Numbers), plaintext from Numbers-Deuteronomy.
Run: caffeinate -ims .venv/bin/python experiments/e082_hebrew_script_languages.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from collections import Counter  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from e049_attack_voynich import voynich_seqs  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402
from e052_shortlist_attack import norm  # noqa: E402
from e063_wide_attack import judge  # noqa: E402

SEED = 82082
OUT = ROOT / "experiments/results/e082.json"
SRC = ROOT / "data/external/hebrew_script"
LANGS = {"aramaic_onkelos": "onkelos.txt", "judeoarabic_saadia": "rasag.txt"}
SPLIT_FRACTION = 0.62     # Genesis-Leviticus are about 62% of Torah verses (1,533 + 1,213 + 859 of 5,845)


def log(*a):
    print(*a, flush=True)


def words_split(fname):
    lines = [l for l in (SRC / fname).read_text(encoding="utf-8").splitlines() if l.strip()]
    cut = int(len(lines) * SPLIT_FRACTION)
    lm = [w for l in lines[:cut] for w in norm(l) if any("א" <= c <= "ת" for c in w)]
    te = [w for l in lines[cut:] for w in norm(l) if any("א" <= c <= "ת" for c in w)]
    return lm, te, len(lines)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    VA, _, locked = voynich_a_by_folio()
    VB, _, _, _ = voynich_seqs("B")
    _, sw = K.voynich_signs()
    K.LMS.clear(); tasks, metas = [], {}
    for name, fn in LANGS.items():
        lmw, tew, nl = words_split(fn)
        K.LMS[name] = K.SpaceLM(lmw, name)
        plain = K.keep_letters(tew, K.LMS[name].letters)
        log(f"{name}: verses {nl}, model words {len(lmw)}, plaintext words {len(plain)}, letters {''.join(K.LMS[name].letters)}")
        assert len(plain) >= 2 * len(VA), name
        freq = Counter(c for w in plain for c in w)
        for k in range(2):
            st = rng.randrange(0, len(plain) - len(VA)); key = K.make_key(K.LMS[name].letters, freq, rng)
            s, lab = K.encode(plain[st:st + len(VA)], key, sw, rng)
            tasks.append((f"{name}:crack{k}", name, s, lab, rng.randrange(1 << 30)))
        for k in range(2):
            tasks.append((f"{name}:control:generator{k}", name, K.gibberish_streams(len(VA), rng), None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{name}:control:pseudo{k}", name, markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_A", name, VA, None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{name}:controlB:pseudo{k}", name, markov_pseudo(VB, len(VB), rng), None, rng.randrange(1 << 30)))
        tasks.append((f"{name}:VOYNICH_B", name, VB, None, rng.randrange(1 << 30)))
        metas[name] = {"model_words": len(lmw), "plain_words": len(plain), "letters": K.LMS[name].letters}
    with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    dec = {r["name"]: r.pop("decoded", None) for r in res}
    out = {}
    for name in LANGS:
        R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(name + ":")}
        j = judge(name, R); out[name] = {**metas[name], **j}
        log(f"{name:20s} cracks acc/lex {[(round(x, 3), round(y, 3)) for x, y, _ in j['cracks']]} ctrlA max {j['controls_max_A']:.3f} "
            f"-> {'VALIDATED T=%.3f' % j['threshold'] if j['validated'] else 'NOT VALIDATED'} | A lex {j['voynich_A']['lexrate']:.3f} "
            f"agr {j['voynich_A']['agreement']:.2f} {'CLAIM' if j['voynich_A']['claim'] else 'no claim'} | B lex {j['voynich_B']['lexrate']:.3f} "
            f"agr {j['voynich_B']['agreement']:.2f} ctrlB max {j['controls_max_B']:.3f} {'CLAIM' if j['voynich_B']['claim'] else 'no claim'}")
        for t in "AB":
            log(f"  decoded {t}: {' '.join(dec[f'{name}:VOYNICH_{t}'][:30])}")
    claims = [(n, t) for n, o in out.items() for t in "AB" if o[f"voynich_{t}"]["claim"]]
    allval = all(o["validated"] for o in out.values())
    verdict = ("CLAIM: " + ", ".join(f"{n}/{t}" for n, t in claims)) if claims else ("NO CLAIM, validated" if allval else "NO CLAIM, partly validated")
    OUT.write_text(json.dumps({"experiment": "E082", "seed": SEED, "languages": out, "verdict": verdict, "locked_test_excluded": locked,
                               "results": res, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False, default=str))
    log(f"VERDICT {verdict} | {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
