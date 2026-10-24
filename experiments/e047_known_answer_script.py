"""E047 (attack step 3a): known-answer test of a language attack on Voynich-like invented scripts.
See reports/E047_PREREG.md. Voynich is NOT touched (apart from its fixed sign inventory and sign frequencies).

Cipher class "VOY23": a real language, letters folded to at most 23, written word by word (spaces kept) with the 23
commonest Voynich-A signs (cleaned EVA, S3 units). Every letter gets >= 1 sign; spare signs are extra homophones of the
commonest letters (chosen uniformly when writing). Then free spelling variation as E036: each word token, with
probability 0.12, gets one random sign edit (substitute 2 : insert 1 : delete 1, signs drawn by Voynich-A frequency).
Attack: many-to-one annealing (E017 schedule and moves; full re-scoring, FullScorer; word boundaries fixed to space) under a
4-gram Kneser-Ney LM with spaces, built from DISJOINT books of the same Bible; RESTARTS x ITERS; best restart kept.
Signals: agreement (E017 definition) and lexrate = share of decoded word tokens of >= 3 letters found in the LM's
training vocabulary. Accuracy (truth only): share of letters decoded correctly in tokens without a spelling edit.
Stage DEV fixes the lexrate threshold; stage TEST uses fresh texts, keys and seeds.
Run: caffeinate -ims .venv/bin/python experiments/e047_known_answer_script.py [--smoke]
"""
from __future__ import annotations

import argparse, glob, hashlib, json, random, re, sys, time, unicodedata
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e024_atoms as A24  # noqa: E402
from e040_clean_profile import n1  # noqa: E402
from vcl.solvers.engine import NgramTable, freq_init  # noqa: E402
from vcl.solvers.lm import ORDER, _kn_dense  # noqa: E402

SEED = 47047
OUT = ROOT / "experiments/results/e047.json"
BIB = ROOT / "data/external/bibles"
NSIGN, P_VAR, N_WORDS = 23, 0.12, 8806
RESTARTS, ITERS = 32, 30_000
AGREE_MIN, ACC_CRACK = 0.95, 0.80
LANGS = {"he": "hboWLC", "tr": "turytc", "la": "latVUC"}
LM_BOOKS = ["GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "1SA", "2SA", "1KI", "2KI"]
DEV_BOOKS = ["ISA", "JER"]
TEST_BOOKS = ["EZK", "PSA", "PRO", "JOB", "1CH", "2CH"]
FINALS = str.maketrans("ךםןףץ", "כמנפצ")


# ------------------------------------------------------------------ text
def norm(text, lang):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = unicodedata.normalize("NFC", t)
    if lang == "he":
        t = t.translate(FINALS)
    if lang == "tr":
        t = t.replace("ı", "i")
    if lang == "la":
        t = t.replace("æ", "ae").replace("œ", "oe").replace("j", "i").replace("v", "u")
    return re.findall(r"[^\W\d_]+", t)


def book_words(lang, books):
    bid = LANGS[lang]
    fs = sorted(f for f in glob.glob(str(BIB / bid / "txt" / "*_read.txt")) if any(f"_{b}_" in f for b in books))
    out = []
    for f in fs:
        out += norm("\n".join(Path(f).read_text(encoding="utf-8-sig").splitlines()[1:]), lang)
    return out


# ------------------------------------------------------------------ LM with spaces
class SpaceLM:
    def __init__(self, words, lang):
        lc = Counter(c for w in words for c in w if lang != "he" or "\u05d0" <= c <= "\u05ea")
        self.letters = [c for c, _ in lc.most_common(NSIGN)]
        keep = set(self.letters)
        ws = ["".join(c for c in w if c in keep) for w in words]
        ws = [w for w in ws if w]
        self.alphabet = [" "] + self.letters
        self.idx = {c: i for i, c in enumerate(self.alphabet)}
        self.A = len(self.alphabet)
        ids = np.array([self.idx[c] for c in " ".join(ws)], dtype=np.int64)
        logp = _kn_dense(np.concatenate([np.zeros(ORDER - 1, dtype=np.int64), ids]), self.A)
        self.flat = np.asarray(logp).reshape(-1)
        uni = np.bincount(ids, minlength=self.A).astype(float); uni[0] = 0; self.unigram = uni / uni.sum()
        self.vocab = {w for w, c in Counter(ws).items() if len(w) >= 3}
        self.lang = lang


def keep_letters(words, letters):
    keep = set(letters)
    out = ["".join(c for c in w if c in keep) for w in words]
    return [w for w in out if w]


# ------------------------------------------------------------------ cipher
def voynich_signs():
    L, cur, _, _ = E.voynich_lines()
    u = Counter(x for l, c in zip(L, cur) if c == "A" for w in l if w for x in A24.segment(n1(w), A24.SEGS["S3"]))
    top = u.most_common(NSIGN)
    return [s for s, _ in top], np.array([c for _, c in top], float)


def make_key(letters, freq, rng):
    """letters (commonest first), freq dict -> {letter: [sign ids 1..NSIGN]}"""
    signs = list(range(1, NSIGN + 1)); rng.shuffle(signs)
    key = {l: [signs[i]] for i, l in enumerate(letters)}
    for s in signs[len(letters):]:
        l = max(letters, key=lambda x: freq[x] / len(key[x]))
        key[l].append(s)
    return key


def encode(words, key, sign_w, rng):
    seqs, labels = [], []
    for w in words:
        u = [rng.choice(key[c]) for c in w]
        lab = w
        if rng.random() < P_VAR:
            op = rng.choices(("sub", "ins", "del"), (2, 1, 1))[0]
            if op == "del" and len(u) < 2:
                op = "sub"
            i = rng.randrange(len(u) + (op == "ins"))
            s = rng.choices(range(1, NSIGN + 1), sign_w)[0]
            if op == "sub":
                u[i] = s
            elif op == "ins":
                u.insert(i, s)
            else:
                del u[i]
            lab = None
        seqs.append(u); labels.append(lab)
    return seqs, labels


def gibberish_streams(n_words, rng):
    """Copy-generator output (E032 work dir), cleaned and cut into the 23 signs (rarer units dropped)."""
    signs, _ = voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    out = []
    for s in range(1, 11):
        for ln in (ROOT / f"experiments/results/e032_work/seed{s}/generate/generated_text.txt").read_text().splitlines():
            if ln.startswith("#") or not ln.strip():
                continue
            for w in ln.split():
                u = [idx[x] for x in A24.segment(n1(w), A24.SEGS["S3"]) if x in idx]
                if u:
                    out.append(u)
    st = rng.randrange(0, len(out) - n_words)
    return out[st:st + n_words]


def shuffled(seqs, rng):
    flat = [s for u in seqs for s in u]; rng.shuffle(flat)
    out, i = [], 0
    for u in seqs:
        out.append(flat[i:i + len(u)]); i += len(u)
    return out


# ------------------------------------------------------------------ attack
LMS: dict = {}


class FullScorer:
    """Score of a key = sum over the stream's unique padded 4-grams of log P under the LM, minus
    N * KL(decoded letter distribution || LM unigram) (the E017 penalty). Full re-score each step: with only 23 signs
    this is far faster than the delta scorer (whose per-sign row sets cover most rows)."""

    def __init__(self, seq, lm):
        tab = NgramTable(seq)
        self.cols = np.stack(tab.cols); self.counts = tab.counts; self.flat = lm.flat; self.A = lm.A
        self.sym = np.bincount(seq, minlength=NSIGN + 1).astype(float); self.sym[0] = 0; self.N = self.sym.sum()
        self.logp = np.log(np.maximum(lm.unigram, 1e-6))

    def __call__(self, m):
        f = m[self.cols[0]]
        for k in range(1, 4):
            f = f * self.A + m[self.cols[k]]
        lp = float(np.dot(self.flat[f], self.counts))
        q = np.bincount(m, weights=self.sym, minlength=self.A)[1:] / self.N
        nz = q > 0
        return lp - self.N * float((q[nz] * (np.log(q[nz]) - self.logp[1:][nz])).sum())


def anneal_full(sc, m0, p_letters, iters, rng, t0, t1=0.05, p_swap=0.3):
    m = m0.copy(); cur = sc(m); best, best_m = cur, m.copy()
    ratio = (t1 / t0) ** (1.0 / max(iters, 1)); T = t0
    cum = np.cumsum(p_letters); rand = rng.random(iters); kinds = rng.random(iters)
    for it in range(iters):
        c = m.copy()
        if kinds[it] < p_swap:
            i, j = rng.integers(1, NSIGN + 1, size=2)
            if i == j or m[i] == m[j]:
                T *= ratio; continue
            c[i], c[j] = m[j], m[i]
        else:
            i = int(rng.integers(1, NSIGN + 1)); L = 1 + int(np.searchsorted(cum, rng.random() * cum[-1]))
            if L == m[i]:
                T *= ratio; continue
            c[i] = L
        s = sc(c); d = s - cur
        if d >= 0 or rand[it] < np.exp(d / T):
            m, cur = c, s
            if cur > best:
                best, best_m = cur, m.copy()
        T *= ratio
    return best_m, best


def _init(state):
    LMS.update(state)


def attack(task):
    name, lang_lm, seqs, labels, seed = task
    lm = LMS[lang_lm]
    seq = []
    for u in seqs:
        seq += u + [0]
    seq = np.array(seq[:-1], dtype=np.int64)
    sc = FullScorer(seq, lm)
    p = lm.unigram[1:] ** 0.5; p = p / p.sum()
    rng = np.random.default_rng(seed)
    m0 = freq_init(seq, NSIGN, lm, injective=False)
    t0 = max(1.0, 0.03 * len(seq))
    runs = []
    t = time.time()
    for _ in range(RESTARTS):
        m, s = anneal_full(sc, m0, p, ITERS, rng, t0=t0)
        runs.append((s, m))
    runs.sort(key=lambda x: -x[0])
    best = runs[0][1]
    nz = seq[seq > 0]
    agree = max(float(np.mean(m[nz] == best[nz])) for _, m in runs[1:])
    alpha = np.array(lm.alphabet)
    dec = ["".join(alpha[best[np.array(u)]]) for u in seqs]
    toks = [d for d in dec if len(d) >= 3]
    lexrate = sum(d in lm.vocab for d in toks) / max(1, len(toks))
    acc = None
    if labels is not None:
        ok = tot = 0
        for d, lab in zip(dec, labels):
            if lab is not None and len(d) == len(lab):
                ok += sum(a == b for a, b in zip(d, lab)); tot += len(lab)
        acc = ok / tot if tot else 0.0
    return {"name": name, "lm": lang_lm, "agreement": agree, "lexrate": lexrate, "accuracy": acc,
            "seconds": round(time.time() - t, 1), "sample": " ".join(dec[:12])}


# ------------------------------------------------------------------ main
def build_tasks(stage, n_keys, n_ctrl, seed, plain):
    rng = random.Random(seed)
    signs, sw = voynich_signs()
    tasks, truth = [], {}
    for lang in LANGS:
        words = plain[lang]
        letters = LMS[lang].letters
        freq = Counter(c for w in words for c in w)
        for k in range(n_keys):
            st = rng.randrange(0, len(words) - N_WORDS)
            key = make_key(letters, freq, rng)
            seqs, labels = encode(words[st:st + N_WORDS], key, sw, rng)
            name = f"{stage}:{lang}:key{k}"
            truth[name] = lang
            for lml in LANGS:
                tasks.append((name, lml, seqs, labels if lml == lang else None, rng.randrange(1 << 30)))
            if k < n_ctrl:
                sh = shuffled(seqs, rng); cname = f"{stage}:shuffled:{lang}{k}"; truth[cname] = None
                for lml in LANGS:
                    tasks.append((cname, lml, sh, None, rng.randrange(1 << 30)))
    for k in range(n_ctrl):
        g = gibberish_streams(N_WORDS, rng); cname = f"{stage}:generator:{k}"; truth[cname] = None
        for lml in LANGS:
            tasks.append((cname, lml, g, None, rng.randrange(1 << 30)))
    return tasks, truth


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    # --smoke: timing of 3 full-budget attacks on a throw-away DEV cipher; only seconds are printed
    lmw = {l: book_words(l, LM_BOOKS) for l in LANGS}
    for l in LANGS:
        LMS[l] = SpaceLM(lmw[l], l)
    plain = {}
    for stage, books in (("DEV", DEV_BOOKS), ("TEST", TEST_BOOKS)):
        plain[stage] = {l: keep_letters(book_words(l, books), LMS[l].letters) for l in LANGS}
    info = {l: {"letters": LMS[l].letters, "lm_words": len(lmw[l]), "dev_words": len(plain["DEV"][l]),
                "test_words": len(plain["TEST"][l])} for l in LANGS}
    print("letters/sizes:", info, flush=True)
    if a.smoke:
        tasks, _ = build_tasks("SMOKE", 1, 1, SEED + 9, plain["DEV"])
        with Pool(3, initializer=_init, initargs=(LMS,)) as pool:
            r = pool.map(attack, tasks[:3])
        print("smoke timing only:", [(x["name"], x["lm"], x["seconds"]) for x in r]); return
    res = {"info": info}
    with Pool(3, initializer=_init, initargs=(LMS,)) as pool:
        # DEV
        tasks, truth = build_tasks("DEV", 2, 1, SEED + 1, plain["DEV"])
        dev = pool.map(attack, tasks)
        for r in dev:
            print("DEV ", r["name"], r["lm"], {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k in ("agreement", "lexrate", "accuracy")}, flush=True)
        crack = [r for r in dev if r["accuracy"] is not None and r["accuracy"] >= ACC_CRACK]
        non = [r for r in dev if not (r["accuracy"] is not None and r["accuracy"] >= ACC_CRACK)]
        lo = min((r["lexrate"] for r in crack), default=None); hi = max(r["lexrate"] for r in non)
        if lo is None or lo <= hi:
            thr, dev_ok = None, False
        else:
            thr, dev_ok = (lo + hi) / 2, True
        print(f"DEV: cracks {len(crack)}, min crack lexrate {lo}, max non-crack lexrate {hi:.3f} -> threshold {thr}", flush=True)
        res["dev"] = {"results": dev, "truth": truth, "lex_threshold": thr, "separated": dev_ok}
        if not dev_ok:
            res["verdict"] = "NOT VALIDATED (DEV could not separate cracks from non-cracks)"
            OUT.write_text(json.dumps(res, indent=1)); print("VERDICT:", res["verdict"]); return
        # TEST
        tasks, truth = build_tasks("TEST", 3, 2, SEED + 2, plain["TEST"])
        test = pool.map(attack, tasks)
    claim = lambda r: r["agreement"] >= AGREE_MIN and r["lexrate"] >= thr
    for r in test:
        r["claim"] = claim(r)
        print("TEST", r["name"], r["lm"], {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k in ("agreement", "lexrate", "accuracy", "claim")}, flush=True)
    per_lang = {}
    for l in LANGS:
        rs = [r for r in test if truth[r["name"]] == l and r["lm"] == l]
        per_lang[l] = sum(r["claim"] and r["accuracy"] >= ACC_CRACK for r in rs)
    false = [r for r in test if r["claim"] and (truth[r["name"]] != r["lm"] or (r["accuracy"] is not None and r["accuracy"] < ACC_CRACK))]
    ok_crack = all(v >= 2 for v in per_lang.values())
    res["test"] = {"results": test, "truth": truth, "claimed_cracks_per_language": per_lang, "false_claims": [(r["name"], r["lm"]) for r in false]}
    res["verdict"] = ("GO: method validated for VOY23" if ok_crack and not false else
                      "NO-GO: false claims" if false else "NO-GO: too few cracks")
    print("claimed cracks per language (of 3):", per_lang, "| false claims:", len(false)); print("VERDICT:", res["verdict"])
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
