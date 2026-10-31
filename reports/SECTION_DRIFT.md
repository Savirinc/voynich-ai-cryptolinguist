# E103 (Arham): section-by-section vocabulary drift, a confirmatory test

- **Pre-registration:** `E103_PREREG.md` (sha256 b6fdc596…), commit bd43223.
- **Script:** `experiments/e103_section_drift.py`.
- **Results:** `experiments/results/e103.json`, log `e103_run.log`. Run 2026-10-31, 40 s.

## Verdict (pre-registered): VOID, no factor
COMPACT is the mean drift over the three compact sections (bathing, stars, pharma). It asks whether near pages share
more words than far pages, with scribe, section and Currier language fixed and same-sheet pairs excluded.

| Variant | Meaningful p10–p90 (median) | Generator p10–p90 (median) | Valid | Voynich COMPACT (sd) |
|---|---|---|---|---|
| V1 ZL, cosine (seen in E102) | +0.03 to +0.33 (+0.18) | −0.10 to +0.14 (+0.02) | no | −0.021 (0.114) |
| V2 ZL, Jaccard | +0.10 to +0.41 (+0.27) | −0.06 to +0.17 (+0.04) | no | −0.006 (0.116) |
| V3 Takahashi, cosine | −0.02 to +0.37 (+0.19) | −0.10 to +0.18 (+0.04) | no | +0.041 (0.121) |
| V4 Glen Claston, cosine | +0.07 to +0.35 (+0.20) | −0.11 to +0.18 (+0.05) | no | +0.077 (0.106) |

The medians differ clearly, with languages drifting and the generator not. But the spread is wide because the three
compact sections give only 44–129 page pairs each. The bands overlap in every variant, so no variant is valid.

## Unscored observations
- **The Voynich sits low in every variant.** Meaningful texts at or below it number 1 of 69 (V1), 2 (V2), 11 (V3) and
  8 (V4). Generator stretches at or below it number 22–36 of 60. Its sampling sd (about 0.11) is large, so this is a
  lean, not a finding.
- **A herbal catalogue also does not drift.** Culpeper's herbal gives +0.05 (V1), −0.03 (V2) and +0.09 (V4), next to
  the Voynich. Narrative and treatise texts give +0.13 to +0.48. In a catalogue, each entry stands alone, so near
  entries need not share words. This is the same catalogue alternative that E070 left open for content-word partners.
- **Herbal A drifts in every transcription** (+0.28 to +0.33). Scribe 1's long herbal run changes vocabulary steadily,
  whereas Culpeper's alphabetical entries do not.

## Ledger
No change: M 0.4897, L 0.3594, C 0.0676, O 0.0833.
