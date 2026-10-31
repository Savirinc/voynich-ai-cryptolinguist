# E113 pre-registration: do gallows letters change by section, within the same scribe? (Arham, Reddit idea R12, 2026-10-31)

## Question
Reddit (1sj3vlq, 1kzhkjt) suggests that the gallows letters differ by section: *t* in zodiac, *f* in herbal, *p* in
pharma. If the mix of gallows follows the **subject** even when the same scribe writes two sections, that is a small
sign of content. If it follows only the scribe, the layout or the gradual drift from page to page, it is writing habit.

## Data and procedure (`experiments/e113_gallows_by_section.py`)
- **Tokens:** DEV clean tokens of all modes, in page order, excluding paragraph-first lines (where *p* and *f* gather;
  E106, E110). LOCKED_TEST leaves are excluded.
- **Eligible:** scribes with ≥ 2 sections of ≥ 3 pages each:
  - scribe 1: herbal 76 pages, pharma 12;
  - scribe 2: herbal 20, bathing 17;
  - scribe 3: stars 20, herbal 7;
  - scribe 4: zodiac 12, astronomical 7, cosmological 6.
- **Statistic:** for each eligible scribe, a section × gallows (*t, k, p, f* glyph counts) table and its
  likelihood-ratio G. TOTAL = the sum over the four scribes.
- **Null that keeps drift and sheet clustering:** within each scribe the page order stays fixed, and the sequence of
  section labels is rotated by a random offset, independently per scribe. Contiguous blocks stay contiguous.
  2,000 draws.
- **Known answers:** 10 copy-generator stretches poured token-for-token into the same slots:
  - UNPLANTED;
  - PLANTED: in each scribe's smallest section, 30% of *k* become *t*.
- **Validity:** unplanted p < 0.01 in ≤ 2 of 10, and planted p < 0.01 in ≥ 8 of 10.

| Outcome | Rule |
|---|---|
| SECTION-SPECIFIC | p < 0.01 |
| WEAK | 0.01 ≤ p < 0.05 |
| NOT SECTION-SPECIFIC | p ≥ 0.05 |
| VOID | validity fails |

- **Rule 8:** if 0.005 ≤ p ≤ 0.02 or 0.035 ≤ p ≤ 0.07, run 10 fresh seeds; at least 8 must give the same verdict,
  otherwise WEAK.
- **No Bayes factor.** A gallows mix that follows the section fits L (topic vocabulary) but also M and C (a
  section-specific habit or table), so it is recorded as a fact.
- **Unscored:** per-scribe G and p; *p* and *f* merged (E110: one letter); paragraph-first lines included.

## Seen beforehand
- **Raw gallows counts per scribe × section** (outside paragraph lines). For example:
  - scribe 1 herbal *t* 1,177 / *k* 1,107 against pharma *t* 109 / *k* 455;
  - scribe 2 herbal *t* 264 / *k* 680 against bathing *t* 725 / *k* 1,582;
  - scribe 4 zodiac *t* 88, *k* 98, *p* 18, *f* 17.
  - So a raw difference is visible; the test asks whether it exceeds drift between contiguous blocks.
- **Smoke run** (3 generator stretches, 300 draws): unplanted p 0.75, 0.053, 0.096; planted p 0.003 in all three.
- E106, E108 (scribe styles WEAK), E110 (*p* and *f* one letter).
