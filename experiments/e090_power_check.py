"""E090 (approach check 1): how often does the validated letter attack find a real text that is NOT the same kind of text
as its language model? See reports/E090_PREREG.md. Voynich is NOT decoded (only its sign inventory, sign frequencies and
the pseudo-Voynich controls built from Voynich A, exactly as E063).

Per language (LM = the Bible model used on Voynich in E049/E063): 10 VOY23 ciphers of held-out Bible books (in-genre),
10 VOY23 ciphers of each out-of-genre text, 7 controls (2 generator, 5 pseudo-Voynich-A). Each cipher is Voynich-A length.
Validation and threshold exactly as E063 from in-genre keys 0 and 1: T = (min crack lexrate + max control lexrate) / 2.
FOUND iff agreement >= 0.95, lexrate >= T and lexrate > max control + 0.05 (the E063 Voynich-A CLAIM rule).
CRACKED iff letter accuracy >= 0.80 (the decoder recovered the key, whether or not the rule would have claimed it).
Out-of-genre power p_out = mean over languages of (share FOUND over that language's out-of-genre ciphers).
Run: caffeinate -ims .venv/bin/python experiments/e090_power_check.py [--dry] [--workers 3]
"""
from __future__ import annotations

import argparse, glob, hashlib, json, random, re, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
import e052_shortlist_attack as S52  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402

SEED = 90090
OUT = ROOT / "experiments/results/e090.json"
EXT = ROOT / "data/external"
N_KEYS = 10
LIBJUNK = re.compile(r"latin library|classics page|miscellany", re.I)
# ledger entries built with the absence rule (m = 0.2) from VOY23 letter-attack searches: (entry, L factor, C factor)
ABSENCE_ENTRIES = [("E049-E050", 0.902, 0.92), ("E052", 0.885, None), ("E053", 0.958, None), ("E063", 0.94, 0.96)]


def log(*a):
    print(*a, flush=True)


def latin_technical():
    fs = sorted(glob.glob(str(EXT / "latin_library_e043/apicius/*.txt"))) + [str(EXT / "latin_library_e043/cato/cato.agri.txt")] \
        + sorted(glob.glob(str(EXT / "latin_library_e043/varro.rr*.txt"))) + sorted(glob.glob(str(EXT / "latin_library_e043/columella/*.txt")))
    txt = "\n".join(ln for f in fs for ln in Path(f).read_text(encoding="utf-8", errors="ignore").splitlines() if not LIBJUNK.search(ln))
    return K.norm(txt, "la"), fs


def culpeper():
    f = EXT / "pg_herbal/pg49513.txt"
    lines = f.read_text(encoding="utf-8-sig").splitlines()
    a = next(i for i, l in enumerate(lines) if "*** START OF" in l); b = next(i for i, l in enumerate(lines) if "*** END OF" in l)
    return S52.norm("\n".join(lines[a + 1:b])), [str(f)]


def talmud():
    f = EXT / "hebrew_script/talmud.txt"
    return K.norm(f.read_text(encoding="utf-8"), "he"), [str(f)]


def specs():
    """language -> (LM words, in-genre plaintext words, {out-of-genre name: (words, files)}, LM norm tag)"""
    return {
        "latin": (K.book_words("la", K.LM_BOOKS), K.book_words("la", K.TEST_BOOKS), {"latin_recipes_agriculture": latin_technical()}, "la"),
        "english": (S52.book_words("eng-kjv", S52.OT_LM), S52.book_words("eng-kjv", S52.OT_TEST), {"culpeper_herbal_1652": culpeper()}, "en"),
        "hebrew": (K.book_words("he", K.LM_BOOKS), K.book_words("he", K.TEST_BOOKS), {"talmud_mishnah_gemara": talmud()}, "he"),
    }


def ciphers(tag, plain, n, sw, rng, letters):
    freq = Counter(c for w in plain for c in w)
    out = []
    for k in range(n):
        st = rng.randrange(0, len(plain) - NV)
        key = K.make_key(letters, freq, rng)
        seqs, labels = K.encode(plain[st:st + NV], key, sw, rng)
        out.append((f"{tag}{k}", seqs, labels))
    return out


NV = None


def main():
    global NV
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    VA, _, locked = voynich_a_by_folio(); NV = len(VA)
    _, sw = K.voynich_signs()
    tasks, meta = [], {}
    for lang, (lmw, ing, outs, tag) in specs().items():
        K.LMS[lang] = K.SpaceLM(lmw, tag)
        letters = K.LMS[lang].letters
        m = {"letters": "".join(letters), "lm_words": len(lmw), "texts": {}}
        texts = {"in_genre": (K.keep_letters(ing, letters), [])}
        for name, (w, fs) in outs.items():
            kept = K.keep_letters(w, letters)
            texts[name] = (kept, fs)
        for name, (kept, fs) in texts.items():
            lost = 1 - sum(map(len, kept)) / max(1, sum(len(x) for x in (ing if name == "in_genre" else outs[name][0])))
            vocab_hit = sum(x in K.LMS[lang].vocab for x in kept if len(x) >= 3) / max(1, sum(len(x) >= 3 for x in kept))
            m["texts"][name] = {"words": len(kept), "letters_dropped": round(lost, 4), "plain_vocab_rate": round(vocab_hit, 4),
                                "files": {Path(f).name: hashlib.sha256(Path(f).read_bytes()).hexdigest()[:16] for f in fs}}
            for nm, seqs, labels in ciphers(f"{name}:", kept, N_KEYS, sw, rng, letters):
                tasks.append((f"{lang}:{nm}", lang, seqs, labels, rng.randrange(1 << 30)))
        for k in range(2):
            tasks.append((f"{lang}:control:generator{k}", lang, K.gibberish_streams(NV, rng), None, rng.randrange(1 << 30)))
        for k in range(5):
            tasks.append((f"{lang}:control:pseudo{k}", lang, markov_pseudo(VA, NV, rng), None, rng.randrange(1 << 30)))
        meta[lang] = m
        log(lang, json.dumps(m, ensure_ascii=False))
    log(f"Voynich A length {NV}; tasks {len(tasks)}")
    if a.dry:
        log("dry run complete"); return
    with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    samples = {}
    for r in res:
        dec = r.pop("decoded")
        if r["name"].endswith("0") and "control" not in r["name"]:
            samples[r["name"]] = " ".join(dec[:25])
    out, powers = {}, {}
    for lang in meta:
        R = {r["name"].split(":", 1)[1]: r for r in res if r["name"].startswith(lang + ":")}
        ctl = [v["lexrate"] for k, v in R.items() if k.startswith("control:")]
        cmax = max(ctl)
        val = [R["in_genre:0"], R["in_genre:1"]]
        cmin = min(v["lexrate"] for v in val)
        valid = all(v["accuracy"] >= K.ACC_CRACK and v["agreement"] >= K.AGREE_MIN for v in val) and cmin > cmax
        T = (cmin + cmax) / 2 if valid else None
        o = {"validated": valid, "threshold": T, "controls": ctl, "controls_max": cmax, "texts": {}}
        for name in meta[lang]["texts"]:
            rows = [R[f"{name}:{k}"] for k in range(N_KEYS)]
            found = [bool(valid and r["agreement"] >= K.AGREE_MIN and r["lexrate"] >= T and r["lexrate"] > cmax + 0.05) for r in rows]
            cracked = [r["accuracy"] >= K.ACC_CRACK for r in rows]
            o["texts"][name] = {"found": sum(found), "cracked": sum(cracked), "n": N_KEYS,
                                "rows": [(round(r["accuracy"], 3), round(r["lexrate"], 3), round(r["agreement"], 3)) for r in rows]}
            log(f"{lang:8s} {name:28s} FOUND {sum(found)}/{N_KEYS} CRACKED {sum(cracked)}/{N_KEYS} "
                f"lexrate {[round(r['lexrate'], 2) for r in rows]} T {T if T is None else round(T, 3)} ctrl max {cmax:.3f}")
        outg = [t for n, t in o["texts"].items() if n != "in_genre"]
        powers[lang] = sum(t["found"] for t in outg) / sum(t["n"] for t in outg) if valid else None
        out[lang] = o
    vp = [p for p in powers.values() if p is not None]
    p_out = sum(vp) / len(vp) if vp else None
    if p_out is None:
        verdict, corr = "VOID (no language validated)", None
    else:
        pe = min(p_out, 0.8)
        corr = []
        for e, fL, fC in ABSENCE_ENTRIES:
            row = {"entry": e, "L_old": fL, "L_new": round(1 - (1 - fL) / 0.8 * pe, 4)}
            if fC is not None:
                row.update({"C_old": fC, "C_new": round(1 - (1 - fC) / 0.8 * pe, 4)})
            corr.append(row)
        verdict = ("ABSENCE FACTORS STAND" if p_out >= 0.8 else "ABSENCE FACTORS TOO STRONG") + f" (p_out {p_out:.3f})"
    log(f"VERDICT {verdict} | powers {powers} | corrections {corr} | {time.time() - t0:.0f}s")
    OUT.write_text(json.dumps({"experiment": "E090", "seed": SEED, "voynich_a_len": NV, "meta": meta, "languages": out,
                               "powers": powers, "p_out": p_out, "verdict": verdict, "corrections": corr, "samples": samples,
                               "locked_test_excluded": locked, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
