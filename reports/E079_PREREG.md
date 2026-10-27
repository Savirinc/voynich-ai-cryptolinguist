# E079 pre-registration: skeleton decipherment - pair Voynich's pieces with each language's by behaviour alone

Written 2026-10-27, before the run, at Arham's direction (option 2 of three). Script
`experiments/e079_skeleton_match.py`; output `experiments/results/e079.json`, `e079_run.log`; report
`reports/SKELETON_MATCH.md`.

## Question
Under the working model (fronts, bridges, about 20 endings), a language's grammar skeleton is visible without its
vocabulary or its letters. If a real language sits under Voynich, Voynich's fronts and endings should pair with that
language's fronts and endings, by how they behave, about as well as a second sample of a language pairs with itself.

## Method (no letters involved)
- Pieces: each text's 10 commonest fronts (1–2 characters) and 20 commonest endings (1–4 characters) (E078 lists).
- Fingerprint of a piece (z-scored across the text's pieces): SHARE (log share of tokens carrying it), FREE (share of
  its uses where it stands alone as a word), DETACH (share of its word types whose remainder is a word), HAPAX (share of
  its word types used once), TTR (log types/tokens), AGREE (log ratio: next token carries the same piece).
- Pairing: fronts with fronts, endings with endings, one to one, minimum total distance (Hungarian method). Score =
  mean distance of the 30 pairs (lower = closer).
- References: every Bible on disk (as E076/E078), 28,841 tokens from token 10,000.

## Known answers (validity)
A second window (tokens 60,000–88,840) of Hebrew, Latin, Persian, Arabic, Turkish and German is scored against every
reference. VALID iff the own language ranks first for ≥ 5 of the 6 and the median share of pieces paired with the
same piece of their own language is ≥ 0.5. Same-language band = the largest own-language distance among the six.

## Voynich and the generator
Voynich DEV prose (28,841 tokens) and generator seeds 31–33 are scored against every reference.
| Outcome | Rule | Ledger |
|---|---|---|
| **SKELETON MATCH** | VALID; Voynich's best distance ≤ the same-language band; all three generator best distances above it | **M × 1/2**; the paired pieces are reported as the first grammar reading |
| SKELETON MATCH, GENERATOR TOO | Voynich within the band, any generator seed within it | none |
| NO LANGUAGE MATCHES LIKE ITSELF | Voynich's best distance above the band | none (a lost or unrecorded language, the leading form of L, predicts this as well) |
| VOID | validity fails | none |
In every case the full Voynich ranking and the piece pairing with the closest language are reported.

## Disclosed (seen beforehand)
E078 (Hebrew, Urdu, Arabic, Persian closest on six summary traits; generator closer than any language). E076 and E075
piece behaviour. Toy check: same toy language 1.07 vs different language 1.90, pieces paired correctly 0.43 (below
the 0.5 validity bar, so the real check may fail). No real text has been scored with this script. One attempt.
