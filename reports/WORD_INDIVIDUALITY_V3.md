# E066 (E058 v3): do individual words repeat themselves beyond their family? — FAMILY-LEVEL (generator-like), M × 3

Pre-registration `reports/E066_PREREG.md` (sha256 b1d00ba2…b28405), amendment `E066_AMENDMENT.md` (one-line filing fix,
sha256 094a6bd8…ee0bcf), script `experiments/e066_word_individuality_v3_v2.py` (sha256 9343a9a6…67637b). Results
`experiments/results/e066.json`, `e066_run.log`. 24 s.

## Verdict
**VALID** (4 measurable languages separate from the generator; 3 were needed). **Voynich: FAMILY-LEVEL**, z −1.2, below
the generator median (+0.55) and far from its maximum (+2.0); not borderline. Pre-registered factor **M × 3**.

**Plain reading.** Voynich's 112 common words repeat back to back exactly as their shape-families predict (observed 188,
expected 189, no word-specific excess). The copying generator does the same (z −0.3 to +2.0). Four real languages do
not: Tagalog, Indonesian, Oromo and Lingala give words individual repeat habits (z +4.1 to +13.8). But eleven other
measurable languages, Malay, Tamil, Swahili, Dutch and others, are also family-level by this test. So the test can tell
"vocabulary-like" from "generator-like" only for some languages, and Voynich lands on the generator's side.

## Results
| Text | Kept words (families) | Observed / expected repeats | z | p |
|---|---|---|---|---|
| **Voynich DEV** | 112 (35) | 188 / 189 | **−1.2** | 0.88 |
| Copy generator, 10 stretches | 150–185 | | −0.3 to +2.0 (median +0.55) | |
| Tagalog | 33 (11) | 7 / 103 | **+13.8** | 0.0005 |
| Indonesian | 72 (29) | 92 / 103 | **+4.8** | 0.0005 |
| Oromo | 70 (31) | 10 / 50 | **+4.4** | 0.005 |
| Lingala | 53 (23) | 16 / 33 | **+4.1** | 0.003 |
| Khumi Chin, Kikuyu, Huichol, Malay | 44–79 | | +1.8 to +2.9 | 0.03–0.05 |
| Shi, Dutch, Motu, Thaiphum Chin, Cebuano, Swahili, Tamil | 42–74 | | −0.3 to +1.1 | ≥ 0.13 |
| 45 other languages | | | not measurable (fewer than 20 kept words or expected repeats < 30) | |

Measurable 15 of 60. The power gate was set on inputs only (word counts and line lengths), as pre-registered.

**Watched Voynich words (observed / expected):** aiin 0 / 6.5 and daiin 11 / 21.8 avoid; qokeedy 16 / 9.1, chol 15 / 9.3
and qokeey 11 / 7.4 attract; dal 1 / 2.9, shey 1 / 3.6, okaiin 6 / 4.4, chedy 8 / 10.0, shedy 9 / 8.9, ol 8 / 11.0. Words
do differ, but no more than their families differ: the family model absorbs it (z −1.2).

## Ledger
Pre-registered: FAMILY-LEVEL → M × 3.

| | M | L | C | O |
|---|---|---|---|---|
| Before (after E065) | 0.0259 | 0.9401 | 0.0296 | 0.0043 |
| **After E066** | **0.0739** | **0.8939** | **0.0281** | **0.0041** |

**Sensitivity, two ways.**
- From the range edges (M 0.43, L 0.31 after E064–E065): **M 0.70, L 0.17, C 0.12.**
- **Empirical likelihood ratio.** The pre-registered × 3 was a judgement set before seeing that most real languages are
  also family-level here. Measured: P(family-level | generator) = 10/10; P(family-level | measurable language) = 11/15 =
  0.73; BF(M:L) ≈ 1.4, not 3. With × 1.4 the ledger would be M 0.035, L 0.93, C 0.029, O 0.004. The rule is applied as
  written (as E031 was), and the empirical ratio is recorded as the fairer reading: **weak evidence for M, not moderate**.

## What this does and does not show
- It shows that on the one word-level measure the forum called generator-proof, Voynich behaves like the generator and
  unlike the four languages that give words personalities.
- It does not show Voynich is generator-made: most real languages without heavy doubling also look family-level, because
  their words almost never repeat back to back at all (observed 1–16 against expected 30–220). The statistic has teeth
  only where repeats exist. Voynich has 188 repeats, enough to show personalities if they were there, and they are not.
- The forum's examples hold in part: aiin never repeats and daiin avoids; but these are family effects (the -iin family),
  not word effects.
- This closes the per-word-repeat family for good (E057, E058, E066); no further variant.
