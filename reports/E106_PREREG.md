# E106 pre-registration: paragraph-initial gallows as decorative capitals (Arham, Reddit idea R7, 2026-10-31)

## Question
About 85% of Voynich paragraphs start with a gallows letter (*p, t, k, f*). Reddit (slu7jf, 12vrnwm, oyeayi, 1qavl2o)
suggests these are decorative capitals added to an ordinary word. If so, removing that gallows should leave an
ordinary word more often than removing the first gallows of a gallows-initial word elsewhere.

## Data and procedure (`experiments/e106_gallows_capitals.py`)
- **PARA words:** the first word of each DEV paragraph-start line (ZL para_start), clean and starting with *t/k/p/f*.
  There are 629 paragraph-start lines; LOCKED_TEST leaves are excluded.
- **MID words:** clean gallows-initial words that are neither line-first nor in a paragraph-start line.
- **KNOWN:** the remainder (the word without its first glyph) occurs ≥ 2 times among all tokens that are not
  paragraph-first words.
- **Statistic:** D = R_para − R_mid, where R_mid is standardised to the PARA length mix (lengths 2–9; 9 covers 9+).
  The sd comes from 200 bootstraps.
- **Known answer:** 10 copy-generator stretches poured into the Voynich lines. In paragraph-start lines, a gallows is
  prefixed to the first word with probability 0.85, in the Voynich proportions (p 280, t 146, k 68, f 26).
- **Validity:** planted z > 2 in ≥ 9 of 10, and unplanted |z| ≤ 2 in ≥ 8 of 10.

| Outcome | Rule |
|---|---|
| DECORATIVE | Voynich z > 2 and D ≥ planted-generator D p10 |
| PARTLY | Voynich z > 2 but D below planted p10 |
| INTEGRAL | Voynich z ≤ 2 |
| VOID | validity fails |

- **No Bayes factor.** This is a fact about writing conventions, compatible with M, L and C.
- **Unscored:** the commonest remainders against the commonest first words of ordinary lines, and the rate for each
  gallows.

## Seen beforehand
- First glyphs of paragraph-first words: p 280, t 146, k 68, q 27, f 26, o 26 (of 613 clean).
- Counts of gallows-initial words elsewhere.
- E072 (*ot/ok* detachable front piece).
- **Smoke run** (2 generator stretches, no Voynich):
  - unplanted D −0.006 and +0.031 (z −0.1, +1.1);
  - planted D +0.082 and +0.045 (z +5.0, +2.4).
  - The generator's mid-word remainders are already KNOWN 82–84% of the time, so the test has limited room. Planted
    detection is modest.
