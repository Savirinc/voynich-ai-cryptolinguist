# E019 pre-registration: methodology test A1 — what does one Voynich word carry?

Written 2026-10-18, BEFORE the full run. See reports/METHODOLOGY.md, Stage A1.

## Disclosure (protocol slip)
The smoke run of the script (1 twin sample per family/language) also computed the Voynich DEV features and printed
them: I_word 0.387, top_word 0.285, I_sub 0.150, top_sub 0.582. The features, families, z threshold, the
word-family high-side exception, and the decision rule below were already written in the script before that
printout; nothing was changed after it. The script file sha256 at lock time is recorded below. Logged in
experiments/FAILURES.md. Future smoke runs must not compute the target statistic.

## Question
Topic words cluster in a text; letter pairs barely do. If a Voynich word is a whole word, Voynich word types should
cluster by position as strongly as real words do. If it carries 1–2 letters (Naibbe-type verbose cipher), they
should cluster far less. Syllables should fall in between. Meaningless generators: Rugg (none expected),
self-citation (clusters everything through local copying, letters included).

## Features (experiments/e019_unit_burstiness.py)
Text in reading order, cut into 32 equal chunks; types with >= 8 tokens.
- I_word: token-weighted mean entropy deficit (bits) of a type's spread over chunks vs 5 shuffles.
- top_word: share of types whose chunk counts are concentrated (chi-square p < 1e-3).
- I_sub, top_sub: the same for within-word bigrams.

## Twins (development on synthetic texts only, scratchpad a1_dev.py)
Families: word, syll, naibbe (E014 best naibbe_rep spec per language), naibbe_max (the 4 source segments from 4
different languages: an upper bound for letter-level topic signal), rugg_rep, self_citation_rep (E014 best specs).
Sources: the 4 tune+ref books per language (la, it, fr, de), one segment each, Greshko-cleaned. 10 samples per
language (40 per family) for the language families; 20 per generator. Generated at Voynich DEV size (28,841) and
Currier B size (19,490). Seed 19019.

## Decision rule (fixed in code before the disclosed printout)
For each family: z = (Voynich − family mean) / family SD (SD floor 0.01) on each feature.
- A family is REJECTED if |z| > 4 on I_word or top_word. Exception: the word family is not rejected for Voynich
  being MORE topical, since Voynich's illustrated sections may differ in topic more than our 4 books do.
- I_sub and top_sub are reported, not used for rejection (sensitive to scribe/dialect drift).
- Reported: surviving families; favoured family = lowest RMS z over all 4 features. Primary = DEV; Currier B
  reported as a secondary result.

## Interpretation fixed now
- naibbe and naibbe_max REJECTED, word survives → Voynich words carry word-sized meaning units; the 1–2-letter
  verbose cipher class (Greshko-type, any tables) is deprioritised in Stage B.
- word REJECTED (too little clustering) and naibbe survives → the opposite; B1 (learned tables) goes first.
- Several families survive → A1 is not decisive; A2–A4 decide.

## What this cannot show
Our 4-book sources are a proxy for Voynich's topic structure. A codebook or a cipher acting on whole words behaves
like word here. Scribe and dialect drift (Currier A/B) inflate clustering at every level.
Script sha256 at lock: 27697235f683877e0639e53f1a47644d827eb6ff3e161fb03b5e2023174e16c9  experiments/e019_unit_burstiness.py
