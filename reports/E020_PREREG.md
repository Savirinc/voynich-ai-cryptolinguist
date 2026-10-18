# E020 pre-registration: methodology test A1b — drift and compound words

Written 2026-10-18, BEFORE the full run. A smoke run (1 sample per family/language, twins only; the Voynich
statistic is not computed in smoke runs any more) showed naibbe_drift twins reach word-level clustering near
Voynich's. It is reported here because it motivates the test; no setting was changed after it.

## Question
E019: Voynich word types cluster like real words (I_word 0.387, top_word 0.285) while within-word glyph pairs
cluster more than in any language twin (I_sub 0.150, top_sub 0.582). These values are already known. Which systems,
with settings fixed a priori (not tuned to Voynich), reproduce all four?

## Families (experiments/e020_drift_compound.py; E019 features and sources; 40 samples each; seed 20020)
- naibbe_drift4 / naibbe_drift8: the Naibbe-class cipher (E016 encoder) with an independent secret key per section.
- word_drift4: real words with section-specific spelling variants (each letter p=0.3 has a variant, used p=0.7).
- compound (the user's hypothesis): stem → codeword (a Voynich word type of matching frequency rank), plus
  ending (last 2 letters) → a short glyph suffix from a seeded table.
- compound_drift4: compound with a different ending table per section.

## Decision rule (fixed now)
CONSISTENT iff |z| <= 3 on all four features (z vs the family's 40 samples). Reported: z per feature, RMS z.

## Interpretation fixed now
- naibbe_drift CONSISTENT → E019's rejection of the letter-level cipher does NOT hold once tables may change by
  section. B1 (learned, section-specific tables) stays in the programme, and a test separating drift from topic is
  needed (e.g. whether the most frequent "function-word" types persist across sections, as they do in language).
- naibbe_drift inconsistent while word/compound families are consistent → the E019 reading stands.
- Nothing consistent → no tested family explains the profile; report which feature fails.

## What this cannot show
Fit to an already-known profile is weaker evidence than a blind prediction. The drift settings are one choice
each. A consistent family is possible, not proven.
