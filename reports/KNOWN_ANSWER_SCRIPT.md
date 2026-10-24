# E047 (attack step 3a): known-answer test on Voynich-like 23-sign scripts — GO

Pre-registration `reports/E047_PREREG.md` (sha 423c0993…fb52, commit 8ebd21f). Script
`experiments/e047_known_answer_script.py`. Results: `experiments/results/e047.json`, `e047_run.log`. About 40 min, 81
attacks.

## Results
| Stage | True-language attacks | Wrong-language attacks | Controls (shuffled, generator) |
|---|---|---|---|
| DEV | 6 of 6 cracked (accuracy 0.998–1.000; lexrate 0.648–0.782) | lexrate 0.042–0.133 | lexrate 0.014–0.379 |
| **TEST** | **9 of 9 claimed and cracked** (accuracy 0.996–1.000; lexrate 0.692–0.830) | **0 claims** (lexrate ≤ 0.144) | **0 claims** (lexrate ≤ 0.422) |

- **DEV threshold:** T = 0.514, the midpoint between the lowest crack (0.648) and the highest non-crack (0.379, the
  copy generator).
- **Verdict (pre-registered): GO.** Hebrew 3/3, Turkish 3/3, Latin 3/3, with zero false claims and the language
  identified every time.

## Margins and limits (honest reading)
- **Agreement does not separate anything here.** Wrong-language and generator attacks also often reach 1.0, because
  with only 23 signs every restart falls into the same best wrong key. **The claim rests on lexrate alone.**
- **The copy generator** reaches lexrate 0.21–0.42 under every LM: short words decoded from gibberish often hit real
  dictionary words. The gap to the threshold is about 0.09; the gap to real cracks is about 0.27. **That narrowest
  margin belongs to gibberish, which is exactly the alternative that matters for Voynich.**
- **What this validates:** a real language written with up to 23 signs, letter by letter, with homophones, about 12%
  spelling slips, and word order intact.
- **What it does not cover:**
  - signs standing for syllables;
  - abbreviation;
  - scrambled word order (E048 tests whether that is needed);
  - languages without a Bible LM;
  - vowel-less writing *of a language that normally writes vowels*.
