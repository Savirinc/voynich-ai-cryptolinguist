# E113 (Arham, Reddit idea R12): do gallows letters change by section, within the same scribe?

- **Pre-registration:** `E113_PREREG.md`, commit 6c68334.
- **Script:** `experiments/e113_gallows_by_section.py`.
- **Results:** `experiments/results/e113.json`, log `e113_run.log`.

## Verdict (pre-registered): SECTION-SPECIFIC, no factor
Comparing sections written by the same scribe, the gallows mix differs more than the gradual drift from page to page
would give: G 276.5, p 0.0015 against a null that rotates section blocks along each scribe's page order. p is outside
the rule-8 band, so no seed check was needed.
- **Validity:** VALID. Planted section preferences were caught 10/10 (p 0.0005–0.014; 9 of 10 below 0.01). Unplanted
  generator text gave 0/10 false alarms (p 0.05–0.91).

| Scribe | Sections | *t* : *k* (outside paragraph first lines) | Per-scribe p |
|---|---|---|---|
| 1 | herbal 76 pages / pharma 12 | **1,177 : 1,107 (1.06)** / **109 : 455 (0.24)** | 0.014 |
| 2 | herbal 20 / bathing 17 | 264 : 680 (0.39) / 725 : 1,582 (0.46) | 0.076 |
| 3 | stars 20 / herbal 7 | 1,047 : 2,424 (0.43) / 96 : 165 (0.58) | 0.53 |
| 4 | zodiac 12 / astro 7 / cosmo 6 | 88 : 98 / 47 : 105 / 93 : 73 | 0.20 |

## What drives it
- **Mostly one contrast.** Scribe 1 writes *t* about as often as *k* in the herbal pages, but *k* four times as often
  as *t* in the pharma pages. This holds in running prose alone (herbal *t/k* 1.06, pharma 0.24; unscored check). Same
  hand, different subject, different gallows. The other three scribes show smaller differences that are not
  significant on their own.
- **Not Reddit's version.** Outside paragraph first lines, *p* and *f* are rare everywhere: pharma has 2 *p* and 2 *f*.
  So "*f* in herbal, *p* in pharma" does not hold. Zodiac pages (scribe 4) do have relatively many *p/f* (18, 17).
- **Robust (unscored):** with *p* and *f* merged (one letter, E110), p 0.001; with paragraph first lines included,
  p 0.0005.

## Caveats
- **Driven by one comparison.** The pooled result rests mainly on scribe 1's herbal against pharma (88 pages).
- **"Section" stands for more than subject.** Pharma pages differ in layout and vocabulary as well. The gallows shift
  may follow the vocabulary of the section rather than any single letter rule.
- **Fits all hypotheses.** Topic vocabulary (L) predicts this, but so does a section-specific generating habit or
  table (M, C). So no factor, as pre-registered.

## Ledger
No change: M 0.7422, L 0.1816, C 0.0342, O 0.0421.
