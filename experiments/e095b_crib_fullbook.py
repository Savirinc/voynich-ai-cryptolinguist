"""E095b (Test B2, Arham): find a key in the zodiac, prove it on the whole book. See reports/E095B_PREREG.md.

Stage 1 (zodiac): for a crib assignment (sign -> meaning set), keys under which the zodiac pages hold words matching their
assigned meanings (E095 matching: exact or abbreviation >= 6 letters, forwards or backwards; targets >= 4 letters) are
collected by greedy consistent construction (R1 restarts; on each page one of the TOP_CHOICE candidates that make the
book most plausible is taken: mean LM bigram log-prob over book bigrams of fixed units); among keys with coverage >=
best - 1, the N_KEYS most plausible go on.
Units are the VOY23 signs (E047: cleaned EVA, S3 units, the 23 commonest Voynich-A signs); letters are the language
model's 23 letters.
Stage 2 (whole book): each partial key is completed on the whole Voynich A (or B) prose by the E047 annealer with the
crib's units held fixed (R2 x IT2), under the language's 4-gram model; score = best objective per sign.
Statistic per configuration (language x section): the best stage-2 score among the TRUE crib's keys, compared with the
same for N_PERM wrong cribs (meaning sets shuffled among signs; two-page signs together). Max-T over configurations.
Calibration: synthetic books (E047 VOY23 cipher of held-out Bible text, Voynich-A length) with synthetic zodiac pages of
the real pages' word counts drawn from the same cipher, each holding one planted own-sign meaning word.
Run: caffeinate -ims .venv/bin/python experiments/e095b_crib_fullbook.py [--smoke] [--workers 3]
"""
from __future__ import annotations

import argparse, glob, json, random, sys, time, unicodedata
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e024_atoms as A24  # noqa: E402
import e047_known_answer_script as K  # noqa: E402
import e052_shortlist_attack as S52  # noqa: E402
from e040_clean_profile import n1  # noqa: E402
from e049_attack_voynich import voynich_seqs  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
from vcl.solvers.engine import freq_init  # noqa: E402

SEED = 95195
OUT = ROOT / "experiments/results/e095b.json"
CON = json.loads((ROOT / "reports/data/e095_concepts.json").read_text())
ORDER = ["f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v"]
SIGNS = CON["signs"]
MIN_TARGET, MIN_PREFIX = 4, 6
R1, N_KEYS, R2, IT2, TOP_CHOICE = 2000, 8, 2, 8000, 3
N_PERM = 99
HEB = dict(zip("AbgdhwzHTyklmnsEpcqrSt", "אבגדהוזחטיכלמנסעפצקרשת"))
ARA = dict(zip("AbtVjHxdDrzsSCQTZEGfqklmnhwy", "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"))
LANGS = {"latin": ("la", None), "french_occitan": ("fraLSG", "OT"), "italian": ("ita1885", "OT"), "german": ("deu1912", "OT"),
         "hebrew": ("he", None), "arabic": ("arb-vd", "OT")}


def log(*a):
    print(*a, flush=True)


def lm_words(lang, test=False):
    tag, _ = LANGS[lang]
    if tag in ("la", "he"):
        return K.book_words(tag, K.TEST_BOOKS if test else K.LM_BOOKS)
    has_ot = bool(glob.glob(str(ROOT / f"data/external/bibles/{tag}/txt/*_GEN_*")))
    books = (S52.OT_TEST if test else S52.OT_LM) if has_ot else (S52.NT_TEST if test else S52.NT_LM)
    return S52.book_words(tag, books)


def norm_target(lang, t):
    if lang == "hebrew":
        return K.norm("".join(HEB.get(c, "") for c in t), "he")
    if lang == "arabic":
        return S52.norm("".join(ARA.get(c, "") for c in t))
    if lang == "latin":
        return K.norm(t, "la")
    return S52.norm(t)


def targets(lang, lm):
    L = CON["languages"][lang]; keep = set(lm.letters); out = {}
    for s in SIGNS:
        a = CON["attributes"][s]; raw = set()
        for m in a["months"]:
            raw |= set(L["months"][m])
        raw |= set(L["sign"][s]) | set(L["animal"][s]) | set(L["planet"][a["planet"]]) | set(L["element"][a["element"]]) | set(L["season"][a["season"]])
        ts = set()
        for t in raw:
            for w in norm_target(lang, t):
                w = "".join(c for c in w if c in keep)
                if len(w) >= MIN_TARGET:
                    ts.add(tuple(lm.idx[c] for c in w))
        out[s] = sorted(ts)
    return out


def zodiac_seqs():
    signs, _ = K.voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    out = {}
    for p in ORDER:
        ws = sorted({t.eva for t in toks if t.folio == p and t.is_clean and t.leaf not in locked})
        sq = [tuple(idx[x] for x in A24.segment(n1(w), A24.SEGS["S3"]) if x in idx) for w in ws]
        out[p] = sorted({s for s in sq if s})
    return out


def candidates(zpages, tg):
    cand = {}
    for p in ORDER:
        for s in SIGNS:
            cs = set()
            for sq0 in zpages[p]:
                for sq in (sq0, sq0[::-1]):
                    n = len(sq)
                    for t in tg[s]:
                        if n == len(t) or (MIN_PREFIX <= n < len(t)):
                            m = {}; ok = True
                            for u, c in zip(sq, t[:n]):
                                if m.setdefault(u, c) != c:
                                    ok = False; break
                            if ok:
                                cs.add(tuple(sorted(m.items())))
            cand[(p, s)] = sorted(cs)
    return cand


def bigram_tables(seq, lm):
    """unit bigram counts in the book (0 = space) and the LM's letter bigram log-probabilities (from its unigram/bigram
    counts in the LM's own flat table is not exposed, so use add-1 bigram counts of the training stream)."""
    C = np.zeros((K.NSIGN + 1, K.NSIGN + 1)); np.add.at(C, (seq[:-1], seq[1:]), 1)
    return C


def prescreen(keys, C, LB):
    """mean LM bigram log-prob over book bigrams whose two units are both fixed by the key (spaces count as fixed)"""
    out = []
    for k in keys:
        m = np.full(K.NSIGN + 1, -1); m[0] = 0
        for u, l in k.items():
            m[u] = l
        ok = m >= 0; sub = C[np.ix_(ok, ok)]; mm = m[ok]
        out.append(float((sub * LB[np.ix_(mm, mm)]).sum() / max(1.0, sub.sum())))
    return out


def stage1(cand, assign, rng, C=None, LB=None):
    """Greedy consistent key construction, pages in random order; on each page, among candidates consistent with the
    partial key, one of the TOP_CHOICE most book-plausible (prescreen of key + candidate) is taken at random.
    Keys with coverage >= best - 1 are ranked by prescreen; the top N_KEYS go to stage 2."""
    bypage = defaultdict(list)
    for pi, p in enumerate(ORDER):
        bypage[pi] = cand[(p, assign[CON["pages"][p]])]
    pages = [p for p in bypage if bypage[p]]; found = {}
    for _ in range(R1):
        rng.shuffle(pages); key = {}; cov = 0
        for p in pages:
            opts = []
            for cons in bypage[p]:
                ok = True
                for u, l in cons:
                    k = key.get(u)
                    if k is not None and k != l:
                        ok = False; break
                if ok:
                    opts.append(cons)
            if opts:
                if len(opts) > 1:
                    sc = prescreen([{**key, **dict(o)} for o in opts], C, LB)
                    top = list(np.argsort(sc)[::-1][:TOP_CHOICE]); pick = opts[rng.choice(top)]
                else:
                    pick = opts[0]
                for u, l in pick:
                    key[u] = l
                cov += 1
        fk = tuple(sorted(key.items()))
        found[fk] = max(found.get(fk, 0), cov)
    if not found:
        return [], 0
    best = max(found.values())
    keys = [dict(k) for k, c in found.items() if c >= best - 1]
    sc = prescreen(keys, C, LB); order = np.argsort(sc)[::-1]
    return [keys[i] for i in order[:N_KEYS]], best


def complete(seq, lm, fixed, rng_np):
    sc = K.FullScorer(seq, lm)
    p = lm.unigram[1:] ** 0.5; p = p / p.sum(); cum = np.cumsum(p)
    free = [u for u in range(1, K.NSIGN + 1) if u not in fixed]
    m0 = freq_init(seq, K.NSIGN, lm, injective=False)
    for u, l in fixed.items():
        m0[u] = l
    best = -1e18
    for _ in range(R2):
        m = m0.copy(); cur = sc(m); T = max(1.0, 0.03 * len(seq)); ratio = (0.05 / T) ** (1.0 / IT2)
        if not free:
            best = max(best, cur); break
        for it in range(IT2):
            c = m.copy()
            if rng_np.random() < 0.3 and len(free) > 1:
                i, j = rng_np.choice(free, 2, replace=False)
                if m[i] == m[j]:
                    T *= ratio; continue
                c[i], c[j] = m[j], m[i]
            else:
                i = free[int(rng_np.integers(len(free)))]; L = 1 + int(np.searchsorted(cum, rng_np.random() * cum[-1]))
                if L == m[i]:
                    T *= ratio; continue
                c[i] = L
            s = sc(c); d = s - cur
            if d >= 0 or rng_np.random() < np.exp(d / T):
                m, cur = c, s
                if cur > best:
                    best = cur
            T *= ratio
        best = max(best, cur)
    return best / max(1, int((seq > 0).sum()))


_STATE = {}


def _init(state):
    _STATE.update(state)


def run_assignment(args):
    cfg, aid, assign, seed = args
    st = _STATE[cfg]; rng = random.Random(seed)
    keys, cov = stage1(st["cand"], assign, rng, st["C"], st["LB"])
    if not keys:
        return cfg, aid, cov, -1e9, None
    rs = np.random.default_rng(seed)
    scores = [complete(st["seq"], st["lm"], k, rs) for k in keys]
    i = int(np.argmax(scores))
    return cfg, aid, cov, float(scores[i]), {str(u): int(l) for u, l in keys[i].items()}


def lm_bigram(lm, words):
    """add-1 letter bigram log-probabilities (index 0 = space) from the LM's training words"""
    keep = set(lm.letters); B = np.ones((lm.A, lm.A))
    for w in words:
        w = "".join(c for c in w if c in keep)
        if not w:
            continue
        ids = [0] + [lm.idx[c] for c in w] + [0]
        for a, b in zip(ids, ids[1:]):
            B[a, b] += 1
    return np.log(B / B.sum(axis=1, keepdims=True))


def flat(seqs):
    s = []
    for u in seqs:
        s += list(u) + [0]
    return np.array(s[:-1], dtype=np.int64)


def perms(n, rng):
    out = []
    for _ in range(n):
        sh = SIGNS[:]; rng.shuffle(sh); out.append(dict(zip(SIGNS, sh)))
    return out


def synthetic(lang, lm, zreal, nA, rng):
    plain = K.keep_letters(lm_words(lang, test=True), lm.letters)
    freq = Counter(c for w in plain for c in w); key = K.make_key(lm.letters, freq, rng)
    _, sw = K.voynich_signs()
    st = rng.randrange(0, len(plain) - nA - 5000)
    body, _ = K.encode(plain[st:st + nA], key, sw, rng)
    pool = plain[st + nA:st + nA + 5000]
    tg = targets(lang, lm); zp = {}
    for p in ORDER:
        ws = [tuple(rng.choice(key[c]) for c in w) for w in rng.sample(pool, len(zreal[p]))]
        t = rng.choice(tg[CON["pages"][p]]); ws.append(tuple(rng.choice(key[lm.alphabet[i]]) for i in t))
        zp[p] = sorted(set(ws))
    return body, zp


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(); t0 = time.time(); rng = random.Random(SEED)
    global N_PERM
    zreal = zodiac_seqs()
    VA, _, _, _ = voynich_seqs("A"); VB, _, _, _ = voynich_seqs("B")
    LM = {}
    for lang, (tag, _) in LANGS.items():
        LM[lang] = K.SpaceLM(lm_words(lang), tag); LM[lang].idx = {c: i for i, c in enumerate(LM[lang].alphabet)}
        LM[lang].LB = lm_bigram(LM[lang], lm_words(lang))
    log("zodiac words (VOY23) per page:", {p: len(zreal[p]) for p in ORDER}, "| A", len(VA), "B", len(VB))
    state, configs = {}, []
    for lang in ("latin", "french_occitan", "hebrew"):
        body, zp = synthetic(lang, LM[lang], zreal, len(VA), rng)
        fb = flat(body)
        state[f"CAL/{lang}"] = {"cand": candidates(zp, targets(lang, LM[lang])), "seq": fb, "lm": LM[lang], "C": bigram_tables(fb, LM[lang]), "LB": LM[lang].LB}
    if not a.smoke:
        for lang in LANGS:
            tg = targets(lang, LM[lang]); cand = candidates(zreal, tg)
            for sec, V in (("A", VA), ("B", VB)):
                fv = flat(V)
                state[f"{lang}/{sec}"] = {"cand": cand, "seq": fv, "lm": LM[lang], "C": bigram_tables(fv, LM[lang]), "LB": LM[lang].LB}
                configs.append(f"{lang}/{sec}")
    if a.smoke:
        N_PERM = 4
    ident = dict(zip(SIGNS, SIGNS)); P = perms(N_PERM, rng)
    jobs = []
    for cfg in state:
        jobs.append((cfg, "true", ident, rng.randrange(1 << 30)))
        jobs += [(cfg, i, P[i], rng.randrange(1 << 30)) for i in range(N_PERM)]
    log(f"jobs {len(jobs)} | {time.time() - t0:.0f}s")
    with Pool(a.workers, initializer=_init, initargs=(state,)) as pool:
        res = pool.map(run_assignment, jobs, chunksize=1)
    R = defaultdict(dict)
    for cfg, aid, cov, sc, key in res:
        R[cfg][aid] = {"cov": cov, "score": sc, "key": key}
    out = {}
    for cfg in state:
        tr = R[cfg]["true"]["score"]; nl = [R[cfg][i]["score"] for i in range(N_PERM)]
        mu, sd = float(np.mean(nl)), float(np.std(nl)) or 1e-9
        out[cfg] = {"true": tr, "true_cov": R[cfg]["true"]["cov"], "null": nl, "null_cov": [R[cfg][i]["cov"] for i in range(N_PERM)],
                    "z": (tr - mu) / sd, "p": (1 + sum(x >= tr for x in nl)) / (1 + N_PERM), "true_key": R[cfg]["true"]["key"]}
        log(f"{cfg:24s} true {tr:+.4f} (cov {R[cfg]['true']['cov']})  null mean {mu:+.4f} sd {sd:.4f} max {max(nl):+.4f}  z {out[cfg]['z']:+.2f} p {out[cfg]['p']:.2f}")
    cal = {c: out[c]["p"] for c in out if c.startswith("CAL/")}
    validated = all(v <= 0.01 for v in cal.values()) if not a.smoke else None
    verdict, pT = "SMOKE", None
    if configs:
        def zof(c, x, excl=None):
            nl = [v for i, v in enumerate(out[c]["null"]) if i != excl]; return (x - np.mean(nl)) / (np.std(nl) or 1e-9)
        Treal = max(zof(c, out[c]["true"]) for c in configs)
        Tnull = [max(zof(c, out[c]["null"][i], i) for c in configs) for i in range(N_PERM)]
        pT = (1 + sum(x >= Treal for x in Tnull)) / (1 + N_PERM); best = max(configs, key=lambda c: zof(c, out[c]["true"]))
        if not validated:
            verdict = "VOID (calibration failed)"
        elif pT <= 0.01:
            verdict = f"CLAIM (max-T {Treal:.2f}, p {pT:.3f}, best {best}) - seed check and blind reading follow"
        else:
            verdict = f"NO CLAIM (max-T {Treal:.2f}, p {pT:.2f}, best {best})"
    log(f"VERDICT {verdict} | calibration {cal} | {time.time() - t0:.0f}s")
    OUT.with_name("e095b_smoke.json" if a.smoke else OUT.name).write_text(json.dumps(
        {"experiment": "E095b", "seed": SEED, "results": out, "calibration": cal, "validated": validated, "p_maxT": pT,
         "verdict": verdict, "runtime_s": time.time() - t0}, indent=1))


if __name__ == "__main__":
    main()
