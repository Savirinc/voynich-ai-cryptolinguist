# E107 (Arham): are gallows decorative anywhere in a word, like Arabic kashida?

- **Pre-registration:** `E107_PREREG.md` (sha256 a5960890…), commit e9950fd.
- **Script:** `experiments/e107_gallows_context.py`.
- **Results:** `experiments/results/e107.json`, log `e107_run.log`. Run 2026-10-31.

## Verdict (pre-registered): PARTLY, no factor
CD measures how differently a word with a gallows and the same word without it are used (neighbouring words). 0 means
interchangeable, like a decoration; 1 means as different as two unrelated words.

| | CD (median over pairs) |
|---|---|
| Planted decoration in 5 languages | −0.13 to +0.003 |
| Real minimal pairs in 5 languages (e.g. word vs word minus a letter) | 0.84 to 0.98 |
| Copy generator, gallows pairs (10 stretches) | 0.52 to 0.93 (median about 0.68) |
| **Voynich gallows pairs** (13) | **0.705** |

VALID. The Voynich lies between decoration and real different words, at the copy generator's level. Words with and
without a gallows are partly interchangeable, as in a copy-and-vary process. They are neither pure decoration nor
fully distinct words.

## Unscored observations (after the run)
- **Bench gallows look more decorative.** A gallows written across *ch* gives low values:
  - *cthy/chy* 0.22, *cthol/chol* 0.36, *cthor/chor* 0.48;
  - the exception is *cthey/chey* 1.30;
  - median 0.42 over only 4 pairs.
- **Plain gallows tend to make a different word:** *kain/ain* 1.33, *taiin/aiin* 1.23, *tar/ar* 0.92, *kaiin/aiin* 0.87
  (median 0.73, 9 pairs).
- With only 13 pairs this is a lead, not a finding.
- **Reporting bug:** the per-letter medians for other-letter deletions show *nan* for letters with any pair lacking a
  frequency-matched comparison word, because the median was taken before dropping missing values. The scored figure
  drops them correctly. The overall other-letter CD is 0.496 (144 pairs).

## Ledger
No change: M 0.7422, L 0.1816, C 0.0342, O 0.0421.
