# E040 pre-registration (attack step 1d): the core profile on the cleaned sign inventory

Written 2026-10-22, before the run. Script: `experiments/e040_clean_profile.py`. Working assumption L. This is a
measurement, with no ledger factor.

## Question
E038 and E039 showed that the EVA alphabet over-counts signs:
- *e* and *ee* are one sign;
- *t* and *k* are almost certainly one sign;
- *d* is a scribe habit.

**How much of Voynich's profile survives once these are cleaned up?** This is the profile that step 2 (the shortlist
of candidate languages) will use.

## Cleaning (N1)
- Every run of *e* (e, ee, eee) is written as *e*.
- Every *t* is written as *k* (so *cth* becomes *ckh*).
- **Not changed:**
  - *d*: handled by measuring Currier A and B separately, since d mostly follows the scribe;
  - *q*: follows location and may carry content;
  - *r* and *l*: a real distinction.

## Texts and measures
- **Texts:** Voynich DEV (all), Currier A and Currier B, each in RAW EVA and in N1.
- **Unit level:** h1, h2 and L at segmentation S2 (E024/E027 code), checked against E027's simple-syllable range
  (h2 2.23–2.88, L 2.74–4.21, h1 3.33–4.71), plus the nearest language.
- **Word level:** types, share of words seen once, Zipf slope (top 100), R and NR (E031), the ending count (NSUF95)
  and endings per stem.
- **A versus B:** word measures depend on text size, so B is also measured on 10 random runs of consecutive B lines
  with A's token count (seed 40040).

## Readings, fixed now
| Question | Reading |
|---|---|
| Is N1 DEV still inside the simple-syllable range? | **If yes:** the syllable picture (E027) survives cleaning. **If no:** it depended on EVA's over-counting, and must be reported as such. |
| Is the N1 Zipf slope still flatter than every Bible (−0.79)? | **If it reaches −0.79 or steeper:** C11 (the flat head) was mostly a spelling artefact, and is re-labelled "spelling-dependent". **Otherwise** C11 stands. |
| Does the share of words seen once fall? | Report how much of C4 (rich vocabulary) was spelling variation |
| Is R still well above 1? | Expected yes: normalising can only *add* exact repeats. Reported. |
| A versus B(A-size) | Any measure differing by more than 1.5× (or by more than 0.1 on h2 or Zipf) is reported as a real A/B difference that survives cleaning |

The output is the **cleaned profile**, which feeds step 2.

## What was seen before writing this (disclosed)
- E024/E027/E037/E038/E039 results on RAW EVA.
- No N1 statistic has been computed.
