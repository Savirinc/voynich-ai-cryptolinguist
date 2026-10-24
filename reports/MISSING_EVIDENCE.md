# E051: missing-evidence audit — C21 does NOT favour gibberish on fresh data (no factor); labels say something

Pre-registration `reports/E051_PREREG.md` (sha 83c6b3a2…5a46, commit 1c66bd6). Script
`experiments/e051_missing_evidence.py`. Results: `experiments/results/e051.json`, `e051_run.log`.

## Part 1 (scored): no avoidance of identical neighbours (C21), on fresh data
AS: about 1 means back-to-back repeats are as common as anywhere in the line; about 0 means they are avoided.

| | AS (1 = no avoidance) | Texts with AS ≥ 0.85 |
|---|---|---|
| **Voynich A / B** | **1.04 / 1.01** | |
| 30 fresh meaningful texts (new languages) | median 0.17; **Tamil 1.01, Assamese 0.87**, Malayalam 0.76 | **2 of 30** |
| 10 fresh copy-generator samples | 0.71 – 0.81 | **0 of 10** |

p_M = 0.045 and p_L = 0.081, so **BF(M : L) = 0.56. No factor, by the pre-registered bands.**

**This corrects my reading after E045.** I said C21 "leans towards M". On a fresh, wider sample of languages:
- **Real languages do reach Voynich's level.** Tamil matches it exactly, and Assamese gets close.
- **The machine generator never does.**

The earlier impression came from samples dominated by European languages. The South Asian languages that reach it are
known for heavy suffixing and for *echo-word* doubling. **C21 is not a gibberish signature.** It is a property some
languages have. The unscored caution in the ledger is withdrawn.

## Part 2 (descriptive): dogs that did not bark
- **(a) Zodiac labels: not a calendar.** 29% of the 341 nymph-label tokens recur as labels on another zodiac page
  (277 distinct words). Day numbers repeated each month would give at least 50%. The labels are mostly distinct names,
  with some recurring elements.
- **(b) Labels do echo their own page.** 10.5% of label words also occur in that page's running text, against 6.3% for
  frequency-matched words: **1.7× enrichment.** A label is somewhat more likely to appear in its own page's text, as
  names do in real illustrated books. This is weak, and a copy-style process could also do it, so it is not scored.
- **(c) Corrections and erasures:** not measurable from the transcription. This needs the manuscript images.

## Lead for later (not a finding)
The languages that matched C21 (Tamil, Assamese, Malayalam) also share Voynich's other measured shape:
- simple syllables;
- heavy suffixing;
- doubling as normal grammar.

The only South Asian language present in Central Europe around 1400 is **Romani**, which is Indo-Aryan. But the
Carpathian Romani Bible tested in E042 showed no doubling. This is worth one pre-registered look; it is not
evidence.
