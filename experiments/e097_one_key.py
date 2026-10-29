"""E097 (Arham): ONE key for the whole book; the hidden writing may borrow signs or features from several scripts of
the time and region; anchor: the zodiac pages are meaningful. See reports/E097_PREREG.md.

Model. Every candidate language (Latin, Italian, Occitan, Catalan, French, German, Czech, Greek, Hebrew, Arabic) is
rewritten in ONE sound alphabet (30 sounds; period pronunciation rules below), so a single key can read all of them.
The key maps each of the 23 VOY23 signs (E047: cleaned EVA, S3 units, the 23 commonest Voynich-A signs) to one sound
or to one of 10 scribal shorthand values (us, um, is, er, ur, rum, con, per, pro, que). The key is the same everywhere;
each LINE may be in any of the ten languages (the line takes the language that reads it best).
Objective of a key on a text: sum over lines of the best language's 4-gram Kneser-Ney log-probability of the decoded
line (spaces kept), minus N_l * KL(decoded sound distribution of language-l lines || language l's sound distribution)
(the E047/E017 penalty, per language).
Stage 1 (anchor, 6 training zodiac pages): keys under which training-page words read exactly as their own sign's
zodiac material (months x2, sign, animal, planet, element, season in 8 languages; Lilly's fixed-star names), by greedy
consistent construction (E095b), top N_KEYS by plausibility.
Stage 2 (whole book, training half): each anchor key (anchor signs held fixed) and one free start are completed by
annealing; the best objective wins.
Held-out checks: Q1 lexrate on the held-out half (decoded words of >= 3 sounds found in the vocabulary of the line's
language) against a threshold fixed on DEV known answers; Q2 on the 6 held-out zodiac pages: number of pages with a NEW
word (not on a training zodiac page) that reads as own-sign material, against all 720 assignments of the six signs.
Run: caffeinate -ims .venv/bin/python experiments/e097_one_key.py [--smoke] [--workers 3]
"""
from __future__ import annotations

import argparse, glob, html, itertools, json, random, re, sys, time, unicodedata
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e024_atoms as A24  # noqa: E402
import e047_known_answer_script as K  # noqa: E402
from e040_clean_profile import n1  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
from vcl.solvers.lm import _kn_dense  # noqa: E402

SEED = 97097
OUT = ROOT / "experiments/results/e097.json"
BIB = ROOT / "data/external/bibles"
PER = ROOT / "data/external/period_texts_e097"
CON = json.loads((ROOT / "reports/data/e095_concepts.json").read_text())
ORDER = ["f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v"]
ZTRAIN, ZHELD = ORDER[0::2], ORDER[1::2]
NSIGN = 23
SOUNDS = list("aeiou") + list("pbtdkgfvszSZCJcxhmnlrjwqT")      # S sh, Z zh, C ch, J dzh, c ts, x kh, j y, q glottal, T th
A = len(SOUNDS) + 1                                               # 0 = space
SID = {s: i + 1 for i, s in enumerate(SOUNDS)}
CLUSTERS = ["us", "um", "is", "er", "ur", "rum", "kon", "per", "pro", "kwe"]
VALS = [(SID[s],) for s in SOUNDS] + [tuple(SID[c] for c in cl) for cl in CLUSTERS]
VNAME = SOUNDS + ["-" + c for c in CLUSTERS]
NV = len(VALS); SPACE_V = NV
VLEN = np.array([len(v) for v in VALS] + [1], dtype=np.int64)
VMAT = np.zeros((NV + 1, 3), dtype=np.int64)
for _i, _v in enumerate(VALS):
    VMAT[_i, :len(_v)] = _v
LANGS = ["latin", "italian", "occitan", "catalan", "french", "german", "czech", "greek", "hebrew", "arabic"]
LT = 0.12                                   # spelling-slip rate of the known-answer ciphers (E047)
MIN_MAT = 3                                 # zodiac material words of >= 3 sounds; Voynich words of >= 3 signs
R1, N_KEYS, TOP_CHOICE = 2000, 8, 3
R2, IT2 = 1, 20000                          # stage-2 restarts x steps per start
TOPB, ROUNDS, IT_SUB = 2, 3, 8000           # refit: best starts per book, rounds, steps (sub-fit and joint)
BLOCK = 20                                  # lines per language block in mixed known answers
P_ABBR = 0.7                                # chance a cluster is written with its shorthand sign
CRACK = 0.80


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ sound rules (period pronunciation, simplified)
V = "aeiouy"
RULES = {
    "latin": [("ae", "e"), ("oe", "e"), ("ph", "f"), ("th", "t"), ("ch", "k"), ("qu", "kw"), ("x", "ks"),
              (f"c(?=[eiy])", "c"), (f"t(?=i[{V}])", "c"), ("j", "i"), ("v", "u"), ("y", "i"), ("c", "k"), ("q", "k")],
    "italian": [("sci(?=[aou])", "S"), ("sc(?=[ei])", "S"), ("ci(?=[aou])", "C"), ("c(?=[ei])", "C"),
                ("gi(?=[aou])", "J"), ("g(?=[ei])", "J"), ("gli", "li"), ("gn", "nj"), ("ch", "k"), ("gh", "g"),
                ("qu", "kw"), ("z", "c"), ("h", ""), ("x", "ks"), ("j", "j"), ("y", "i"), ("c", "k"), ("q", "k")],
    "occitan": [("ch", "C"), ("nh", "nj"), ("lh", "lj"), ("qu", "k"), ("gu(?=[ei])", "g"), ("tz", "c"),
                ("c(?=[eiy])", "s"), ("ç", "s"), ("g(?=[ei])", "J"), ("j", "J"), ("h", ""), ("x", "ks"), ("y", "i"),
                ("c", "k"), ("q", "k")],
    "catalan": [("tx", "C"), ("ny", "nj"), ("ll", "lj"), ("ch", "k"), ("qu(?=[ei])", "k"), ("qu", "kw"),
                ("gu(?=[ei])", "g"), ("ss", "s"), ("c(?=[eiy])", "s"), ("ç", "s"), ("x", "S"), ("g(?=[eiy])", "Z"),
                ("j", "Z"), ("h", ""), ("y", "i"), ("c", "k"), ("q", "k")],
    "french": [("eau", "o"), ("au", "o"), ("ou", "u"), ("oi", "wa"), ("ch", "S"), ("ph", "f"), ("qu", "k"),
               ("gu(?=[eiy])", "g"), ("gn", "nj"), ("c(?=[eiy])", "s"), ("ç", "s"), ("g(?=[eiy])", "Z"), ("j", "Z"),
               ("h", ""), ("x", "ks"), ("y", "i"), ("c", "k"), ("q", "k")],
    "german": [("tsch", "C"), ("sch", "S"), ("ch", "x"), ("ck", "k"), ("tz", "c"), ("z", "c"), ("ei", "ai"),
               ("ey", "ai"), ("ie", "i"), ("äu", "oi"), ("eu", "oi"), ("ph", "f"), ("qu", "kv"), ("ß", "s"),
               ("ä", "e"), ("ö", "e"), ("ü", "i"), ("w", "v"), ("v", "f"), ("j", "j"), ("y", "i"), ("x", "ks"),
               ("c", "k"), ("q", "k")],
    "czech": [("ch", "x"), ("č", "C"), ("š", "S"), ("ž", "Z"), ("ř", "rZ"), ("ě", "je"), ("ň", "nj"), ("ť", "tj"),
              ("ď", "dj"), ("c", "c"), ("j", "j"), ("w", "v"), ("y", "i"), ("qu", "kv"), ("x", "ks"), ("q", "k")],
    "greek": [("ου", "u"), ("αι", "e"), ("ει", "i"), ("οι", "i"), ("υι", "i"), ("αυ", "av"), ("ευ", "ev"), ("ηυ", "iv"),
              ("γγ", "ng"), ("γκ", "g"), ("α", "a"), ("β", "v"), ("γ", "g"), ("δ", "d"), ("ε", "e"), ("ζ", "z"),
              ("η", "i"), ("θ", "T"), ("ι", "i"), ("κ", "k"), ("λ", "l"), ("μ", "m"), ("ν", "n"), ("ξ", "ks"),
              ("ο", "o"), ("π", "p"), ("ρ", "r"), ("σ", "s"), ("ς", "s"), ("τ", "t"), ("υ", "i"), ("φ", "f"),
              ("χ", "x"), ("ψ", "ps"), ("ω", "o")],
    "greek_rom": [("ph", "f"), ("th", "T"), ("ch", "x"), ("ps", "ps"), ("ou", "u"), ("ai", "e"), ("ei", "i"),
                  ("oi", "i"), ("au", "av"), ("eu", "ev"), ("y", "i"), ("b", "v"), ("h", ""), ("x", "ks"),
                  ("c", "k"), ("q", "k")],
    "hebrew": list(zip("אבגדהוזחטיכלמנסעפצקרשת", ["q", "b", "g", "d", "h", "w", "z", "x", "t", "j", "k", "l", "m", "n",
                                                    "s", "q", "p", "c", "k", "r", "S", "t"])),
    "arabic": list(zip("اءبتثجحخدذرزسشصضطظعغفقكلمنهويىة", ["a", "q", "b", "t", "T", "J", "h", "x", "d", "d", "r",
                                                               "z", "s", "S", "s", "d", "t", "z", "q", "g", "f", "k",
                                                               "k", "l", "m", "n", "h", "w", "j", "a", "a"])),
}
KEEP_MARKS = {"occitan": "ç", "catalan": "ç", "french": "ç", "german": "äöüß", "czech": "čšžřěňťď"}
HEB_FIN = str.maketrans("ךםןףץ", "כמנפצ")
HEB_TR = dict(zip("AbgdhwzHTyklmnsEpcqrSt", "אבגדהוזחטיכלמנסעפצקרשת"))
ARA_TR = dict(zip("AbtVjHxdDrzsSCQTZEGfqklmnhwy", "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"))


def _compile(lang):
    rules = RULES[lang]
    if lang not in ("greek", "hebrew", "arabic"):
        rules = rules + [(c, c) for c in "abdefgiklmnoprstuvz"]
    rx = re.compile("|".join(f"({p})" for p, _ in rules))
    outs = [o for _, o in rules]
    return rx, outs


_RX = {}


def to_sounds(word, lang):
    """one word (any case) -> tuple of sound ids (unknown letters dropped)"""
    if lang not in _RX:
        _RX[lang] = _compile(lang)
    rx, outs = _RX[lang]
    w = unicodedata.normalize("NFC", word.lower())
    keep = KEEP_MARKS.get(lang, "")
    w = "".join(c if c in keep else "".join(d for d in unicodedata.normalize("NFD", c) if unicodedata.category(d) != "Mn")
                for c in w)
    if lang == "hebrew":
        w = w.translate(HEB_FIN)
    s = rx.sub(lambda m: "\0" + outs[m.lastindex - 1] + "\0", w)
    return tuple(SID[c] for c in "".join(p for i, p in enumerate(s.split("\0")) if i % 2 == 1) if c in SID)


def words_of(text, lang):
    t = "".join(c for c in unicodedata.normalize("NFC", text) if unicodedata.category(c) != "Mn")
    raw = re.findall(r"[^\W\d_]+", t)
    out = [to_sounds(w, lang) for w in raw]
    return [w for w in out if w]


# ------------------------------------------------------------------ corpora (LM part / held-out part)
BIBLES = {"latin": "latVUC", "italian": "ita1885", "french": "fraLSG", "german": "deu1912", "czech": "ces1613",
          "greek": "grcbyz", "hebrew": "hboWLC", "arabic": "arb-vd"}
OT_LM = ["GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "1SA", "2SA", "1KI", "2KI"]
OT_TEST = ["EZK", "PSA", "PRO", "JOB", "1CH", "2CH"]
NT_LM = ["MAT", "MRK", "LUK", "JHN", "ACT"]
NT_TEST = ["ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS", "1PE",
           "2PE", "1JN", "2JN", "3JN", "JUD", "REV"]


def bible_text(bid, books):
    fs = sorted(f for f in glob.glob(str(BIB / bid / "txt" / "*_read.txt")) if any(f"_{b}_" in f for b in books))
    return "\n".join("\n".join(Path(f).read_text(encoding="utf-8-sig").splitlines()[1:]) for f in fs)


def strip_wiki(t):
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t); t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t); t = re.sub(r"'{2,}", "", t)
    return html.unescape(t)


def period_pages(lang):
    if lang == "catalan":
        d = json.loads((PER / "catalan_muntaner.json").read_text())
        pages = []
        for k in sorted(d):
            t = d[k]; i = t.find("CAPITOL")
            if i >= 0:
                pages.append(t[i:])
        return pages
    seen, pages = set(), []
    for f in ("occitan_old.json", "occitan_memorias.json"):
        d = json.loads((PER / f).read_text())
        for k in sorted(d):
            body = strip_wiki(d[k]); key = re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", body.lower()))[:80]
            if key in seen or k == "Libre de Memorias":
                continue
            seen.add(key); pages.append(body)
    return pages


def corpus(lang):
    """(LM words, held-out words), each a list of sound tuples"""
    if lang in ("catalan", "occitan"):
        pages = period_pages(lang); cut = int(0.8 * len(pages))
        return words_of("\n".join(pages[:cut]), lang), words_of("\n".join(pages[cut:]), lang)
    bid = BIBLES[lang]
    has_ot = bool(glob.glob(str(BIB / bid / "txt" / "*_GEN_*")))
    lm, te = (OT_LM, OT_TEST) if has_ot else (NT_LM, NT_TEST)
    return words_of(bible_text(bid, lm), lang), words_of(bible_text(bid, te), lang)


class SoundLM:
    def __init__(self, words, lang):
        ids = []
        for w in words:
            ids += list(w) + [0]
        ids = np.array(ids, dtype=np.int64)
        self.flat = np.asarray(_kn_dense(np.concatenate([np.zeros(3, dtype=np.int64), ids]), A)).reshape(-1)
        uni = np.bincount(ids, minlength=A).astype(float); uni[0] = 0; self.unigram = uni / uni.sum()
        self.vocab = {w for w in set(words) if len(w) >= 3}
        self.lang = lang; self.H = None

    def xent(self, words):
        """typical cross-entropy (nats per scored symbol, spaces included) on held-out words, in 12-word lines"""
        tot = n = 0.0
        for i in range(0, len(words) - 12, 12):
            ids = [0, 0, 0]
            for w in words[i:i + 12]:
                ids += list(w) + [0]
            ids = np.array(ids)
            f = ids[:-3] * A ** 3 + ids[1:-2] * A ** 2 + ids[2:-1] * A + ids[3:]
            tot -= float(self.flat[f].sum()); n += len(f)
        return tot / n


# ------------------------------------------------------------------ zodiac material in sounds
MONTH = {"feb": "February", "mar": "March", "apr": "April", "may": "May", "jun": "June", "jul": "July", "aug": "August",
         "sep": "September", "oct": "October", "nov": "November", "dec": "December", "jan": "January"}
CON_RULES = {"latin": ["latin"], "french_occitan": ["french", "occitan"], "catalan": ["catalan"], "italian": ["italian"],
             "german": ["german"], "greek": ["greek_rom"], "hebrew": ["hebrew"], "arabic": ["arabic"]}


def load_stars():
    raw = (ROOT / "data/external/degree_tables_x097/deginf.html").read_text(encoding="latin-1")
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
             "Aquarius", "Pisces"]
    out, k = defaultdict(list), -1
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)[-7:]
        if len(tds) < 7:
            continue
        deg = re.sub(r"<[^>]+>|&nbsp;|\s", "", tds[0])
        if not deg.isdigit():
            continue
        if deg == "1":
            k += 1
        txt = html.unescape(re.sub(r"<[^>]+>", " ", tds[6])).replace("\xa0", " ")
        for nm in re.split(r"[,()]", txt):
            for w in nm.split():
                out[signs[k]].append((w, f"fixed star at {signs[k]} {deg} deg"))
    return out


def material():
    """sign -> {sound tuple: [(language, written form, meaning)]}"""
    stars = load_stars(); out = {}
    for s in CON["signs"]:
        a = CON["attributes"][s]; m = defaultdict(list)
        for cl, rules in CON_RULES.items():
            L = CON["languages"][cl]; items = []
            for mo in a["months"]:
                items += [(w, f"month: {MONTH[mo]}") for w in L["months"][mo]]
            items += [(w, f"sign name: {s}") for w in L["sign"][s]] + [(w, f"animal/figure of {s}") for w in L["animal"][s]]
            items += [(w, f"planet: {a['planet']}") for w in L["planet"][a["planet"]]]
            items += [(w, f"element: {a['element']}") for w in L["element"][a["element"]]]
            items += [(w, f"season: {a['season']}") for w in L["season"][a["season"]]]
            for w, mean in items:
                src = "".join(HEB_TR.get(c, c) for c in w) if cl == "hebrew" else \
                      "".join(ARA_TR.get(c, c) for c in w) if cl == "arabic" else w
                for r in rules:
                    for part in src.split():
                        t = to_sounds(part, r)
                        if len(t) >= MIN_MAT:
                            m[t].append((r, w, mean))
        for w, mean in stars.get(s, []):
            t = to_sounds(w, "latin")
            if len(t) >= MIN_MAT:
                m[t].append(("star name", w, mean))
        out[s] = dict(m)
    return out


# ------------------------------------------------------------------ books: lines of sign tuples
def voynich_signs():
    signs, sw = K.voynich_signs()
    return signs, sw


def voynich_book():
    """{'lines': [(page, sheet, [word sign tuples])], ...} for all non-locked DEV lines, clean words, VOY23 units"""
    signs, _ = voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    lines, cur = [], None
    for t in toks:
        if t.leaf in locked or not t.is_clean:
            continue
        key = (t.folio, t.line_no, t.locus)
        u = tuple(idx[x] for x in A24.segment(n1(t.eva), A24.SEGS["S3"]) if x in idx)
        if not u:
            continue
        if key != cur:
            lines.append([t.folio, t.bifolio_id, []]); cur = key
        lines[-1][2].append(u)
    return [tuple(l) for l in lines]


def split(lines, rng):
    """train / held-out line indices: zodiac pages alternate (ZTRAIN/ZHELD); other pages by sheet, half each"""
    sheets = sorted({sh for p, sh, _ in lines if p not in ORDER}); rng.shuffle(sheets)
    tr_sheets = set(sheets[:len(sheets) // 2])
    tr, he = [], []
    for i, (p, sh, _) in enumerate(lines):
        if p in ORDER:
            (tr if p in ZTRAIN else he).append(i)
        else:
            (tr if sh in tr_sheets else he).append(i)
    return tr, he


# ------------------------------------------------------------------ scorer
class Stream:
    def __init__(self, lines_w):
        S, line, scored = [], [], []
        for li, ws in enumerate(lines_w):
            S += [0, 0, 0]; line += [li] * 3; scored += [False] * 3
            for w in ws:
                S += list(w) + [0]; line += [li] * (len(w) + 1); scored += [True] * (len(w) + 1)
        self.S = np.array(S, dtype=np.int64); self.line = np.array(line, dtype=np.int64)
        self.scored = np.array(scored, dtype=bool); self.n_lines = len(lines_w)
        self.n_signs = int((self.S > 0).sum())


class Scorer:
    def __init__(self, stream, lms):
        self.st = stream; self.FL = np.stack([lm.flat for lm in lms]); self.nL = len(lms)
        self.logu = np.log(np.maximum(np.stack([lm.unigram for lm in lms]), 1e-6))
        self.H = np.array([lm.H for lm in lms])[:, None]

    def decode(self, m):
        st = self.st; mm = np.append(m, SPACE_V)
        vv = np.where(st.S > 0, mm[st.S], SPACE_V)
        lens = VLEN[vv]; tot = int(lens.sum())
        rep = np.repeat(np.arange(len(vv)), lens)
        within = np.arange(tot) - np.repeat(np.cumsum(lens) - lens, lens)
        let = VMAT[vv[rep], within]; let[vv[rep] == SPACE_V] = 0
        return let, st.line[rep], st.scored[rep]

    def __call__(self, m, detail=False):
        let, line, sc = self.decode(m)
        f = let[:-3] * A ** 3 + let[1:-2] * A ** 2 + let[2:-1] * A + let[3:]
        keep = sc[3:]; f = f[keep]; ln = line[3:][keep]; lt = let[3:][keep]
        starts = np.searchsorted(ln, np.arange(self.st.n_lines))
        LP = self.FL[:, f]
        sums = np.add.reduceat(LP, starts, axis=1)
        a = np.argmax(sums, axis=0); best = sums[a, np.arange(self.st.n_lines)]
        al = a[ln]
        cnt = np.bincount(al * A + lt, minlength=self.nL * A).reshape(self.nL, A)[:, 1:].astype(float)
        N = cnt.sum(axis=1, keepdims=True)
        q = np.divide(cnt, N, out=np.zeros_like(cnt), where=N > 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            kl = np.where(q > 0, q * (np.log(np.where(q > 0, q, 1)) - self.logu[:, 1:]), 0).sum(axis=1)
        val = float(best.sum() - (N[:, 0] * kl).sum())
        return (val, a) if detail else val


def pooled_unigram(lms):
    u = np.mean([lm.unigram for lm in lms], axis=0)
    return u


def free_init(stream, lms):
    cnt = np.bincount(stream.S, minlength=NSIGN + 1)[1:]
    u = pooled_unigram(lms)[1:]; order_let = np.argsort(-u)
    p = u[order_let] / u[order_let].sum(); tot = cnt.sum(); acc = np.zeros(len(order_let))
    m = np.zeros(NSIGN + 1, dtype=np.int64)
    for s in np.argsort(-cnt) + 1:
        k = int(np.argmax(p * tot - acc)); m[s] = order_let[k]; acc[k] += cnt[s - 1]
    return m   # values 0..NV-1 (single sounds have value index = sound index - 1)


def value_probs(lms):
    u = pooled_unigram(lms)[1:] ** 0.5; u = u / u.sum()
    w = np.concatenate([u, np.full(len(CLUSTERS), u.mean() * 0.5)])
    return w / w.sum()


def anneal(sc, m0, fixed, pv, iters, rng):
    free = [s for s in range(1, NSIGN + 1) if s not in fixed]
    m = m0.copy(); cur = sc(m); best, best_m = cur, m.copy()
    if not free:
        return best_m, best
    T = max(1.0, 0.03 * sc.st.n_signs); ratio = (0.05 / T) ** (1.0 / iters); cum = np.cumsum(pv)
    for _ in range(iters):
        c = m.copy()
        if rng.random() < 0.3 and len(free) > 1:
            i, j = rng.choice(free, 2, replace=False)
            if m[i] == m[j]:
                T *= ratio; continue
            c[i], c[j] = m[j], m[i]
        else:
            i = free[int(rng.integers(len(free)))]; v = int(np.searchsorted(cum, rng.random() * cum[-1]))
            if v == m[i]:
                T *= ratio; continue
            c[i] = v
        s = sc(c); d = s - cur
        if d >= 0 or rng.random() < np.exp(d / T):
            m, cur = c, s
            if cur > best:
                best, best_m = cur, m.copy()
        T *= ratio
    return best_m, best


# ------------------------------------------------------------------ stage 1 (anchor)
def candidates(book, train_idx, mat):
    """page -> list of partial keys {sign: value} making one page word read as own-sign material"""
    byp = defaultdict(set)
    for i in train_idx:
        p, _, ws = book[i]
        if p in ZTRAIN:
            byp[p] |= {w for w in ws if len(w) >= MIN_MAT}
    cand = {}
    for p in ZTRAIN:
        sign = CON["pages"][p]; cs = set()
        for w in byp[p]:
            for t in mat[sign]:
                if len(t) != len(w):
                    continue
                m = {}; ok = True
                for u, c in zip(w, t):
                    if m.setdefault(u, c - 1) != c - 1:
                        ok = False; break
                if ok:
                    cs.add(tuple(sorted(m.items())))
        cand[p] = sorted(cs)
    return cand


def bigram_logp(lms):
    B = np.zeros((A, A))
    for lm in lms:
        P = np.exp(lm.flat.reshape(A, A, A, A)[0, 0])          # P(b | space space a) as a bigram proxy
        B += P
    return np.log(B / len(lms))


def prescreen(keys, C, LB):
    out = []
    for k in keys:
        mm = np.full(NSIGN + 1, -1); mm[0] = 0
        for u, v in k.items():
            mm[u] = v + 1
        ok = mm >= 0; sub = C[np.ix_(ok, ok)]; x = mm[ok]
        out.append(float((sub * LB[np.ix_(x, x)]).sum() / max(1.0, sub.sum())))
    return out


def stage1(cand, C, LB, rng):
    pages = [p for p in ZTRAIN if cand[p]]; found = {}
    for _ in range(R1):
        rng.shuffle(pages); key = {}; cov = 0
        for p in pages:
            opts = [o for o in cand[p] if all(key.get(u, v) == v for u, v in o)]
            if not opts:
                continue
            if len(opts) > 1:
                sc = prescreen([{**key, **dict(o)} for o in opts], C, LB)
                pick = opts[rng.choice(list(np.argsort(sc)[::-1][:TOP_CHOICE]))]
            else:
                pick = opts[0]
            key.update(dict(pick)); cov += 1
        fk = tuple(sorted(key.items())); found[fk] = max(found.get(fk, 0), cov)
    if not found or max(found.values()) == 0:
        return [], 0
    best = max(found.values()); keys = [dict(k) for k, c in found.items() if c >= best - 1]
    sc = prescreen(keys, C, LB)
    return [keys[i] for i in np.argsort(sc)[::-1][:N_KEYS]], best


# ------------------------------------------------------------------ evaluation
def dec_word(m, w):
    return tuple(x for u in w for x in VALS[m[u]])


def evaluate(book, held_idx, train_idx, m, lms, mat):
    lines_w = [book[i][2] for i in held_idx]
    sc = Scorer(Stream(lines_w), lms); _, a = sc(m, detail=True)
    hit = tot = 0; types = {}
    for li, ws in enumerate(lines_w):
        vocab = lms[a[li]].vocab
        for w in ws:
            d = dec_word(m, w)
            if len(d) >= 3:
                tot += 1; hit += d in vocab; types[(a[li], d)] = d in vocab
    lex = hit / max(1, tot); lex_types = sum(types.values()) / max(1, len(types))
    seen = {w for i in train_idx if book[i][0] in ZTRAIN for w in book[i][2]}
    pw = {p: set() for p in ZHELD}
    for i in held_idx:
        p = book[i][0]
        if p in ZHELD:
            pw[p] |= {w for w in book[i][2] if w not in seen and len(w) >= MIN_MAT}
    signs = [CON["pages"][p] for p in ZHELD]
    hitm = np.array([[any(dec_word(m, w) in mat[s] for w in pw[p]) for s in signs] for p in ZHELD])
    obs = int(np.trace(hitm))
    perms = list(itertools.permutations(range(len(ZHELD))))
    null = [int(sum(hitm[i, pi[i]] for i in range(len(ZHELD)))) for pi in perms]
    pz = sum(n >= obs for n in null) / len(perms)
    hits = {p: [(VNAME and "".join(SOUNDS[x - 1] for x in dec_word(m, w)), mat[CON["pages"][p]][dec_word(m, w)][:3])
                for w in pw[p] if dec_word(m, w) in mat[CON["pages"][p]]] for p in ZHELD}
    langs = Counter(LANGS[x] for x in a)
    return {"lexrate": lex, "lexrate_types": lex_types, "zodiac_pages_hit": obs, "zodiac_p": pz, "line_languages": dict(langs.most_common()),
            "zodiac_hits": hits}


def accuracy(book, held_idx, m, true_key):
    ok = tot = 0
    for i in held_idx:
        for w in book[i][2]:
            for u in w:
                tot += 1; ok += (m[u] == true_key[u])
    return ok / max(1, tot)


# ------------------------------------------------------------------ fitting one book
_ST = {}


def _init(state):
    _ST.update(state)


def job(args):
    """one stage-2 start on one book: returns (book, start id, objective, key)"""
    bname, sid, fixed, seed = args
    st = _ST["books"][bname]; lms = _ST["lms"]
    sc = Scorer(st["train_stream"], lms); rng = np.random.default_rng(seed)
    m0 = free_init(st["train_stream"], lms)
    for u, v in fixed.items():
        m0[int(u)] = v
    pv = value_probs(lms); best = (-1e18, None); r2, it2, _, _ = _ST["budget"]
    for _ in range(r2):
        m, s = anneal(sc, m0, {int(u) for u in fixed}, pv, it2, rng)
        if s > best[0]:
            best = (s, m)
    return bname, sid, best[0], best[1].tolist()


def per_line(sc, m):
    let, line, scd = sc.decode(m)
    f = let[:-3] * A ** 3 + let[1:-2] * A ** 2 + let[2:-1] * A + let[3:]; k = scd[3:]; f = f[k]; ln = line[3:][k]
    starts = np.searchsorted(ln, np.arange(sc.st.n_lines)); n = np.diff(np.append(starts, len(f)))
    return np.add.reduceat(sc.FL[:, f], starts, axis=1).max(axis=0) / n


def refit(args):
    """mixed-language trap breaker: ROUNDS times, the worse-read half of the lines is re-fitted from scratch under
    each single language model in turn (IT_SUB steps), then the whole key is re-annealed on all lines with all models
    (IT_SUB steps); the best candidate replaces the key if its objective is higher"""
    bname, m, seed = args
    st = _ST["books"][bname]["train_stream"]; lms = _ST["lms"]; lines = _ST["books"][bname]["train_lines"]
    sc = Scorer(st, lms); rng = np.random.default_rng(seed); m = np.array(m); cur = sc(m)
    _, _, rounds, it_sub = _ST["budget"]
    for _ in range(rounds):
        pl = per_line(sc, m); bad = [lines[i] for i in np.argsort(pl)[:len(pl) // 2]]
        sb = Stream(bad); best = (cur, m)
        for lm in lms:
            m1, _ = anneal(Scorer(sb, [lm]), free_init(sb, [lm]), set(), value_probs([lm]), it_sub, rng)
            m2, o = anneal(sc, m1, set(), value_probs(lms), it_sub, rng)
            if o > best[0]:
                best = (o, m2)
        cur, m = best
    return bname, cur, m.tolist()


# ------------------------------------------------------------------ synthetic books
def make_key(plain_lines, rng):
    """true key for a known answer: 2 shorthand signs for the 2 commonest clusters, >= 1 sign per kept sound, spare
    signs homophones of the commonest sounds; returns key (sign -> value), encoder table, kept sounds"""
    cc = Counter(); sc = Counter()
    for ws in plain_lines:
        for w in ws:
            sc.update(w); s = "".join(SOUNDS[x - 1] for x in w)
            for k, cl in enumerate(CLUSTERS):
                cc[k] += s.count(cl)
    clus = [k for k, _ in cc.most_common(2)]
    kept = [s for s, _ in sc.most_common(NSIGN - 2)]
    signs = list(range(1, NSIGN + 1)); rng.shuffle(signs)
    key = np.zeros(NSIGN + 1, dtype=np.int64); enc = defaultdict(list); i = 0
    for k in clus:
        key[signs[i]] = len(SOUNDS) + k; enc[("C", k)].append(signs[i]); i += 1
    for s in kept[:NSIGN - i]:
        key[signs[i]] = s - 1; enc[s].append(signs[i]); i += 1
    while i < NSIGN:
        s = max(kept, key=lambda x: sc[x] / len(enc[x])); key[signs[i]] = s - 1; enc[s].append(signs[i]); i += 1
    return key, enc, set(kept), clus


def encode_word(w, enc, kept, clus, sw, rng, slip=True):
    s = [x for x in w if x in kept]; out = []; j = 0
    while j < len(s):
        done = False
        for k in clus:
            cl = VALS[len(SOUNDS) + k]
            if tuple(s[j:j + len(cl)]) == cl and rng.random() < P_ABBR:
                out.append(rng.choice(enc[("C", k)])); j += len(cl); done = True; break
        if not done:
            out.append(rng.choice(enc[s[j]])); j += 1
    if slip and out and rng.random() < LT:
        op = rng.choices(("sub", "ins", "del"), (2, 1, 1))[0]
        if op == "del" and len(out) < 2:
            op = "sub"
        i = rng.randrange(len(out) + (op == "ins")); x = rng.choices(range(1, NSIGN + 1), sw)[0]
        if op == "sub":
            out[i] = x
        elif op == "ins":
            out.insert(i, x)
        else:
            del out[i]
    return tuple(out)


def known_answer(book, mix, held, mat, sw, rng):
    """synthetic book with the Voynich line structure: plaintext from held-out text of the languages in `mix`
    ({lang: share}), language blocks of BLOCK lines; every zodiac page gets one planted own-sign material word in
    one of its languages (or a star name)"""
    pos = {l: rng.randrange(0, max(1, len(held[l]) // 3)) for l in mix}
    langs = list(mix); w = [mix[l] for l in langs]
    plain, line_lang = [], []
    cur = None
    for li, (p, sh, ws) in enumerate(book):
        if li % BLOCK == 0 or cur is None:
            cur = rng.choices(langs, w)[0]
        out = []
        for _ in ws:
            if pos[cur] >= len(held[cur]):
                pos[cur] = 0
            out.append(held[cur][pos[cur]]); pos[cur] += 1
        plain.append(out); line_lang.append(cur)
    key, enc, kept, clus = make_key(plain, rng)
    cipher = [[encode_word(x, enc, kept, clus, sw, rng) for x in ws] for ws in plain]
    planted = {}
    for p in ORDER:
        li = [i for i, (pp, _, _) in enumerate(book) if pp == p]
        s = CON["pages"][p]
        opts = [t for t, src in mat[s].items() if all(x in kept for x in t) and
                any(r in mix or (r == "greek_rom" and "greek" in mix) or r == "star name" for r, _, _ in src)]
        if not opts or not li:
            continue
        t = rng.choice(sorted(opts)); i = rng.choice(li); j = rng.randrange(len(cipher[i]))
        cipher[i][j] = encode_word(t, enc, kept, clus, sw, rng, slip=False); planted[p] = t
    cipher = [[x if x else (1,) for x in ws] for ws in cipher]
    return [(p, sh, cipher[i]) for i, (p, sh, _) in enumerate(book)], key, planted


def generator_book(book, rng, plant_train=None, mat=None, enc_rng=None):
    signs, _ = voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    gen = []
    for s in range(1, 11):
        for ln in (ROOT / f"experiments/results/e032_work/seed{s}/generate/generated_text.txt").read_text().splitlines():
            if ln.startswith("#") or not ln.strip():
                continue
            for w in ln.split():
                u = tuple(idx[x] for x in A24.segment(n1(w), A24.SEGS["S3"]) if x in idx)
                if u:
                    gen.append(u)
    n = sum(len(ws) for _, _, ws in book); st = rng.randrange(0, len(gen) - n); out = []
    for p, sh, ws in book:
        out.append((p, sh, gen[st:st + len(ws)])); st += len(ws)
    if plant_train:
        # anchor without meaning: plant on the TRAINING zodiac pages only, with a random key
        key = rng.sample(range(1, NSIGN + 1), NSIGN); inv = {}
        out = [list(x) for x in out]
        for p in ZTRAIN:
            s = CON["pages"][p]; t = rng.choice(sorted(mat[s]))
            word = tuple(inv.setdefault(x, key[(x - 1) % NSIGN]) for x in t)
            li = [i for i, x in enumerate(out) if x[0] == p]; i = rng.choice(li)
            ws = list(out[i][2]); ws[rng.randrange(len(ws))] = word; out[i][2] = ws
        out = [tuple(x) for x in out]
    return out


def shuffled_book(book, rng):
    flat = [u for _, _, ws in book for w in ws for u in w]; rng.shuffle(flat); out = []; k = 0
    for p, sh, ws in book:
        nw = []
        for w in ws:
            nw.append(tuple(flat[k:k + len(w)])); k += len(w)
        out.append((p, sh, nw))
    return out


# ------------------------------------------------------------------ main
def prepare(name, bk, tr, he, mat, lms, rng):
    C = np.zeros((NSIGN + 1, NSIGN + 1))
    st = Stream([bk[i][2] for i in tr])
    np.add.at(C, (st.S[:-1], st.S[1:]), 1)
    cand = candidates(bk, tr, mat)
    keys, cov = stage1(cand, C, _LB, rng)
    return {"train_stream": st, "keys": keys, "coverage": cov, "n_cand": {p: len(v) for p, v in cand.items()}}


_LB = None


def main():
    global _LB
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(); t0 = time.time()
    global R2, IT2, R1, ROUNDS, IT_SUB
    if a.smoke:
        R2, IT2, R1, ROUNDS, IT_SUB = 1, 1500, 300, 1, 800
    rng = random.Random(SEED)
    lmw, held = {}, {}
    for l in LANGS:
        lmw[l], held[l] = corpus(l)
    lms = [SoundLM(lmw[l], l) for l in LANGS]
    for lm in lms:
        lm.H = lm.xent(held[lm.lang])
    info = {l: {"lm_words": len(lmw[l]), "held_words": len(held[l])} for l in LANGS}
    log("corpora", info, f"{time.time() - t0:.0f}s")
    _LB = bigram_logp(lms); mat = material()
    log("material sizes", {s: len(v) for s, v in mat.items()})
    vb = voynich_book(); tr, he = split(vb, rng)
    log(f"voynich lines {len(vb)} train {len(tr)} held {len(he)}")
    _, sw = voynich_signs()
    books, truth = {}, {}
    DEV = {"D1 latin": {"latin": 1}, "D2 catalan+latin": {"catalan": 0.5, "latin": 0.5}}
    TEST = {"T1 italian+hebrew": {"italian": 0.5, "hebrew": 0.5},
            "T2 czech+german+latin": {"czech": 1 / 3, "german": 1 / 3, "latin": 1 / 3},
            "T3 greek+arabic+latin": {"greek": 1 / 3, "arabic": 1 / 3, "latin": 1 / 3},
            "T4 occitan+catalan": {"occitan": 0.25, "catalan": 0.75}}
    for nm, mix in {**DEV, **TEST}.items():
        bk, key, planted = known_answer(vb, mix, held, mat, sw, rng); books[nm] = bk; truth[nm] = (key, planted)
    books["DC1 generator"] = generator_book(vb, rng)
    books["DC2 voynich shuffled"] = shuffled_book(vb, rng)
    books["TC1 generator"] = generator_book(vb, rng)
    books["TC2 voynich shuffled"] = shuffled_book(vb, rng)
    books["TC3 T1 shuffled"] = shuffled_book(books["T1 italian+hebrew"], rng)
    books["TC4 generator, anchor planted"] = generator_book(vb, rng, plant_train=True, mat=mat)
    books["VOYNICH"] = vb
    if a.smoke:
        books = {k: books[k] for k in ("D1 latin", "DC2 voynich shuffled", "TC4 generator, anchor planted")}   # never Voynich
    state = {}
    for nm, bk in books.items():
        state[nm] = prepare(nm, bk, tr, he, mat, lms, rng)
        log(f"stage1 {nm}: coverage {state[nm]['coverage']}/6, keys {len(state[nm]['keys'])}, cand {state[nm]['n_cand']}")
    jobs = []
    for nm in books:
        starts = [{}] + state[nm]["keys"]
        for k, fx in enumerate(starts):
            jobs.append((nm, k, {str(u): int(v) for u, v in fx.items()}, rng.randrange(1 << 30)))
    log(f"jobs {len(jobs)} | {time.time() - t0:.0f}s")
    shared = {"books": {k: {"train_stream": v["train_stream"], "train_lines": [books[k][i][2] for i in tr]}
                        for k, v in state.items()}, "lms": lms, "budget": (R2, IT2, ROUNDS, IT_SUB)}
    with Pool(a.workers, initializer=_init, initargs=(shared,)) as pool:
        res = pool.map(job, jobs, chunksize=1)
        log(f"stage 2 starts done | {time.time() - t0:.0f}s")
        rjobs = []
        for nm in books:
            rs = sorted([r for r in res if r[0] == nm], key=lambda r: -r[2])
            rjobs += [(nm, r[3], rng.randrange(1 << 30)) for r in rs[:TOPB]]
        rres = pool.map(refit, rjobs, chunksize=1)
    out = {"info": info, "seconds": None, "books": {}}
    for nm in books:
        rf = sorted([r for r in rres if r[0] == nm], key=lambda r: -r[1])
        m = np.array(rf[0][2]); m2 = np.array(rf[1][2]) if len(rf) > 1 else m
        ev = evaluate(books[nm], he, tr, m, lms, mat)
        nh = [u for i in he for w in books[nm][i][2] for u in w]
        ev["agreement"] = float(np.mean([m[u] == m2[u] for u in nh]))
        best_start = sorted([r for r in res if r[0] == nm], key=lambda r: -r[2])[0]
        ev["best_start_before_refit"] = "free" if best_start[1] == 0 else f"anchor key {best_start[1]}"
        ev["objective"] = rf[0][1]; ev["objective_before_refit"] = best_start[2]
        ev["stage1_coverage"] = state[nm]["coverage"]
        ev["key"] = {voynich_signs()[0][u - 1]: VNAME[m[u]] for u in range(1, NSIGN + 1)}
        if nm in truth:
            ev["accuracy"] = accuracy(books[nm], he, m, truth[nm][0])
        out["books"][nm] = ev
        log(f"{nm:32s} lex {ev['lexrate']:.3f} zodiac {ev['zodiac_pages_hit']}/6 p {ev['zodiac_p']:.3f} agr {ev['agreement']:.2f}"
            f" acc {ev.get('accuracy', float('nan')):.2f} types {ev['lexrate_types']:.3f} langs {list(ev['line_languages'].items())[:3]}")
    B = out["books"]
    if not a.smoke:
        ka_dev = [B[k] for k in DEV]; ct_dev = [B[k] for k in ("DC1 generator", "DC2 voynich shuffled")]
        cracked = [r["lexrate_types"] for r in ka_dev if r["accuracy"] >= CRACK]
        hi = max(r["lexrate_types"] for r in ct_dev)
        thr = (min(cracked) + hi) / 2 if len(cracked) == len(ka_dev) and min(cracked) > hi else None
        out["threshold"] = thr
        claim = lambda r: thr is not None and r["lexrate_types"] >= thr and r["zodiac_p"] <= 0.05
        for k, r in B.items():
            r["claim"] = bool(claim(r))
        ka_ok = sum(B[k]["claim"] and B[k]["accuracy"] >= CRACK for k in TEST)
        false = [k for k in B if k.startswith(("TC", "DC")) and B[k]["claim"]] + \
                [k for k in TEST if B[k]["claim"] and B[k]["accuracy"] < CRACK]
        valid = thr is not None and ka_ok >= 3 and not false
        out["validation"] = {"threshold": thr, "test_cracks_claimed": ka_ok, "false_claims": false, "valid": valid}
        out["verdict"] = ("VOID (not validated)" if not valid else "CLAIM" if B["VOYNICH"]["claim"] else "NO CLAIM")
        log("validation", out["validation"], "| VERDICT", out["verdict"])
    out["seconds"] = round(time.time() - t0)
    (OUT.with_name("e097_smoke.json") if a.smoke else OUT).write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    log(f"done {out['seconds']}s")


if __name__ == "__main__":
    main()
