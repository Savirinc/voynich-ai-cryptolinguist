"""E098 (Arham): can any of five untested period cipher classes make the Voynich's fingerprint? See reports/E098_PREREG.md.

Plaintexts: Latin, Italian, German, Occitan, Hebrew as period sound words (E097 corpora and sound rules, LM + held parts
joined; read cyclically from a seeded offset). Output signs: the 23 VOY23 units (EVA strings), so cipher words are EVA.
Bases:
  S  many-to-one substitution sound -> unit, frequency-rank matched to the target's units (ranks jittered in blocks of 3
     by seed; sounds beyond rank 23 -> a unit drawn by target frequency)
  V  Naibbe verbose cipher (published tables, glyph strings permuted among letters by seed, as E062); sounds -> letters
Classes and settings (declared now; no others):
  K1 nomenclator, base S: the plaintext's N commonest words -> the target's N commonest types by rank (jittered in
     blocks of 3); N in {30, 50, 80, 120, 180, 260, 380, 550, 800}
  K2 letters rearranged inside each word, base S: reverse | sort by the units' mean relative position in the target's
     words | a seeded fixed position permutation per word length
  K3 null words, bases S and V: before each token, with probability r, a null word drawn from the target's 20
     commonest types by frequency; r in {0.10, 0.15, ..., 0.50}
  K4 rotating tables, bases S and V: a new table every 1, 2, 3, 4, 6, 8 or 12 lines | every page. S: the rank-matched table
     cyclically shifted over the 23 units by a seeded block offset (Alberti-style); V: a fresh permuted Naibbe table set
  K5 abbreviation then cipher, base S: words of >= 4 sounds -> first sound + consonants (vowels dropped) | first 3
     sounds | first 2 + last 2
Each set = class x setting x base x language; 10 seeds; poured into the target's page and line shape.
Judge: E032's 13 features, z = (target - set mean) / max(sd, 2%|target|, 0.01), fail iff |z| > 3 (as E032, E062).
Known answers: K-planted targets (Italian, off-grid settings) must be reproduced (best set of class K <= 1 fail);
the copy generator (E032 output, Voynich shape) must not be reproduced (best set >= 2 fails). A class failing either is
VOID. Voynich, per valid class: best set <= 1 fail -> REPRODUCES; every set >= 5 fails -> CLASS FAILS; else PARTIAL.
Rule-8 check: the deciding set re-run with seeds 11-20 must give the same verdict, else PARTIAL.
Run: caffeinate -ims .venv/bin/python experiments/e098_cipher_classes.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, json, random, sys, time, zlib
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e024_atoms as A24  # noqa: E402
import e047_known_answer_script as K47  # noqa: E402
import e086_spaces_and_lines as E86  # noqa: E402
import e093_explanation_model as E93  # noqa: E402
import e097_one_key as E97  # noqa: E402
from e032_copy_generator import FEATS, Z_OK, features  # noqa: E402
from e040_clean_profile import n1  # noqa: E402
from e043_line_recurrence import gen_lines  # noqa: E402
from e062_scribe_tables import permuted_key  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

SEED = 98098
OUT = ROOT / "experiments/results/e098.json"
LANGS = ["latin", "italian", "german", "occitan", "hebrew"]
SEEDS, CHECK_SEEDS = list(range(1, 11)), list(range(11, 21))
NULL_TOP = 20
SHARES = {"K1": 0.20, "K2": 0.08, "K3": 0.12, "K4": 0.10, "K5": 0.10}       # shares of C, fixed in the prereg
GRID = {"K1": [("S", n) for n in (30, 50, 80, 120, 180, 260, 380, 550, 800)],
        "K2": [("S", r) for r in ("reverse", "sort", "perm")],
        "K3": [(b, r) for b in ("S", "V") for r in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)],
        "K4": [(b, u) for b in ("S", "V") for u in ("line", "2lines", "3lines", "4lines", "6lines", "8lines", "12lines", "page")],
        "K5": [("S", r) for r in ("novowel", "first3", "first2last2")]}
PLANT = {"K1": ("S", 300), "K2": ("S", "sort"), "K3": ("S", 0.275), "K4": ("S", "5lines"), "K5": ("S", "first3last1")}
PLANT_LANG, PLANT_SEED = "italian", 777
SOUNDS = E97.SOUNDS
VOWELS = set("aeiou")
NAIBBE = dict(zip(SOUNDS, "aeiou" "pbtdcgfvszszcgzxhmnlryuqt"))   # sound -> Naibbe letter (K->c, S->s, Z->z, C->c ...)
UNITS, _ = K47.voynich_signs()


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ data
def plaintexts():
    out = {}
    for lang in LANGS:
        lm, held = E97.corpus(lang)
        out[lang] = ["".join(SOUNDS[i - 1] for i in w) for w in lm + held]
    return out


def voynich_target():
    pages, _, locked = E93.voynich()
    return pages, locked


def pour(tokens, shape):
    out, i = [], 0
    for lens in shape:
        page = []
        for L in lens:
            page.append(tokens[i:i + L]); i += L
        out.append(page)
    return out


def generator_target(shape):
    flat = [w for l in gen_lines() for w in l]
    return pour(flat, shape)


def prep(pages):
    """what a generous cipher designer may take from the target"""
    toks = [w for p in pages for l in p for w in l]
    uc, pos, npos = Counter(), Counter(), Counter()
    for w in toks:
        us = [u for u in A24.segment(n1(w), A24.SEGS["S3"]) if u in UNITS]
        for j, u in enumerate(us):
            uc[u] += 1; pos[u] += (j / (len(us) - 1)) if len(us) > 1 else 0.5; npos[u] += 1
    for u in UNITS:
        uc[u] += 0
    tc = Counter(toks)
    return {"shape": [[len(l) for l in p] for p in pages], "units_ranked": sorted(UNITS, key=lambda u: (-uc[u], u)),
            "unit_freq": [uc[u] for u in sorted(UNITS, key=lambda u: (-uc[u], u))],
            "mean_pos": {u: (pos[u] / npos[u] if npos[u] else 0.5) for u in UNITS},
            "top_types": [w for w, _ in tc.most_common(600)], "top_freq": [c for _, c in tc.most_common(600)]}


# ------------------------------------------------------------------ cipher machinery
def jitter(seq, rng, block=3):
    out = []
    for i in range(0, len(seq), block):
        b = list(seq[i:i + block]); rng.shuffle(b); out += b
    return out


def sub_table(plain, tg, rng):
    sc = Counter(c for w in plain[:200000] for c in w)
    ranked = sorted(SOUNDS, key=lambda s: (-sc[s], s))
    units = jitter(tg["units_ranked"], rng)
    tab = {}
    for i, s in enumerate(ranked):
        tab[s] = units[i] if i < len(units) else rng.choices(tg["units_ranked"], weights=tg["unit_freq"])[0]
    return tab, units


def enc_s(word, tab):
    return [tab[c] for c in word]


class Stream:
    """plaintext words read cyclically from a seeded offset"""
    def __init__(self, words, rng):
        self.w = words; self.i = rng.randrange(len(words))

    def next(self):
        x = self.w[self.i % len(self.w)]; self.i += 1
        return x

    def letters(self, n):
        out = []
        while len(out) < n:
            out += [NAIBBE[c] for c in self.next()]
        return "".join(out)


def book(cls, setting, lang, plain, tg, seed):
    base, par = setting
    rng = random.Random(seed * 7919 + zlib.crc32(f"{cls}|{par}|{base}|{lang}".encode()))
    st = Stream(plain, rng)
    shape = tg["shape"]
    n_lines = [L for p in shape for L in p]
    page_of = [pi for pi, p in enumerate(shape) for _ in p]
    if base == "V":
        nk = permuted_key(rng.randrange(1 << 20))
    else:
        tab, units = sub_table(plain, tg, rng)
    if cls == "K1":
        pc = Counter(plain)
        top = [w for w, _ in pc.most_common(par)]
        code = dict(zip(top, jitter(tg["top_types"][:par], rng)))
    if cls == "K2":
        if par == "perm":
            perms = {}
        order = tg["mean_pos"]
    if cls == "K3":
        nulls, nw = tg["top_types"][:NULL_TOP], tg["top_freq"][:NULL_TOP]

    def word_s(w):
        us = enc_s(w, tab)
        if cls == "K2":
            if par == "reverse":
                us = us[::-1]
            elif par == "sort":
                us = sorted(us, key=lambda u: (order[u], u))
            else:
                L = len(us)
                if L not in perms:
                    p = list(range(L)); rng.shuffle(p); perms[L] = p
                us = [us[j] for j in perms[L]]
        return "".join(us)

    def abbrev(w):
        if len(w) < 4:
            return w
        if par == "novowel":
            return w[0] + "".join(c for c in w[1:] if c not in VOWELS)
        if par == "first3":
            return w[:3]
        if par == "first3last1":
            return w[:3] + w[-1]
        return w[:2] + w[-2:]

    out_lines = []
    if base == "S":
        cur_block, shift = None, 0
        for li, L in enumerate(n_lines):
            if cls == "K4":
                blk = page_of[li] if par == "page" else li // (1 if par == "line" else int(par[:-5]))
                if blk != cur_block:
                    cur_block = blk; shift = rng.randrange(1, len(UNITS))
                    rot = {u: units[(units.index(u) + shift) % len(units)] for u in units}
            line = []
            while len(line) < L:
                if cls == "K3" and rng.random() < par:
                    line.append(rng.choices(nulls, weights=nw)[0]); continue
                w = st.next()
                if cls == "K1" and w in code:
                    line.append(code[w]); continue
                if cls == "K5":
                    w = abbrev(w)
                s = word_s(w)
                if cls == "K4":
                    s = "".join(rot[tab[c]] for c in w)
                line.append(s)
            out_lines.append(line)
    else:   # base V (K3, K4)
        buf, cur_block = [], None
        for li, L in enumerate(n_lines):
            if cls == "K4":
                blk = page_of[li] if par == "page" else li // (1 if par == "line" else int(par[:-5]))
                if blk != cur_block:
                    cur_block = blk; nk = permuted_key(rng.randrange(1 << 20)); buf = []
            line = []
            while len(line) < L:
                if cls == "K3" and rng.random() < par:
                    line.append(rng.choices(nulls, weights=nw)[0]); continue
                if not buf:
                    buf, _ = NX.encode_tokens(st.letters(60), nk, rng.randrange(1 << 30))
                line.append(buf.pop(0))
            out_lines.append(line)
    pages, k = [], 0
    for p in shape:
        pages.append(out_lines[k:k + len(p)]); k += len(p)
    return pages


# ------------------------------------------------------------------ jobs
_P, _T = {}, {}


def init(plains, targets):
    _P.update(plains); _T.update(targets)


def task(a):
    tname, cls, setting, lang, seed = a
    pages = book(cls, setting, lang, _P[lang], _T[tname], seed)
    lines = [l for p in pages for l in p if l]
    f = features(lines, SEED + seed)
    if seed in (1, 11):
        f["lines_z"] = E86.continuity(pages, random.Random(E86.SEED))["z"]
    if seed == 1 and tname == "VOYNICH":
        f["sample"] = [" ".join(l) for l in pages[0][:3]]
    return a, f


def judge(V, rows):
    M = {k: float(np.mean([g[k] for g in rows])) for k in FEATS}
    S = {k: max(float(np.std([g[k] for g in rows], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in FEATS}
    Z = {k: round((V[k] - M[k]) / S[k], 2) for k in FEATS}
    fail = [k for k in FEATS if abs(Z[k]) > Z_OK]
    return {"z": Z, "fail": fail, "n_fail": len(fail), "mean": M}


def class_sets(cls):
    return [(cls, s, l) for s in GRID[cls] for l in LANGS]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    global SEEDS, LANGS
    if a.smoke:
        SEEDS, LANGS[:] = [1, 2, 3], ["latin", "italian"]
    plains = plaintexts()
    log("plaintext words " + str({k: len(v) for k, v in plains.items()}))
    vpages, locked = voynich_target()
    shape = [[len(l) for l in p] for p in vpages]
    log(f"Voynich DEV pages {len(vpages)}, tokens {sum(map(sum, shape))}")
    T = {"generator": prep(generator_target(shape))}
    targets_pages = {"generator": generator_target(shape)}
    tv = prep(vpages)
    for cls, st in PLANT.items():
        pp = book(cls, st, PLANT_LANG, plains[PLANT_LANG], tv, PLANT_SEED)
        targets_pages[f"plant_{cls}"] = pp; T[f"plant_{cls}"] = prep(pp)
    if not a.smoke:
        targets_pages["VOYNICH"] = vpages; T["VOYNICH"] = tv
    V = {t: features([l for p in pp for l in p if l], SEED) for t, pp in targets_pages.items()}
    for t in V:
        log(f"target {t:10s} " + " ".join(f"{k} {V[t][k]:.3g}" for k in FEATS))
    jobs = []
    for t in T:
        classes = [t.split("_")[1]] if t.startswith("plant_") else list(GRID)
        for cls in classes:
            for (c, s, l) in class_sets(cls):
                jobs += [(t, c, s, l, sd) for sd in SEEDS]
    log(f"jobs {len(jobs)} | {time.time() - t0:.0f}s")
    with Pool(a.workers, initializer=init, initargs=(plains, T)) as pool:
        rows = pool.map(task, jobs, chunksize=4)
        R = {}
        for (t, c, s, l, sd), f in rows:
            R.setdefault((t, c, s, l), []).append(f)
        J = {k: judge(V[k[0]], v) for k, v in R.items()}
        log(f"main pass done | {time.time() - t0:.0f}s")

        def best(t, cls):
            ks = [k for k in J if k[0] == t and k[1] == cls]
            return min(ks, key=lambda k: (J[k]["n_fail"], k[3])) if ks else None

        res = {"experiment": "E098", "seed": SEED, "targets": V, "classes": {}, "locked_test_excluded": locked}
        checks = []
        for cls in GRID:
            bp, bg = best(f"plant_{cls}", cls), best("generator", cls)
            row = {"plant_best": [str(bp), J[bp]["n_fail"], J[bp]["fail"]], "generator_best": [str(bg), J[bg]["n_fail"], J[bg]["fail"]]}
            row["valid"] = J[bp]["n_fail"] <= 1 and J[bg]["n_fail"] >= 2
            if "VOYNICH" in T:
                bv = best("VOYNICH", cls); nf = J[bv]["n_fail"]
                row["voynich_best"] = [str(bv), nf, J[bv]["fail"], J[bv]["z"]]
                row["voynich_all_sets"] = {f"{k[2]}|{k[3]}": J[k]["n_fail"] for k in J if k[0] == "VOYNICH" and k[1] == cls}
                row["raw"] = "REPRODUCES" if nf <= 1 else ("CLASS FAILS" if nf >= 5 else "PARTIAL")
                row["voynich_best_lines_z"] = [f.get("lines_z") for f in R[bv] if "lines_z" in f]
                row["voynich_sample"] = next((f["sample"] for f in R[bv] if "sample" in f), None)
                if row["valid"] and row["raw"] != "PARTIAL":
                    checks.append((cls, bv))
            res["classes"][cls] = row
            log(f"{cls}: valid {row['valid']} plant {row['plant_best'][:2]} generator {row['generator_best'][:2]}"
                + (f" | VOYNICH best {row['voynich_best'][:2]} fails {row['voynich_best'][2]} -> {row['raw']}" if "raw" in row else ""))
        cj = [(k, sd) for cls, k in checks for sd in CHECK_SEEDS]
        crow = pool.map(task, [(k[0], k[1], k[2], k[3], sd) for k, sd in cj], chunksize=2) if cj else []
    for cls, k in checks:
        rr = [f for (t, c, s, l, sd), f in crow if (t, c, s, l) == k]
        jc = judge(V["VOYNICH"], rr); res["classes"][cls]["seed_check"] = [jc["n_fail"], jc["fail"]]
        log(f"{cls}: seed check {k} fails {jc['n_fail']} {jc['fail']}")
    if "VOYNICH" in T:
        fac = {}
        for cls, row in res["classes"].items():
            if not row["valid"]:
                v, f = "VOID", 1.0
            elif row["raw"] == "PARTIAL":
                v, f = "PARTIAL", 1.0
            else:
                nf = row["seed_check"][0]
                same = (nf <= 1) if row["raw"] == "REPRODUCES" else (nf >= 5)
                v, f = (row["raw"], 3.0 if row["raw"] == "REPRODUCES" else 1 / 3) if same else ("PARTIAL", 1.0)
            row["verdict"], row["share_factor"] = v, f; fac[cls] = f
        cf = 1 + sum(SHARES[c] * (fac[c] - 1) for c in fac)
        res["C_factor"] = cf
        log("VERDICTS " + " ".join(f"{c} {r['verdict']}" for c, r in res["classes"].items()) + f" | C x {cf:.4f}")
    res["runtime_s"] = time.time() - t0
    OUT.with_name("e098_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
