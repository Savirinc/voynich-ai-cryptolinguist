# E037 (attack step 1): the grammatical shape of Voynich, key-free

Pre-registration: `reports/E037_PREREG.md` (sha256 800023e7…ba2d, locked before the run, commit ac9036e). Script
`experiments/e037_grammar_profile.py`. Results: `experiments/results/e037.json`, `e037_run.log`. This is a
measurement under the working assumption L; no ledger change.

## Numbers
| | Endings (NSUF95) | Endings per stem | Stem decides ending (I_EXCESS) | Doubled = frequent? (ρ) | Doubled words suffixed (ratio) | Doubling at line start (ratio) | Near-copy difference at end (ENDZ) | Near-copy same stem (SAMESTEM) |
|---|---|---|---|---|---|---|---|---|
| **Voynich DEV** | **28** | **9.9** | **0.32** | **+0.44** | **0.98** | **0.31** | **0.98** | **1.15** |
| Voynich A | 27 | 7.6 | 0.33 | +0.40 | 0.97 | 0.31 | 0.99 | 0.97 |
| Voynich B | 27 | 8.3 | 0.36 | +0.44 | 0.99 | 0.27 | 0.94 | 1.08 |
| Indonesian | 13 | 1.9 | 0.70 | +0.19 | 0.71 | — | 0.91 | 1.71 |
| Malay | 26 | 1.9 | 0.70 | +0.23 | 0.71 | — | 0.46 | 0 |
| Latin | 79 | 4.3 | 0.53 | +0.10 | 1.17 | — | 0.90 | 0.54 |
| Swahili | 75 | 2.7 | 0.67 | +0.18 | 1.07 | — | 0.45 | 2.48 |

- **Most often doubled Voynich words:** qokeedy 16, chol 15, daiin 11, qokeey 11, qokedy 10, shedy 9, dy, ol, chedy
  8.
- **Most common edits in neighbouring near-copies:** e deleted 50 / added 44; r→l 48, l→r 36; d deleted 47 / added
  29; q deleted 43 / added 39; t→k 33, k→t 29.

## Readings, by the pre-registered table
1. **Near-copies are not inflected forms; they look like spelling variation.**
   - ENDZ is 0.98, in the "no special place" band (0.8–1.25). SAMESTEM is 1.15, below 1.3.
   - So the E035/E036 picture stands: neighbouring near-copies differ wherever variation falls, not at the ending.
   - **New observation:** the variation is **patterned, not random**. Five alternations make up most of it:
     - e/ee;
     - r/l;
     - d present or absent;
     - q- present or absent;
     - t/k.

     These are candidates for glyphs that are interchangeable in the script (allographs, or the same sound).
2. **Doubling is of the frequent-word kind, unlike Indonesian.**
   - ρ is +0.44, more than double Indonesian's +0.19 and Malay's +0.23.
   - Voynich doubles its *common* words. They are ordinary suffixed words (ratio 0.98), whereas Indonesian doubles
     bare roots (0.71).
   - **An error in my rule, stated plainly:** the pre-registered threshold assumed Indonesian would score below
     −0.1, but it scores +0.19. So I read the result against the Indonesian yardstick, as the pre-registration also
     said to do. Voynich is far beyond it.
3. **Doubling avoids line starts** (ratio 0.31, inside the "≤ 0.5" band, so tied to line position).
   - The pre-registered reading is "a writing convention, less likely grammar".
   - **A confound, stated now:** Voynich's line-first words are a special vocabulary (E025). A rare first word is
     less likely to be doubled anyway. So this result is weaker than the band suggests.
4. **The ending system is unlike all four references.**
   - The ending count is small, like Malay's (28 vs 26).
   - But each stem takes about 10 different endings, 2–5× more than any reference.
   - The stem barely decides which endings it takes (0.32, lowest of all; references 0.53–0.70).
   - Endings combine almost freely with stems. That is more like a slot system (Stolfi's word grammar) than Latin's
     stem classes or Malay's few affixes.
5. **A and B have the same grammar shape.** No measure differs by a factor of 1.5.

## What this means for the attack
The shortlist criteria for step 2 are now:
- simple syllables (E027);
- frequent, ordinary words doubled, avoiding line starts;
- about 28 endings, combined freely with stems, about 10 per stem;
- patterned spelling alternations.

**None of the four reference languages fits this.** In particular, the Indonesian match in E036 was a match of
*statistics*. Indonesian *grammar* doesn't fit: Voynich doubles different kinds of words, in a different way.

**The most concrete lead** is the five alternations (e/ee, r/l, d, q-, t/k). If some of them are free variants of the
same script unit, the right next step is at the level of the script:
- test which glyphs can be merged without destroying any measured structure;
- then re-measure syllables and endings on the merged script.

That would give the real sign inventory, which every decipherment attempt needs and none so far has established.
