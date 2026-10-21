# E029a pre-registration: a key-free check of family F (adjacent word repeats)

Written 2026-10-21, before the run. Script: `experiments/e029a_word_repeats.py`.

## Declared deviation from FINAL_ROUND.md
FINAL_ROUND.md (locked) planned to settle family F by attack: E029 known-answer, then E030 Voynich. It did not
foresee a key-free check. Arham agreed on 2026-10-21 ("okay") to run a key-free check first. If family F survives
this check, the locked procedure continues unchanged, with the revision budget untouched.

The proposal Arham agreed to was a count of syllable-sized signs. That count needs a segmenter, and our segmenter
under-segments (dev: 42% of words split right). While setting it up, a simpler measurement turned up in our own
records (E011 feature `adj_repeat`). It needs no segmenter and no key, so by the Occam rule it goes first.

## The logic
Family F, and any scheme where **each Voynich word stands for one word** of the plaintext, works as follows.
- Two different plaintext words can never be written as the same Voynich word, or the text could not be read back.
- So the same Voynich word twice in a row means the same plaintext word twice in a row.
- Homophones (several spellings per word) can only *remove* such repeats.
- Therefore **Voynich's adjacent-repeat rate cannot exceed the plaintext's**, whatever the table.

The argument covers family F, word codebooks and a plain reading. It does not cover:
- schemes where Voynich words are not plaintext words (Naibbe-type pieces, verbose ciphers);
- added null words;
- meaningless text.

## What was seen before writing this (disclosed)
- Voynich DEV adj_repeat = 0.0096 (block sd 0.0028) was published in E011 (`experiments/results/e011.json`).
- An exploratory look on 2026-10-21 at the Latin Library files of at least 5,000 words, and at the la/it/fr/de PG
  files, showed:
  - median 0.013%, 99th percentile 0.30%, maximum 0.735% (`poree.txt`, from abbreviation sigla);
  - none at or above Voynich.

So this rule is written after the data were seen. The evidence is the size of the margin, not a p-value.

## Data
- **Voynich:** DEV prose lines (LOCKED_TEST leaves excluded), clean tokens. Pairs are counted only within a line,
  with E011's definition and blocks (`voynich_lines`, `cut_blocks`). Currier A and B are reported separately.
- **Reference (all four languages):**
  - every Latin Library file in `latlib_keep.json` with at least 5,000 words;
  - every la/it/fr/de file in `data/raw/corpora/pg` with at least 5,000 words.
- **Words:** lowercase runs of letters `[a-zà-ÿ]+`. Combined sha256 of the files is recorded in the output.

## Decision
- V = Voynich DEV rate. Rmax, R99 = maximum and 99th percentile over the reference texts.
- **EXCLUDED** iff V > Rmax **and** the 10th percentile of Voynich DEV blocks > R99. Every word-for-word scheme over
  ordinary la/it/fr/de prose is then out, family F included.
- **DISFAVOURED** iff V > R99 but not EXCLUDED.
- **NOT EXCLUDED** otherwise. Family F then continues by the locked procedure (E029 known-answer test).

## Consequence under the stop rule
EXCLUDED means family F cannot give a confirmed claim. The FINAL_ROUND stop rule then applies:
- the Voynich search stops;
- the final report is written;
- work moves to the Indus script.

Only a *new fact* could justify adding a layer to save family F (for example, null words that repeat), per the Occam
rule. A finding that hurts the hypothesis is not such a fact.
