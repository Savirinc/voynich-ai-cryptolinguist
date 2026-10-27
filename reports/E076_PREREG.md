# E076 pre-registration: light pieces (antonym/synonym-type) versus heavy pieces (grammar), and which languages are closest

Written 2026-10-27, before the run, at Arham's direction: pieces like English *im-possible*, Farsi *ba-tameez* /
*be-tameez*; find such patterns in Voynich, compare with other scripts, "see whom they are closer to"; the copy
generator is left out for now (so this test cannot speak to M versus L and carries **no ledger factor**).
Script `experiments/e076_light_heavy_pieces.py`; output `experiments/results/e076.json`, `e076_run.log`; report
`reports/LIGHT_HEAVY_PIECES.md`.

## What can and cannot be measured
Without meanings, an antonym (*possible / impossible*) and a synonym look the same: both forms sit in the same places.
So the test does not label pieces "opposite" or "same". It sorts swaps into:
- **light**: the new form sits where the old one sits (antonym- or synonym-making pieces: *un-*, *im-*, Farsi *nā-*);
- **heavy**: the new form moves to other places (grammar pieces: case endings, tense);
- **medium**: between.

## Measure
E075's machinery (kit, contexts from neighbours' pieces, swap pairs with ≥ 8 cores, both forms ≥ 5 occurrences,
consistency z with 300 sign-flip draws). **Lightness** of a swap a → b on core X: the share of other frequent words
whose context is less similar to aX than bX is (cosine), median over cores; 0.5 is what two random words give.
Light ≥ 0.80, medium 0.65–0.80, heavy < 0.65. **Profile** of a text: light, medium and heavy shares, consistent share
(z > 3), share of front pieces among light swaps and among heavy swaps. **Closeness** to Voynich: Euclidean distance
between profiles; languages with ≥ 10 eligible swaps are ranked.

## Texts
Voynich DEV prose lines (28,841 tokens; LOCKED_TEST excluded). Every Bible on disk with ≥ 38,841 tokens except
cmn-cu89s, jpn1965 (no word spaces), vie1934 (syllable-spaced) and engWycliffe; 28,841 tokens from token 10,000, cut
into Voynich line lengths; Arabic-script, Hebrew and Yiddish texts with marks removed. Includes Persian (pesOPV, Old
Persian Version 1895, public domain, downloaded 2026-10-27 for this test).

## Validity (known antonym pieces must come out light)
On whole texts (lines of 10 tokens): English *un-* pairs (*unclean/clean*; *unto, unless, under, until, understand…*
excluded) and German *un-* pairs (*unrein/rein*; *und, uns, unser…, unter…* excluded), cores ≥ 3 letters, both forms
≥ 5: median lightness ≥ 0.80 for both. Persian *nā-* reported. Otherwise VOID.

## Reported
The profile of every text; the ranking of languages by closeness to Voynich; every Voynich swap with its class,
lightness and examples (the Voynich candidates for antonym- or synonym-type pieces are the light ones).

## Disclosed (seen beforehand)
E075's Voynich results (consistent swaps and their shifts). Counts while choosing known answers: English *un-* 26
candidate pairs in KJV, German *un-* 41, Persian *nā-* 19, Persian *bi-*/*bā-* mostly not prefixes in this text.
Toy checks: on a toy with word-specific habits a planted light prefix scored 0.85 and planted case endings 0.53–0.55;
on a toy where all nouns shared identical neighbours lightness cannot work (0.64), which is why the cut-offs were set to
0.80 / 0.65 before any real text was measured. No real text has been measured. One attempt.
