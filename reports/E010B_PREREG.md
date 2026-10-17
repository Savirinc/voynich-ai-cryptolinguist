# E010B pre-registration: zodiac month-name and day-label tests (v1)

Written 2026-10-17T06:35Z, before any statistic was computed on Voynich zodiac labels. Its SHA-256 is recorded in
`experiments/results/e010b.json` (`prereg_sha256`). This file is not edited after the first run. Any change becomes
`E010B_PREREG_v2.md`, logged in `experiments/FAILURES.md`, and v1 results are still reported.

**Scope.** These tests only ask whether structure predicted by two hypotheses is present. Nothing here proposes a
reading of any Voynich word. A positive result would not be a decipherment: Gate 5 is untouched.

## 0. Disclosure: what the analyst had already seen
While assembling the E010 anchor dataset, the analyst (Claude) printed the full ZL3b label lists for f70v2–f73v
and read the transcription's page comments. No counts, overlaps or statistics were computed. The analyst
informally noticed that a few labels (e.g. `otaly`, `okaly`, `otal`) occur on several pages, and that labels
often begin with `ot`/`ok`. The published literature already reports the same (voynich.nu labels page: 299
zodiac labels, 80% hapax, most frequent label word 5 occurrences; `ok`+`ot` = 52% of tokens). H2 is therefore
**not blind**, and that is why its decisive null (Nb) is a within-zodiac shuffle that keeps those known
properties. H1's predicted pair structure was fixed from the Latin-script month spellings alone, before any
glyph-level comparison of candidate words was made.

## 1. Data
- ZL3b IVTFF (protocol §1 hash), parsed by `src/vcl/corpus/ivtff.py`. Page structure (label groups, circular
  text rings) is read by `vcl.anchors.zodiac_structure` from the transcription's own comments and locus codes.
- Zodiac pages, in order: f70v2 Pisces `mars`, f70v1 Aries `aberil`, f71r Aries `aberil`, f71v Taurus `may`,
  f72r1 Taurus `may`, f72r2 Gemini `jong`, f72r3 Cancer `iollet`, f72v3 Leo `augst`, f72v2 Virgo
  `septe(m)b(r)`, f72v1 Libra `octe(m)bre`, f73r Scorpius `nove(m)bre`, f73v Sagittarius `decebre`
  (spellings from voynich.nu/writing.html). Leaves 70–73: **none is LOCKED_TEST** (locked leaves are
  1, 8, 9, 30, 35, 38, 51, 52, 56, 75, 86, 87, 102, 105, 114), so no zodiac folio is excluded. f74 (presumably
  Capricorn and Aquarius) is missing from the manuscript.
- Token form: the parser's `eva` (first alternative, braces dropped). A token containing `?` or a rare glyph
  `@nnn;` is dropped from candidate sets. A label containing such a token is excluded from H2 statistics and
  counted separately. The glyph unit is the EVA character.

## 2. H1: the month name is written in Voynichese near the month annotation
**Candidate set K_p (primary), fixed by structure:** the tokens of (i) every label in the page's label group
whose ZL heading contains "inner" (case-insensitive), (ii) every label in a group whose heading contains
"central", and (iii) the first token of the innermost circular text ring (the last circular ring in
transcription order). A multi-word label contributes each of its tokens.
**Full-page pool F_p (for null N2):** all clean tokens on the page (labels plus circular text).

**Predicted-similar pairs P (8):**
- Same month written twice: (f70v1, f71r) `aberil`, and (f71v, f72r1) `may`.
- The `-bre` group {f72v2, f72v1, f73r, f73v}: all 6 pairs.

All other page pairs form Q (58 pairs).

**Similarity:** sim(w, v) = max(longest common prefix, longest common suffix), in EVA characters. Identical
words score their length.

**Statistics.**
- T1 (primary): s(p, q) = max over w in K_p, v in K_q of sim(w, v), and T1 = mean over P of s − mean over Q of s.
- T2: the same with s̄(p, q) = the mean over all w, v of sim. T2 is the expected T of one uniformly random
  word per page.
- T3 (search test): T_sel(choice) = mean over P of sim(w_p, w_q) − mean over Q, for one chosen word per page.
  T3 = the maximum of T_sel, found by coordinate ascent with 20 random restarts.

**Nulls (one-sided, larger = more structure).**
- N1, month-assignment permutation: the 12 pages are randomly permuted over the 12 month slots, so P/Q membership
  is reassigned. Used for T1 and T2 (10,000 permutations) and for T3, rerunning the full search each time
  (2,000 permutations). T3's p is therefore corrected for the search.
- N2, candidate-set null: each K_p is replaced by a random same-size sample without replacement from F_p.
  Used for T1 (10,000 draws).
- Also reported, but not part of the test family: the *uncorrected* p of the best T3 selection against the
  distribution of T_sel for single random selections. This shows how much searching inflates significance.

p = (1 + #{null ≥ obs}) / (1 + n). Effect size: z = (obs − mean_null) / sd_null.

## 3. H2: the nymph labels are day labels
**Counts first:** the number of labels per page and per ring group, compared with the expected 30 (or 15 + 15
on the split Aries and Taurus pages).

**Label string:** the locus tokens joined with '.'. **Sequence order:** label groups and labels in transcription
order (ZL/Petersen order).

**Statistics.**
- O (recurrence): the sum over page pairs p < q of |label types of p ∩ label types of q|, using exact string match.
- A (ordered alignment): for each page pair, the best cyclic shift c of q's sequence maximising
  mean_{i < min(n_p, n_q)} esim(p_i, q_{(i+c) mod n_q}), where esim = 1 − Levenshtein/max length. A is the mean of
  that maximum over the 66 pairs. Taking the maximum over shifts inside the statistic means the null pays the same
  search cost.

**Nulls (one-sided).**
- Nb (decisive): all clean zodiac labels are shuffled at random across the zodiac label loci, keeping page sizes.
  10,000 shuffles.
- Na (as requested; confounded): each zodiac label is replaced by a random non-zodiac Voynich label (an L locus
  outside f70–f73 and outside LOCKED_TEST leaves) of the same EVA length, or the nearest length if none exists.
  10,000 draws. Zodiac labels have a known section style (ot/ok), so Na can fire from style alone. **H2 counts as
  supported only if the Nb tests are significant.**

## 4. Test family and decision rule
Family: {H1-T1-N1, H1-T1-N2, H1-T2-N1, H1-T3-N1, H2-O-Nb, H2-A-Nb, H2-O-Na, H2-A-Na}, with Holm correction at
family-wise α = 0.01.
- H1 is *supported* if H1-T1-N1 survives Holm. H2 is *supported* if H2-O-Nb or H2-A-Nb survives Holm.
- A non-significant result counts as *negative* only if H3 shows power ≥ 0.8 for that test under at least one
  mechanism at the matching structure. Otherwise it is *uninformative*.
- Whatever the outcome, no Voynich word is read or glossed.

## 5. H3: synthetic positive and negative controls (same code, same structure)
- Synthetic pages copy the Voynich structure exactly: the same 12 pages, the same per-page label counts, ring
  groups and |K_p| sizes (structure only, no words).
- Calendars (two languages, both train family 'romance'):
  - French month names on the Voynich month slots: mars, avril, avril, mai, mai, juin, juillet, août,
    septembre, octobre, novembre, décembre. Day labels are French cardinals un … trente (compounds written
    without spaces or hyphens).
  - Latin: martius, aprilis, aprilis, maius, maius, iunius, iulius, augustus, september, october, november,
    december. Day labels are Latin cardinals unus … triginta (compounds without spaces).
  - Filler words are random word types of length 3–9 from a `tune`-role book of the same language
    (book_roles.json).
- Mechanisms: `mono` and `homophonic` from `vcl.synthetic.encoders` (train families), plus a local *verbose
  homophonic* variant (homophonic, then a fixed extra modifier glyph after each occurrence of one third of the
  letters). One key for the whole synthetic manuscript.
- Conditions:
  - (i) H1-true: one random member of each K_p is the encoded month name, the rest are filler.
  - (ii) H2-true: the labels are the encoded day labels in order. Full pages get days 1–30, with the last
    29/30 label truncated when a page has 29. Split pages: the first page of a pair gets days 1–15, the second
    16–30.
  - (iii) Control: the same as (i) and (ii) combined, but with month slots and day labels shuffled across
    pages/loci before encoding (no structure).
- Replicates: 100 per mechanism × language × condition, using 1,000 permutations (N1/Nb/Na/N2) and 100 search
  permutations for T3. Power = the fraction with p < 0.01, without Holm, reported per test. The false-positive
  rate comes from condition (iii).
- Seeds: E010B master seed 20261017. Everything is recorded in e010b.json.
