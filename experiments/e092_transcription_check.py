"""E092 (approach check 3): do key Voynich facts survive another transcription or another way of cutting glyphs?
See reports/E092_PREREG.md.

Variants (DEV only: prose, LOCKED_TEST leaves excluded by the ZL leaf list):
  ZL      ZL 3b (the project's transcription; baseline, must reproduce the published conclusions)
  ZL_J    ZL with uncertain spaces (',') removed: the two sides are joined into one word
  ZL_S3   ZL with every E024 S3 unit (ch, sh, cth, iin, ee, qo, dy ...) written as ONE symbol
  IT      Takahashi (voynich.nu IT2a-n.txt; own readings and own spaces; EVA)
  GC      Glen Claston (voynich.nu GC2a-n.txt; v101 alphabet = a different glyph cut; own readings and spaces)
Facts, each re-measured with the original experiment's own functions and judge, only Voynich swapped:
  F1 E086 spaces: MECHANICAL iff PRED > max language PRED (stored E086 references)
  F2 E086 lines:  INDEPENDENT iff continuity z < min language z / 2 (stored E086 references)
  F3 E067 verdict (vocabulary at 150 tokens; references recomputed with E067's seed; E067 seed rule if borderline)
  F4 E068 verdict (small-scale battery; references recomputed with E068's seed; E068 seed rule if borderline)
  F5 E066 verdict (family- vs word-level repeats; stored generator z, E066 judge and seed rule)
Run: caffeinate -ims .venv/bin/python -I experiments/e092_transcription_check.py [--smoke]
"""
from __future__ import annotations

import argparse, glob, hashlib, json, random, re, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e024_atoms as A24  # noqa: E402
import e066_word_individuality_v3_v2 as E66  # noqa: E402
import e067_gibberish_vocabulary as E67  # noqa: E402
import e068_gibberish_battery as E68  # noqa: E402
import e086_spaces_and_lines as E86  # noqa: E402
from e058_word_repeat_individuality_v2 import stats  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402

OUT = ROOT / "experiments/results/e092.json"
TR = ROOT / "data/external/transcriptions_e092"
FILES = {"IT": ("IT2a-n.txt", "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5"),
         "GC": ("GC2a-n.txt", "b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f")}
BAD = re.compile(r"[?@\[\]{}<>;]")


def log(*a):
    print(*a, flush=True)


def gc_clean(t):
    return bool(t.eva) and not t.uncertain_glyph and not t.rare_glyph and not t.alternative and not BAD.search(t.eva)


def lines_from(toks, locked, clean, join_uncertain=False):
    """ordered DEV prose lines (lists of words, None for unclean) and their pages"""
    L = defaultdict(list)
    for t in toks:
        if t.mode != "prose" or t.leaf in locked:
            continue
        k = (t.folio, t.line_no); w = t.eva if clean(t) else None
        if join_uncertain and t.space_before == "," and L[k]:
            prev = L[k][-1]
            L[k][-1] = (prev + w) if (prev is not None and w is not None) else None
        else:
            L[k].append(w)
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    pages = defaultdict(list)
    for k in order:
        pages[k[0]].append(L[k])
    folios = sorted(pages, key=lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f))
    return [L[k] for k in order], [pages[f] for f in folios]


def s3_map(lines, pages):
    sym = {}
    def m(w):
        if w is None:
            return None
        return "".join(sym.setdefault(u, chr(0xE000 + len(sym))) for u in A24.segment(w, A24.SEGS["S3"]))
    return [[m(w) for w in l] for l in lines], [[[m(w) for w in l] for l in p] for p in pages]


def variants():
    _, zl = parse(); locked = set(locked_test_leaves(zl))
    ev = lambda t: t.is_clean
    V = {"ZL": (*lines_from(zl, locked, ev), True), "ZL_J": (*lines_from(zl, locked, ev, join_uncertain=True), True)}
    V["ZL_S3"] = (*s3_map(*lines_from(zl, locked, ev)), False)
    meta = {}
    for name, (fn, sha) in FILES.items():
        raw = (TR / fn).read_bytes(); h = hashlib.sha256(raw).hexdigest()
        assert h == sha, (fn, h)
        _, toks = parse(raw.decode("ascii").splitlines())
        V[name] = (*lines_from(toks, locked, ev if name == "IT" else gc_clean), name == "IT")
    for n, (lines, pages, _) in V.items():
        ws = [w for l in lines for w in l if w]; c = Counter(ws)
        meta[n] = {"lines": len(lines), "pages": len(pages), "tokens": len(ws), "unclean": sum(w is None for l in lines for w in l),
                   "types": len(c), "hapax_share_of_types": round(sum(v == 1 for v in c.values()) / len(c), 4),
                   "symbols": len({ch for w in ws for ch in w}), "mean_word_len": round(float(np.mean([len(w) for w in ws])), 3)}
    return V, meta, sorted(locked)


def f12(lines, pages, ref):
    p = E86.pred(lines)["PRED"]
    z = E86.continuity(pages, random.Random(E86.SEED))["z"]
    return {"PRED": p, "F1": "MECHANICAL" if p > max(ref["languages_PRED"]) else "NOT MECHANICAL",
            "cont_z": z, "F2": "INDEPENDENT" if z < min(ref["languages_z"]) / 2 else "NOT INDEPENDENT"}


def f3(tokens, refs, GIB):
    def run(seed):
        VOY0, LANG, *_ = refs(seed)
        VOY = E67.windows(tokens, E67.N_VOY, random.Random(seed))
        return E67.judge(VOY, LANG, GIB)
    J = run(E67.SEED); verdict = J["verdict"]
    if J["borderline"]:
        votes = [run(E67.SEED + s)["verdict"] for s in range(1, 11)]; top = max(set(votes), key=votes.count)
        verdict = top if votes.count(top) >= 8 else "INCONCLUSIVE (seed rule undecided)"
    return {"T": J["voy_mean"]["T"], "H": J["voy_mean"]["H"], "d_lang_T": J["d_lang"]["T"], "d_gib_T": J["d_gib"]["T"], "F3": verdict}


def f4(tokens, refs, GIB):
    def run(seed):
        _, LANG, GEN, _ = refs(seed)
        VOY = E68.windows(tokens, E68.N_VOY, random.Random(seed))
        return E68.judge(VOY, LANG, GIB, GEN, seed)
    J = run(E68.SEED); verdict = J["verdict"]
    if J["borderline"] and len(J["diagnostic"]) >= 3:
        votes = [run(E68.SEED + s)["verdict"] for s in range(1, 11)]; top = max(set(votes), key=votes.count)
        verdict = top if votes.count(top) >= 8 else "TWO-WAY STREET (seed rule undecided)"
    return {"rows": {k: {x: J["rows"][k][x] for x in ("voynich", "languages", "gibberish", "diagnostic", "voynich_like")} for k in E68.FEATS},
            "F4": verdict}


def f5(lines, eva, e66):
    vl = [[w for w in l if w] for l in lines if any(l)]
    v = stats(vl, eva, random.Random(E66.SEED))
    gz20 = [e66["results"]["generator"][f"gen{k}"]["z"] for k in range(20)]; gz10 = gz20[:10]
    def judge(gz):
        if v["z"] > max(gz) and v["p"] < 0.01:
            return "WORD-SPECIFIC (vocabulary-like)"
        if v["z"] <= float(np.median(gz)):
            return "FAMILY-LEVEL (generator-like)"
        return "INCONCLUSIVE"
    verdict = judge(gz10)
    if abs(v["z"] - max(gz10)) < 0.5 or abs(v["z"] - float(np.median(gz10))) < 0.5:
        r2 = random.Random(E66.SEED + 1); votes = [judge(r2.sample(gz20, 10)) for _ in range(10)]
        top = max(set(votes), key=votes.count); verdict = top if votes.count(top) >= 8 else "INCONCLUSIVE (seed rule undecided)"
    return {"fam_z": v["z"], "kept_words": v["kept_words"], "F5": verdict}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    V, meta, locked = variants()
    for n, m in meta.items():
        log(n, m)
    ref86 = json.loads((ROOT / "experiments/results/e086.json").read_text())
    e66 = json.loads((ROOT / "experiments/results/e066.json").read_text())
    names = ["ZL", "GC"] if a.smoke else list(V)
    c67, c68 = {}, {}
    refs67 = lambda s: c67.setdefault(s, E67.references(s))
    refs68 = lambda s: c68.setdefault(s, E68.references(s))
    if a.smoke:
        E67.N_LANG = E68.N_LANG = 2; E68.N_BOOT = 20
    gib67 = [E67.measure(t[:E67.W]) for t in (E67.clean_tokens(f) for f in sorted(glob.glob(str(E67.GB / "gib/*.txt")))) if len(t) >= E67.W]
    rng68 = random.Random(E68.SEED)
    gib68 = [E68.window_stats(t[:E68.W], rng68) for t in (E67.clean_tokens(f) for f in sorted(glob.glob(str(E67.GB / "gib/*.txt")))) if len(t) >= E68.W]
    R = {}
    for n in names:
        lines, pages, eva = V[n]
        tokens = [w for l in lines for w in l if w]
        r = {**f12(lines, pages, ref86)}
        r.update(f3(tokens, refs67, gib67)); r["F4_detail"] = f4(tokens, refs68, gib68); r["F4"] = r["F4_detail"]["F4"]
        r.update(f5(lines, eva, e66))
        R[n] = r
        log(f"{n:6s} PRED {r['PRED']:.3f} {r['F1']} | z {r['cont_z']:+.2f} {r['F2']} | T {r['T']:.1f} H {r['H']:.3f} {r['F3']} | "
            f"{r['F4']} | E066 z {r['fam_z']:+.2f} {r['F5']} | {time.time() - t0:.0f}s")
        for k, x in r["F4_detail"]["rows"].items():
            log(f"         {k:5s} v {x['voynich']:.3f} lang {x['languages']:.3f} gib {x['gibberish']:.3f} diag {x['diagnostic']} like {x['voynich_like']}")
    # verdicts
    summary = {}
    if "ZL" in R:
        for F in ("F1", "F2", "F3", "F4", "F5"):
            base = R["ZL"][F]; others = {n: R[n][F] for n in R if n != "ZL"}
            fails = [n for n, v in others.items() if v != base]
            summary[F] = {"baseline": base, "variants": others, "fails": fails,
                          "status": "SURVIVES" if not fails else ("FRAGILE" if len(fails) == 1 else "DEPENDS ON TRANSCRIPTION")}
            log(f"{F}: baseline {base} | {summary[F]['status']} {fails}")
    OUT.with_name("e092_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(
        {"experiment": "E092", "meta": meta, "results": R, "summary": summary, "locked_test_excluded": locked,
         "files": FILES, "runtime_s": time.time() - t0}, indent=1, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
