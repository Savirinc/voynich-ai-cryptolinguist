"""E050: settle E049's Hebrew near miss. See reports/E050_PREREG.md.
Part 1  null distribution: Voynich A (3 attack seeds) vs 40 controls under the Hebrew LM, all with E047's attack:
        20 pseudo-Voynich-A texts (sign-level order-2 Markov model of A's own cleaned words: same signs, same
        word-shape statistics, no language) and 20 copy-generator samples (E032 seeds, random stretches).
        BEATS ALL = Voynich A's mean lexrate over its 3 seeds > every control's lexrate.
Part 2  blind reading: writes 7 unlabelled passages of 60 decoded words (Hebrew letters, no vowels) to
        experiments/results/e050_passages.json: 3 Voynich A pages (the first three DEV Currier-A folios with >= 60
        words, decoded with the best Voynich key), 3 control passages (the 3 highest-lexrate controls), and 1 positive
        control (real Hebrew from the E047 TEST books, written in a fresh VOY23 key with spelling slips, decoded by the
        same attack). Labels go to e050_labels.json (not printed). Judges are run separately (see the pre-registration).
Run: caffeinate -ims .venv/bin/python experiments/e050_hebrew_nearmiss.py
"""
from __future__ import annotations

import json, random, sys
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

SEED, N_PSEUDO, N_GEN, N_VSEED, PW = 50050, 20, 20, 3, 60
OUT = ROOT / "experiments/results/e050.json"


def voynich_a_by_folio():
    signs, _ = K.voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    _, toks = parse(); locked = set(locked_test_leaves(toks))
    words, folio = [], []
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked and t.is_clean and t.currier == "A":
            u = [idx[x] for x in A24.segment(n1(t.eva), A24.SEGS["S3"]) if x in idx]
            if u:
                words.append(u); folio.append(t.folio)
    return words, folio, sorted(locked)


def markov_pseudo(words, n, rng):
    tr = defaultdict(Counter)
    for w in words:
        s = ["^", "^"] + w + ["$"]
        for a, b, c in zip(s, s[1:], s[2:]):
            tr[(a, b)][c] += 1
    out = []
    while len(out) < n:
        a, b, w = "^", "^", []
        while True:
            ch = tr[(a, b)]; c = rng.choices(list(ch), list(ch.values()))[0]
            if c == "$" or len(w) > 15:
                break
            w.append(c); a, b = b, c
        if w:
            out.append(w)
    return out


def attack_full(task):
    r = K.attack(task)
    name, lml, seqs, labels, seed = task
    lm = K.LMS[lml]
    return r, seqs


def main():
    rng = random.Random(SEED)
    K.LMS["he"] = K.SpaceLM(K.book_words("he", K.LM_BOOKS), "he")
    VA, folio, locked = voynich_a_by_folio()
    tasks = [(f"VOYNICH_A:seed{k}", "he", VA, None, rng.randrange(1 << 30)) for k in range(N_VSEED)]
    for k in range(N_PSEUDO):
        tasks.append((f"CONTROL:pseudo{k}", "he", markov_pseudo(VA, len(VA), rng), None, rng.randrange(1 << 30)))
    for k in range(N_GEN):
        tasks.append((f"CONTROL:generator{k}", "he", K.gibberish_streams(len(VA), rng), None, rng.randrange(1 << 30)))
    # positive control for the blind reading: real Hebrew in a fresh VOY23 key
    _, sw = K.voynich_signs()
    hw = K.keep_letters(K.book_words("he", K.TEST_BOOKS), K.LMS["he"].letters)
    st = rng.randrange(0, len(hw) - len(VA)); freq = Counter(c for w in hw for c in w)
    key = K.make_key(K.LMS["he"].letters, freq, rng)
    pos_seqs, pos_lab = K.encode(hw[st:st + len(VA)], key, sw, rng)
    tasks.append(("POSITIVE:hebrew", "he", pos_seqs, pos_lab, rng.randrange(1 << 30)))
    with Pool(3, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    V = [r for r in res if r["name"].startswith("VOYNICH")]; C = [r for r in res if r["name"].startswith("CONTROL")]
    vmean = float(np.mean([r["lexrate"] for r in V])); cmax = max(r["lexrate"] for r in C)
    beats = vmean > cmax
    part1 = "VOYNICH A BEATS ALL 40 CONTROLS" if beats else "VOYNICH A DOES NOT BEAT ALL CONTROLS"
    print(f"Voynich A lexrate per seed {[round(r['lexrate'], 3) for r in V]} mean {vmean:.3f}; agreement {[round(r['agreement'], 3) for r in V]}")
    for kind in ("pseudo", "generator"):
        xs = sorted(r["lexrate"] for r in C if kind in r["name"])
        print(f"  {kind:9s} controls: min {xs[0]:.3f} median {np.median(xs):.3f} max {xs[-1]:.3f}")
    pos = [r for r in res if r["name"].startswith("POSITIVE")][0]
    print(f"  positive control (real Hebrew, VOY23): lexrate {pos['lexrate']:.3f} accuracy {pos['accuracy']:.3f}")
    print("PART 1:", part1)
    # Part 2 passages
    best = max(V, key=lambda r: r["score"])
    seen, pages = [], []
    for f in folio:
        if f not in seen:
            seen.append(f)
    for f in seen:
        ids = [i for i, x in enumerate(folio) if x == f]
        if len(ids) >= PW:
            pages.append((f, [best["decoded"][i] for i in ids[:PW]]))
        if len(pages) == 3:
            break
    top3 = sorted(C, key=lambda r: -r["lexrate"])[:3]
    passages = [("voynich:" + f, " ".join(w)) for f, w in pages]
    passages += [("control:" + r["name"], " ".join(r["decoded"][:PW])) for r in top3]
    passages += [("positive", " ".join(pos["decoded"][:PW]))]
    order = list(range(len(passages))); random.Random(SEED + 7).shuffle(order)
    shown = [{"id": chr(65 + k), "text": passages[i][1]} for k, i in enumerate(order)]
    labels = {chr(65 + k): passages[i][0] for k, i in enumerate(order)}
    (ROOT / "experiments/results/e050_passages.json").write_text(json.dumps(shown, indent=1, ensure_ascii=False))
    (ROOT / "experiments/results/e050_labels.json").write_text(json.dumps(labels, indent=1))
    for r in res:
        r.pop("decoded", None)
    OUT.write_text(json.dumps({"experiment": "E050", "results": res, "voynich_mean_lexrate": vmean,
                               "max_control_lexrate": cmax, "part1": part1, "locked_test_excluded": locked},
                              indent=1, ensure_ascii=False))
    print("Part 2 passages written (labels hidden).")


def decode_task(task):
    """K.attack plus the full decoded word list and the best objective."""
    import numpy as np  # noqa: F811
    name, lml, seqs, labels, seed = task
    lm = K.LMS[lml]
    seq = []
    for u in seqs:
        seq += u + [0]
    seq = np.array(seq[:-1], dtype=np.int64)
    sc = K.FullScorer(seq, lm)
    p = lm.unigram[1:] ** 0.5; p = p / p.sum()
    rng = np.random.default_rng(seed)
    m0 = K.freq_init(seq, K.NSIGN, lm, injective=False)
    t0 = max(1.0, 0.03 * len(seq))
    runs = [K.anneal_full(sc, m0, p, K.ITERS, rng, t0=t0) for _ in range(K.RESTARTS)]
    runs.sort(key=lambda x: -x[1])
    best = runs[0][0]; nz = seq[seq > 0]
    agree = max(float(np.mean(m[nz] == best[nz])) for m, _ in runs[1:])
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
    return {"name": name, "lm": lml, "agreement": agree, "lexrate": lexrate, "accuracy": acc,
            "score": float(runs[0][1]), "decoded": dec}


if __name__ == "__main__":
    main()
