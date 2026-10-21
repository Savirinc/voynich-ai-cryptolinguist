# E029a: adjacent word repeats, a key-free check of family F — EXCLUDED

Pre-registration: `reports/E029A_PREREG.md` (sha256 dde61138…3369, locked before the run). Script
`experiments/e029a_word_repeats.py` (sha256 8145e377…220e). Result: `experiments/results/e029a.json`.

## Plain-language result
Voynich writes the same word twice in a row (*daiin daiin*, *qokedy qokedy*) about **once in every 105 word
pairs**. Ordinary Latin, Italian, French and German prose does it about **once in every 7,400**, which is
**70 times less often**. None of the 973 reference texts comes close: the most repetitive is a Latin commentary
full of abbreviation sigla, at 0.74%.

If each Voynich word stands for one plaintext word, Voynich cannot repeat words more often than its plaintext. That
holds whatever the table, and homophones only lower the count. So no word-for-word system over ordinary prose in
these four languages can have produced the text.

## Numbers
| | adjacent-repeat rate |
|---|---|
| Voynich DEV (25,304 within-line pairs) | **0.95%** |
| Voynich DEV blocks (14): min / 10th pct / max | 0.53% / 0.64% / 1.44% |
| Voynich Currier A / B | 0.97% / 0.95% |
| Reference, 973 texts (950 Latin Library + 23 PG la/it/fr/de): median | 0.014% |
| Reference 99th percentile | 0.30% |
| Reference maximum | 0.74% (`poree.txt`, abbreviation sigla) |
| Reference texts at or above Voynich | **0 of 973** |
| Max by PG language: la / it / fr / de | 0.45% / 0.15% / 0.19% / 0.31% |

**Rule:** V > Rmax (0.95% > 0.74%) **and** Voynich block 10th percentile > R99 (0.64% > 0.30%), so the verdict is
**EXCLUDED**.

## What this excludes and what it does not
**Excluded:** every system in which each Voynich word is one word of ordinary la/it/fr/de prose, with or without
homophones. That covers:
- family F (syllable notation), the last family of the final round;
- word codebooks and nomenclators;
- stem + ending codes;
- a plain reading of the text.

**Not excluded:**
- systems where Voynich words are *not* plaintext words, such as Naibbe-type pieces. E019 already rules those out
  for unknown tables, on topic clustering;
- added null or filler words that themselves repeat. That would be a new layer, and only a new fact could justify it;
- languages or genres that naturally repeat words (reduplication, litanies);
- meaningless text written by a person.

## Caveats
- The rule was written after Voynich's value (E011) and an exploratory look at the reference had been seen. The
  evidence is the margin: 70 times the median, and zero of 973 texts.
- Voynich's word spaces are a transcription choice (EVA). Uncertain spaces could merge or split words. That would
  change the rate by a little, not by a factor of 70.
- The reference texts are mostly classical and later printed prose, not 15th-century herbals. But no genre in the
  950 Latin Library files approaches Voynich.
