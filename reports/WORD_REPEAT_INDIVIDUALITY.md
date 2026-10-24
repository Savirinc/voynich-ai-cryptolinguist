# E057: do individual words differ in repeating themselves beyond their form? — VOID (design too weak)

Pre-registration `reports/E057_PREREG.md` (sha 6df19bfa…f528e, commit 52b82d6). Script
`experiments/e057_word_repeat_individuality.py`. Results: `experiments/results/e057.json`, `e057_run.log`.

PHI is how much individual words differ from their family's prediction (about 1 = no word-specific variation beyond
chance).

| Text | Words kept (families) | PHI | z vs Poisson |
|---|---|---|---|
| Voynich DEV | 26 (12) | 0.62 | +0.4 (p 0.31) |
| Copy generator, 10 samples | — | 0.19–0.85 | −1.7 to +0.9 |
| Indonesian | 13 | **1.94** | **+5.1 (p 0.0005)** |
| Malay, Tamil, Assamese, Malayalam | 0–2 | not computable | — |

**Verdict (pre-registered): VOID, no factor.** Only 1 of the 5 reference languages could be measured at all.

## Why it failed (a design flaw, stated plainly)
- **The eligibility rule was too strict.** It required each word to *expect* at least one same-line repeat
  (E_w ≥ 1), and families to hold 2 or more such words.
- **In a 28,841-token sample** that leaves only 26 Voynich words and almost no words in the languages. The test had no
  power, so it says nothing either way.
- **Indonesian, the one measurable language, shows strong word-specific behaviour (z +5.1),** as a real vocabulary
  should. Voynich, on its 26 words, shows none (z +0.4), like the generator. With so few words this is a hint, not a
  result.
- **The forum's examples were not reproduced here.** Only aiin is a "never-repeater" among the kept words; dal, shey
  and saiin did not meet the eligibility bar.

## Next
A redesigned v2, pre-registered before running:
- a looser eligibility rule;
- a likelihood-ratio statistic (word-specific rate against family rate);
- reference texts sampled so that enough words are eligible.

No conclusion is drawn from v1.
