# E040 (attack step 1d): the core profile on the cleaned sign inventory — results

Pre-registration `reports/E040_PREREG.md` (sha 541acf72…a5d7). Script `experiments/e040_clean_profile.py`. Results:
`experiments/results/e040.json`, `e040_run.log`. This is a measurement under working assumption L; no ledger change.

Cleaning N1: e-runs → *e*, *t* → *k*.

## Numbers
| | h2 (in-word predictability; simple-syllable range 2.23–2.88) | Words seen once | Distinct words | Zipf head (Bibles −0.79 to −1.12) | R | NR | Endings (NSUF95) | Endings per stem |
|---|---|---|---|---|---|---|---|---|
| DEV raw | 2.37 ✓ | 0.678 | 6,077 | −0.65 | 2.65 | 2.06 | 28 | 9.8 |
| **DEV cleaned** | **2.22 ✗ (just below)** | **0.662** | **5,080** | **−0.74** | 2.96 | 1.92 | 21 | 8.6 |
| A cleaned | 2.33 ✓ | 0.691 | 2,340 | −0.69 | 2.02 | 2.10 | 21 | 7.3 |
| B cleaned (A-size samples) | **2.04 ✗** | 0.680 | 1,970 | **−0.84** | 2.18 | 1.43 | 20 | 6.6 |

(B was already outside the range before cleaning: raw h2 2.22, or 2.17 at A size.)

## Readings, by the pre-registered table
1. **The simple-syllable picture holds for Currier A, but not for B, and only marginally for the whole text.**
   - Cleaned DEV falls just under the range (2.22 against a floor of 2.23), and B falls well under it (2.04).
   - B's glyphs are *more predictable within words* than any natural language in our comparison set.
   - Per the pre-registration, this is reported as: the E027 picture partly depended on EVA's over-counting.
   - **Possible explanations, all untested:**
     - B writes more fixed glyph groups as single sounds than our S2 segmentation assumes (S3, with *qo* and *dy*,
       would raise h2);
     - B's language has an even more restricted syllable set than Hawaiian or Mandarin;
     - B is a more formulaic text.
2. **C11 (the flat Zipf head) stands, weakened, and it is mostly an A/B mixing effect.**
   - Cleaned DEV is −0.74, still flatter than every Bible (−0.79), so C11 stands by the rule.
   - But cleaned **B alone is −0.84, inside the Bible range**, while A alone is −0.69.
   - Pooling two scribes or dialects with different favourite words splits the "top words" between them, which
     flattens the head. **Much of the "unexplained" flat head is two vocabularies mixed, plus spelling variation.**
3. **The rich vocabulary is mostly real.** Cleaning removes 16% of distinct words (6,077 → 5,080). The share of
   words seen once barely moves (0.68 → 0.66). C4 stands.
4. **Repeats and near-copies stand.** R rises to 2.96, as expected, since merging can only create repeats. NR is
   1.92.
5. **Endings: 21 after cleaning** (from 28), with about 8.6 per stem. Cleaning merged some endings that differed only
   by e or ee.
6. **A and B really differ on two things after cleaning:**
   - in-word predictability (h2 2.33 vs 2.04);
   - the Zipf head (−0.69 vs −0.84): B's text is dominated by fewer favourite words.

   Vocabulary richness, repeats and ending counts are the same.

## The cleaned profile (input to step 2)
| Property | Value |
|---|---|
| Sign inventory | e = ee, t = k; q and r/l are real; d is a scribe habit |
| Syllable structure | Simple, rigid syllables (A inside the natural range). B is even more rigid than any sampled language. |
| Vocabulary | Rich: about 5,100 words in 28,800, 66% seen once |
| Endings | About 21, combining freely with stems (about 8–9 per stem) |
| Repeats | Common words doubled (R about 3), avoiding line starts |
| Spelling | Loose but patterned; partly scribe-dependent (d) |
| Varieties | A and B: same grammar shape; B more rigid and more repetitive in its favourite words |
