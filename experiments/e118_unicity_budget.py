"""E118 (Arham, move 4): can any attack of a given cipher class work at Voynich length? See reports/E118_PREREG.md.
Known answers only: the Voynich is NOT decoded (only its sign inventory and frequencies, exactly as E047).

Part A, K1 = VOY23 letter cipher (E047 class: many-to-one homophones over 23 Voynich-A signs, 12% spelling slips; E047
attack unchanged: 32 restarts x 30,000 steps, 4-gram KN LM from disjoint books of the same Bible).
  Ladder of lengths LADDER (words); 4 keys x 3 languages (he, tr, la) per length, TEST books, fresh keys.
  CRACK = letter accuracy >= 0.80. SPURIOUS = a restart whose score >= the TRUE key's score but accuracy < 0.80
  (a wrong key that fits as well as the right one: Shannon's equivocation, below unicity).
  U1 = shortest ladder length with >= 9/12 cracks.
Part B, K3 = whole-word code (one plaintext word <-> one code word, one-to-one; the most favourable code for an attacker).
  Plain: 28,841 consecutive TEST-book tokens (Voynich DEV length); LM: word bigram (absolute discounting 0.75) from the
  LM books, top VP types, then every top-M plaintext word the LM lacks appended with zero count (favours the attacker:
  the true key is always representable), + UNK. Attack: annealing over the top M code types (rest -> UNK in every key),
  frequency-rank start (restarts 2-4 jittered), rank-local proposals, T0 200 -> 0.5, 4 restarts x STEPS.
  Accuracy = share of ALL tokens decoded to the true word.
  SPURIOUS = best found key scores >= the true key. ORACLE DRIFT = a gentle search (T0 5, 5M steps) started AT the
  true key ends scoring >= the true key with accuracy more than 0.10 below it.
  Two models: 'disjoint' (the honest one, used for the verdict) and 'in-sample' (LM = the plaintext itself, a
  perfect-knowledge bound, unscored; its rank start is already the true key, so only its oracle probe is informative).
Decision (pre-registered; no ledger factor, this is a budget, except the K1 branch marked *):
  K1  DECIDABLE-WITH-MARGIN  U1 <= 4,400 words (half of Voynich A)
      DECIDABLE-TIGHT        U1 = 8,806 (Voynich A length)
      UNDECIDABLE*           no ladder length reaches 9/12 -> letter-attack absence factors withdrawn by amendment
  K3  DECIDABLE              accuracy >= 0.50 in >= 2 of 3 languages
      UNDECIDABLE            accuracy < 0.50 in all 3 and (SPURIOUS or ORACLE DRIFT) in >= 2 of 3 (wrong keys fit as well as the true one)
      SEARCH-LIMITED         otherwise (the true key scores best but the search did not find it)
  An UNDECIDABLE class is retired from statistical attack; past absence results never applied to it.
Unscored: Shannon's formula U = H(K) / D per class with D measured from the LM; generator-stream agreement per length.
Run: caffeinate -ims .venv/bin/python experiments/e118_unicity_budget.py [--smoke]
"""
from __future__ import annotations

import argparse, json, math, os, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from vcl.solvers.engine import freq_init  # noqa: E402

SEED = 118118
OUT = ROOT / "experiments/results/e118.json"
LADDER = [125, 250, 500, 1000, 2000, 4400, 8806]
N_KEYS, CRACK_N = 4, 9
N_TOK, VP, M, B_RESTARTS, STEPS = 28841, 4000, 1000, 4, 20_000_000
T0_FREE, T0_ORACLE, ORACLE_STEPS = 200.0, 5.0, 5_000_000
log = K.log if hasattr(K, "log") else (lambda *a: print(*a, flush=True))


# ------------------------------------------------------------------ part A
def attack_k1(task):
    name, lang, seqs, labels, key, seed = task
    lm = K.LMS[lang]
    seq = []
    for u in seqs:
        seq += u + [0]
    seq = np.array(seq[:-1], dtype=np.int64)
    sc = K.FullScorer(seq, lm)
    p = lm.unigram[1:] ** 0.5; p = p / p.sum()
    rng = np.random.default_rng(seed)
    m0 = freq_init(seq, K.NSIGN, lm, injective=False)
    t0 = max(1.0, 0.03 * len(seq))
    mt = np.zeros(K.NSIGN + 1, dtype=np.int64)
    if key is not None:
        for l, ss in key.items():
            for s in ss:
                mt[s] = lm.idx[l]
    true_s = sc(mt) if key is not None else None
    alpha = np.array(lm.alphabet)

    def acc(m):
        if labels is None:
            return None
        ok = tot = 0
        for u, lab in zip(seqs, labels):
            if lab is not None:
                d = "".join(alpha[m[np.array(u)]])
                if len(d) == len(lab):
                    ok += sum(a == b for a, b in zip(d, lab)); tot += len(lab)
        return ok / tot if tot else 0.0
    runs = []
    for _ in range(K.RESTARTS):
        m, s = K.anneal_full(sc, m0, p, K.ITERS, rng, t0=t0)
        runs.append((s, m))
    runs.sort(key=lambda x: -x[0])
    nz = seq[seq > 0]; best = runs[0][1]
    agree = max(float(np.mean(m[nz] == best[nz])) for _, m in runs[1:])
    accs = [acc(m) for _, m in runs]
    spurious = None if key is None else sum(s >= true_s and a < K.ACC_CRACK for (s, _), a in zip(runs, accs))
    return {"name": name, "lang": lang, "n_words": len(seqs), "accuracy": accs[0], "agreement": agree,
            "true_score": true_s, "best_score": runs[0][0], "spurious_restarts": spurious}


def part_a(pool, plain, rng):
    signs, sw = K.voynich_signs()
    tasks = []
    for n in LADDER:
        for lang in K.LANGS:
            words = plain[lang]; letters = K.LMS[lang].letters; freq = Counter(c for w in words for c in w)
            for k in range(N_KEYS):
                st = rng.randrange(0, len(words) - n); key = K.make_key(letters, freq, rng)
                seqs, labels = K.encode(words[st:st + n], key, sw, rng)
                tasks.append((f"A:{n}:{lang}:key{k}", lang, seqs, labels, key, rng.randrange(1 << 30)))
        g = K.gibberish_streams(n, rng)
        tasks.append((f"A:{n}:generator", "la", g, None, None, rng.randrange(1 << 30)))
    tasks.sort(key=lambda t: -t[2].__len__())          # longest first for load balance
    R = pool.map(attack_k1, tasks)
    for r in sorted(R, key=lambda r: (r["n_words"], r["name"])):
        log(f"{r['name']:24s} acc {r['accuracy'] if r['accuracy'] is None else round(r['accuracy'], 3)} agree {r['agreement']:.3f} spurious {r['spurious_restarts']}")
    summ = {}
    for n in LADDER:
        rs = [r for r in R if r["n_words"] == n and r["accuracy"] is not None]
        summ[n] = {"cracks": sum(r["accuracy"] >= K.ACC_CRACK for r in rs), "of": len(rs),
                   "spurious_texts": sum((r["spurious_restarts"] or 0) > 0 for r in rs),
                   "generator_agreement": [r["agreement"] for r in R if r["n_words"] == n and r["accuracy"] is None]}
    ok = [n for n in LADDER if summ[n]["cracks"] >= CRACK_N]
    U1 = min(ok) if ok else None
    v = ("UNDECIDABLE" if U1 is None else "DECIDABLE-WITH-MARGIN" if U1 <= 4400 else "DECIDABLE-TIGHT")
    return {"results": R, "summary": summ, "U1": U1, "verdict": v}


# ------------------------------------------------------------------ part B
class WordLM:
    """types = the LM books' top VP words, then (favouring the attacker) every keyed plaintext word the LM books lack,
    appended at the end with zero count, so the true key is always representable; UNK = len(types)"""
    def __init__(self, words, extra=()):
        c = Counter(words); self.types = [w for w, _ in c.most_common(VP)]
        have = set(self.types); self.types += [w for w in extra if w not in have]
        self.id = {w: i for i, w in enumerate(self.types)}; U = self.U = len(self.types)
        ids = np.array([self.id.get(w, U) for w in words])
        n = U + 1
        big = np.zeros((n, n), dtype=np.float64)
        np.add.at(big, (ids[:-1], ids[1:]), 1.0)
        uni = np.bincount(ids, minlength=n).astype(float) + 0.5; uni /= uni.sum()
        rows = big.sum(1, keepdims=True); types_after = (big > 0).sum(1, keepdims=True)
        lam = np.where(rows > 0, 0.75 * types_after / np.maximum(rows, 1), 1.0)
        P = np.where(rows > 0, np.maximum(big - 0.75, 0) / np.maximum(rows, 1), 0.0) + lam * uni[None, :]
        self.B = np.log(P).astype(np.float32); self.uni = uni


def attack_k3(task):
    lang, lm_words, plain, seed, steps, restarts, model = task
    if model == "in-sample":                      # the perfect-knowledge bound: the LM is the plaintext itself
        lm_words = plain
    rng = np.random.default_rng(seed)
    ctypes = [w for w, _ in Counter(plain).most_common()]          # code type id = frequency rank of its plaintext word
    cid = {w: i for i, w in enumerate(ctypes)}
    c = np.array([cid[w] for w in plain])
    top = min(M, len(ctypes))
    lm = WordLM(lm_words, ctypes[:top]); U = lm.U; NV = U
    pos = [np.nonzero(c == a)[0] for a in range(top)]
    truth_plain = np.array([lm.id.get(w, U) for w in plain])
    true_map = np.array([lm.id.get(ctypes[a], U) for a in range(top)])

    def decode(mp):
        d = np.full(len(c), U); sel = c < top; d[sel] = mp[c[sel]]; return d

    def score(d):
        return float(lm.B[d[:-1], d[1:]].sum())

    def acc(d):
        return float(np.mean(d == np.where(truth_plain == U, -1, truth_plain)))
    # the true key must be one-to-one; duplicates impossible since ctypes are distinct words
    true_d = decode(true_map); true_s = score(true_d)
    ceiling = float(np.mean((truth_plain != U) & (c < top)))
    def search(mp, T0, steps):
        mp = mp.astype(np.int64).copy()
        owner = np.full(NV + 1, -1, dtype=np.int64); real = mp < U; owner[mp[real]] = np.arange(top)[real]
        d = decode(mp); cur = score(d)
        T1 = 0.5; ratio = (T1 / T0) ** (1 / steps); T = T0
        A = rng.integers(0, top, steps); Z = rng.normal(0, 0.7, steps); Ru = rng.random(steps)
        for it in range(steps):
            a = int(A[it]); q = int(min(NV - 1, max(0, round((a + 1) * math.exp(Z[it])) - 1)))
            if q == mp[a]:
                T *= ratio; continue
            b = int(owner[q])
            P_ = pos[a] if b < 0 else np.concatenate([pos[a], pos[b]])
            J = np.unique(np.concatenate([P_ - 1, P_])); J = J[(J >= 0) & (J < len(c) - 1)]
            old = float(lm.B[d[J], d[J + 1]].sum())
            pa = mp[a]
            d[pos[a]] = q
            if b >= 0:
                d[pos[b]] = pa
            new = float(lm.B[d[J], d[J + 1]].sum()); delta = new - old
            if delta >= 0 or Ru[it] < math.exp(delta / T):
                cur += delta; mp[a] = q; owner[q] = a
                if b >= 0:
                    mp[b] = pa; owner[pa] = b
                else:
                    owner[pa] = -1
            else:
                d[pos[a]] = pa
                if b >= 0:
                    d[pos[b]] = q
            T *= ratio
        return score(d), acc(d), d.copy()
    runs = [search(np.arange(top) if r == 0 else np.array(sorted(range(top), key=lambda i: i * math.exp(rng.normal(0, 0.3)))),
                   T0_FREE, steps) for r in range(restarts)]
    # oracle probe: start AT the true key, search gently; does it drift to wrong keys that score at least as well?
    o_s, o_a, _ = search(true_map, T0_ORACLE, ORACLE_STEPS)
    assert (true_map < U).all()
    runs.sort(key=lambda x: -x[0])
    agree = float(np.mean(runs[0][2] == runs[1][2]))
    base = acc(decode(np.arange(top)))
    return {"lang": lang, "model": model, "accuracy": runs[0][1], "restart_accuracies": [x[1] for x in runs], "agreement": agree,
            "true_score": true_s, "best_score": runs[0][0], "spurious": runs[0][0] >= true_s,
            "oracle_score": o_s, "oracle_accuracy": o_a, "true_accuracy": acc(true_d),
            "oracle_drift": bool(o_s >= true_s and o_a < acc(true_d) - 0.10),
            "rank_baseline": base, "ceiling": ceiling, "code_types": len(ctypes),
            "per_word_bits_true": -true_s / (len(c) - 1) / math.log(2)}


def part_b(pool, rng, smoke):
    tasks = []
    for lang in K.LANGS:
        lw = K.book_words(lang, K.LM_BOOKS); tw = K.book_words(lang, K.TEST_BOOKS)
        st = rng.randrange(0, len(tw) - N_TOK)
        for model in ("disjoint", "in-sample"):
            tasks.append((lang, lw, tw[st:st + N_TOK], rng.randrange(1 << 30), 200_000 if smoke else STEPS, B_RESTARTS, model))
    R = pool.map(attack_k3, tasks[:2] if smoke else tasks)
    for r in R:
        log(f"K3 {r['lang']} [{r['model']}]: acc {r['accuracy']:.3f} (restarts {[round(x, 3) for x in r['restart_accuracies']]}, rank baseline "
            f"{r['rank_baseline']:.3f}, ceiling {r['ceiling']:.3f}) | best {r['best_score']:.0f} vs true {r['true_score']:.0f} spurious {r['spurious']} | agree {r['agreement']:.3f}")
    D_ = [r for r in R if r["model"] == "disjoint"]           # the verdict uses the honest (disjoint-book) model only
    n_ok = sum(r["accuracy"] >= 0.5 for r in D_); n_sp = sum(r["spurious"] or r["oracle_drift"] for r in D_)
    v = ("DECIDABLE" if n_ok >= 2 else "UNDECIDABLE" if n_ok == 0 and n_sp >= 2 else "SEARCH-LIMITED")
    return {"results": R, "verdict": v}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    for l in K.LANGS:
        K.LMS[l] = K.SpaceLM(K.book_words(l, K.LM_BOOKS), l)
    plain = {l: K.keep_letters(K.book_words(l, K.TEST_BOOKS), K.LMS[l].letters) for l in K.LANGS}
    res = {"experiment": "E118", "seed": SEED}
    with Pool(3, initializer=K._init, initargs=(K.LMS,)) as pool:
        if a.smoke:
            res["B"] = part_b(pool, rng, True)
            res["runtime_s"] = time.time() - t0
            OUT.with_name("e118_smoke.json").write_text(json.dumps(res, indent=1, default=str)); log(f"smoke done {res['runtime_s']:.0f}s"); return
        res["A"] = part_a(pool, plain, rng)
        log(f"K1 summary {res['A']['summary']} | U1 {res['A']['U1']} | VERDICT K1 {res['A']['verdict']}")
        res["B"] = part_b(pool, rng, False)
        log(f"VERDICT K3 {res['B']['verdict']}")
    res["runtime_s"] = time.time() - t0
    OUT.write_text(json.dumps(res, indent=1, default=str))
    log(f"done {res['runtime_s']:.0f}s")


if __name__ == "__main__":
    main()
