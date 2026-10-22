# E039 (attack step 1c): scribe habit or location habit? — results

Pre-registration `reports/E039_PREREG.md` (sha c650b00a…fbfc). Script `experiments/e039_scribe_habits.py`. Results:
`experiments/results/e039.json`, `e039_run.log`. This is a measurement under working assumption L; no ledger change.

**Controls passed.** The planted scribe habit came out SCRIBE HABIT, and the planted location habit came out LOCATION
HABIT. **The test is VALID.**

## Results
"Share" is how much of the uncertainty about which form is written (given the word pair) is explained. All listed
effects have p ≤ 0.004 unless marked "n.s." (not significant).

| Alternation | By scribe (overall) | Scribe, same quire | Quire, same scribe | Verdict | "With" form by scribe (1 = A; 2, 3, 5 = B) |
|---|---|---|---|---|---|
| **d ±** | **12.8%** | 2.2% | 1.8% | **BOTH** | 1: **23%** · 2: 56% · 3: 42% · 5: 59% |
| **q ±** | 1.8% | n.s. (p 0.09) | 2.2% | **LOCATION HABIT** | 1: 45% · 2: 44% · 3: 44% · 5: 39% |
| **r / l** | 1.4% | n.s. | 3.0% | **LOCATION HABIT** | 1: 51% · 2: 57% · 3: 55% · 5: 65% |
| **t / k** | 0.9% | 0.5% | 1.4% | BOTH (small) | 1: 55% · 2: 59% · 3: 57% · 5: 63% |
| **e / ee** | 3.1% | n.s. | n.s. | ENTANGLED | 1: 30% · 2: 31% · 3: **45%** · 5: 25% |

## Plain reading
1. **d is mainly a scribe habit.** It is the only large effect: scribe explains 13%.
   - Scribe 1, who writes Currier A, uses the d-form a quarter of the time. Scribes 2 and 5 use it more than half the
     time.
   - Even within the same quire, scribes differ, so this is a real scribe or dialect difference. Location adds a
     little on top.
   - **This likely explains part of the A/B difference itself:** A's *chey/shey/aiin* against B's
     *chedy/shedy/daiin*.
2. **q is NOT a scribe habit; it depends on the part of the book.**
   - Given the word, all three main scribes use q equally often (44–45%).
   - But within one scribe, different quires use it differently.
   - **This corrects my E038 reading.** There, q-words looked about twice as common in B lines than in A lines.
     That came from *which words* B uses, not from B adding q.
   - So q tracks location, which could mean content, as you suggested. But E038 showed that q-forms share
     neighbours with plain forms, so it isn't a change of grammatical role. Possible meanings consistent with both:
     a marker of topic or register, or a section convention. **q stays open, as a candidate meaning-carrier.**
3. **r/l also follows location, not scribe.** Together with E038 (different neighbours), r vs l looks like a real
   linguistic difference whose use varies across the book's content.
4. **t/k and e/ee: small effects.** e/ee is one sign (E038); scribe 3 just writes *ee* more often. t/k differences are
   slight.

## Consequences for the sign inventory (step 1d)
| Sign | Treatment when re-measuring |
|---|---|
| e / ee | Merge (one sign, E038); scribe 3's preference for *ee* is a scribal habit |
| t / k | Merge provisionally (E038 near-variant; effects here are small) |
| d | **A scribe/dialect feature.** Report results with and without d-normalisation, separately for A and B. |
| q | **Keep.** It follows location, so it may carry content. |
| r / l | **Keep separate.** It is a real distinction. |
