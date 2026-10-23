# E046 pre-registration: is C21 everywhere, or concentrated in some pages, scribes or sections?

Written 2026-10-23, before the run. Script: `experiments/e046_as_location.py`. This is a measurement, with no ledger
factor.

## Question
C21: Voynich doesn't avoid identical neighbours (AS ≈ 1). Meaningful texts avoid them (≤ 0.53), human gibberish
reaches 0.66, and the copy generator 0.76 (E043–E045).
- **If the effect is concentrated** in a few pages or sections (for instance list-like passages), it may reflect a
  local text type. That weakens the lean towards M.
- **If it is spread evenly** through every scribe and section, it is a property of the whole writing process, and
  the lean stands.

## Design
- **Data:** Voynich DEV prose, clean tokens (raw EVA), own lines. Each line carries its folio, scribe (hand, as in
  ZL), quire and Currier variety.
- **AS** as in E045: ΣO ÷ ΣE, with E = Σ n_w(n_w − 1) ÷ L per line.
- **By scribe and by quire** (where E ≥ 10): AS with a 95% interval from resampling pages (2,000 draws, seed 46046).
- **Dispersion over pages:**
  - D = Σ_p (O_p − AS·E_p)² ÷ (AS·E_p), against a Poisson null with 2,000 simulations.
  - Also the share of all repeats held by the 10% of pages with the highest excess, against the null.

| Verdict | Rule | Reading |
|---|---|---|
| CONCENTRATED | dispersion p < 0.01 **and** the top 10% of pages hold at least 2× their null share of repeats | Local; look at those pages (lists? labels? specific sections?) |
| WIDESPREAD | not concentrated, **and** every scribe with E ≥ 20 has AS ≥ 0.75 | The whole writing process behaves this way |
| UNEVEN | otherwise | Some scribes avoid neighbours, others don't; reported by scribe |

## What was seen before writing this (disclosed)
- AS for Currier A and B overall (E045: 1.04, 1.01).
- Nothing per scribe, quire or page.
