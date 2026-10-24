"""E052: the E047 attack extended to the rest of the shortlist plus Romani, each language validated on known answers
first, then run on Voynich Currier A. See reports/E052_PREREG.md.

Per language (LM books disjoint from plaintext books; letters: lowercase, accents/diacritics removed, commonest 23
kept, as E047):
  VALIDATION  2 VOY23 ciphers of real text (fresh keys, E047 encoder) attacked with the language's LM -> cracks need
              accuracy >= 0.80; 7 controls with the same LM: 2 copy-generator samples + 5 pseudo-Voynich-A (E050).
              T_l = midpoint(min crack lexrate, max control lexrate). VALIDATED iff both cracked and min crack > max
              control and both cracks have agreement >= 0.95.
  VOYNICH A   attacked with the same LM (same seed scheme). CLAIM iff VALIDATED, agreement >= 0.95,
              lexrate >= T_l and lexrate > (max control lexrate) + 0.05.
Run: caffeinate -ims .venv/bin/python experiments/e052_shortlist_attack.py
"""
from __future__ import annotations

import glob, json, random, re, sys, unicodedata
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402

SEED = 52052
OUT = ROOT / "experiments/results/e052.json"
BIB = ROOT / "data/external/bibles"
LANGS = {"cs": "ces1613", "sh": "srp1865", "sk": "slk", "uk": "ukr1871", "ro": "ron1924", "it": "ita1885", "rom": "rmc"}
OT_LM = ["GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "1SA", "2SA", "1KI", "2KI"]
OT_TEST = ["EZK", "PSA", "PRO", "JOB", "1CH", "2CH"]
NT_LM = ["MAT", "MRK", "LUK", "JHN", "ACT"]
NT_TEST = ["ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS",
           "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV"]


def norm(text):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[^\W\d_]+", unicodedata.normalize("NFC", t))


def book_words(bid, books):
    fs = sorted(f for f in glob.glob(str(BIB / bid / "txt" / "*_read.txt")) if any(f"_{b}_" in f for b in books))
    out = []
    for f in fs:
        out += norm("\n".join(Path(f).read_text(encoding="utf-8-sig").splitlines()[1:]))
    return out


def main():
    rng = random.Random(SEED)
    VA, _, locked = voynich_a_by_folio()
    _, sw = K.voynich_signs()
    tasks, meta = [], {}
    for code, bid in LANGS.items():
        has_ot = bool(glob.glob(str(BIB / bid / "txt" / "*_GEN_*")))
        lmb, tb = (OT_LM, OT_TEST) if has_ot else (NT_LM, NT_TEST)
        K.LMS[code] = K.SpaceLM(book_words(bid, lmb), code)
        plain = K.keep_letters(book_words(bid, tb), K.LMS[code].letters)
        freq = Counter(c for w in plain for c in w)
        meta[code] = {"bible": bid, "lm_books": "OT" if has_ot else "NT gospels+Acts", "letters": K.LMS[code].letters,
                      "plain_words": len(plain)}
        for k in range(2):
            st = rng.randrange(0, len(plain) - len(VA))
            key = K.make_key(K.LMS[code].letters, freq, rng)
            seqs, labels = K.encode(plain[st:st + len(VA)], key, sw, rng)
            tasks.append((f"{code}:crack{k}", code, seqs, labels, rng.randrange(1 << 30)))
        for k in range(2):
            tasks.append((f"{code}:control:generator{k}", code, K.gibberish_streams(len(VA), rng), None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{code}:control:pseudo{k}", code, markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
        tasks.append((f"{code}:VOYNICH_A", code, VA, None, rng.randrange(1 << 30)))
    print("languages:", {c: (m["bible"], m["lm_books"], m["plain_words"]) for c, m in meta.items()}, flush=True)
    with Pool(3, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    for r in res:
        r.pop("decoded", None)
    out = {}
    for code in LANGS:
        R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(code + ":")}
        cr = [R["crack0"], R["crack1"]]; ct = [v for k, v in R.items() if k.startswith("control")]
        cmax = max(c["lexrate"] for c in ct); cmin = min(c["lexrate"] for c in cr)
        valid = all(c["accuracy"] >= K.ACC_CRACK and c["agreement"] >= K.AGREE_MIN for c in cr) and cmin > cmax
        T = (cmin + cmax) / 2 if valid else None
        v = R["VOYNICH_A"]
        claim = bool(valid and v["agreement"] >= K.AGREE_MIN and v["lexrate"] >= T and v["lexrate"] > cmax + 0.05)
        out[code] = {**meta[code], "cracks": [(c["accuracy"], c["lexrate"], c["agreement"]) for c in cr],
                     "controls_max": cmax, "controls": {k: v_["lexrate"] for k, v_ in R.items() if k.startswith("control")},
                     "validated": valid, "threshold": T, "voynich_lexrate": v["lexrate"], "voynich_agreement": v["agreement"],
                     "claim": claim}
        print(f"{code:4s} {meta[code]['bible']:8s} cracks acc/lex {[(round(a, 3), round(l, 3)) for a, l, _ in out[code]['cracks']]} "
              f"controls max {cmax:.3f} -> {'VALIDATED T=%.3f' % T if valid else 'NOT VALIDATED'} | Voynich A lexrate {v['lexrate']:.3f} "
              f"agreement {v['agreement']:.2f} -> {'CLAIM' if claim else 'no claim'}", flush=True)
    claims = [c for c, o in out.items() if o["claim"]]
    verdict = ("CLAIM: " + ", ".join(claims) + " (blind reading + LOCKED_TEST confirmation next)") if claims else "NO CLAIM"
    print("VERDICT:", verdict)
    OUT.write_text(json.dumps({"experiment": "E052", "languages": out, "results": res, "verdict": verdict,
                               "locked_test_excluded": locked}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
