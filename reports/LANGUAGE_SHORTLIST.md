# E042 (attack step 2): the language shortlist — results

Pre-registration `reports/E042_PREREG.md` (sha b6060f92…fa49, commit 2507f60). Script
`experiments/e042_language_shortlist.py`. Results: `experiments/results/e042.json`, `e042_run.log`. This is a
measurement under working assumption L; no ledger change.

## Stage 2a: documented grammar (WALS)
**How rare is Voynich A's shape worldwide?** WALS has 156 languages coded on syllables, suffixing and reduplication.
- 46 of them (29%) have simple or moderately complex syllables and are suffixing.
- **35 (22%) also double words.**

The shape is **not rare**. The matches spread over Australia, Eurasia, Africa, the Americas and New Guinea, for
example Turkish, Mandarin, Japanese, Korean, Burmese, Amharic, Somali, Aymara and many Australian languages. A match
on these three features alone therefore means little.

**Candidates:**

| Out at 2a (complex syllables, as coded in WALS) | Through to 2b (not failed; some features uncoded) | No text |
|---|---|---|
| German, Polish, Hungarian, French, English, Lithuanian, Greek (Modern), Arabic (Egyptian), Albanian | Latin, Hebrew, Czech, Italian, Serbian-Croatian, Slovak, Romanian, Romani, **Turkish**, Yiddish, Dutch, Ukrainian, **Mandarin** | Occitan, Catalan, Slovene, Armenian, Albanian |

**Only two candidates are coded as passing all three WALS features: Turkish and Mandarin.** Hebrew and Armenian are
coded as doubling but lack a syllable code.

## Stage 2b: statistics against Voynich Currier A (cleaned, 8,806 tokens)
| Candidate | Fails (of 8) | Fails without R | R z | Note |
|---|---|---|---|---|
| **Hebrew** (Biblical) | 1 | 0 | +6.8 | closest overall |
| **Turkish** | 1 | 0 | +13.9 | the only plausible language passing all WALS features |
| Croatian | 1 | 0 | +21.7 | |
| Serbian-Croatian (1865) | 1 | 0 | +30.6 | |
| Czech (1613) | 1 | 0 | +34.2 | |
| Slovak | 1 | 0 | +48.0 | |
| Latin | 2 | 1 (Zipf) | +29.9 | |
| Ukrainian | 2 | 1 (Zipf) | +46.9 | |
| Romanian | 2 | 1 (Zipf) | +48.7 | |
| Italian | 2 | 1 (Zipf) | +49.0 | |
| Dutch | 3 | 2 | | |
| Mandarin (syllable tokens) | 3 | 2 | +14.5 | far too few distinct "words" when words are syllables |
| Romani (Carpathian) | 4 | 3 | | |
| Yiddish | 6 | 5 | | |

**By the pre-registered rule (at most 2 fails): SHORTLIST of 10:** Hebrew, Turkish, Croatian, Serbian-Croatian,
Czech, Slovak, Latin, Ukrainian, Romanian, Italian.

## What this really says
1. **The statistics separate languages on one thing only: doubling (R).**
   - Every candidate fails R. None doubles words in Bible prose anywhere near Voynich's rate.
   - On the other 7 features, nearly every candidate passes at A's size. These features don't discriminate between
     languages at this sample size, as feared before the run.
   - So the 10-language shortlist is broad, and its ranking is essentially **"which languages double words most"**.
2. **Two languages stand out on both lines of evidence:**
   - **Hebrew:** closest on R, and documented as a doubling language.
   - **Turkish:** the only plausible candidate passing all three WALS features, second-closest on R, and documented
     as doubling.
   - Both were present around 1400–1440:
     - Hebrew was the learned language of Jewish communities across Central Europe, Prague included.
     - Ottoman Turkish was in the Balkans after 1389, in contact with Hungary and Venice.
   - Both have been proposed before (Hebrew by Hauer & Kondrak 2016; Turkic readings by several authors). **None of
     those proposals passed independent checks.** That is a reason for care, not a point in their favour.
3. **The ordinary European vernaculars** (German, Polish, Hungarian, French, English) are out on syllable structure.
   Czech and the South Slavic texts pass the statistics, but only because their syllables aren't coded in WALS; they
   are known to be complex. This is a gap in the filter, stated here, not corrected after the fact.
4. **The profile is common worldwide (22%),** so the match is weak evidence for any one language. Step 3 must do the
   real work.

## Order for step 3 (attack), from this result
1. **Hebrew and Turkish first:** the top two by the statistics, and both doubling languages.
2. **Then the Slavic group** (Croatian, Serbian, Czech, Slovak, Ukrainian), which needs a syllable-structure check
   first.
3. **Latin, Romanian and Italian last:** each fails Zipf, and Latin is already excluded in its plain forms.
