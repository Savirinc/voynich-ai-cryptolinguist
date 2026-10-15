# Voynich Experiment 059: Positional glyphs versus genuine abbreviation

**Date:** 13 October 2026. **Source:** User-supplied IVTFF ZL3b EVA transcription dated 13 May 2025 (`IVTFF Eva.txt.docx`). 4,119 running-text lines, 32,132 conservatively parsed word tokens. Code: `voynich_experiment_059.py`. Machine-readable measurements: `Voynich_Experiment_059_results.json`.

**Status:** This work has **not** deciphered any Voynich word. EVA represents glyph shapes, not their sounds. Allograph and ligature identities are still hypotheses.

## Key external research
Matlach, Janečková & Dostál (2022), *The Voynich manuscript: Symbol roles revisited*, PLOS ONE, DOI 10.1371/journal.pone.0260948, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260948. Their proposed decompositions include `n` resembling a word-final `i` form and `m` possibly resembling a ligature of `i` and `d`. These are proposed decompositions, not confirmed readings. Their paper also raises the possibility of a smaller underlying glyph inventory.

## Reproduced positional asymmetries

| Glyph (EVA) | Word-final glyph occurrences | Inside word occurrences |
| --- | ---: | ---: |
| `m` | 848 | 42 |
| `n` | 5,561 | 146 |
| `i` | 7 | 10,704 |
| `q` | 0 | 5,215 |

Counts refer to parsed glyph occurrences in running-text word tokens only; uncertain transcription segments were excluded.

## Test 1: `-m` as a variant of `-iin`
Forty-two literal stem families had at least three examples each of the `-m` and `-iin` forms. They supplied 3,318 occurrences: 357 line-final `-m`, 287 line-final `-iin`, 138 within-line `-m`, and 2,536 within-line `-iin`.

The marginal odds ratio for `-m` at the end of a line was 22.86. Stratifying by **the same stem and Currier A/B text variety** yielded an odds ratio of 19.89 (95% CI 15.17–26.08). This is a powerful positional association. It does **not** establish that each pair has the same underlying pronunciation or meaning.

## Test 2: Is `-m` a space-saving abbreviation?
If the writer switched to shorter `-m` forms when the line was crowded, lines ending in `-m` might contain more preceding text than lines ending in `-iin`.

A broad comparison across folios suggested a difference: the median ratio of preceding EVA characters to the folio's median line length was 1.135 for `-m` versus 1.054 for `-iin` (Mann–Whitney exploratory p=0.000135).

**But this clue did NOT survive the more stringent control.** Restricting the comparison to the **same folio and the same literal stem** left 26 comparable groups with 69 line-final occurrences. The mean excess preceding EVA length was only 0.28 characters for the `-m` lines. A 20,000-repetition paired permutation test gave p=0.90. Therefore there is **no robust evidence here for abbreviation driven by lack of horizontal space**. EVA character count is in any case only a very rough proxy for physical ink width.

## Other suffix controls
- `-m` versus `-in`, same stem: adjusted OR approximately 20.08 for line endings.
- `-n` versus `-iin`, same stem: adjusted OR about 1.99, much smaller than the `-m` effect.
- `-r` versus `-l`, same stem: adjusted OR 0.67, opposite direction.
- `-dy` versus `-ey`, same stem: adjusted OR about 2.08, indicating other, weaker position-dependent spelling effects.

These are observational comparisons and involve multiple hypotheses, not a decisive cipher test.

## Illustrative image/transcription checks
- f46v lines 1–3: first two lines end with `daiin`, line 3 ends with `dam` in the supplied transcription. https://www.voynich.com/folios/f46v.jpg
- f34v line 2 ends `oldam` and line 9 ends `oldaiin`. https://www.voynich.com/folios/f34v.jpg
- f54r line 9 ends `daiin`; lines 3, 6, 7 end `dam`. https://www.voynich.com/folios/f54r.jpg

These are concrete transcription loci to verify against high-resolution **Yale color scans**. The above public black-and-white photographs are useful references, not calibrated glyph-crop data.

## Decision

1. **Keep:** The original transcription shows strong position-specific letterforms and/or abbreviation conventions, especially for `m` and `n`.
2. **Do not assume:** `-m = -iin`, `-m = -id`, `n = i`, or a particular meaning for `q`. Neither the images nor the tests demonstrate identity.
3. **Reject for now:** The stronger claim that a shorter `-m` variant is selected because the written line is running out of space. Within-folio/within-stem controls don't support it.
4. **Next:** Establish a human-reviewed glyph-location dataset with physical coordinates from Yale scans for `n`, `m`, `i`, `d` at ~100 known loci. Then compare candidate letter decompositions by their stroke geometry and their held-out positional predictions. Only after that should a contextual transcription normalizer be trained.
