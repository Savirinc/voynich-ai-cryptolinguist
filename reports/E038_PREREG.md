# E038 pre-registration (attack step 1b): the true sign inventory

Written 2026-10-22, before the run. Script: `experiments/e038_sign_inventory.py`. Working assumption L. This is a
measurement, with no ledger factor.

## Questions
- **A. Five alternations:** are the two forms one sign or two? E037 found that most neighbouring near-copies come
  from five alternations: e/ee, r/l, t/k, d present or absent, q present or absent.
- **B. Positional forms:** does any glyph look like another glyph's start or end shape, as letters do in Arabic and
  Urdu?
- **C. q:** is q- a prefix that does a job, or just spelling?

## Method, Part A (key-free)
**Minimal pairs.** These are pairs of words that differ only by the alternation (e.g. *chol/chor*, *okeedy/qokeedy*),
both seen at least 5 times.

**Two ways of measuring how alike the two words of each pair are:**
- **PAGE:** do they appear on the same pages? This is the cosine of their page distributions.
- **NBR:** do they have the same neighbours? This is the cosine of their left and right neighbours within the line.
  - Neighbours among the 300 most common words are kept as words; rarer ones are reduced to their last glyph.
  - A neighbour that is the word itself, or one glyph different from it, is ignored.

**Two baselines for each pair, with exactly the same token counts (20 draws each):**
- **SELF:** one word of similar frequency, its tokens split at random into two groups. This shows how alike "the
  same word" looks.
- **RAND:** two unrelated words of similar frequencies. This shows how alike "different words" look.

**Score.** S = Σ(pair − RAND) ÷ Σ(SELF − RAND), summed over pairs.
- S = 1 means the pair behaves like one word.
- S = 0 means it behaves like two unrelated words.
- A 95% bootstrap interval over pairs is reported.

**Calibration on known answers** (Latin Vulgate, first E033 window; pages are chunks of Voynich's mean page size):

| Control | How it's built | Expected |
|---|---|---|
| **F, free variant** | Every *e* written *E* at random, half the time, so *e/E* are known to be one sign | S near 1 |
| **C, real contrast** | Latin's own minimal pairs r/l, t/s, e/i (different letters, and so different or related words) | S low |

For each measure, t = (S − C) ÷ (F − C) places Voynich between the controls. **A measure is VOID if F − C < 0.4**:
the method cannot tell variants from contrasts.

**Verdict per alternation** (needs at least 10 pairs; otherwise INSUFFICIENT):

| Verdict | Rule | Meaning |
|---|---|---|
| FREE VARIANT | t_nbr ≥ 0.75 and t_page ≥ 0.75 | One sign, written two ways at random |
| SCRIBAL/SECTIONAL VARIANT | t_nbr ≥ 0.75 and t_page ≤ 0.5 | Same word, but different scribes or sections prefer different forms |
| GRAMMATICAL (related forms) | t_page ≥ 0.75 and t_nbr ≤ 0.25 | Same topic but different neighbours: two forms of one word, as inflection does |
| CONTRASTIVE (different signs) | t_nbr ≤ 0.25 and t_page ≤ 0.25 | Two different signs making different words |
| MIXED | otherwise | |

## Part B: positional forms
- **Each glyph's position profile:** the share of its occurrences at word start, middle and end, for words of 2+
  glyphs.
- **Candidate pairs** are complementary: profile overlap < 0.10, and both glyphs seen at least 200 times.
- **Context compared:**
  - the glyph to the left, if neither glyph is mostly word-initial;
  - the glyph to the right, if neither is mostly word-final.
  - Start-versus-end pairs have no comparable side, so they are listed but not judged.
- **A pair is a CANDIDATE POSITIONAL FORM** if its context cosine is at least 0.8 × the control's and in the top 10%
  of all glyph pairs.
- **Control:** Latin with every word-final *s* written *S*. The s/S pair must be complementary and in the top 10%.
  If not, Part B is VOID.

## Part C: q
- **The q± verdict from Part A:**
  - FREE or SCRIBAL means q is spelling;
  - GRAMMATICAL or CONTRASTIVE means q does a job, as a prefix or a different word.
- **Also reported:** the share of words starting with q in Currier A and B, and at line start versus elsewhere.

## Limits (stated now)
- **Units are single EVA glyphs.** Benches (ch, sh) and minim runs are not merged here; that is a follow-up once
  Part A is known.
- **Neighbour similarity is sparse** in a text where 68% of words occur once. The SELF and RAND baselines, matched
  in token counts, are there to absorb that.
- **The Latin contrast control includes related forms** (e.g. *regis/reges*), since real minimal pairs do. This
  makes C higher and the test more conservative about calling anything a free variant.

## What was seen before writing this (disclosed)
- E037's alternation counts and the positional habits of glyphs known from the literature (q initial; y, n, l, r
  final; gallows early).
- The scoring functions were checked on a toy random corpus. No measure here has been computed on Voynich or Latin.
