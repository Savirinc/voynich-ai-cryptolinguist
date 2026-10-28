# E087: the letter attack with spaces removed, one line = one record. NO CLAIM (3 languages validated; the Hebrew
# family and Arabic not validated by the score)

Run 2026-10-27/28 (66,277 s, about 18 hours) under `E087_PREREG.md` with `E087_AMENDMENT.md` and `E087_AMENDMENT2.md`
(two crash fixes before any decoding; v3 script). Results `experiments/results/e087.json`, log `e087_run.log`.

## Results
COVER = share of decoded letters inside dictionary words of 3+ letters in the best segmentation of each line.
| Language | cracks (accuracy, COVER) | A controls max | validated | Voynich A (agreement) | Voynich B (agreement) | B controls max |
|---|---|---|---|---|---|---|
| Latin | (1.00, 0.724), (1.00, 0.699) | 0.507 | yes, T 0.603 | 0.426 (1.00) | 0.465 (0.75) | 0.477 |
| Turkish | (1.00, 0.803), (1.00, 0.777) | 0.719 | yes, T 0.748 | 0.713 (1.00) | 0.731 (0.99) | 0.787 |
| German | (1.00, 0.808), (1.00, 0.844) | 0.708 | yes, T 0.758 | 0.639 (0.69) | 0.700 (0.58) | 0.709 |
| Hebrew | (1.00, 0.797), (1.00, 0.800) | **0.827** | **no** | 0.749 (0.48) | 0.812 (0.85) | 0.840 |
| Aramaic (Onkelos) | (1.00, 0.724), (0.98, 0.681) | **0.754** | **no** | 0.700 (1.00) | 0.742 (0.99) | 0.773 |
| Judeo-Arabic (Saadia) | (1.00, 0.710), (1.00, 0.672) | **0.737** | **no** | 0.710 (1.00) | 0.758 (0.94) | 0.773 |
| Talmud | (1.00, 0.777), (1.00, 0.792) | **0.801** | **no** | 0.793 (0.66) | 0.785 (0.64) | 0.829 |
| Arabic | (1.00, 0.862), (1.00, 0.825) | **0.949** | **no** | 0.912 (1.00) | 0.913 (0.65) | 0.916 |

**Verdict: NO CLAIM, partly validated.**
- **The decoder itself works without spaces**: every crack in every language was recovered at 98–100% accuracy.
- **Latin, Turkish, German (validated): no claim.** Voynich scores below its own pseudo-Voynich imitations on A and B.
- **Hebrew, Aramaic, Judeo-Arabic, Talmud, Arabic: untested.** In consonant-only scripts almost any 3-letter string is
  a dictionary word, so meaningless imitations reach a higher COVER (0.74–0.95) than correctly decoded text
  (0.67–0.86). The COVER score cannot tell right from wrong for these scripts. In every one of the five, Voynich
  also scored below its imitations, but because the score failed its known-answer check, nothing is concluded.

## What this means and what comes next
The spaceless line-by-line form is excluded for Latin, Turkish and German. For the Hebrew family it is still open:
the attack cracks Hebrew perfectly, but its yardstick fails in consonantal scripts. A new pre-registration (E088) needs
a yardstick validated on Hebrew known answers before Voynich is scored, for example dictionary words of 4+ letters
only, or how often the decoded words occur next to each other in real Hebrew (a word-pair score), chosen by which one
separates the cracks from the imitations on known answers alone.
