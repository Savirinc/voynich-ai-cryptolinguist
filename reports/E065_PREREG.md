# E065 pre-registration: the syllable route, go/no-go

Written 2026-10-25, before the run. Script: `experiments/e065_syllable_gonogo.py`. Output: `experiments/results/e065.json`,
`e065_run.log`, report `reports/SYLLABLE_GONOGO.md`. Updates `LEDGER.md` (absence rule only, or no factor).

## Question
Within L, the two leading forms are now tied (0.29 each): a known language written with **syllable signs**, and a lost
or unrecorded language. Only the first can be searched with text we own. Before building a syllable attack, two cheap,
key-free checks decide whether any candidate language's syllable structure can fit Voynich at all.

**Terms.** A *syllabary* writes each syllable with one sign (Linear B, Japanese kana). A *CV-reduced* syllabary writes
only the onset consonant(s) and the vowel, dropping the closing consonant (as Linear B does). The *final-syllable
inventory* of a language is how many distinct last syllables its words use.

## Half 1: could Voynich words be syllable-sign spellings of a known language?
If each Voynich word is a real word written sign by sign, its **last glyph group** is the word's last syllable sign. Voynich
has few distinct final groups: E026's segmenter finds about 28 endings covering 95% of suffixed tokens. A one-to-one
syllabary cannot have fewer final signs than the language has final syllables.
- **Voynich side (E95):** the number of final-group classes (E026 suffix with E061's settings on DEV, the empty suffix
  as its own class) covering 95% of the 28,841 DEV word tokens. Also reported: the last S3 unit inventory (U95).
- **Language side (F95):** for each candidate, words 10,000–38,841 syllabified by a declared crude rule (nuclei =
  maximal vowel runs; one consonant to the coda, the rest to the next onset; marks stripped; *y* a vowel only when not
  next to a vowel, never in Turkish). F95 = final syllables covering 95% of word tokens, in two renderings: FULL and
  CV-reduced. Also reported: initial-syllable inventory I95, all-syllable inventory S95, syllables per word.
- **Candidates (11):** Latin, Italian, German, Czech, Hungarian, Byzantine Greek, Turkish, French, English, Polish,
  Dutch (the languages of 15th-century Europe and its neighbours that are on disk in Latin or Greek script; Hebrew and
  Arabic are abjads, their syllabification needs vowels we do not have, and they are out of scope here).
- **Syllabifier gate:** syllables per word must be within 0.4 of the typical value declared in the script (Latin 2.4,
  Italian 2.3, German 1.8, Czech 2.0, Hungarian 2.3, Greek 2.5, Turkish 2.5, French 1.7, English 1.4, Polish 2.1,
  Dutch 1.7); otherwise that language is UNRELIABLE and not judged.
- **Pass:** F95 ≤ 2 × E95 in either rendering. The factor 2 covers homophone merging and segmentation error.

## Half 2: could each Voynich word be one syllable of a European text (pfeaster's hypothesis)?
The forum's own go/no-go: Voynich has 6,077 distinct words per 28,841 tokens, 68% seen once. A syllable stream of a
European language must reach that.
- For each candidate: the stream of 28,841 consecutive syllables (from syllable 20,000) by the same syllabifier:
  distinct types, hapax share, Zipf slope, R and NR (E031 statistics on the stream).
- **Pass:** 4,860 ≤ types ≤ 7,290 (±20% of Voynich) and hapax ≥ 0.55.
- **Reference row (not a candidate):** Vietnamese (vie1934), a real syllable-spaced text, excluded as a plain language
  by X5 for its small vocabulary; it shows what a true syllable stream looks like.

## Seed rule
A language within 10% of a bar (F95, types) or 0.055 of the hapax bar is re-measured on 10 random windows; ≥ 8 of 10
decide.

## Outcomes
| Outcome | Rule | Ledger |
|---|---|---|
| **GO** | any reliable language passes half 1 or half 2 | none; the passing languages go to a validated syllable attack under its own pre-registration (known answers first, zero false claims) |
| **NO GO** | no reliable language passes either half | absence rule on L-syll: share 0.20 of L, coverage 0.6 × (reliable languages ÷ 11), m = 0.2 → **L × (1 − 0.20 × coverage × 0.8)**, about × 0.90 with all 11 reliable. Within L the lead passes to the lost-language form |

Why coverage 0.6: these 11 languages are the main written languages of the region and period, but a syllabary of
Hebrew, Arabic, a Slavic language not on disk, or a non-European language is not tested here.
Why this is only a go/no-go: passing shows the structure *could* fit; only a validated attack that reads text can move
L up. Failing is logical within scope (too many final syllables for the signs available, even dropping codas), with m
= 0.2 for cleverer many-to-one systems and the crude syllabifier.

## Disclosed
- E027 (glyph groups S2/S3 put Voynich inside the simple-syllable range), E024 (34 S3 units), E026/E061 (about 28
  endings, 892 stems covering 95%), X5 (one-syllable-per-word languages have far too few words), E033/E034 (no plain
  prose matches Voynich's word statistics). E024's report had already noted the Telugu vowel-sign defect.
- The syllabifier was exercised on six sample words per language in a dry run (output in `e065_run.log` is not kept;
  samples such as *ci-vi-ta-tis*, *ge-fun-den*, *συλ-λα-λουν-τες* looked right; *eg-re-dien-tur* shows the crude
  cluster rule). No inventory, stream statistic or Voynich E95 has been computed.
- E061's segmenter ending counts for 22 languages (NSUF95 7–148) were seen; they are a different statistic (unsupervised
  endings, suffixed tokens only) and are not used here.
- One attempt (standing rule 9).
