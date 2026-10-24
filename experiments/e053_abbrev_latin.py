"""E053: the validated attack for ABBREVIATED Latin (L-abbrev form), technical and sacred. See reports/E053_PREREG.md.
Texts (Gaskell & Bowern 2022 meaningful set, @ d076a7d0; not redistributed): 'Historical - Latin (Abbreviated) -
Technical - Pliny's Natural History' and '... - Literary - NT (Vulgate)'. Each: lowercase, whitespace tokens, the 23
commonest characters kept (abbreviation signs such as '9' included if common); first 70% of tokens -> LM, last 30% ->
plaintext for known-answer ciphers. Per LM exactly as E052: 2 VOY23 ciphers (validation), 7 controls (2 generator,
5 pseudo-Voynich-A), Voynich A; VALIDATED / CLAIM rules as E052.
Run: caffeinate -ims .venv/bin/python experiments/e053_abbrev_latin.py GASKELL_MEANINGFUL_TEXTS_DIR
"""
from __future__ import annotations

import hashlib, json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402

SEED = 53053
OUT = ROOT / "experiments/results/e053.json"
FILES = {"abbr_tech": "Historical - Latin (Abbreviated) - Technical - Pliny's Natural History.txt",
         "abbr_sacred": "Historical - Latin (Abbreviated) - Literary - NT (Vulgate).txt"}


def main():
    d = Path(sys.argv[1]); rng = random.Random(SEED)
    VA, _, locked = voynich_a_by_folio(); _, sw = K.voynich_signs()
    tasks, meta = [], {}
    for code, fn in FILES.items():
        raw = (d / fn).read_bytes(); toks = raw.decode("utf-8", errors="ignore").lower().split()
        cut = int(len(toks) * 0.7)
        K.LMS[code] = K.SpaceLM(toks[:cut], code)
        plain = K.keep_letters(toks[cut:], K.LMS[code].letters)
        freq = Counter(c for w in plain for c in w)
        meta[code] = {"file": fn, "sha256": hashlib.sha256(raw).hexdigest(), "tokens": len(toks),
                      "letters": K.LMS[code].letters, "mean_word_len": sum(map(len, plain)) / len(plain)}
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
    print("LMs:", {c: (m["tokens"], round(m["mean_word_len"], 2), "".join(m["letters"])) for c, m in meta.items()}, flush=True)
    with Pool(3, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    samples = {r["name"]: " ".join(r["decoded"][:20]) for r in res if "VOYNICH" in r["name"]}
    for r in res:
        r.pop("decoded", None)
    out = {}
    for code in FILES:
        R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(code + ":")}
        cr = [R["crack0"], R["crack1"]]; ct = [v for k, v in R.items() if k.startswith("control")]
        cmax = max(c["lexrate"] for c in ct); cmin = min(c["lexrate"] for c in cr)
        valid = all(c["accuracy"] >= K.ACC_CRACK and c["agreement"] >= K.AGREE_MIN for c in cr) and cmin > cmax
        T = (cmin + cmax) / 2 if valid else None
        v = R["VOYNICH_A"]
        claim = bool(valid and v["agreement"] >= K.AGREE_MIN and v["lexrate"] >= T and v["lexrate"] > cmax + 0.05)
        out[code] = {**meta[code], "cracks": [(c["accuracy"], c["lexrate"], c["agreement"]) for c in cr], "controls_max": cmax,
                     "validated": valid, "threshold": T, "voynich_lexrate": v["lexrate"], "voynich_agreement": v["agreement"], "claim": claim}
        print(f"{code:11s} cracks acc/lex {[(round(a, 3), round(l, 3)) for a, l, _ in out[code]['cracks']]} controls max {cmax:.3f} -> "
              f"{'VALIDATED T=%.3f' % T if valid else 'NOT VALIDATED'} | Voynich A lexrate {v['lexrate']:.3f} agreement {v['agreement']:.2f} -> "
              f"{'CLAIM' if claim else 'no claim'}", flush=True)
    claims = [c for c, o in out.items() if o["claim"]]
    verdict = ("CLAIM: " + ", ".join(claims)) if claims else "NO CLAIM"
    print("VERDICT:", verdict)
    OUT.write_text(json.dumps({"experiment": "E053", "lms": out, "results": res, "voynich_samples": samples,
                               "verdict": verdict, "locked_test_excluded": locked}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
