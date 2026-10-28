# E091 pre-registration (approach check 2 of 4): ledger audit

Written 2026-10-28, before the final computation. Script: `experiments/e091_ledger_audit.py` (arithmetic only).
Output: `experiments/results/e091.json`, `e091_run.log`, report `reports/LEDGER_AUDIT.md`. Updates `LEDGER.md`.
Arham asked (2026-10-28) for the approach itself to be checked; this is check 2.

## Question
The ledger multiplies Bayes factors that we set ourselves, test by test. Are any of them (a) counted on a basis that a
later test overturned, (b) counted twice for the same observation, (c) larger than the test's own measurement, and
(d) is the arithmetic itself right?

## Factors in force (after withdrawals of E031 by E064 and E035 by E035b, and the E090 correction)
E030 L×3; E032 M×1/3; E036 L×10, C×3; E049–E050 L×0.9428, C×0.9533; E052 L×0.9329; E053 L×0.9755; E062 C×1/3;
E063 L×0.965, C×0.9767; E065 L×0.921; E066 M×3; E067 M×3; E068 M×1/3; E085 M×1.4. Start M 0.45, L 0.30, C 0.20, O 0.05.

## The audit rules (complete list; no others will be added)
- **R0 exact arithmetic.** Recompute from the start with no intermediate rounding.
- **R1 superseded basis.** If a later pre-registered, validated test measured the property an earlier factor rested on
  and showed the earlier factor's model is unlike Voynich there, the earlier factor is withdrawn and the later one kept
  (precedent: E064 withdrew E031 and added nothing). Candidates, fixed now:
  - **E030 L×3** ("doubling languages explain Voynich's back-to-back repeats"): E066 and E064 Part C showed Voynich's
    repeats are family-level, unlike the doubling languages, whose repeats are word-specific. → withdrawn.
  - **E036 L×10, C×3** ("Indonesian + free invented spellings reproduces Voynich's word features"): E066 showed
    Indonesian repeats word-specifically (+4.8) where Voynich does not (−1.2); E067/E068 showed human gibberish also
    makes the one-off richness and near-copies E036 credited to invention. → withdrawn.
  - Checked and kept: E032 (re-confirmed by E064 Part B), E062, E065, E066, E067, E068, E085, the absence factors.
- **R2 overlap.** Same-direction factors that rest on the same Voynich measurement keep only the larger. Candidate list
  drawn up from the factors above: none found (the same-observation pairs, E030/E066 and E032/E067, point in opposite
  directions and are handled by R1 or test different processes).
- **R3 measured ratio.** Where a test itself reported a measured ratio different from its pre-registered factor, the
  measured ratio is used. Only E066 reported one (×1.4 instead of ×3).
- **R4 forms of L after E090.** The searched shares of L-alpha-known (0.946 of it) and L-abbrev (0.35, E053) were
  reduced with m = 0.2; with E090's power 0.467 they are reduced with m = 0.533 instead. Shares then renormalised.

## Reporting and decision
Each rule is shown alone and all together, from the point values and from the two range-edge starts used since E030
(M 0.60 / L 0.15 and M 0.30 / L 0.45; C 0.20, O 0.05). **The ledger is replaced by the "all rules" point values.** The
verdict names which of M and L leads from each start. No outcome is preferred; the rules are the audit.

## Disclosed (seen before locking)
- This is arithmetic, so the direction of each rule is foreseeable: R1 lowers L (removes L×30, C×3), R3 lowers M.
- A trace while writing the script showed the written ledger drifted through rounding: early rows were rounded to 2–3
  decimals and later rows continued from the rounded values (e.g. after E036, 0.0054 was written 0.006 and O 0.0018 as
  0.001). The exact current values differ from the written ones by up to about 0.007 in M.
- The script was run once to check that it executes; its output was not read.
