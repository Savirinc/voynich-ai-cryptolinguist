# E032 pre-registration (ledger test 3): the authors' own copy-and-change generator against Voynich's facts

Written 2026-10-21, before the run. Script: `experiments/e032_copy_generator.py`. Updates `reports/LEDGER.md`.

## Question
Every "meaningless" (M) likelihood in the ledger has so far been *assumed* from how the copy-and-change mechanism
should behave. Our own earlier versions were approximations (E011 `self_citation`), and they failed. The fair test
is the **authors' own published generator**:
- T. Timm & A. Schinner, "A possible generating algorithm of the Voynich manuscript", *Cryptologia* 2019/20;
- code at github.com/TorstenTimm/SelfCitationTextgenerator, MIT licence, commit a6ede22 (2019-11-29), file
  `executable/text-generator.jar`, sha256 dc9b2f3c…fef8.

Does it reproduce what we measured on Voynich?

## Setup (no tuning by us)
- The authors' shipped `conf.properties`, with only two changes:
  - `text.lines_to_create=3400`, enough for Voynich DEV length;
  - `method.random.pseudo.seed` = 1, 2, …, 10, giving 10 samples.
- Each sample is cut to 28,841 tokens (Voynich DEV size). Lines are kept as written by the generator, 55 characters
  each, and pairs are counted within lines.
- Voynich: DEV prose lines, clean tokens. LOCKED_TEST is untouched.
- The authors built their rules from knowledge of Voynich (allowed glyph sequences, a repeat allowance, word-final
  substitutions). That is part of their hypothesis, and we test it as published.

## The 13 features (all with existing code, unchanged)
| Feature | What it measures | Source |
|---|---|---|
| R | exact copies of neighbouring words ÷ chance | E030/E031 |
| NR | near-copies of neighbouring words ÷ shuffled | E031 |
| wl_mean | word length | — |
| types | distinct words | — |
| h2 | glyph predictability inside words | — |
| I_word, top_word | topic clustering | E019 |
| PERS_30, COV_30 | persistence of common words | E021 |
| type_hapax, zipf_slope | vocabulary spectrum | E011 |
| NSUF95, DIST | ending inventory | E026, same segmenter settings |

## Decision
For each feature, z = (Voynich − generator mean) ÷ sd. The sd is the larger of: the sd over the 10 samples,
2% of |Voynich|, and 0.01. A feature fails if |z| > 3.

| Outcome | Rule | Bayes factor |
|---|---|---|
| M REPRODUCES | at most 1 of 13 fails | M × 10 |
| PARTIAL | 2–4 fail | none |
| AUTHORS' GENERATOR FAILS | 5 or more fail | M × 1/3 |

**Why the factors are asymmetric.** If the proponents' own generator matches nearly everything we measured, that is
moderate evidence for M. If it fails, that is only weak evidence against M, because a human writer is more flexible
than any program. The authors say this themselves: "we also don't argue that our program is able to simulate the
complexity of human behavior".

## What was done before writing this (disclosed)
- **Exploratory, our own generator.** Our approximation (E011 self-citation plus a global-copy source) was tuned on
  6 features with 1,600 evaluations. It could match exact repeats, word length and topic clustering. It could not
  reach Voynich's near-copies (NR 1.09 vs 2.06) or its glyph predictability (h2 2.65 vs 2.10). The held features
  were never computed. This led us to use the authors' generator instead, and our version is not part of the
  verdict.
- **Smoke run.** One smoke run of the authors' jar (seed 1) checked only that it runs and gives about 31,700
  words. No feature was computed on it.
- **Voynich values already published:**

  | Feature | Value |
  |---|---|
  | R | 2.65 |
  | NR | 2.06–2.14 |
  | I_word | 0.387 |
  | top_word | 0.285 |
  | PERS_30 | 0.264 |
  | COV_30 | 0.917 |
  | types | 6,077 |

## Limits
- This tests one published implementation with its default settings, not every possible copying writer.
- The 10 samples share one design, so their sd is small, and the 2% floor keeps the test from being unfairly strict.
