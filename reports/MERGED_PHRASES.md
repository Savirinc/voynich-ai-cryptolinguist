# E116 (Arham, move 2): do repeated phrases appear once the spelling families are merged?

Pre-registration `E116_PREREG.md` (sha256 e800c77f…), script `experiments/e116_merged_phrases.py` (sha256 e67c8b70…).
Results `experiments/results/e116.json`, log `e116_run.log`. Run 2026-11-01, 655 s.

## Verdict (pre-registered rule): NO PHRASES, M × 3

## Merge
- **Steps:** drop a word-initial q; drop every d; l → r; k → t; e-runs → e.
- **Applied to:** the Voynich and every EVA control alike.
- **Voynich:** 6,077 → 3,478 types.
- **Matched band:** 2,956–4,000 types.

## Results
| Group (matched) | n | Q3 | Raw repeated 3-word tokens | Repeated 4-word tokens |
|---|---|---|---|---|
| Meaningful (L*, as written) | 12 | min 5.01, p10 5.23, median 18.1 | 2,860–8,092 | 728–3,946 |
| Generator, merged (G*: copy generator 27; no dice book fell in the band) | 27 | 1.36–3.84 | 36–472 | 0–11 |
| **Voynich, merged** | | **2.41** (1,713 vs 709 ± 36 by shuffle; sd 0.12) | **1,713** | **86** |

- **Validity:** VALID (12 and 27 members; L* p10 5.23 > G* max 3.84).
- **Placing:** the Voynich is inside the generator range and below the lowest language. No boundary was within
  0.5 sd, so no seed check was needed.

## Power check (unscored): free spelling *can* hide phrases
The 12 matched texts were given five planted free variants: two letter swaps, a doubled vowel, a dropped consonant and
an optional first letter, each at 50%. This cut their raw repeated triples from 2,860–8,092 to 18–238. That is the
Voynich's unmerged level (236). So the free-spelling explanation was coherent: it could have explained the missing
phrases. Undoing it should have brought them back.

## Each merge step alone on the Voynich (unscored)
| Step | Types | Q3 | RP3 | RP4 |
|---|---|---|---|---|
| none (E100) | 6,077 | 10.8 | 236 | 0 |
| q | 5,688 | 8.3 | 330 | 2 |
| d | 5,042 | 5.3 | 451 | 6 |
| l→r | 5,588 | 7.5 | 305 | 2 |
| k→t | 5,484 | 8.8 | 310 | 2 |
| e-runs | 5,621 | 10.0 | 345 | 2 |
| all five | 3,478 | 2.4 | 1,713 | 86 |

Merging raises raw repeats (236 → 1,713), but chance repeats rise faster (shuffle 21 → 709). Merging only makes
words more alike; it does not bring out any fixed word order.

## What it means
**Not a free-spelling message:** if the Voynich were a message whose words are spelled freely through these five
alternations, merging them should have restored phrase reuse at the level of real languages. It did not. After
merging, the Voynich looks like merged copy-generator text. The missing phrases are not explained by these spelling
variants.

**Limits (rule 11):** spelling variants outside these five, or a merge of different signs, are untested. A message
whose word order is free (not phrase-forming) is not excluded by this test alone.

## Ledger
**M × 3**, renormalised:

| M | L | C | O |
|---|---|---|---|
| 0.8860 | 0.0803 | 0.0151 | 0.0186 |
