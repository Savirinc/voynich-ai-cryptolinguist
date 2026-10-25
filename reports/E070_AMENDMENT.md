# E070 amendment (before any real text was measured): the statistic is replaced, nothing else changes

Written 2026-10-25. The pre-registration (`E070_PREREG.md`, sha256 1f1b48a6…daeedc) and the original script
(`e070_content_partners.py`, sha256 a2847b8c…4e31a4) stay locked and unchanged. The run uses
`experiments/e070_content_partners_v2.py`.

## What went wrong
E069's statistic (rank correlation of smoothed pair associations between halves, minus a shuffle baseline) gave a
**negative** value (−0.09) on the toy language used to smoke-test E070, which should score high. Diagnosis: among
content words, pairs from different topics never share a line, so their association is a deterministic function of
their expected count; expected counts of the same word in the two halves are anti-correlated (a word used more in one
half is used less in the other), and this coupling drags the rank correlation negative. Within-half shuffling does not
cancel it, because shuffled co-occurrence counts are noisy rather than deterministic zeros. E069's top-200 band was
shielded by its many function words, which co-occur with everything. No real text had been measured for E070 when this
was found.

## The fix
**Partner-set overlap (PSO).** In each half, a pair of band words is a *partner* iff it shares at least two lines and
co-occurs at least three times chance. PSO = (partners in both halves) ÷ (partners in either half), minus the mean over
3 within-half shuffles. On the toy texts: toy language 0.88, toy copy-from-previous-lines process 0.02, shuffled 0.01.
Band (ranks 51–250), texts, sizes, gate, fair bar, decision rules and seed rule are exactly as pre-registered; the
judge is reused unchanged (PSO is passed under the field E070's judge reads).
