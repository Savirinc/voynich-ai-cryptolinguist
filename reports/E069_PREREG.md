# E069 pre-registration: do Voynich words have partners that persist across the book?

Written 2026-10-25, before the run. Script: `experiments/e069_word_partners.py`. Output: `experiments/results/e069.json`,
`e069_run.log`, report `reports/WORD_PARTNERS.md`. Updates `LEDGER.md`.

## Question
Inside L the leading form is a language nobody recorded, which can only be tested on grammar shape. One shape property
separates every language from a copying process: **words have partners.** In a real text, certain pairs of words seek
each other out (king and son, bread and eat) because they mean related things, and they keep doing so from the first
half of the book to the second. A copy-and-change process creates clusters by *proximity* (a word copied from the line
above), so pairs that sit together in one place need not sit together elsewhere. Does Voynich's partnership persist
across halves, like a language, or not, like the generator? Arham's framing: the work continues inside L with M kept
symmetric; this test can be won by either.

**Terms.** *Association* s of a pair in a half: log of (lines containing both + 0.5) over (expected by chance + 0.5).
*RAW*: the rank correlation of s between the two halves over all pairs of the 200 commonest words. *Baseline*: the same
RAW after shuffling each half's words across its lines (frequencies and line lengths kept), repeated 3 times.
**STAB = RAW − baseline.** Positive STAB means partnerships persist beyond what word frequencies alone produce.

## Data
- **Voynich ALL (primary):** DEV prose lines in manuscript order (28,841 tokens), halves by token count.
- **Voynich A-only and B-only (secondary):** the Currier A lines and the B lines, each halved in order.
- **Languages:** 60 Bibles (E064 TOK), one random stretch per language from word 2,000 at each of the three sizes (ALL,
  A, B), cut into pseudo-lines of Voynich DEV line lengths.
- **Generator:** 10 random stretches of the E032 output at each size, own lines.
- K = 200 commonest words of each text, kept only if present in both halves. Seed 69069.

## Known-answer gate
At least 8 of the 10 generator stretches must fall below the 10th percentile of the 60 languages (ALL size). Otherwise
the measure does not separate a copying process from language, and the test is VOID.

## Decision (primary, Voynich ALL)
| Outcome | Rule | Factor |
|---|---|---|
| **LANGUAGE-LIKE** | Voynich STAB ≥ the languages' 10th percentile and > every generator stretch | **L × 3** |
| **GENERATOR-LIKE** | Voynich STAB ≤ the generator median | **M × 3** |
| INCONCLUSIVE | otherwise | none |

**Secondary check, fixed now.** Voynich's two halves in reading order are mostly Currier A (first) and B (second);
a dialect shift could lower STAB for a reason that has nothing to do with meaning. So the primary verdict stands only
if the **A-only** result agrees in direction (LANGUAGE-LIKE needs A ≥ its languages' 10th percentile and > its generator
maximum; GENERATOR-LIKE needs A ≤ its generator median); otherwise INCONCLUSIVE. B-only is reported.

**Seed rule:** Voynich STAB within 0.05 of a boundary → languages and generator stretches re-drawn with 10 seeds, ≥ 8 of
10 agree, else INCONCLUSIVE.

**Why × 3.** Partnership persistence is one grammar-shape property; a language with heavy topic drift could score low,
and a copying process with a long memory could score high. Weak either way.

## Disclosed
- Known facts: topic clustering I_word (E019) is matched by the generator; words cluster by sheet (C24, E059); Currier A
  precedes B in reading order; E043/E054 line-recurrence and page-topic results.
- The statistic was built and corrected on **fabricated** texts only (a 30-topic toy language: STAB +0.17; a toy
  copy-from-previous-lines process: −0.03; a shuffled toy: 0.00). The first version filtered pairs by expected count
  and gave 0 for the toy language; the filter was replaced by the shuffle baseline before locking. No real text,
  Voynich included, has been measured.
- The script's per-text seeds use a CRC of the text name (not Python's randomized hash; lesson of E061).
- One attempt (standing rule 9).
