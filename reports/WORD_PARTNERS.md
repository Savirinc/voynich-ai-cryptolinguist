# E069: do Voynich words have partners that persist across the book? — INCONCLUSIVE (between)

Pre-registration `reports/E069_PREREG.md` (sha256 b808630a…280b09), script `experiments/e069_word_partners.py` (sha256
92c4a833…c8be32), locked in the commit before the run. Results `experiments/results/e069.json`, `e069_run.log`. 5.4 min.

## Verdict
Gate passed: all 10 generator stretches fall below the languages' 10th percentile, so the measure separates copying from
language. **Voynich ALL: STAB 0.073, above every generator stretch (max 0.053) and below the languages' 10th percentile
(0.083).** That is the INCONCLUSIVE band. It was within 0.05 of both boundaries, so the seed rule re-drew the references
ten times: INCONCLUSIVE in 9 of 10 (one VOID). **No factor.** Secondary: Currier A alone 0.023 (generator-like: at its
generator median 0.029; its languages' 10th percentile 0.056); Currier B alone 0.044 (between: generator median 0.043,
languages' 10th percentile 0.075).

**Plain reading.** Voynich's common words do have partners that carry over from the first half of the book to the
second, more than the copying generator ever manages, but less than 56 of the 60 languages. Only Polish (0.071),
Slovak (0.056), Azerbaijani (0.022) and unvocalised Hebrew (0.011) score as low or lower. Inside Currier A on its own,
the carry-over is at the generator's level, but A is a third of the size and the generator's own A-sized stretches
scatter from −0.004 to 0.046, so that reading is weak.

## Numbers
| Text | STAB (RAW − shuffled baseline) | Note |
|---|---|---|
| **Voynich ALL** (28,841 tokens) | **0.073** (RAW 0.075, baseline 0.002) | between |
| Voynich A only (8,806) | 0.023 | generator-like at that size |
| Voynich B only (19,490) | 0.044 | between |
| 60 languages, ALL size | min 0.011, 10th pct 0.083, median 0.126, max 0.215 | Sunwar 0.22, Hiligaynon 0.21, Oromo 0.21, Yiddish 0.20 … Polish 0.07, Slovak 0.06, Azerbaijani 0.02, Hebrew 0.01 |
| Generator, ALL size (10) | 0.040–0.053, median 0.047 | all below the language 10th percentile |
| Languages, A size | 10th pct 0.056, median 0.086 | |
| Generator, A size | −0.004 to 0.046, median 0.029 | |

PART (strong partners in both halves beyond baseline) was 0.000 for every Voynich text: Voynich has no pair of common
words that is a strong partner (3× chance) in both halves. Most languages have a few; this was reported, not scored.

## Reading for the ledger
- Voynich sits where a **language with weak partnerships** would sit: above a pure copying process, below a typical
  Bible. The four languages at or below it are all ones where the 200 commonest "words" are dominated by grammatical
  pieces (Hebrew prefixes and particles, Slavic inflected function words, Azerbaijani particles), so their content
  partners fall outside the top 200. Voynich's 200 commonest words may be of the same kind, which is consistent with
  C14 (the ending system carries much of the variety) and with E066 (its common words behave as families).
- It also sits where a **copying process with a longer memory than Timm's** would sit. The test cannot tell these apart.
- Honest summary: the first grammar-shape test aimed at the "unrecorded language" form neither confirms nor refutes it.
  Ledger unchanged: M 0.0739, L 0.8939, C 0.0281, O 0.0041.

## What would sharpen it
Partners among *content-like* words only (words outside the 50 commonest), at book scale, with the four low-scoring
languages as the relevant comparison; and the same measure on a longer-memory generator if one can be run. Not
pre-registered here; one attempt was declared.
