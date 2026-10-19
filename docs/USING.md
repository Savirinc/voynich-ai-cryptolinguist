# Using this toolkit for your own Voynich (or other script) hypothesis

You don't need to agree with our conclusions to use the tools. What we ask is that you follow the same rules:
- validate on known answers first;
- attack controls the same way;
- pre-register;
- publish the result, whatever it is.

All snippets below are run from the repository root. Each one has been checked against the current code.

## 0. Install
```bash
uv venv --python 3.11 .venv && uv pip install -e ".[dev,repro]"
.venv/bin/python -m vcl.synthetic.corpora fetch        # Project Gutenberg plaintexts (hash-verified)
.venv/bin/python -m pytest -q
```

## 1. The fastest way in: the known-answer demo
```bash
.venv/bin/python examples/known_answer_demo.py --lang it                  # encrypt, crack, apply the claim rule
.venv/bin/python examples/known_answer_demo.py --lang it --control rugg   # meaningless control
.venv/bin/python examples/known_answer_demo.py --text my_plain.txt --lang la
.venv/bin/python examples/known_answer_demo.py --cipher my_words.txt --lang la      # attack your own cipher
.venv/bin/python examples/known_answer_demo.py --cipher my_words.txt --lm-text my_corpus.txt
```
Each run reports the restart agreement, the long-word coverage and the verdict. It also reports letter accuracy
when the answer is known.

**Important.** The claim thresholds (agreement ≥ 0.95, long-word coverage ≥ 0.08) were validated in E017 with the
built-in dictionaries. If you use `--lm-text`, a larger dictionary raises long-word coverage for everything,
controls included. So **run `--control rugg` and `--control shufchar` with the same `--lm-text`** and check that
they stay well below your thresholds before trusting a claim.

## 2. The Voynich text (DEV leaves only)
```python
import sys; sys.path[:0] = ["src", "experiments"]
import e011_twin_search as E
lines, currier, dev_words, locked = E.voynich_lines()
# lines: 3,406 prose lines (lists of EVA words; None = unclean token), currier: 'A'/'B' per line,
# dev_words: 28,841 clean prose words, locked: the 15 LOCKED_TEST leaves (excluded, never load them)
```
The parser itself is `vcl.corpus.ivtff.parse()`: it returns pages and tokens with folio, line, locus type,
Currier language, hand and uncertainty flags. **Please keep the LOCKED_TEST leaves out of any development work**,
so that a final confirmation stays possible for everyone.

## 3. Encrypt any text with any family
```python
import random
from vcl.synthetic.encoders import ENCODERS      # 13 families: mono, homophonic, vigenere, columnar, nulls,
                                                  # verbose, abjad, syllabary, autokey, boundary_noise,
                                                  # reversed_words, nomenclator, one_time_pad
symbols, key, identifiability, _ = ENCODERS["homophonic"]("in principio erat verbum", random.Random(1))
```
Voynich-like verbose cipher (Greshko's Naibbe tables, plus context-dependent spelling and nulls, as in E014/E017):
```python
from vcl.solvers import verbose as V
from vcl.synthetic import edge_twins as X, rep_twins as R, twins as T
C, nulls = X.coupling_matrix(lines), R.null_pool(dev_words)
key = V.random_key(123)
enc_lines, labels = V.encode_labelled("inprincipioeratverbum...", key, C, nulls, seed=7)
```

## 4. Meaningless controls
```python
p = R.random_params("rugg_rep", random.Random(5))                       # Rugg-style grille
g = R.generate("rugg_rep", p, 5, T.chunk_pools(dev_words), 20000, C, nulls)
control_words = [w for l in g["lines"] for w in l]
```
Other controls: `"self_citation_rep"` (Timm & Schinner), and letter-shuffled plaintext (shuffle the letters before
encrypting). `vcl.synthetic.decoys` has markov, autocopy, grille and zipf_bag streams.

## 5. The validated attack and claim rule
```python
from vcl.solvers.lm import get_lm
from vcl.synthetic import naibbe_exact as NX
r = V.attack_portfolio(words, get_lm("la", "nospace"), iters=100_000, restarts=128, seed=0)
dec = NX.clean("".join(r["decoded_words"]))
vocab = {NX.clean(w) for w in get_lm("la", "space").vocab}
lex = V.lexical_coverage(dec, vocab, min_len=7)
claim = r["agreement"] >= 0.95 and lex >= 0.08
```
This attack is validated (E017) for the verbose-cipher class with the Naibbe inventory. For another cipher class,
build the class's generator first and show that the attack cracks it, with controls, before using it on Voynich.

## 6. Your own language corpus
```python
from vcl.solvers.fast_anneal import lm_from_text
lm = lm_from_text(open("my_old_occitan.txt").read(), "old_occitan")   # no-space Kneser-Ney 4-gram letter LM
```
Built-in languages (36, from Project Gutenberg) are listed in `vcl.synthetic.corpora.LANGUAGES`. The open CLTK
Latin Library (13M words, `github.com/cltk/lat_text_latin_library`) is what Stage B uses. Remove any overlap with
your test texts first (see `reports/STAGE_B_DEV.md`).

## 7. Word-level and compound (stem + ending) attacks: in development
These are development probes, not yet validated:
- `experiments/dev/endfirst.py`: decodes inflectional endings from frequency, adjacent-ending bigrams and
  same-stem ending pairs.
- `experiments/dev/stemsecond.py` and `ctxassign.py`: decode stems given the endings.
- `experiments/dev/wordsub_*.py`: whole-word codebooks.

They currently expect our local paths (scratchpad imports). Treat them as worked examples until they're promoted
into `src/`.

## 8. Fingerprints, twins and Stage A tests
Every Stage A test (`experiments/e019`–`e025`) is a standalone script. Each one compares Voynich with synthetic
"twins" of each hypothesis family, generated by `vcl.synthetic.twins`, `edge_twins` and `rep_twins`. To test a new
mechanism:
1. Write a generator that turns plaintext into Voynich-like words.
2. Add it as a family next to the existing ones in, for example, `experiments/e021_persistence.py`.
3. Pre-register the decision rule, and run it.

## 9. Pre-register and lock
Before a run that looks at Voynich:
```bash
cp docs/PREREG_TEMPLATE.md reports/EXXX_PREREG.md     # fill it in: question, data, procedure, decision rule
chmod 444 reports/EXXX_PREREG.md && shasum -a 256 reports/EXXX_PREREG.md
```
Have your script check that hash before it runs (see `experiments/e025_line_effects.py`). Smoke runs must not
compute the Voynich target statistic: see the 2026-10-18 entry in `experiments/FAILURES.md` for why.

## 10. Other scripts
Nothing here is Voynich-specific apart from the parser. To use it elsewhere:
1. Supply your corpus as lists of words or lines.
2. Build twins for the hypotheses you care about.
3. Follow the same rules.

We plan to apply the method to the Indus script next.
