# E036 (ledger test 7): free invention of spellings — ROBUST MATCH by the rule, with heavy caveats

Pre-registration: `reports/E036_PREREG.md` (sha256 98429f3b…2e9a, locked before the run, commit 4d56612). Script
`experiments/e036_free_invention.py`. Results: `experiments/results/e036.json`, `e036_run.log`.

## Plain-language result
- **The model:** Indonesian with one added rule. About 1 use in 8 (p = 0.12) of a word gets a freshly invented
  spelling, one letter different, used once.
- **The result:** this matched in **9 of 10 seed runs**, failing 1 of 9 features each time. By the pre-registered
  rule (8 or more): **ROBUST MATCH**, so L × 10 and C × 3. Every other Bible fails 3 to 8.

The table gives means over the 10 runs.

| Feature | Voynich | Indonesian + free invention | Result |
|---|---|---|---|
| distinct words (fitted) | 6,077 | about 6,030 | pass |
| exact neighbour copies, R | 2.65 | 2.80 | pass |
| near-copies, NR | 2.14 | 1.74 | pass |
| topic clustering, I_word / top_word | 0.39 / 0.29 | 0.40 / 0.41 | pass |
| words seen once | 0.68 | 0.72 | pass (z −2.6 to −3.0) |
| persistence, PERS_30 | 0.26 | 0.48 | pass (z −2.7 to −3.05; failed in 1 run) |
| persistence, COV_30 | 0.92 | 0.95 | pass |
| **Zipf slope, top 100** | **−0.65** | **−0.85** | **fail in all 10 (z +4.3 to +4.6)** |

## Why this "match" must be read with care
1. **Persistence is not really matched.**
   - Indonesian's persistence is nearly double Voynich's (0.48 against 0.26). It passes only because persistence
     varies a lot between Indonesian windows (sd 0.075).
   - The seed replicates could not test this, because the windows are fixed. The 9 of 10 says that the *variation
     draw* doesn't matter; it says nothing about this gap.
   - In plain words: this persistence pass is real by the rule but weak in substance.
2. **Words seen once now overshoot slightly** (0.72 against 0.68), at the edge.
3. **The two models each fit a different half:**

   | Model | Fits | Misses |
   |---|---|---|
   | E035, reused spellings | flat Zipf head, near-copies | one-off words, persistence |
   | E036, fresh spellings | one-off words | flat Zipf head |

   Neither fits Voynich's flat head *and* its one-off words at once. A mixture probably would, but this file's
   pre-registration said E036 is the last model in the family, so no mixture is scored.
4. **This was the second model tried.** The factor was fixed in advance for this test. But two tries on the same
   question make a match easier.
   - Had the factor been discounted to ×3 for that, the ledger would read M 0.02, L 0.95, C 0.025, O 0.003.
   - The ranking is the same either way.

## What it means
- **Shown:** a real language that doubles words (Indonesian), plus unstandardised spelling, comes within the
  rule's tolerance on 8 of 9 word features, across seeds. No other text or generator we have tested does.
- **Not shown:**
  - The flat Zipf head is still unexplained by any single model that also fits the rest.
  - Persistence is only tolerated, not matched.
  - Nothing here says which language Voynich is, or what it says. These are statistics of the *kind* of writing.

## Ledger
L × 10 and C × 3, as pre-registered. The new values are **M 0.006, L 0.970, C 0.023, O 0.001**.
