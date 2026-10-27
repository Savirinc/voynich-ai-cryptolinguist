# The Hebrew campaign (from 2026-10-27)

Opened at Arham's direction: "I think it's Hebrew in some form or shape ... you have to disprove it 100% or try proving
it 100% ... try all the possible tests to decode it". Rules are in `E080_PREREG.md`: proof needs a validated claim,
a blind reading by Hebrew readers and a LOCKED_TEST prediction; exclusion is per form, within the scope of an attack
that cracks that form on known answers. "Hebrew in any form whatever" cannot be excluded by any test.

## Status by form
| Form | Hidden how | Result | Scope of the exclusion |
|---|---|---|---|
| H1 | one Voynich sign per Hebrew letter, any permutation incl. atbash, homophones, 12% slips | **A: no claim (E049, E080). B: no claim (E080)** | 23 commonest signs; attack cracks Hebrew 2/2 at accuracy 1.00 |
| H2 | as H1, word letters reversed | **A and B: no claim (E080)** | as H1; cracks 2/2 at 0.99–1.00 |
| H3 | morpheme code (fronts = prefixes, endings = suffixes, bridges = root letters) | **A and B: no claim (E081)** | these unit cuts, 40 symbols, many-to-one; attack cracks Hebrew unit code 2/2 at 0.99 |
| H4 | vocalised syllables, one chunk per syllable | **excluded by count** (2026-10-27, E065 logic) | Hebrew needs 79 syllable types for 95% of text; Voynich has 37 glyph units in all. Without vowels H4 is H1 |
| H5 | another language in Hebrew letters | **Yiddish (E063), Aramaic and Judeo-Arabic (E082): no claim on A and B.** Ladino, Judeo-Italian, Judeo-Persian untested (no texts found) | as H1; cracks 0.98–1.00 |
| H6 | Naibbe-type verbose cipher of Hebrew | class fails (E062) | 13-feature battery, 10 seeds |

## E080: Hebrew letters on Currier B, and Hebrew written backwards
Run 2026-10-27 (369 s). Script `experiments/e080_hebrew_letters_b.py`; results `experiments/results/e080.json`, log
`e080_run.log`.
| Variant | cracks (accuracy, lexrate) | controls max (A) | threshold | Voynich A lexrate | Voynich B lexrate | B controls max | verdict |
|---|---|---|---|---|---|---|---|
| Hebrew forward | (1.00, 0.70), (1.00, 0.71) | 0.576 | 0.640 | 0.521 | 0.501 | 0.564 | no claim on A or B |
| Hebrew reversed | (1.00, 0.75), (0.99, 0.61) | 0.486 | 0.549 | 0.449 | 0.498 (agreement 0.79) | 0.613 | no claim on A or B |
In every case Voynich scores **below** the pseudo-Voynich imitations (texts with Voynich's letter statistics and no
meaning): the attack can make Hebrew-looking strings from anything Voynich-like, and makes them no better from Voynich.
Decoded sample (forward, A), as the attack left it: מהביןה הכאור בים ומאיר הכאים עורלה בותאותה ... (word salad with
common Hebrew pieces, as in E050).

**Verdict: NO CLAIM, validated.** H1 is now excluded on both A and B, and H2 on both, within the scope above.

## E081: the morpheme-code attack (H3)
Run 2026-10-27 (524 s) under `E081_PREREG.md`. Voynich words cut into front + bridge glyphs + ending (63 unit types,
40 kept); Hebrew words into prefix + root letters + suffix (71 types, 40 kept); many-to-one annealing, 32 × 60,000.
| | accuracy | lexrate | agreement |
|---|---|---|---|
| crack 1 / crack 2 (Hebrew unit code) | 0.99 / 0.99 | 0.618 / 0.623 | 1.00 / 1.00 |
| controls A max (2 generator, 5 pseudo-Voynich) | | 0.596 | |
| **Voynich A** | | **0.472** | 0.94 |
| controls B max (5 pseudo-Voynich-B) | | 0.640 | |
| **Voynich B** | | **0.630** | **0.62** |
VALIDATED, threshold 0.607. Voynich A scores far below its imitations. Voynich B reaches 0.630, above the threshold but
below its own imitations (0.640), and its 32 restarts disagree (agreement 0.62 against the 0.95 required): the attack
finds no stable Hebrew reading. Decoded sample (B, unstable): אשאל היאשור ר ואת אול ואל ואל ויאמר ואל ...
**Verdict: NO CLAIM, validated.** H3 excluded within scope.

## H4 by count (not a new scored test; E065's pre-registered logic applied to Hebrew)
Vocalised Hebrew (hboWLC with points; vowel classes a/e/i/o/u/none): 139 consonant+vowel syllable types, 79 needed to
cover 95% of the text. Voynich: 37 S3 glyph-unit types in all, 15 cover 95%. A code with one Voynich chunk per Hebrew
syllable needs at least as many chunk types as syllable types; Voynich has under half. With vowels ignored, the code is
H1 (excluded). H4 is excluded by logic within this scope.

## E082: Aramaic and Judeo-Arabic in Hebrew letters (H5)
Run 2026-10-27 (360 s) under `E082_PREREG.md`. Texts from Sefaria: Targum Onkelos and Saadia Gaon's Tafsir (whole
Torah, 5,845 verses each); model from Genesis–Leviticus, plaintext from Numbers–Deuteronomy.
| Language | cracks (accuracy, lexrate) | controls A max | threshold | Voynich A | Voynich B | B controls max | verdict |
|---|---|---|---|---|---|---|---|
| Aramaic (Onkelos) | (0.98, 0.69), (1.00, 0.74) | 0.438 | 0.565 | 0.410 | 0.391 | 0.465 | no claim |
| Judeo-Arabic (Saadia) | (1.00, 0.68), (1.00, 0.70) | 0.503 | 0.591 | 0.355 | 0.413 (agreement 0.87) | 0.463 | no claim |
Voynich again scores below its pseudo-Voynich imitations in all four cases. **Verdict: NO CLAIM, validated.**

## Where the campaign stands (2026-10-27)
Every concrete form listed has now been attacked with a method that first cracked that form on known answers, and
none read Voynich better than meaningless imitations of Voynich do:
| Form | Result |
|---|---|
| H1 Hebrew letter by letter (A, B) | no claim |
| H2 Hebrew backwards (A, B) | no claim |
| H3 Hebrew morpheme code (A, B) | no claim |
| H4 Hebrew syllables | excluded by count |
| H5 Yiddish, Aramaic, Judeo-Arabic in Hebrew letters (A, B) | no claim |
| H6 Naibbe-type verbose cipher of Hebrew | class fails |
Not covered: Hebrew under a code that also changes word boundaries or word order, a code with more than one sign per
letter in fixed groups other than Naibbe's, abbreviated Hebrew (acronyms, *roshei teivot*), Ladino, Judeo-Italian,
Judeo-Persian, and any form not yet named. These cannot be excluded until each is stated and attacked.
