# EXXX pre-registration: <one-line question>

Written <date>, BEFORE the full run. Author(s): <names>. Smoke run: <what it checked; it must NOT compute the
Voynich target statistic>. Settings changed after the smoke run: <none / list>.

## Question
<What will this test decide? Which hypotheses (doors / families) does each outcome favour or rule out?>

## Data
<Exact text: DEV leaves only (LOCKED_TEST excluded), which loci, which transliteration version and hash.
Synthetic texts: generators, languages, sizes, seeds.>

## Procedure
<Script path and command. Features or attack. Budgets. Seeds. Number of samples per family.>

## Positive control (rule 9, required for any meaning test; known-answer test for any attack)
<A real text or a synthetic cipher of the same kind on which the test must succeed, and the success criterion.>

## Controls
<Meaningless twins attacked or scored identically (e.g. rugg_rep, self_citation_rep, letter-shuffled).>

## Decision rule (fixed now)
<Exact thresholds and what verdict each outcome produces, e.g. "CLAIM iff agreement >= 0.95 and lexcov7 >= 0.08".
Include what happens if the positive control fails (verdict VOID / NO POWER).>

## What would change our mind
<Outcomes that would falsify the favoured hypothesis.>

---
Lock: `chmod 444` this file and record `shasum -a 256` in the script's output and in the ledger before running.
