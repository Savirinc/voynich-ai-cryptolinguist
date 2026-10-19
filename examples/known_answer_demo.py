"""Known-answer demo: encrypt a text with a fresh secret key, attack it, and apply the claim rule.

Uses the same cipher class, attack and claim rule as E017 (verbose homophonic cipher with Greshko's published
Naibbe tables, context-dependent spelling and nulls; attack_portfolio; CLAIM iff agreement >= 0.95 and >= 8% of
decoded letters covered by dictionary words of 7-14 letters). With --cipher it attacks YOUR word list instead and
reports the claim statistics (no accuracy, since there is no answer key).

  .venv/bin/python examples/known_answer_demo.py                      # Latin tune text, 16 restarts
  .venv/bin/python examples/known_answer_demo.py --text my.txt --lang it --letters 20000
  .venv/bin/python examples/known_answer_demo.py --cipher my_cipher_words.txt --lang la
  .venv/bin/python examples/known_answer_demo.py --control rugg       # a meaningless control: should NOT claim
  .venv/bin/python examples/known_answer_demo.py --cipher my_cipher_words.txt --lm-text my_corpus.txt
                                                                      # score against YOUR language corpus

Full E017 budget is --restarts 128 (about 10-20 min per attack on a laptop); 16 restarts usually suffices for a
40k-letter Latin or Italian text, but the agreement statistic is then based on fewer restarts.
"""
from __future__ import annotations

import argparse, json, random, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from vcl.solvers import verbose as V  # noqa: E402
from vcl.solvers.lm import get_lm  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

AGREE_MIN, LEX_MIN, LEX_LEN = 0.95, 0.08, 7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="la", help="plaintext / LM language (la, it, fr, de, ...)")
    ap.add_argument("--text", help="your own plaintext file (default: the benchmark's 'tune' text)")
    ap.add_argument("--cipher", help="attack this file of whitespace-separated EVA-like words instead")
    ap.add_argument("--control", choices=["rugg", "shufchar"], help="encrypt a meaningless control instead")
    ap.add_argument("--lm-text", help="build the language model (and long-word dictionary) from this corpus file")
    ap.add_argument("--letters", type=int, default=40_000)
    ap.add_argument("--restarts", type=int, default=16)
    ap.add_argument("--iters", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=random.SystemRandom().randrange(10**6))
    a = ap.parse_args()

    lines, _, dev_words, _ = E.voynich_lines()          # DEV leaves only (LOCKED_TEST excluded)
    C, nulls = X.coupling_matrix(lines), R.null_pool(dev_words)
    labels = None
    if a.cipher:
        words = Path(a.cipher).read_text().split()
    elif a.control == "rugg":
        p = R.random_params("rugg_rep", random.Random(a.seed))
        g = R.generate("rugg_rep", p, a.seed, T.chunk_pools(dev_words), int(a.letters / 1.5), C, nulls)
        words = [w for l in g["lines"] for w in l]
    else:
        if a.text:
            text = NX.clean(Path(a.text).read_text(errors="ignore"))
        else:
            roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
            books = [b | {"role": roles.get(b["id"], {}).get("role")} for b in load_books() if b["lang"] == a.lang]
            text = NX.clean(" ".join(c[2] for c in E.plain_chunks(books, a.lang, "tune", size=24000, step=24000)))
        text = text[:a.letters]
        if a.control == "shufchar":
            t = list(text); random.Random(a.seed).shuffle(t); text = "".join(t)
        key = V.random_key(a.seed)
        enc, labs = V.encode_labelled(text, key, C, nulls, seed=a.seed + 1)
        words, labels = [w for l in enc for w in l], [x for l in labs for x in l]
    print(f"{len(words)} cipher words; e.g. {' '.join(words[:12])}", flush=True)
    if a.lm_text:
        from vcl.solvers.fast_anneal import lm_from_text
        corpus = Path(a.lm_text).read_text(errors="ignore")
        lm = lm_from_text(corpus, Path(a.lm_text).stem)
        vocab = {w for w in (NX.clean(x) for x in corpus.split()) if w}
    else:
        lm, vocab = get_lm(a.lang, "nospace"), {NX.clean(w) for w in get_lm(a.lang, "space").vocab}
    t0 = time.time()
    r = V.attack_portfolio(words, lm, iters=a.iters, restarts=a.restarts, seed=a.seed)
    dec = NX.clean("".join(r["decoded_words"]))
    lex = V.lexical_coverage(dec, vocab, min_len=LEX_LEN)
    claim = r["agreement"] >= AGREE_MIN and lex >= LEX_MIN
    print(f"decoded (first 200 letters): {dec[:200]}")
    if labels:
        print(f"letter accuracy vs the hidden answer: {V.char_accuracy(r['decoded_words'], labels):.3f}")
    print(f"agreement {r['agreement']:.3f} (need >= {AGREE_MIN}); long-word coverage {lex:.3f} (need >= {LEX_MIN}); "
          f"unparsed words {r['n_unparsed']}")
    print(f"VERDICT: {'CLAIM' if claim else 'NO CLAIM'}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
