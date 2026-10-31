# E104 pre-registration: AB/BA word-pair reversal (Arham, Reddit idea R13, 2026-10-31)

## Question
Fincher (Reddit 1um5ejs) reports that Voynich word pairs often occur in both orders, AB and BA. Real languages fix
order ("of the", never "the of"). Do Voynich adjacent word pairs prefer one order as languages do, or are they
order-free like the copy generator? E048 measured order *information* and was VOID; pair reversal has not been
measured (E069/E070 measured partner stability).

## Data and procedure (`experiments/e104_pair_reversal.py`)
- **Pairs:** adjacent within-line word pairs A B with A ≠ B. Voynich lines are broken at unclean tokens; DEV only, with
  LOCKED_TEST leaves excluded.
- **Per pair:** for each unordered pair {A, B} seen n ≥ 6 times in total, asym = |n_AB − n_BA| / n − E|2X − n| / n,
  with X ~ Binomial(n, ½) computed exactly. This is the order preference beyond a coin toss.
- **Statistic:** ASYM = the mean of asym over those pairs.
- **Controls:** each cut to 28,841 tokens and poured into the Voynich line lengths:
  - 69 meaningful texts (E099 set);
  - 60 copy-generator stretches (E032 × 10, E100 grid × 50).
- **Bands:** L band = meaningful ASYM [p10, p90]; G band = generator ASYM [p10, p90].
- **Validity:** the bands do not overlap.

| Outcome | Rule | Factor |
|---|---|---|
| LANGUAGE-LIKE | Voynich in L band, outside G band | M × 1/3 |
| GENERATOR-LIKE | Voynich in G band, outside L band | M × 3 |
| NEITHER | otherwise (including between or outside both bands) | none |
| VOID | bands overlap | none |

- **Rule 8:** if the Voynich is within 0.5 sd of a band edge (sd from 200 line bootstraps), take 10 bootstraps; at
  least 8 must agree, otherwise NEITHER.
- **Unscored:** REV (share of pairs seen in both orders), the number of pairs, and the most reversible Voynich pairs.

## Seen beforehand
- E048 (Voynich word order weak but not scrambled), E069, E070, and the Reddit claim. No Voynich pair-reversal value
  has been computed.
- **Smoke run** (no Voynich):
  - meaningful: eng-kjv 0.608, hboWLC 0.650, latVUC 0.607, Culpeper 0.616;
  - generator: 0.115, 0.127, 0.146.
