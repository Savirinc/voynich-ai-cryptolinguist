# E079: skeleton decipherment by piece behaviour. VALID; NO LANGUAGE MATCHES LIKE ITSELF (no factor)

Run 2026-10-27 under `E079_PREREG.md` (locked). Script `experiments/e079_skeleton_match.py`; results
`experiments/results/e079.json`, log `e079_run.log`. Arham's option 2.

## The method works on known answers
A second sample of each language, scored against all 62 languages using only how its pieces behave (no letters):
| Language | own language ranked | distance to itself | pieces paired with the same piece | next closest |
|---|---|---|---|---|
| Latin | 1st | 0.99 | 0.83 | French 1.45 |
| Arabic | 1st | 1.04 | 0.60 | Hebrew 1.43 |
| Hebrew | 1st | 1.10 | 0.60 | Arabic 1.47 |
| German | 1st | 1.23 | 0.57 | Yiddish 1.48 |
| Persian | 1st | 1.34 | 0.43 | Nahuatl 1.65 |
| Turkish | 1st | 1.43 | 0.43 | English 1.45 |
6 of 6 first, median pairing 0.58: **VALID**. The method also sees family resemblance (Hebrew–Arabic, German–Yiddish,
Latin–French). Same-language band: distances up to 1.43.

## Voynich
| Rank | Language | distance |
|---|---|---|
| 1 | Nahuatl (Huasteca, nheBl) | 1.74 |
| 2 | Tagalog | 1.84 |
| 3 | Lingala | 1.85 |
| 4 | **Hebrew** | 1.87 |
| 5–10 | Ewe, Yoruba, Huichol, Malay, Kikuyu, Hawaiian | 1.88–1.93 |
| — | Urdu 1.96, Arabic 2.00, Persian 2.06, Latin 2.11, English 2.12, Greek 2.13, Italian 2.18, German 2.21, Turkish 2.28 | |
| 62 | Hungarian | 2.34 |
Copy generator (seeds 31–33): best matches Hebrew or Arabic at 1.80–1.83.

**Verdict: NO LANGUAGE MATCHES LIKE ITSELF.** Voynich's best distance (1.74) is well outside the same-language band
(≤ 1.43); it is about as far from its nearest language as unrelated languages are from each other. No factor, as
pre-registered.

## Reading
- Whatever language may sit under Voynich, it is none of the 62 on disk, and none of their close relatives (relatives
  score 1.43–1.48 in the known answers).
- This is what the leading form of L predicts (a lost, unrecorded or constructed language, 0.35 of L) and also what a
  cipher or a meaningless system predicts; it does not move M, L or C.
- The ordering near the top is not meaningful: the first ten lie within 0.2 of each other. Nahuatl's first place is
  noted only because a Nahuatl reading has been proposed in print (Tucker & Talbert 2014); the margin over Tagalog is
  0.10, far smaller than the gap to the band.
- The generator sits about as far from every language (1.80–1.83) as Voynich does (1.74).
