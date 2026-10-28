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

## E083: proof by construction (Arham: "LHS = RHS, prove it")
Run 2026-10-27 (581 s) under `E083_PREREG.md`. A flexible transformation (prefix → Voynich front, first M root letters
→ Voynich chunks or dropped, suffix → Voynich ending) was fitted so that transformed text reproduces Voynich's words at
Voynich's frequencies; then Voynich was decoded with the fitted tables and the decoded word order was tested.

**Check 1, known answer: passed.** Hebrew hidden by a secret table: 67.3% of tokens decoded to the exact Hebrew word,
root length recovered, decoded order z = +229 (real word order is overwhelmingly visible when the decode is right).

**Check 2, Hebrew-specific fit: failed.**
| Source | share of Voynich's running text matched word for word | root letters kept |
|---|---|---|
| Turkish | **0.485** | 1 |
| Hebrew (data-driven affixes) | 0.466 | 1 |
| Latin | 0.461 | 1 |
| Arabic | 0.454 | 1 |
| German | 0.435 | 1 |
| Greek | 0.408 | 1 |
| Hebrew (linguistic affixes) | 0.399 | 1 |
| Aramaic (Onkelos) | 0.373 | 1 |
| Judeo-Arabic (Saadia) | 0.359 | 1 |
| letter-scrambled Hebrew (meaningless) | 0.339 | 1 |
Best Hebrew-family 0.466 vs best other 0.485: Hebrew does not fit better than Turkish or Latin. Every source chose to
keep **one** root letter: Voynich's vocabulary is best imitated by front + one chunk + ending from any language.

**Check 3, decoded order: failed for the best Hebrew-family source** (Hebrew data-driven z +0.90; Hebrew linguistic
−1.16). Other sources: Aramaic +8.01, Turkish +6.50, Latin +3.45, scrambled Hebrew +2.61, Arabic +2.42, Greek +2.01,
Judeo-Arabic +1.16, German +0.13. Positive values appear even for meaningless scrambled Hebrew, so part of every z is
Voynich's own local order (repeats, ending agreement) carried through the decode; all are two orders of magnitude below
the known answer's +229. Aramaic's +8.0 is the highest and is noted, not scored.
Decoded sample (Hebrew, data-driven; · = no decode): "בארץ ועל בשדה / בדרך · בהמה / · בתים גדול · / לרב אלהים אלהים".

**Verdict: CONSTRUCTION FAILS** (fit not Hebrew-specific; decoded order not Hebrew). The construction can be made to
produce Voynich-like vocabulary from Hebrew, but it does so as well or better from Turkish and Latin, and it does not
turn Voynich's word order into Hebrew word order.

## E084: mixed-language sources (Arham: "why assume just one language?")
Run 2026-10-27 (1,942 s) under `E084_PREREG.md`. Real Talmud (Hebrew and Aramaic mixed, 193,485 words) and mixtures
built from 10-word stretches.

**Part 1, construction: VOID.** The known answer failed: a hidden-table Talmud window was recovered at only 0.8% exact
words (intersection 0.279, order z −3.06), against 67% for plain Hebrew in E083. The construction cannot recover a
Talmud-like mixed text, so its Voynich results cannot be read. Unscored, for the record: every mixture fitted Voynich
equally (0.455–0.487), the **meaningless** scrambled mixture among the best (0.478); order z ranged from −3.9 (Hebrew +
Latin) to +5.8 (Hebrew + Greek), with Latin + German +4.1: no pattern that singles out Hebrew.

**Part 2, letter attack with mixture models: NO CLAIM, validated (7 of 7).**
| Mixture | cracks | threshold | Voynich A | controls A max | Voynich B | controls B max |
|---|---|---|---|---|---|---|
| Talmud (Hebrew + Aramaic) | 1.00 / 1.00 | 0.653 | 0.472 | 0.558 | 0.554 | 0.572 |
| Hebrew + Aramaic (Onkelos) | 1.00 / 1.00 | 0.650 | 0.472 | 0.539 | 0.435 (agreement 0.59) | 0.523 |
| Hebrew + Judeo-Arabic | 1.00 / 1.00 | 0.619 | 0.450 | 0.526 | 0.396 | 0.406 |
| Hebrew (Latin letters) + Latin | 1.00 / 1.00 | 0.621 | 0.527 | 0.539 | 0.427 | 0.414 |
| Hebrew (Latin letters) + Turkish | 1.00 / 1.00 | 0.678 | 0.544 | 0.617 | 0.544 | 0.627 |
| Latin + German (comparison) | 1.00 / 1.00 | 0.631 | 0.413 | 0.436 | 0.480 | 0.502 |
| Latin + Turkish (comparison) | 1.00 / 1.00 | 0.617 | 0.443 | 0.462 | 0.405 (agreement 0.19) | 0.463 |
Every mixture cracks its own hidden text perfectly; on Voynich every mixture scores below the threshold, and all but one
(Hebrew + Latin on B, 0.427 vs 0.414, still far below its threshold 0.621) below its own pseudo-Voynich imitations.

## E087: spaceless, line-by-line attack (after E086)
Hebrew, Aramaic, Judeo-Arabic, Talmud with spaces removed and each line decoded alone: the decoder cracked every
known answer (98–100% accuracy), but the coverage yardstick failed its known-answer check in consonantal scripts
(imitations 0.74–0.83 vs correct decodes 0.67–0.80), so the Hebrew family is **untested** in this form. Latin, Turkish,
German were validated: no claim. Details: `SPACELESS_ATTACK.md`. Next (E088): a yardstick validated on Hebrew first.
