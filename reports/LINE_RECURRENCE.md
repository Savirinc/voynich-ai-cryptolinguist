# E043: which kind of text makes words recur within a line? — NOTHING MATCHES

Pre-registration `reports/E043_PREREG.md` (sha 35d5d295…414d7a, commit 85c8bf8). Script
`experiments/e043_line_recurrence.py`. Results: `experiments/results/e043.json`, `e043_run.log`.

## Numbers
- **SL:** how often a word has a copy of itself somewhere in its line, ÷ chance.
- **AS:** whether back-to-back is special. About 1 means "as likely as anywhere else in the line". About 0 means
  "avoided".

| Text | Group | SL | AS | Match? |
|---|---|---|---|---|
| **Voynich DEV** | | **2.62** | **1.01** | |
| Voynich A / B | | 1.76 / 2.21 | 1.00 / 0.98 | |
| Latin hymns | SACRED | 2.68 | 0.53 | no (AS) |
| Hebrew Genesis–Exodus | SACRED | 2.47 | 0.12 | no (AS) |
| Hebrew Psalms | SACRED | 2.07 | 0.22 | no (AS) |
| Latin Psalms | SACRED | 1.07 | 0.09 | no |
| Latin Genesis–Exodus | SACRED | 0.92 | 0.03 | no |
| Apicius + Cato + Varro | PRACTICAL | 1.86 | 0.07 | no (AS) |
| Columella | PRACTICAL | 1.06 | 0.02 | no |
| Culpeper herbal | PRACTICAL | 0.84 | 0.03 | no |
| Ovid | OTHER | 1.74 | 0.26 | no |
| Vergil | OTHER | 1.15 | 0.15 | no |
| Caesar | OTHER | 0.94 | 0.00 | no |
| *Indonesian (doubling reference, not scored)* | | 1.82 | 1.45 | *within tolerance* |
| Copy generator | GENERATOR | 2.73 | 0.76 | no (AS, z +3.3) |

**Verdict (pre-registered): NOTHING MATCHES. No Bayes factor.** The new L sub-hypotheses keep their starting
shares (sacred 0.30, practical 0.45, other 0.25).

## What it shows
1. **The distinctive fact is AS ≈ 1, not the amount of repetition.**
   - Every ordinary text strongly *avoids* putting the same word back to back (AS 0.00–0.26). Voynich doesn't
     avoid it at all (1.01).
   - Only three things come near:
     - a doubling language (Indonesian, 1.45);
     - the copy generator (0.76);
     - **Latin hymns (0.53), the only language text halfway there**, thanks to refrains such as *Veni, veni*.
   - New fact C21.
2. **The amount of same-line recurrence is not unusual.**
   - Latin hymns (2.68) and Hebrew scripture (2.07–2.47) reach Voynich DEV's level. Recipes (1.86) and Ovid (1.74)
     reach Currier A's level (1.76).
   - **Caveat found in the run:** DEV's value (2.62) is higher than A's (1.76) or B's (2.21). Pooling two
     vocabularies lowers the "chance" baseline, the same mixing effect as with the Zipf head (E040). A and B alone
     are the fairer targets, and they look less extreme.
3. **On the sacred-book idea:**
   - The closest *language* texts on both statistics are **sacred**: Latin hymns, and Hebrew scripture on the
     amount of recurrence.
   - No practical text came close on AS.
   - But no sacred text matched either, so the rule gives no factor. It is a **lean, not evidence**.
4. **On the earlier "doubling" evidence (E030):** by these pre-registered statistics, Indonesian is still within
   tolerance of Voynich. The E030 update therefore stands. The exploratory distance profile (Indonesian 0.76 at
   distance 2 against Voynich's 3.18) still shows the two are not the same mechanism, so the comparison is noted,
   not scored.

## What this points to next
Voynich puts identical words next to each other as freely as anywhere else in the line. In real language that
happens with:
- grammatical doubling;
- refrains and chant;
- lists and tables.

It also happens if the "words" are smaller units than words, for example syllables written with spaces, as in
Vietnamese or Chinese. These are untested and worth a pre-registered check.
