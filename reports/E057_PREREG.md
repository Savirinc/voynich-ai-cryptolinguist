# E057 pre-registration: do individual words differ in repeating themselves, beyond their form?

Written 2026-10-24, before the run. Script: `experiments/e057_word_repeat_individuality.py`. Updates
`reports/LEDGER.md`.

## Why
The voynich.ninja sweep (`FORUM_SYNTHESIS.md`) found that a 2026 generator trained on ZL3b reproduces Voynich's
back-to-back repeats (C9/C21). That weakens C21 as evidence of meaning. Its stated failure is this:
- **Real common words differ individually.** dal, shey and saiin almost never follow themselves, while okaiin does so
  5× chance.
- **The generator "only knows families of words".**

A real vocabulary gives each word its own behaviour, whereas a family-level process does not. This test measures
**word-specific variation in self-repetition beyond what the word's form predicts.**

## Statistic (per text, 28,841 tokens)
- **Expected and observed repeats:** for each word w, E_w is the number of times w would meet a copy of itself if
  each line's words were shuffled (exact formula). O_w is the observed number of back-to-back pairs.
- **Eligible words:** E_w ≥ 1.
- **Family:** (first unit, last two characters). For EVA the first unit is the E024 S3 segment; otherwise it is the
  first letter. Families with at least 2 eligible words are kept.
- **Family prediction:** λ_w = A_family × E_w, where A_family is the family's pooled observed/expected ratio.
- **PHI** = the mean of (O_w − λ_w)² ÷ λ_w over the kept words. Values above the Poisson null mean that words differ
  individually within a family.
  - **Null:** O_w ~ Poisson(λ_w), with A_family refitted each draw (2,000 draws).
- **Also reported:** the share of words that never repeat although E_w ≥ 3, and the share with O/E ≥ 3.

## Texts
- **Voynich DEV**, own lines.
- **Copy generator** (Timm & Schinner, E032 output, 10 random stretches of 28,841 tokens, own lines). quimqu's newer
  generator is not available to us; this is a stated limitation.
- **Reference languages that reach Voynich's back-to-back level (C21):** Indonesian, Malay, Tamil, Assamese and
  Malayalam, cut into Voynich-length pseudo-lines.

## Decision
| Outcome | Rule | Factor |
|---|---|---|
| VOID | fewer than 3 of the 5 reference languages have PHI above the maximum generator PHI (the measure does not separate language from this generator) | none |
| WORD-SPECIFIC (vocabulary-like) | Voynich PHI > every generator sample **and** Voynich's own p < 0.01 | M × 1/3 |
| FAMILY-LEVEL (generator-like) | Voynich PHI ≤ the generator median | M × 3 |
| INCONCLUSIVE | otherwise | none |

**Why ×3.**
- Only one generator family is available as the M reference.
- quimqu's generator, the one reported to fail here, cannot be run.

## What was seen before writing this (disclosed)
- The forum's claim: dal, shey and saiin never self-repeat; okaiin 5×; the generator gives 21% "never" against 16%
  real.
- E043–E051 values for back-to-back repeats.
- No per-word statistic has been computed on any text.
