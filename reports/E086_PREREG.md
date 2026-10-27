# E086 pre-registration: are Voynich's spaces mechanical, and is each line its own record?

Written 2026-10-27, before the run, at Arham's direction (road 2). Script `experiments/e086_spaces_and_lines.py`;
output `experiments/results/e086.json`, `e086_run.log`; report `reports/SPACES_AND_LINES.md`. Measurement of the two
assumptions every attack so far has made; **no ledger factor**.

## Earlier work
E044: the spaces are not syllable breaks (WORD-UNIT 0.92). E025: the line is a functional unit (first and last glyphs
change at line edges 4–15× more than in any tested system). Neither asked whether spaces carry information beyond the
glyphs around them, or whether consecutive lines continue each other.

## Part A: space predictability
Every gap between two adjacent glyphs inside a line is labelled space / no space. Context = 2 glyphs left and 2 right
(spaces ignored; line edges padded). Context table from the first half of lines, scored on the second half.
PRED = 1 − H(label | context) / H(label). Texts: Voynich DEV prose (EVA characters; unreadable tokens break the line);
10 languages (Latin, German, English, Italian, Turkish, Hungarian, Czech, Indonesian, Hebrew and Arabic consonantal),
28,841 tokens in Voynich line lengths; reported beside them: a single-table Naibbe cipher of Latin (E062 machinery) and
generator seeds 31–32.
Reading: **SPACES MECHANICAL** if Voynich PRED exceeds every language and the language mean + 2 sd; **LESS
PREDICTABLE** if below every language; otherwise **LANGUAGE-LIKE**.

## Part B: line continuity
Word-bigram model (add-0.1) from the first half of pages; on the second half, the mean log-probability of each
cross-line pair (last word of a line → first word of the next line on the same page) against 200 versions in which the
following line is replaced by a random other line of the same page. z = (real − shuffled mean) / sd. Pages: Voynich's
own folios; languages and others in blocks of 25 lines. Validity: ≥ 8 of 10 languages give z > 3, else VOID. Reading:
**LINES CONTINUE** if Voynich z > 3; **LINES INDEPENDENT** if |z| ≤ 3; **LESS CONNECTED THAN RANDOM** if z < −3.

## Consequences (not ledger factors)
SPACES MECHANICAL → the earlier attacks are repeated with spaces removed (decoder must place its own word breaks).
LINES INDEPENDENT → decoders model each line as a separate record.

## Disclosed
E025, E044, E059 line-position effects. Toy checks: a toy with a space after every -y gave PRED 0.97, a toy with free
word lengths 0.32; a word-chain toy gave continuity z +371. The decision rule's sign for Part B was corrected after the
toy (continuity gives positive z) and before any real text was measured. One attempt.
