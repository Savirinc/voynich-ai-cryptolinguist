# E010D pre-registration: do the two pages of the same month share material? (v1)

Written 2026-10-17T08:51Z (UTC), BEFORE any statistic below was computed on Voynich text. Its SHA-256 is recorded
in `experiments/results/e010d.json` (`prereg_sha256`) and is checked by `experiments/e010d_zodiac_shared.py`, which
aborts if the file changed. The file is set read-only after writing. Any change becomes `E010D_PREREG_v2.md`, is
logged in `experiments/FAILURES.md`, and v1 results are still reported.

**Scope.** These tests ask only whether structure predicted by two broad cipher classes is present. They do not
require the cipher tables. Nothing here proposes a reading of any Voynich word. A positive result is not a
decipherment and Gate 5 is untouched.

## 0. Disclosure: what the analyst had already seen
- The E010B/E010C pre-registrations and result summaries: E010B month-name tests were negative for one-glyph-per-
  letter spellings and uninformative for verbose spellings. Labels do not behave as day labels, and labels resemble
  their own page more than other pages (ordered alignment z = -3.6). In E010C, Greshko's published Naibbe tables
  give 0 own-month runs on all pages. Also the E010B per-page label counts and sizes, and E010B's remark that
  labels such as `otaly`, `okaly` and `otal` occur on several zodiac pages.
- For this design: page-header metadata (quire, page-in-quire, illustration, hand, Currier, fold) for f67r1–f76v,
  and the clean-token counts per page by locus type (L/C/R/P) for f67r1–f73v. These are sizes only, used to choose
  the control set and the size normalisation. No word content, overlap, sharing count or n-gram statistic was
  computed or viewed for any page before this file was written.
- In this session the analyst has not printed any zodiac word list. The E010B prereg states that the full label
  lists were printed in an earlier session, while the anchor dataset was being built.

## 1. Data and text units
- ZL3b IVTFF (protocol §1 hash), parsed by `vcl.corpus.ivtff`. **DEV only**: tokens on LOCKED_TEST leaves
  (protocol §1) are never read. No leaf in 67–73 is locked.
- **Token**: a parser token with `is_clean` true (`eva` matches `[a-z]+` and contains no uncertain glyph). The
  first alternative reading is used, braces are dropped, and an uncertain space counts as a word break (protocol
  default). Non-clean tokens are dropped and break word bigrams.
- **Page text unit U_p**: all clean tokens of page p, in transcription order, with their line (locus) ids. On the
  12 zodiac pages this is exactly the label (L) plus circular-ring (C) text: the zodiac pages have no P/R loci. A
  multi-token label contributes each token. n_p = the number of clean tokens and V_p = the set of word types.
- **Zodiac pages Z** (12, `vcl.anchors.ZODIAC`): f70v2 mars, f70v1 aberil, f71r aberil, f71v may, f72r1 may,
  f72r2 jong, f72r3 iollet, f72v3 augst, f72v2 septe(m)b(r), f72v1 octe(m)bre, f73r nove(m)bre, f73v decebre.
  **Same-month pairs M** = {(f70v1, f71r), (f71v, f72r1)}. The other 64 zodiac pairs are "other".
- **Hand-4 run H** (26 pages, transcription order): f67r1 f67r2 f67v2 f67v1 f68r1 f68r2 f68r3 f68v3 f68v2 f68v1 f69r
  f69v f70r1 f70r2 + the 12 zodiac pages. This is the contiguous astronomical/cosmological/zodiac block in quires
  I–L. All 26 pages are hand 4 (Davis) with no Currier language, and all are circular-diagram pages with ring
  text and labels. **Adjacent pairs A** = the 25 pairs of consecutive pages in H. Both M pairs are in A.
  **Adjacent controls** = A \ M (23 pairs, 9 of them zodiac–zodiac).
- **Rest of DEV for a pair (p, q)**: every clean DEV token not on page p or page q, including the other zodiac and
  run pages. f_rest(w; p, q) = the token count of w there, and N_rest = their number.

## 2. Physical structure and how adjacency is handled (pre-declared)
- Both same-month pairs are **consecutive in the zodiac sequence and are facing pages of one opening**. f70v1
  (quire J, last leaf, foldout verso) faces f71r (quire K, first leaf): a quire boundary. f71v faces f72r1
  (foldout recto), both in quire K. All zodiac pages are hand 4, so hand and Currier language cannot separate
  same-month from other pairs.
- Consecutive pages share a scribe session, page-level style and possible drift. E010B already found that labels
  resemble their own page more than other pages. Adjacency alone could therefore inflate sharing between the two
  same-month pairs.
- Handling: T1 compares same-month pairs with all other zodiac pairs, which is NOT adjacency-robust. **The codebook
  hypothesis can be supported only if T2 also rejects.** T2 and T3 compare the same-month pairs only with other
  *consecutive* pairs of the same scribe-4 circular-diagram run (the adjacent controls), using an exact relabeling
  null restricted to adjacent pairs. Two adjacent controls cross a quire boundary as f70v1|f71r does (f68v1|f69r,
  quires I/J, and f72v1|f73r, quires K/L), and several are panels of the same foldout surface. Physical relations are listed in the results JSON for transparency.

## 3. Statistics

### T1, codebook / nomenclator (one Voynich word = one plaintext word)
- Prediction: the two pages of a month share at least one exact word type that is rare in the rest of DEV, more
  than other zodiac page pairs do.
- Pair score: S(p, q) = Σ over w ∈ V_p ∩ V_q with f_rest(w; p, q) ≤ K (K = 3) of log2((N_rest + 1) /
  (f_rest(w; p, q) + 1)). This is the size-normalised **s(p, q) = S(p, q) / (n_p · n_q / 10⁴)**. In the rare-word
  regime, the expected number of shared rare types under independent sampling scales with n_p · n_q.
- T1 = mean of s over M − mean of s over the 64 other zodiac pairs.
- Null N_all, every relabeling of month slots: exact enumeration of all 1,485 ways to choose 2 disjoint pairs of
  zodiac pages as "same-month pairs". This is equivalent to every permutation of the 12 pages over the 12 slots.
  p = #{configurations with T ≥ T_obs} / 1485 (the observed configuration counts as one). One-sided.

### T2, codebook robustness against adjacency
- The same s(p, q). T2 = mean of s over M − mean of s over the 23 adjacent controls.
- Null N_adj: exact enumeration of all 276 ways to choose 2 disjoint pairs from the 25 adjacent pairs A, with T
  computed for each (chosen versus the other 23). p = #{T ≥ T_obs} / 276. The minimum attainable p is 1/276 =
  0.0036.

### T3, verbose homophonic cipher with unknown tables (Naibbe-like)
- Prediction: two encryptions of the same month name with the same unknown tables reuse the same table entries.
  Same-month pages should therefore share glyph chunks, words and word pairs more than different-month adjacent
  pages do.
- Features of page p, as a set G_p: (i) the character n-grams, n = 3, 4, 5, of `^w$` for every clean token w (this
  includes prefix and suffix chunks); (ii) the whole word `W:w`; (iii) the word bigram `B:w1 w2` for consecutive
  clean tokens on the same line.
- Weight: idf(g; p, q) = ln((N_rest + 1) / (df_rest(g; p, q) + 1)). df_rest is the number of rest-of-DEV tokens
  containing g for (i) and (ii), and the number of rest-of-DEV same-line consecutive clean-token pairs equal to g
  for (iii).
- Pair score: c(p, q) = Σ over g ∈ G_p ∩ G_q of idf² / sqrt(Σ over G_p of idf² · Σ over G_q of idf²), the cosine of
  the binary idf-weighted feature vectors.
- T3 = mean of c over M − mean of c over the 23 adjacent controls. The null is N_adj as in T2 (276 configurations).

### Test family and alpha
- Family {T1, T2, T3}, Holm at family-wise α = 0.01. Thresholds: 0.01/3, 0.01/2, 0.01.

### Secondary (descriptive, not in the family)
- T1's statistic under a zodiac-only adjacency null (11 consecutive zodiac pairs, 45 configurations; min p 0.022).
- T3's statistic under N_all (1,485).
- T1/T2 with K = 0 and K = 10, and without size normalisation.
- For (f70v1, f71r) and (f71v, f72r1): the list of shared word types with f_rest ≤ K, giving their f_rest and the
  locus type (L/C) on each page, and the top 15 shared T3 features by idf. Descriptive only, with no reading.

## 4. Decision rules
- **Codebook: SUPPORTED** iff T1 AND T2 are both rejected under Holm. If T1 is rejected but T2 is not, this is
  reported as "same-month sharing not separable from adjacency" and is not support.
  **NEGATIVE** iff not supported AND the codebook power (§5, mechanism a1, the share of replicates in which both T1
  and T2 are Holm-rejected) is ≥ 0.8. Otherwise **UNINFORMATIVE** (power < 0.8). A scoped secondary verdict uses
  mechanism a2.
- **Verbose (Naibbe-like): SUPPORTED** iff T3 is rejected under Holm. **NEGATIVE** iff not supported AND T3's
  power (mechanism b, Holm-rejected share) is ≥ 0.8. Otherwise **UNINFORMATIVE**.
- **Calibration guard**: a test whose false-positive rate (unadjusted p < 0.01) is > 0.03 in control c (no
  insertion), or whose Holm rejection rate is > 0.03 in control d (drift, no insertion), is flagged
  "miscalibrated" and cannot yield SUPPORTED. T1 is expected to fail the drift guard, because that is the reason T2
  exists. T1's role in the codebook decision is then only as a necessary condition alongside T2.
- Whatever the outcome, no Voynich word is read or glossed.

## 5. Synthetic power and false-positive controls (same code, same layout)
- **Layout**: every synthetic manuscript copies, for all 26 pages of H, the real line structure (lines, locus
  types and clean-token count per line). Filler tokens are drawn i.i.d. by token frequency from DEV clean tokens
  **outside H**. The synthetic "rest of DEV" is the real DEV outside H plus the synthetic H pages. Real text from
  H is never used in a synthetic manuscript.
- Mechanisms (one secret key per synthetic manuscript):
  - **a1, random codebook**: each of the 10 distinct months gets a distinct codeword drawn uniformly from the
    *word types* of DEV-outside-H (mostly hapaxes, like zodiac labels). Each zodiac page has one uniformly random
    token position (label or ring) replaced by its month's codeword.
  - **a2, novel codebook** (secondary): as a1, but the codeword is a new string absent from DEV. It is built from
    the first half of one random DEV type and the second half of another, and resampled until absent from DEV and
    distinct from the other codewords.
  - **b, random Naibbe-like tables**: Greshko's table structure (`vcl.synthetic.naibbe_exact`) with the glyph
    strings randomly permuted across letters within each (state, table), giving fresh random verbose homophonic
    tables per manuscript. Each zodiac page gets an independent encryption (`encode_tokens`, no space removal) of
    its month name `naibbe_exact.clean(month_latin_script)`. The encryption replaces a contiguous run of tokens in
    one random circular-ring (C) line long enough to hold it, or the longest C line if none is.
  - **c, no insertion**: the false-positive rate.
  - **d, drift, no insertion**: pages are generated in H order. Each filler token is, with probability ρ = 0.25, a
    copy of a uniformly random token of the previous page, and otherwise a fresh draw. This models adjacency/
    scribe drift, the confound T2/T3 are built for.
  - Secondary: a1 + d and b + d (signal under drift).
- 200 replicates per mechanism. In each replicate T1, T2 and T3 are computed exactly as on the real data, including
  the exact nulls, and Holm is applied. Reported: the unadjusted rate p < 0.01 per test, the Holm-rejection rate
  per test, and the joint T1 ∧ T2 Holm-rejection rate (codebook power).
- Master seed 20261019. Per-replicate seeds are derived from sha256(mechanism|replicate).
