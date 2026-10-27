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
| H3 | morpheme code (fronts = prefixes, endings = suffixes, bridges = root letters) | open | |
| H4 | vocalised syllables, one chunk per syllable | open | |
| H5 | another language in Hebrew letters (Aramaic, Judeo-Arabic, Ladino; Yiddish no claim, E063) | open; texts not on disk (eBible has only a modern Neo-Aramaic NT) | |
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
