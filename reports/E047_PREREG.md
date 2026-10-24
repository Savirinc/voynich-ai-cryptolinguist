# E047 pre-registration (attack step 3a): can our attack read a real language written in a Voynich-like invented script?

Written 2026-10-24, before the run. Script: `experiments/e047_known_answer_script.py`. This is a method validation,
with no ledger factor. Its result decides whether step 3b (attacking Voynich itself) may run.

## Why this comes first (rule 3: known answers first)
Before pointing any attack at Voynich, it must:
- crack synthetic texts of the same kind, with every hidden part kept hidden;
- make **no false claims** on meaningless look-alikes or on the wrong language.

## The cipher class "VOY23" (built to look like Voynich A)
- **A real language,** written word by word with spaces kept.
- **Letters:** folded to at most 23.
  - Hebrew: the 22 consonants, final forms merged, no vowel points.
  - Turkish: diacritics folded (ı→i).
  - Latin: j→i, v→u, æ→ae.
  - Only the commonest 23 letters are kept.
- **Signs:** the 23 commonest signs of Voynich Currier A (cleaned EVA, grouped units). These cover 99% of A's units.
  - Each letter gets at least one sign. Spare signs become extra homophones of the commonest letters, chosen at
    random when writing.
  - The key is secret and fresh per text.
- **Free spelling variation, as in E036/E040:** each word, with probability 0.12, gets one random sign edit
  (substitute, insert or delete, 2 : 1 : 1, signs drawn by Voynich-A frequency).
- **Size:** 8,806 words, Currier A's size.

## Languages and data (fixed now; disjoint parts of each Bible)
| Language | Bible | LM training books | DEV plaintext | TEST plaintext |
|---|---|---|---|---|
| Hebrew | hboWLC | Genesis to 2 Kings | Isaiah, Jeremiah | Ezekiel, Psalms, Proverbs, Job, 1–2 Chronicles |
| Turkish | turytc | same books | same | same |
| Latin | latVUC | same books | same | same |

Hebrew and Turkish lead the E042 shortlist. Latin is a third, well-understood check.

## Attack (identical for every text, real or control)
- **Search:** many-to-one simulated annealing over sign → letter keys, using E017's schedule and moves (30% swaps,
  70% reassignments).
- **Score:** a 4-gram Kneser-Ney letter model *with* word boundaries, built only from the LM books, minus E017's
  unigram-KL penalty. Word boundaries are fixed to "space".
- **Budget:** 32 restarts × 30,000 steps. The best restart is kept.

**Change from E017's engine (disclosed).** E017's delta scorer is slow when there are only 23 signs, so a full
re-score is used at each step instead (0.17 ms per step).

## Signals (no access to the answer)
- **agreement:** E017's definition. The largest share of sign tokens decoded identically by the best restart and any
  other restart.
- **lexrate:** the share of decoded word tokens of 3+ letters found in the LM-book vocabulary.
- **Accuracy** (truth, used only for scoring the test): the share of letters decoded correctly, in words without a
  spelling edit. A **crack** is accuracy ≥ 0.80.
- **Claim:** agreement ≥ 0.95 (E017's bar) **and** lexrate ≥ T.

## Stage DEV (fixes T, nothing else)
- **Texts:**
  - 2 secret keys per language (6 ciphers);
  - 1 sign-shuffled copy per language (structure destroyed, 3 controls);
  - 1 copy-generator sample (E032 output, cleaned and cut into the same 23 signs).
- **Attacks:** every text against all three languages' LMs.
- **Threshold:** T = midpoint between the lowest lexrate of any crack and the highest lexrate of any non-crack
  (wrong-language attacks, controls, failed attacks). If they overlap, the verdict is **NOT VALIDATED**, and TEST does
  not run.

## Stage TEST (fresh texts, keys and seeds)
- **Texts:** 3 keys per language (9 ciphers); 2 shuffled copies per language (6); 2 generator samples. All are
  attacked with all three LMs (51 attacks).

| Verdict | Rule |
|---|---|
| **GO** | in every language, at least 2 of 3 true-language attacks are *claimed* cracks; **and** zero false claims (no claim on any control, on any wrong-language attack, or on any attack below 0.80 accuracy) |
| NO-GO: false claims | any false claim |
| NO-GO: too few cracks | otherwise |

On GO, step 3b may pre-register an attack on Voynich Currier A, with this exact attack and claim rule, against the
shortlisted languages that have Bible LMs.

## What was seen before writing this (disclosed)
- **Voynich A's sign inventory and frequencies:** 23 signs cover 99%, about 3.6 signs per word.
- **Each language's letter list and word counts.**
- **Timing only from a smoke run.** A worker-budget bug made the smoke run do three *full-budget* attacks on a
  throw-away DEV-style Hebrew cipher (separate seed). Only their running times (about 73 s each) were printed or
  looked at; no agreement, lexrate or accuracy was printed.
- **Scorer speed on random symbols.**
