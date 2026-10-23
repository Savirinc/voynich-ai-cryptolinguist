# E045: does human-written gibberish avoid identical neighbours? — INCONCLUSIVE (but informative)

Pre-registration `reports/E045_PREREG.md` (sha cbb4f259…c58c, commit 2ad1143). Script
`experiments/e045_human_gibberish.py`. Data: Gaskell & Bowern (2022), github.com/danielgaskell/voynich @ d076a7d0.
Results: `experiments/results/e045.json`, `e045_run.log`.

## Numbers
AS: about 1 means back-to-back is as likely as anywhere else in the line; about 0 means it is avoided.

| Text | AS |
|---|---|
| **Voynich A / B** | **1.04 / 1.01** |
| Human gibberish, 38 writers pooled | **0.66** (95% interval 0.41–0.96) |
| Copy generator (E043) | 0.76 |
| Indonesian (grammatical doubling; E043/E044) | 1.37–1.45 |
| 68 meaningful texts (Gaskell & Bowern's set: modern, historical, conlangs) | median **0.02**, max **0.52** (Chinese pinyin); **none ≥ 0.85** |
| Our earlier texts (E043/E044): prose, verse, hymns, scripture, herbals, syllable-spaced writing | 0.00–0.53 |

**Verdict (pre-registered): INCONCLUSIVE, no factor.**
- Voynich A (1.04) lies just *above* the gibberish interval (upper end 0.96), so this is not "like Voynich".
- The upper end is above 0.75, so this is not "avoids" either.

## Plain reading, including what the rule does not score
1. **Ordering on C21:** meaningful texts (≤ 0.53) < human gibberish (0.66) < copy generator (0.76) < **Voynich (1.0)**
   < grammatical doubling (Indonesian, about 1.4).
2. **Apart from doubling-grammar languages, nothing meaningful comes near.** Of about 90 meaningful texts across E043,
   E044 and E045 (dozens of languages, conlangs, scripture, technical, verse), none exceeds 0.53. The non-meaningful
   sources (people writing gibberish, the copy generator) get two-thirds to three-quarters of the way.
3. **So, informally, C21 leans towards M.** This is honest to say even though the pre-registered rule gives no factor.
   The one thing keeping L in contention on C21 is that languages with grammatical doubling (Indonesian, Malay) reach
   and exceed Voynich's level, but they do so with a different pattern: a back-to-back spike.
4. **The ledger is unchanged by rule** (M 0.006, L 0.970). Its high L figure was built *without* C21. Readers should
   know that C21 is the strongest measured fact that does not fit L easily.
