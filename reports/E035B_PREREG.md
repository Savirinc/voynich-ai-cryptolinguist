# E035b pre-registration: is E035's narrow match robust to the random seeds?

Written 2026-10-21, before the run. Script: `experiments/e035b_seed_replicates.py`. May correct `reports/LEDGER.md`.

## Question
E035 found VARIATION MATCHES: Indonesian with free spelling variation failed 1 of 9 features. The margin was thin.
PERS_30 passed at z −2.98, against a limit of 3. Both the variation and the near-copy shuffles are random. **Would
the same procedure give the same verdict with other random draws?**

## Design
- **What stays the same:** E035's procedure, unchanged. The same 12 Bibles, the same E033 windows, the same α grid,
  the same fit on types, the same 9 features, the same z rule and the same verdict rule (best text fails at most 1
  of 9 = match).
- **What changes:** only the two seeds. Replicate r = 1…10 uses fit seed 35100 + r and eval seed 35600 + r; E035
  used 35035 and 35535. α is refitted in each replicate, and Voynich's NR is recomputed with each eval seed, both
  exactly as in E035.
- **Not used:** E035's own run does not count as one of the 10.

## Decision
This is a check on E035, not new evidence. A robust result adds no further factor, since that would count the same
evidence twice. A fragile result takes back part of E035's factor.

| Outcome | Replicates that MATCH (of 10) | Ledger correction |
|---|---|---|
| ROBUST | 8 or more | none; E035's L × 10, C × 3 stand |
| FRAGILE | 3–7 | L × 1/3, C × 1/3 (E035's net becomes L × 3, C × 1) |
| NOT REPLICATED | 2 or fewer | L × 1/10, C × 1/3 (E035 is withdrawn) |

**Also recorded,** without bearing on the verdict:
- for each replicate, Indonesian's fails and its PERS_30 and hapax z;
- which text is best.

## What was seen before writing this (disclosed)
- E035's full output, with its one seed pair.
- No other seed has been run.
