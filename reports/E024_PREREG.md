# E024 pre-registration: methodology test A3 — what are Voynich's real letters?

Written 2026-10-18, BEFORE running. Prior knowledge declared: published work (Bennett 1976; Lindemann & Bowern
2020) reports Voynich's conditional character entropy (h2) as unusually low for raw EVA, rising when some glyph
groups are merged. Our own exact numbers for these segmentations haven't been computed.

## Question
If Voynich is a real language written in an invented alphabet (Stage B2), some grouping of glyphs into "letters"
should give letter statistics inside the range of real alphabets. Which, if any, of four fixed segmentations does?

## Segmentations (experiments/e024_atoms.py; greedy longest match)
S0 raw EVA; S1 + cth ckh cph cfh ch sh as one unit; S2 S1 + iiin iin in iiir iir ir eee ee; S3 S2 + qo dy.

## Metrics and references
h1 (unigram entropy incl. space), h2 (conditional entropy given previous unit), L (mean word length in units).
References: every language of the corpus with >= 28,841 words (36 languages available), the first 28,841 words
after 2,000 characters of the concatenated books, lowercase letters only.

## Decision (fixed now)
A segmentation is ALPHABET-LIKE iff h1, h2 and L all fall within [min, max] of the reference languages.
- Some segmentation ALPHABET-LIKE → Stage B2 (real language, invented alphabet) uses the lowest-numbered such
  segmentation as its atoms. The nearest reference languages are reported (not evidence of the language).
- None → a simple one-glyph-unit-per-letter alphabet is unlikely under these groupings. B2 needs other units
  (syllables, compound words) and is deprioritised against the compound/word-code families from E019–E021.

## Limits
Four hand-chosen groupings. The language ranges come from modern printed orthographies, not 15th-century
handwriting with abbreviations.
