# E063 (campaign step 3): the validated letter attack on every remaining language on disk — results

Pre-registration `reports/E063_PREREG.md` (sha256 2c4677b1…f276d2), script `experiments/e063_wide_attack.py`
(sha256 a2544244…0ef34), both locked in commit 8b2290d before the run. Results: `experiments/results/e063.json`,
`e063_run.log`. Runtime 2 h 21 min with three workers (seed 63063).

## Verdict: NO CLAIM. All 49 languages validated. Absence rule applied: L × 0.94, C × 0.96.

**Plain reading.** The attack that reads a letter-by-letter cipher of a known language out of Voynich's 23 commonest
signs (E047; homophones allowed, 12% spelling slips, word boundaries kept) was pointed at 49 more languages, on
Voynich A and on Voynich B. For every one of the 49 it first proved itself on two planted ciphers of that language
(97–100% of letters recovered). It then read nothing out of Voynich: for every language, Voynich scored at or below
the fake-Voynich controls and 0.09–0.46 below the threshold a true cipher of that language clears. With E049–E053
this brings the languages searched in this class to 60, plus abbreviated Latin.

## What was run
- **Targets:** Voynich A (8,794 clean DEV words) and Voynich B (19,488 words), S3 units, 23 signs.
- **Per language:** 2 cracks (planted ciphers of the language's own text, fresh keys), 2 copy-generator controls,
  5 pseudo-Voynich-A controls (order-2 Markov imitations), 5 pseudo-Voynich-B controls, Voynich A, Voynich B:
  16 attacks × 49 = 784 runs, each 32 restarts × 30,000 iterations.
- **Language model:** Old Testament books (Genesis present) or gospels + Acts (Hungarian, Greek, Yiddish, Malay);
  plaintext from the disjoint test books. Non-Latin scripts stripped of marks and reduced to their 23 commonest letters
  (crude for the Indic abugidas, as declared).
- **engWycliffe:** UNTESTED (its file set lacks the plaintext books; disclosed in the prereg). 49 languages ran.

## Validation
| Check | Result |
|---|---|
| Both cracks letter accuracy ≥ 0.80 | 49/49 (lowest 0.974, Tamil) |
| Both cracks agreement ≥ 0.95 | 49/49 |
| Lowest crack lexrate > highest control lexrate | 49/49 |
| False claims on 12 controls per language (588 controls) | 0 |

Validation is as clean as it can be: the attack cracks every one of these languages when they are really there.

## Results, language by language
Lexrate = share of decoded words that are real words of the language. Agreement = share of positions where the
restarts agree (below 0.95 means the solver never settled, itself a sign that no key fits). Sorted by how close
Voynich A came to the threshold.

| Language | Crack accuracy (min) | Crack lexrate (min) | Pseudo-A controls (max) | Threshold T | **Voynich A** (agreement) | Pseudo-B controls (max) | **Voynich B** (agreement) |
|---|---|---|---|---|---|---|---|
| Malayalam (mal) | 1.00 | 0.81 | 0.68 | 0.75 | 0.66 (1.00) | 0.66 | 0.65 (1.00) |
| Arabic (arb-vd) | 1.00 | 0.71 | 0.54 | 0.63 | 0.51 (1.00) | 0.42 | 0.53 (0.97) |
| Ewe (ewe) | 1.00 | 0.82 | 0.60 | 0.71 | 0.56 (1.00) | 0.58 | 0.56 (1.00) |
| Shona (sna) | 1.00 | 0.68 | 0.41 | 0.54 | 0.39 (1.00) | 0.38 | 0.36 (1.00) |
| Shi (shr) | 1.00 | 0.73 | 0.46 | 0.60 | 0.44 (1.00) | 0.43 | 0.42 (1.00) |
| Swahili (swhulb) | 1.00 | 0.73 | 0.42 | 0.57 | 0.39 (1.00) | 0.50 | 0.48 (1.00) |
| Dutch (nld) | 1.00 | 0.81 | 0.49 | 0.65 | 0.47 (1.00) | 0.44 | 0.42 (1.00) |
| Nyanja (nya) | 1.00 | 0.72 | 0.41 | 0.57 | 0.38 (1.00) | 0.33 | 0.34 (1.00) |
| Toma (tod) | 1.00 | 0.83 | 0.47 | 0.65 | 0.46 (1.00) | 0.53 | 0.52 (1.00) |
| Baatonum (bba) | 1.00 | 0.83 | 0.48 | 0.65 | 0.46 (1.00) | 0.30 | 0.29 (1.00) |
| Simte (bqcsim) | 0.99 | 0.77 | 0.57 | 0.67 | 0.48 (1.00) | 0.57 | 0.55 (1.00) |
| Chhattisgarhi (hne) | 0.99 | 0.84 | 0.47 | 0.65 | 0.45 (1.00) | 0.50 | 0.33 (0.56) |
| Swedish (swe) | 1.00 | 0.83 | 0.46 | 0.64 | 0.44 (1.00) | 0.49 | 0.41 (1.00) |
| Hungarian (hun) | 1.00 | 0.64 | 0.22 | 0.43 | 0.22 (1.00) | 0.27 | 0.20 (0.60) |
| Thaiphum Chin (cth) | 1.00 | 0.86 | 0.48 | 0.67 | 0.46 (0.94) | 0.47 | 0.44 (1.00) |
| Yapese (yap) | 1.00 | 0.86 | 0.41 | 0.63 | 0.42 (0.98) | 0.45 | 0.41 (1.00) |
| Tamil (tam2017) | 0.97 | 0.87 | 0.72 | 0.80 | 0.58 (0.75) | 0.63 | 0.60 (1.00) |
| Sunwar (suzBl) | 0.98 | 0.79 | 0.41 | 0.60 | 0.38 (1.00) | 0.54 | 0.49 (1.00) |
| Motu (meu) | 1.00 | 0.87 | 0.53 | 0.70 | 0.46 (1.00) | 0.61 | 0.57 (1.00) |
| Assamese (asmfb) | 0.99 | 0.80 | 0.44 | 0.62 | 0.38 (1.00) | 0.54 | 0.49 (1.00) |
| South Azerbaijani (azb) | 1.00 | 0.72 | 0.44 | 0.58 | 0.34 (1.00) | 0.41 | 0.39 (0.62) |
| Greek (Byzantine) (grcbyz) | 1.00 | 0.69 | 0.33 | 0.51 | 0.27 (1.00) | 0.15 | 0.14 (1.00) |
| Māori (mri2012) | 1.00 | 0.88 | 0.51 | 0.69 | 0.45 (1.00) | 0.54 | 0.51 (1.00) |
| Huichol (hch) | 1.00 | 0.83 | 0.49 | 0.66 | 0.42 (1.00) | 0.50 | 0.46 (1.00) |
| French (fraLSG) | 1.00 | 0.82 | 0.43 | 0.63 | 0.37 (1.00) | 0.38 | 0.25 (0.57) |
| Polish (polubg) | 1.00 | 0.75 | 0.26 | 0.51 | 0.25 (1.00) | 0.30 | 0.27 (0.42) |
| Yoruba (yor) | 1.00 | 0.86 | 0.40 | 0.63 | 0.36 (0.99) | 0.49 | 0.40 (1.00) |
| Cebuano (cebulb) | 1.00 | 0.86 | 0.45 | 0.65 | 0.38 (1.00) | 0.36 | 0.32 (1.00) |
| Hausa (hausa) | 1.00 | 0.80 | 0.54 | 0.67 | 0.40 (1.00) | 0.57 | 0.56 (0.70) |
| Uyghur (uigara) | 1.00 | 0.74 | 0.39 | 0.57 | 0.29 (1.00) | 0.34 | 0.36 (1.00) |
| Panjabi (pan) | 1.00 | 0.82 | 0.39 | 0.61 | 0.33 (0.54) | 0.43 | 0.39 (1.00) |
| Tongan (ton) | 1.00 | 0.86 | 0.37 | 0.62 | 0.34 (0.97) | 0.48 | 0.32 (1.00) |
| Luo (luo) | 1.00 | 0.81 | 0.47 | 0.64 | 0.35 (1.00) | 0.44 | 0.40 (1.00) |
| Oromo (gax) | 1.00 | 0.77 | 0.52 | 0.65 | 0.36 (1.00) | 0.56 | 0.52 (1.00) |
| Hiligaynon (hil) | 1.00 | 0.86 | 0.34 | 0.60 | 0.31 (1.00) | 0.41 | 0.39 (0.67) |
| Kikuyu (kik) | 1.00 | 0.80 | 0.40 | 0.60 | 0.31 (1.00) | 0.37 | 0.33 (1.00) |
| Yiddish (ydd) | 1.00 | 0.84 | 0.33 | 0.59 | 0.29 (1.00) | 0.37 | 0.36 (1.00) |
| Urdu (urd) | 0.99 | 0.83 | 0.54 | 0.68 | 0.38 (1.00) | 0.41 | 0.38 (1.00) |
| Danish (dan1931) | 1.00 | 0.81 | 0.40 | 0.61 | 0.30 (1.00) | 0.46 | 0.41 (1.00) |
| Hawaiian (haw1868) | 0.99 | 0.86 | 0.60 | 0.73 | 0.41 (1.00) | 0.62 | 0.58 (0.84) |
| Eastern Khumi Chin (cekak) | 1.00 | 0.87 | 0.51 | 0.69 | 0.36 (1.00) | 0.59 | 0.36 (1.00) |
| English (KJV) (eng-kjv) | 1.00 | 0.87 | 0.31 | 0.59 | 0.22 (1.00) | 0.22 | 0.14 (1.00) |
| German (deu1912) | 0.99 | 0.83 | 0.45 | 0.64 | 0.27 (1.00) | 0.36 | 0.27 (0.58) |
| Ilocano (iloulb) | 1.00 | 0.79 | 0.43 | 0.61 | 0.22 (1.00) | 0.37 | 0.35 (0.59) |
| Tagalog (tglulb) | 1.00 | 0.83 | 0.19 | 0.51 | 0.11 (1.00) | 0.34 | 0.11 (0.91) |
| Lingala (lin) | 1.00 | 0.83 | 0.25 | 0.54 | 0.13 (1.00) | 0.30 | 0.13 (0.69) |
| Indonesian (indayt) | 1.00 | 0.83 | 0.29 | 0.56 | 0.15 (1.00) | 0.26 | 0.23 (1.00) |
| Malay (zlmKSZI) | 1.00 | 0.82 | 0.23 | 0.52 | 0.10 (1.00) | 0.16 | 0.07 (1.00) |
| Nahuatl (Huasteca) (nheBl) | 1.00 | 0.82 | 0.25 | 0.54 | 0.10 (1.00) | 0.36 | 0.32 (0.75) |
**Gaps to the threshold:** Voynich A 0.09–0.44 below T (median 0.26); Voynich B 0.09–0.46 below (median 0.23).

**Where Voynich beat its own controls (still no claim):**
- Voynich A beat the pseudo-A maximum once, by 0.007 (Yapese), 0.22 below T.
- Voynich B beat the pseudo-B maximum three times: Arabic by 0.10 (0.53 vs 0.42; T 0.63; a real Arabic cipher
  scores 0.71–0.79), Nyanja by 0.01, Uyghur by 0.02. Arabic B is the only result of the 98 with a clear margin over
  its controls, and it still sits 0.10 under the threshold and 0.19 under the weakest planted crack. Under the prereg
  it is a miss. It is noted because an Arabic abjad attack (words of 4+ glyphs) is already in the queue
  (CLAUDE.md §6.5); if that test is run, this result is disclosed as seen beforehand.

**Agreement:** Voynich A settled (≥ 0.95) for 46 of 49 languages; Voynich B for only 29 of 49 (down to 0.42 for
Polish). B's instability under A's sign set is expected (E041: B's inventory differs) and is why B was secondary.

**Short-word languages** (Malayalam, Ewe, Tamil, Hawaiian, Arabic) give Voynich high raw lexrates (0.5–0.66), but
their pseudo-Voynich controls score just as high: almost any letter soup lands on short real words. This is exactly
what the controls are for (the lesson of E049's Hebrew near miss).

## Ledger
Pre-registered table: NO CLAIM with all languages validated → absence rule on the "other European and unlisted"
share of L-alpha-known (s = 0.35 × 0.27 × 0.8 coverage = 0.0756; m = 0.2) → **L × 0.94**; C's "simple or homophonic
substitution of these languages" share 0.05 → **C × 0.96**.

Arithmetic note: the script printed L × 0.941, C × 0.961 because it divided the validated count by 50 (including the
disclosed-untested Wycliffe) rather than the 49 that ran. The prereg governs (49 run, 49 validated = full factor); the
difference is 0.001.

| | M | L | C | O |
|---|---|---|---|---|
| Before (after E062) | 0.0078 | 0.9815 | 0.0093 | 0.0013 |
| **After E063** | **0.0083** | **0.9808** | **0.0095** | **0.0014** |

Sensitivity: with m = 0.1 the factor is L × 0.93 and L lands at 0.9807; from the honest-range edges (L 0.60, M 0.25,
C 0.13, O 0.02) the posterior is L 0.59, M 0.26, C 0.13. The ranking does not move.

**L-alpha-known after E063.** Of its prior share 0.35 of L, Hebrew/Turkish/Latin (E049–E050), the Slavic–Romanian–
Italian shortlist (E052) and now the "other" 0.27 have all been searched with m = 0.2. What is left of this form is
about 0.07 of L's original mass: the 0.2 miss allowance on everything searched, plus languages with no text on disk
(the 0.2 of "other" not covered: Catalan, Occitan, Basque, Albanian, Georgian, Armenian, Persian proper, medieval
German and Italian dialects, and the like). A 15th-century language written letter by letter with word boundaries
kept is now the least likely form of L, not the most.

## What this does not cover (stated plainly)
- Letter ciphers that break or hide word boundaries (the attack keeps spaces).
- Syllable writing (L-syll, 0.20 of L, untested), abbreviation systems beyond E053, transposition, nulls above 12%,
  nomenclators and codebooks, and any system where one Voynich word is not one plaintext word.
- Languages with no Bible on disk.
- Biblical language models against a possibly herbal text: that mismatch is what the m = 0.2 allowance is for.

## Reading for the project
The breadth step did what it was asked: it closed the attested-alphabet form of L almost completely, with known-answer
proof at every step and no false claims among 588 controls. It found nothing. Combined with E061 (the stems are
language-shaped, not a code alphabet) and E062 (the last verbose cipher class fails), the surviving pictures are:
a real language in a non-alphabetic or boundary-breaking system (syllables, abbreviation, or a word-level code), or a
meaningless text produced by a process that doubles words the way the generator cannot. The next tests should be
built to separate those two, not to add more alphabet languages.
