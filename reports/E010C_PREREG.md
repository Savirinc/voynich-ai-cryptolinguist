# E010C pre-registration: are the zodiac month names written in Naibbe on their own pages?

Written 2026-10-17, BEFORE any statistic below was computed on Voynich text. The Naibbe encryptions of the month
names were enumerated (from the cipher tables alone) before writing this; no Voynich text was matched against them.
Any change after the first run is a new version, logged in experiments/FAILURES.md.

## Hypothesis
HN: on each zodiac page (f70v2–f73v, 12 pages, `vcl.anchors.zodiac_pages()`), the ring text contains the page's
month name (the later-hand Latin-script name, `month_latin_script`, normalised with Greshko's `clean_line`)
enciphered with the **published Naibbe tables** (Greshko 2025; `vcl.synthetic.naibbe_exact`, tables sha256
4e7cfd54…), i.e. as a run of consecutive Voynich words w1..wk with a segmentation of the name into 1–2-letter
units u1..uk such that each wi is a possible Naibbe output for ui (unigram: any of the 6 unigram glyphs for the
letter; bigram: any prefix(letter1)+suffix(letter2) glyph pair that is not a unigram glyph).

This is a test of one SPECIFIC hypothesis (the author used these exact tables). The tables are a 2025
reconstruction built from common Voynich words, so a priori it is very unlikely; isolated one-word matches are
expected to be common by construction. The test therefore compares each page's OWN month against OTHER months on
the SAME text, which controls for that base rate.

## Data
- Ring text: all tokens of all `text_rings` of each page, in transcription order, one sequence per ring;
  only clean EVA tokens (no uncertain/illegible glyph markup); a non-clean token breaks a run.
- Months: the 10 distinct cleaned names (mars, aberil, may, iong, iollet, augst, septembre, octembre, novembre,
  decembre); duplicates (aberil ×2, may ×2) kept as their pages.
- LOCKED_TEST leaves excluded (none of 70–73 are locked).
- Space removal (3% merged words) is ignored: a Voynich word must encode exactly one unit.

## Statistic
score(page, M) = the maximum number of plaintext letters of M covered by one contiguous run of ring words that
matches consecutive units of some segmentation of a contiguous substring of M (runs of ≥ 2 words only; a single
matching word scores 0).
Primary T = mean over the 12 pages of [score(page, own month) − mean over the other 9 distinct months of
score(page, M)].

## Null and decision
- Null: 10,000 permutations of the month-to-page assignment (shuffle the 12 page labels, duplicates kept).
- One-sided p = P(T_null ≥ T_obs). alpha = 0.01. HN is SUPPORTED only if p < 0.01 AND at least one page has an
  own-month score ≥ 4 letters.
- Secondary (descriptive, no decision): (a) the longest own-month run per page with its words; (b) the null rate of
  runs: the same score for every month computed on all non-zodiac DEV prose/circle lines, giving how often a run
  covering ≥ L letters arises by chance; (c) any exact full-name match anywhere in DEV text.

## Positive control (power)
On copies of the real zodiac rings, replace one random contiguous run of words in one ring per page with a true
Naibbe encryption of the page's month (seeded `naibbe_exact.encode_tokens`, space removal off). Run the identical
test on 200 such replicates; power = share with p < 0.01. Also 200 replicates where the inserted month is a
DIFFERENT page's month (false-positive check, expected ≈ 1%). If power < 0.8 the result is reported as
uninformative, not negative.
