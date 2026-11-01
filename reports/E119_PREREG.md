# E119 pre-registration (Arham, move 5, 2026-11-01): label words as name-cribs in paragraph-first lines

Script `experiments/e119_label_cribs.py` (sha256 in the commit). Locked before any Voynich number is computed.

## Question
- **The crib:** a label beside a drawing is a *name*.
- **Where names go:** in herbals and picture books, the name of the thing is introduced at the start of a paragraph.
  X117 found the Voynich's surprise gathered in paragraph-first lines.
- **Why a crib is the only test:** E118 showed a whole-word code cannot be cracked from the text alone.
- **Prediction:** if labels are names, label words should stand in paragraph-first lines more often than words of the
  same shape and frequency.

## Data
- **Voynich:**
  - DEV prose (28,841 tokens, 3,406 lines, 629 paragraph-first lines, from the transcription's paragraph flags);
  - labels = DEV tokens in mode `label` (788 types; ring and radial text excluded). No locked leaf is used.
- **Culpeper (real positive):** paragraph-first line = first line after a blank line; labels = words (≥ 4 letters) of
  the herb headings.
- **Planted positives (10):** E032 copy-generator seeds.
  - 150 rare words act as page names, one per page.
  - Each paragraph-first line gets the name with probability 0.6, plus one other line of the page with p 0.6.
- **Nulls (70):**
  - 60 copy-generator runs (paragraph = the line after a line under 40 characters);
  - 10 dice books (E114 best set, the Voynich page shapes and paragraph flags);
  - labels = the Voynich's own label words.

## Statistic
- Label types with prose frequency 2–50.
- **Matches:** each label gets up to 5 non-label types with the same first two letters and the nearest frequency. A
  match is never reused. The shape match controls for the first-line glyph habits.
- **s(w)** = the share of a word's prose tokens that stand in paragraph-first lines.
- **ENRICH** = the mean over labels of s(label) − the mean s of its matches.

## Validity and decision
**Valid if:** Culpeper and every planted text score above the null maximum.

| Outcome | Rule | Factor |
|---|---|---|
| ENRICHED | Voynich > null max | M × 1/3 |
| NOT ENRICHED | Voynich ≤ null p90 | M × 1.5 (weak: labels need not be names) |
| BETWEEN | otherwise | none |
| VOID | validity fails | none |

**Rule 8:** if the Voynich is within 0.5 bootstrap-sd (over label types) of null max or p90, 10 bootstrap replicates
must give the same verdict ≥ 8 times, else BETWEEN.

**Unscored:**
- ENRICH by the label's section;
- the share of label-word tokens in paragraph-first lines on the label's own sheet vs other sheets.

## Seen beforehand
- **Development (controls only, this seed):**
  - Culpeper +0.054; planted +0.193 to +0.231;
  - null max +0.028, p90 +0.021: VALID.
- **Known:** X117's head-surprisal map, and E059 (labels echo their neighbourhood, not their own page). No Voynich
  ENRICH has been computed.
