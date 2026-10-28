# E089b pre-registration: seed check of E089's near-threshold result (standing rule 8)

Written 2026-10-28 after E089 and before this check. E089: Hebrew + Aramaic + Judeo-Arabic on Voynich B scored COVER5
0.172 against the threshold 0.175 (B controls maximum 0.114, agreement 1.00): within any reasonable 0.5 sd of the bar,
so rule 8 requires ≥ 8 of 10 seeds before it is scored either way. Script `experiments/e089b_seed_check.py`; output
`experiments/results/e089b.json`, `e089b_run.log`.

Procedure: Voynich B decoded with 10 new seeds (89101–89110), same model, effort and scoring as E089. Each seed passes
iff COVER5 ≥ T and > the B-control maximum (both fixed from `e089.json`) and agreement ≥ 0.95.
| Result | Reading |
|---|---|
| ≥ 8 of 10 pass | CLAIM stands → blind reading by Hebrew/Arabic readers, then a LOCKED_TEST prediction |
| ≤ 2 of 10 pass | NO CLAIM confirmed |
| 3–7 of 10 | UNSTABLE: no claim |
Disclosed: E089's numbers; the E089 decode of this mixture on B consists mostly of the commonest letters א ל ו י ה מ with
one 5-letter dictionary word in its first 8 lines.
