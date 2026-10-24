# E048: is word order inside Voynich lines informative or scrambled? — VOID by rule (but informative)

Pre-registration `reports/E048_PREREG.md` (sha 15f000f2…8f52, commit 6c5e092). Script `experiments/e048_word_order.py`.
Results: `experiments/results/e048.json`, `e048_run.log`.

Q is interior word-order information relative to the median real text. About 1 means as informative as real texts;
about 0 means scrambled.

| Text | Q | Scrambled copy |
|---|---|---|
| Indonesian Bible | 1.86 | 0.00 |
| Turkish Bible | 1.62 | 0.03 |
| Latin Genesis–Exodus | 1.22 | −0.01 |
| Hebrew Genesis–Exodus | 1.00 | −0.02 |
| Apicius + Cato + Varro | 0.78 | −0.01 |
| **Hebrew Psalms** | **0.37** | −0.02 |
| **Voynich B** (A-size) | **0.35** | |
| **Latin hymns** | **0.29** | −0.00 |
| **Copy generator** | **0.20** | |
| **Voynich A** | **0.18** | |

**Verdict (pre-registered): VOID, no factor.** The rule required every real text to score Q ≥ 0.5, but the two
poetic and liturgical texts (Psalms 0.37, hymns 0.29) score lower. Verse carries little order information at this
measure, so a low Q does not by itself mean "scrambled".

## What it shows anyway (unscored)
1. **Voynich's word order is not scrambled.** Every scrambled copy sits at about 0. Voynich A's order information is
   0.073 bits against a shuffle spread of 0.010, about 7 standard deviations above zero. Something real orders the
   words, which makes the pure within-line transposition (secret rearrangement) unlikely.
2. **But the order information is weak.** It is weaker than any prose. Voynich B sits with Hebrew Psalms; Voynich A
   sits with Latin hymns and the copy generator.
3. **Again the closest neighbours are verse or liturgy** (Psalms, hymns) **and the copy generator.** That is the same
   pattern as C21: Voynich behaves either like poetic or liturgical writing or like generated text, and not like prose
   or practical texts.

## Consequence for step 3b
Word order can be used as usual (E047's attack assumes intact order). The ORDER-SCRAMBLED sub-hypothesis keeps its
prior of 0.15 by rule, though the 7-sd result argues against a full shuffle.
