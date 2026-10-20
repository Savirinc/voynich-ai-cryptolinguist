# Final round of the Voynich search: plan and stop rule (locked 2026-10-20)

Agreed with Arham on 2026-10-20 ("ok" to a final, bounded round with a stop rule fixed in advance). This file is
locked read-only and its sha256 is recorded in the commit. Nothing in it may be changed after the fact; any
deviation must be written up as a deviation.

## What has already been tried (so it is not repeated)
| Road | Family | Where | Result |
|---|---|---|---|
| A (small key) | letter substitution, mono and homophonic, 9 unit inventories, 36 languages | E012 | no answer (valid at 2 inventories) |
| A | any fixed-key letter cipher | E019, E021 | ruled out |
| A | plain alphabet over any glyph grouping | E012, E024 | ruled out |
| A | Naibbe-type verbose cipher (1–2 letters per word), published tables, la/it/fr/de | E016–E018 | NO CLAIM, 12/12 |
| A | Naibbe-type verbose cipher with **unknown** tables | E019 | ruled out *whatever the tables*: units of 1–2 letters cannot produce Voynich's word-level topic clustering (z +12.7) |
| A | plain simple-syllable language | E027, E028 | inconsistent (vocabulary far too small) |
| B (anchors) | all known anchors; zodiac months; same-month pages; plants | E010–E010D, E022–E023 | insufficient or negative |
| — | word codebook, stem + ending code (large keys) | Stage B dev | gibberish decodes as well as real text, so these cannot prove themselves |

## The one remaining family: syllable notation (family F)
- **Rule:** each real word is kept as one Voynich word. Each **syllable** of it is written as a glyph group from a
  fixed table (one table, the only moving part). Several codes per syllable (homophones) are allowed.
- **Why it is the last one:** it is the only untested small-key family consistent with every fact we have:
  - word-sized units and a rich vocabulary (E011, E019, E028);
  - syllable-like structure inside words (E027);
  - about 28 endings, which would be the final-syllable codes (E026);
  - plausible word lengths.
- **Languages:** Latin, Italian, French, German, the same four as E017/E018. The conclusion is limited to them.

## Procedure (each step needs the previous one to pass)
1. **Development** on known answers only, using CALIB plaintext (held-out Latin Library files, `experiments/dev/holdout_files.json`)
   and the equivalent held-out books for it/fr/de. Voynich is not touched.
2. **E029, pre-registered known-answer test:**
   - plaintexts: TEST files never used in development;
   - controls: Rugg, self-citation, and letter-shuffled plaintext;
   - claim rule: two signals, fixed in development, validated here;
   - **pass = at least 7 of 8 real ciphers correctly claimed (≥ 0.9 syllable accuracy, right language) and 0 false
     claims on controls.**
3. **E030, pre-registered attack on Voynich DEV** (the LOCKED_TEST leaves stay untouched), only if E029 passes.
4. A claim on Voynich DEV is confirmed only on the LOCKED_TEST leaves, once, with the frozen key.

## Budget (prevents the loop)
- Development may revise the attack **at most 2 times** after its first full known-answer failure.
- If E029 still fails after that, family F is recorded as **"not testable with our methods"**. That counts as a
  failure for the stop rule.
- No new family may be added during this round.

## Stop rule
If family F does not produce a CLAIM on Voynich DEV that is then confirmed on LOCKED_TEST, the Voynich search
**stops**. That covers three cases: E029 fails, E030 gives NO CLAIM, or the confirmation fails.

We will then publish the final report:
- **the conclusion:** *within every small-key family we could test over Latin, Italian, French and German, the
  Voynich text does not decode; it is either a large codebook that needs anchors which do not yet exist, a system
  outside these classes, or meaningless*;
- the complete record of what was tried.

After that, work moves to the Indus script.
