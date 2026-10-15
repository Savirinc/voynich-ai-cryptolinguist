# Voynich Experiment 067: Visual-text joining and first falsification tests

Date: 14 October 2026

## Goal
Test whether words written beside individual zodiac figures encode star shapes or other directly visible features. Preserve all earlier writing-system hypotheses but require independent visual measurements for semantic claims.

## Sources and provenance

1. User-supplied Zandbergen/Landini IVTFF EVA transcription, version 3b, 13 May 2025; its 298 zodiac label records were previously parsed into `voynich_zodiac_slot_map.csv`. These are modern transliterations, not decipherments.
2. External **secondary, hand-annotated** visual catalogue: https://end.rito.one/solved/figures.html ; per-figure JSON: https://end.rito.one/solved/data/all_299_figures.json . This source asserts 299 figures, 294 starred, 4 crowned, and 27 stars without countable rays. Its manual annotations have **not** been independently rechecked against the Yale native-resolution scans in this experiment. Do not adopt the website's decipherment claims.
3. Reference: Yale Beinecke MS 408 and Rene Zandbergen's folio descriptions: https://www.voynich.nu/q10/index.html and https://www.voynich.nu/q11/index.html .

**Important limitation:** This environment could read the external JSON through a web text viewer but could not download it into the computational container. We therefore manually transcribed the ray counts for 29 Pisces and 30 Cancer figures (including unreadable/null ray counts); we also recorded ten-sign summary counts from the public table. The other signs' per-figure labels were not included in the numerical word-to-image similarity test. No native pixel segmentation was performed.

## Data-integrity checks

- Pisces f70v2: 29 ordered EVA figure labels from source transcription aligned in order with 29 secondary figure entries. Star rays: eleven 6-point, fifteen 7-point, three 8-point.
- Cancer f72r3: 30 ordered figure labels aligned with the secondary catalogue; valid ray counts for 25, with 5 missing/unclear. Counts: twelve 7-point, eight 8-point, four 9-point, one 10-point.
- Only one-piece, unambiguous EVA labels matching `[a-z]+` were used for the principal similarity tests: Pisces 21, Cancer 17. This is conservative, but selection could bias the comparison.

## Test A: Do labels describe the number of star points?

Within each ring of each zodiac sign, calculate the Dice similarity of overlapping EVA letter pairs for every pair of eligible labels. Compare the mean similarity for labels whose stars have the *same* point count against those with *different* counts. Test with 1,500 random label/feature permutations within rings and 1,500 ring-preserving cyclic shifts. One-sided p-values check for stronger similarity with the same point count.

| Sign | Eligible labels | Observed same-minus-different bigram similarity | Within-ring permutation p | Within-ring cyclic p |
| --- | ---: | ---: | ---: | ---: |
| Pisces | 21 | +0.0127 | 0.342 | 0.400 |
| Cancer | 17 | -0.0481 | 0.622 | 0.661 |

**Outcome:** No evidence from these two signs for a simple spelling component shared by stars with the same point count. Does **not** rule out other encodings, languages, glyph segmentations, numerical series, or more complex visual attributes. The method's detection power is limited at these sample sizes.

Further check: Spearman correlation between EVA label length and star-point count, with within-ring permutation: Pisces rho=+0.082, p=0.658; Cancer rho=-0.202, p=0.320. No evidence for a simple label-length encoding of star-point count.

## Test B: Do star-point counts vary across the zodiac?

From the third-party catalogue's **aggregate** sign-level counts, 272 stars have countable rays and 27 are uncounted across 299 figures. We tested ten sign groups (combining split Aries/Taurus). Their mean ray counts range from 6.724 (Pisces) to 8.500 (Leo). An F-style between-sign/within-sign statistic is 15.705. In 30,000 permutations of the 272 ray counts across groups while preserving group sizes, no randomized allocation reached the observed statistic: estimated p < 3.4e-5 (more precisely `(0+1)/(30000+1)`).

**Outcome:** Star point counts in this secondary annotation dataset are markedly sign-dependent rather than exchangeable across all ten signs. This indicates organized variation in the artwork or drawing conventions, but does **not** establish why the pattern occurs or what any original labels mean. The manuscript has different physical folios, pigment choices, possible hands, and page conditions, which could influence star drawing.

## Test C: Blue-painted Pisces headgear versus six-pointed stars

The annotated Pisces outer ring has six figures with blue/blue-gray headgear; five have six-pointed stars. Of the other thirteen figures, two have six-pointed stars. A simple Fisher test returns p=0.00955, but this ignores the clustering of headgear and star shapes along the ring. Circularly shifting the fixed pattern of head colors around the 19 outer figures gives overlap at least this high for only 1 of 19 shifts, a one-sided p of 1/19=0.0526. This is an exploratory, borderline result, not a confirmed code, and was noticed after exploring the data. No corresponding Voynich-label spelling signal was detected in the first test.

## Decisions

- **Keep**: Exact label-to-figure order as a useful join key for the tested panels, with independent crosschecks against the original IVTFF sequence.
- **Keep as a provisional visual phenomenon**: zodiac-dependent star-point distributions.
- **Reject as a supported reading**: star-point counts are directly represented by a common obvious EVA label component, based on two tested panels.
- **Keep unresolved**: possible 30-degree zodiac system; ring start/direction; medieval astrological meanings; multi-symbol or context-sensitive encodings; language candidates.
- **Do not claim**: a solved calendar numeral, a decoded glyph, an identified star, or an Old French translation.

## Next test, preregistered before expanding the sample

1. Obtain the actual per-figure JSON as bytes in a network-enabled environment and verify its 299 entries against the original Yale IIIF images, preferably with two independent annotators blind to labels.
2. Harmonize source labels using the IVTFF record number/ring and preserve ambiguous labels, not made-up clean replacements. The Gemini catalogue uses two indices (`k` versus `n`), so verify which one aligns to transcription records.
3. Expand from two signs to all ten signs. Use the **same** word-similarity and within-ring shift controls, *without* reselecting metrics based on outcomes.
4. Run a blinded sign-held-out predictive test: fit glyph n-gram features to star-ray groups, headwear, containers, star strings and crowns on nine signs; predict attributes on the tenth. Compare against prior prevalence, ring-position and artist/folio baselines. Do not infer word meanings from a classifier's small gain.
5. In parallel compare fixed-degree historical astrological iconography and star-count conventions from pre-15th-century manuscripts, keeping comparisons independent of the Voynich words.

## Files
- `voynich_067_pisces_coded_attributes.csv` and `voynich_067_cancer_coded_attributes.csv`: per-figure joined sample.
- `voynich_067_star_count_by_sign.csv`: aggregate visual measures for all ten signs.
- `voynich_067_pisces_test.py`, `voynich_067_cancer_test.py`, `voynich_067_star_summary_test.py`: executable statistical tests.
- `voynich_067_pisces_results.json`, `voynich_067_two_signs_results.json`, `voynich_067_visual_heterogeneity.json`: outputs.

This is **not** a decipherment. It is the first carefully limited image-to-text test using matched figure-level records rather than mere zodiac-panel similarity.
