# E049 (attack step 3b): the validated attack on Voynich — NO CLAIM (one near miss: Hebrew on Currier A)

Pre-registration `reports/E049_PREREG.md` (sha 8863ad63…e4, commit e0931ea). Script
`experiments/e049_attack_voynich.py`. Results: `experiments/results/e049.json`, `e049_run.log`.

Inputs: Voynich A is 8,794 words (306 of 31,695 rare units dropped); Voynich B is 19,488 words.

lexrate is the share of decoded words (3+ letters) that are real words in the language model's vocabulary.

| | Hebrew LM | Turkish LM | Latin LM |
|---|---|---|---|
| **Voynich A** | **0.542** (agreement 1.00) | 0.341 | 0.167 |
| Voynich B (secondary) | 0.469 | 0.410 | 0.354 |
| Generator controls (this run) | 0.358, **0.472** | 0.262, 0.367 | 0.217, 0.192 |
| Shuffled-Voynich-A controls | 0.163, 0.166 | 0.051, 0.054 | 0.057, 0.065 |
| *E047 generator controls* | *0.379–0.419* | *0.323–0.422* | *0.206–0.226* |
| *E047 real cracks* | *0.65–0.79* | *0.70–0.83* | *0.70–0.78* |

**Claim bar:** agreement ≥ 0.95, lexrate ≥ 0.514, and lexrate ≥ highest control + 0.10 = 0.572.

**Verdict (pre-registered): NO CLAIM.**

## Plain reading
1. **Turkish and Latin: searched, not found.** Voynich A decodes no better than gibberish (Turkish 0.34, against
   generator controls of 0.26–0.42) or worse (Latin 0.17). Voynich is not Turkish or Latin written letter by letter
   in a 23-sign script of the validated kind. This had power 9/9 on known answers, with the Biblical-vocabulary limit
   stated in the pre-registration.
2. **Hebrew is a near miss, and it is not a claim.**
   - Voynich A under the Hebrew model reaches 0.542. That is above E047's threshold (0.514) and above every control
     we have run with the Hebrew model (the highest is 0.472).
   - But it falls short of the stricter pre-registered margin (0.572), and far short of real Hebrew cracks
     (0.65–0.79).
   - It sits *between* gibberish and real Hebrew.
   - **Why caution:** under the Hebrew model even gibberish scores high (up to 0.47), because short three-letter
     consonant strings often form real Hebrew words. Voynich A's words are short (about 3.6 signs), which helps the
     same way.
   - **Unresolved:** the 0.542 could come from Voynich's *surface* statistics alone (word length, sign frequencies),
     with no Hebrew in it. Or there could be partial Hebrew whose fit is lowered by non-Biblical vocabulary, a
     different spelling, or an encoding outside the validated class.
3. **Currier B** scores like gibberish under all three models.

## What would settle the Hebrew near miss (not run; to be pre-registered)
The decisive control is **pseudo-Voynich**: text that copies Voynich A's sign and word-length statistics exactly but
contains no language (resampled from a sign-level Markov model of A's own words).
- If such texts also score about 0.54 under Hebrew, the near miss is explained by surface statistics.
- If Voynich A clearly beats a large set of them (and of generator samples), it earns the LOCKED_TEST confirmation
  step.
