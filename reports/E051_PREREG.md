# E051 pre-registration: the missing-evidence audit, scored fairly for M and L

Written 2026-10-24, before the run. Script: `experiments/e051_missing_evidence.py`. Updates `reports/LEDGER.md`
(Part 1 only).

## Why
"M" (meaningless) has sat at about 0.6% since E032. Meanwhile C21 (no avoidance of identical neighbours; E043–E046)
showed a habit that non-meaningful writing approaches and meaningful prose does not, but it was never scored. It
could not be scored on the same data that suggested it. Part 1 scores it on **fresh** data, by a rule that can move M
**up or down**.

## Part 1 (scored): C21 on fresh references
**Statistic.** AS = ΣO ÷ ΣE (E045's exact formula). AS about 1 means back-to-back repeats are as common as anywhere in
the line; AS about 0 means they are avoided. It is computed on pseudo-lines that follow Voynich DEV's line lengths,
over 28,841 tokens.
- Voynich itself: A 1.04, B 1.01 (known from E045).

**Fresh meaningful texts.**
- 30 eBible translations, in languages never used in this project, drawn with seed 51051 from the 92 that qualify
  (redistributable, full Bible, not used before). The list is fixed in `e051_ids.txt`: asmfb azb bba bqcsim cekak cth
  dan1931 ewe gax hch hil hne iloulb kik lin luo mal meu nheBl nya pan shr sna suzBl swe tam2017 tod uigara urd yap.
- Texts whose mean token length is above 15 characters (no word spacing) are excluded and listed.

**Fresh meaningless texts.** 10 copy-generator samples (Timm & Schinner; shipped configuration; seeds 11–20, never
used; their own lines).

**Likelihoods.**
- k is the number of texts with AS ≥ 0.85.
- p_L = (k_L + 0.5) ÷ (n_L + 1); p_M = (k_M + 0.5) ÷ (n_M + 1).
- BF(M : L) = p_M ÷ p_L.

| BF(M : L) | Factor on M |
|---|---|
| ≥ 10 | × 10 |
| 3 to 10 | × 3 |
| 1/3 to 3 | none |
| 1/10 to 1/3 | × 1/3 |
| ≤ 1/10 | × 1/10 |

The cap is ×10, because the meaningless side is represented by one generator family only.

**Limits.**
- **M is represented by a machine.** Human gibberish (E045) is pooled and too short to score per writer, so it is
  reported but not used.
- **L is represented by Bibles,** one genre.
- **0.85 is fixed now,** below Voynich's 1.0, so that "near" counts.

## Part 2 (descriptive, no factor): dogs that did not bark
**(a) Zodiac labels.** Each of the 12 zodiac pages (all DEV) has 17–41 nymph labels.
- **What is measured:** the share of label tokens whose word is also a label on *another* zodiac page.
- If the labels were numbers or day names, as in a calendar, most would repeat month to month (expected ≥ 0.5).

**(b) Labels and their own page.** For DEV pages with labels and at least 20 words of other text:
- **What is measured:** the share of label words (3+ glyphs) that also occur in that page's text, compared with
  frequency-matched random words (20 draws).
- In labelled technical books, a label's word usually appears in the page's own text.
- **Disclosed bias:** label words absent from all running text are matched against words that occur once. This makes
  the baseline slightly higher (conservative).

**(c) Corrections and erasures.** These cannot be measured from the transcription. The gap is recorded, not
estimated.

## What was seen before writing this (disclosed)
- C21's values for Voynich, earlier texts and human gibberish (E043–E046).
- The list of 92 qualifying Bibles. The 30 were drawn by seed, before any was measured.
- The transcription's label counts per zodiac page.
- Whether zodiac leaves are locked (none are).
- No AS has been computed on any fresh text or fresh generator seed.
