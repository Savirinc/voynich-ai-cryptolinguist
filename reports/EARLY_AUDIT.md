# E064: re-audit of the early ledger factors (E030–E032) and the E051 re-measurement — results

Pre-registration `reports/E064_PREREG.md` (sha256 87a6b606…c296c7), script `experiments/e064_early_audit.py` (sha256
b60ab7d6…9b8067), both locked in commit 6c7dfa4 before the run. Results `experiments/results/e064.json`, `e064_run.log`.
Runtime 82 s.

## Verdicts
| Part | Question | Result | Ledger |
|---|---|---|---|
| A | Does any ordinary language (30 fresh ones) show both exact copies and near-copies above chance, as E031's Czech primer did? | **No. 0 of 30.** Highest R 1.07 (Assamese), highest NR 1.52 (Oromo, with R 0.23) | **E031 WITHDRAWN: L × 1/3** |
| B | Does the Timm & Schinner generator reproduce Voynich once it is given five scribes? | **No. Fails 7 of 13**, the same count as the single run | none; E032 stands |
| C | Does any fresh language reach Voynich's back-to-back repeat level once words are cut correctly? | **No. 0 of 30** (was 2 of 30 on fragments). BF(M:L) 2.8, inside the no-factor band | none; **the E045 caution is reinstated** |

**Ledger:** M 0.0083 → **0.024**, L 0.9808 → **0.9445**, C 0.0095 → **0.0274**, O 0.0014 → **0.004**.

**Sensitivity, stated plainly.** From the range edges (M 0.25, L 0.60, C 0.13, O 0.02) the same factor gives **M 0.42,
L 0.33, C 0.22, O 0.03: M leads.** The ranking of M and L now depends on where inside the agreed ranges one starts. At the
point values L still leads by a wide margin because the early chain pushed M to under 1%; this audit removes one of
the three links of that chain and reinstates the caution against the other two.

## Part A: E031 on fresh data
Voynich DEV: R 2.65, NR 2.10 (bar for NR: 1.50). A text "does both" iff R ≥ 1.5 and NR ≥ 1.5.

| Language | R | NR | | Language | R | NR |
|---|---|---|---|---|---|---|
| Assamese | 1.07 | 0.76 | | Nyanja | 0.21 | 0.32 |
| Shi | 0.66 | 0.50 | | Toma | 0.19 | 0.68 |
| Shona | 0.53 | 0.55 | | Chhattisgarhi | 0.18 | 0.37 |
| Motu | 0.49 | 0.72 | | Luo | 0.16 | 0.55 |
| Sunwar | 0.44 | 0.60 | | Panjabi | 0.14 | 0.50 |
| Uyghur | 0.40 | 0.82 | | Ewe | 0.13 | 0.76 |
| Azerbaijani | 0.38 | 0.48 | | Swedish | 0.13 | 0.68 |
| Baatonum | 0.38 | 1.10 | | Danish | 0.11 | 0.93 |
| Simte | 0.36 | 0.76 | | Huichol | 0.11 | 0.93 |
| Tamil | 0.34 | 0.61 | | Malayalam | 0.10 | 0.38 |
| Urdu | 0.29 | 0.30 | | Lingala | 0.08 | 0.25 |
| Oromo | 0.23 | 1.52* | | Kikuyu | 0.06 | 0.43 |
| | | | | Hiligaynon, Khumi Chin | 0.05 | 0.55–0.82 |
| | | | | Thaiphum Chin, Nahuatl | 0.03–0.04 | 0.44–0.45 |
| | | | | Ilocano, Yapese | 0.01–0.02 | 0.07–0.42 |

\*Oromo's NR was within 0.1 of the bar; the seed rule re-drew 10 window sets and the verdict (not both, R far below 1.5)
held in all 10.

**Reading.** In 183 texts across about 70 languages, the only text that ever showed both habits is the Czech spelling
primer. Ordinary prose, whatever the language, has both R and NR near or below 1. E031's L × 3 was the fragile link
its own report said it was, and it is withdrawn under the rule set in advance. "Does both" remains a drill-text property,
which is a lead about *genre* (primers, readers, lists) and not about language. E030's finding stands: Indonesian and
Malay (unaffected by the tokenizer defect) do reach R ≥ 1.5; none of the 30 fresh languages does, so doubling at
Voynich's rate remains rare even among real languages.

## Part B: the generator with five scribes
One generator run per scribe, laid along the 33 scribe runs of the DEV text (tokens per hand 8,061 / 8,838 / 10,534 /
539 / 869), 10 samples, E032's 13 features.

| Feature | Voynich | Single run (E032) | Five scribes (mean ± sd) | z | Fails? |
|---|---|---|---|---|---|
| R (exact neighbour copies ÷ chance) | 2.65 | 2.2 | 1.90 ± 0.37 | +2.0 | no |
| NR (near-copies ÷ shuffled) | 2.10 | ≈ 2.1 | 2.21 ± 0.24 | −0.5 | no |
| word length | 4.99 | 4.63 | 4.66 ± 0.10 | +3.2 | borderline, undecided |
| distinct words | 6,077 | 3,961 | 3,948 ± 338 | +6.3 | **yes** |
| h2 (glyph predictability) | 2.10 | | 2.02 ± 0.05 | +1.7 | no |
| I_word (topic clustering) | 0.39 | | 0.47 ± 0.05 | −1.5 | no |
| top_word (concentrated types) | 0.29 | 0.49 | 0.51 ± 0.03 | −6.9 | **yes** |
| PERS_30 (common words persist) | 0.26 | 0.56 | 0.49 ± 0.03 | −7.2 | **yes** |
| COV_30 (common words cover) | 0.92 | 0.98 | 0.97 ± 0.02 | −2.3 | no (was a fail) |
| share of words seen once | 0.68 | 0.52 | 0.53 ± 0.01 | +11.3 | **yes** |
| Zipf slope | −0.65 | −0.82 | −0.82 ± 0.04 | +4.2 | **yes** |
| NSUF95 (endings) | 27 | | 21.1 ± 1.9 | +3.1 | borderline, undecided |
| DIST (ending spread) | 0.40 | | 0.35 ± 0.06 | +0.8 | no |

Seed rule: word length and NSUF95 were within 0.5 of the bar; on 10 bootstrap draws from 20 samples they failed in 4
and 6 draws, so both are undecided. With both counted as passes the generator still fails 5 (distinct words, one-off
share, Zipf slope, persistence, concentration), so the verdict does not depend on them: **FIVE-SCRIBE GENERATOR FAILS**.

**What five scribes changed, and did not.** Persistence moved from 0.56 to 0.49 and coverage from 0.98 to 0.97
(coverage now passes), the direction E032 predicted for heterogeneity, but only a fifth of the way to Voynich. The
vocabulary did not move at all: five independent runs give 3,948 distinct words against one run's 3,961. The
generator's vocabulary is fixed by its rules, not by who runs it. Voynich's extra 2,100 words, its 68% one-offs and its
flat Zipf head are not products of this copying procedure, however many hands run it. E032's M × 1/3 stands; what M
would need is a procedure that invents far more rare words than Timm's, which is what the forum's newer generator
(quimqu, thread-6219) claims and we cannot run.

## Part C: E051 re-measured with correct words
AS = back-to-back repeats observed ÷ expected within lines (Voynich A 1.04, B 1.01; threshold 0.85).

| Language | AS on fragments (E051) | AS on words (E064) |
|---|---|---|
| Tamil | **1.01** | 0.10 |
| Assamese | **0.87** | 0.75 |
| Malayalam | 0.76 | 0.02 |
| Sunwar | 0.57 | 0.36 |
| Chhattisgarhi | 0.54 | 0.22 |
| Panjabi | 0.46 | 0.18 |
| Urdu | 0.45 | 0.27 |
| the other 23 | 0.01–0.42 | 0.01–0.40 (unchanged within 0.08) |

k_L = 0 of 30 (was 2), k_M = 0 of 10 generator samples; p_L 0.016, p_M 0.045, BF(M:L) 2.8: no factor by E051's bands,
exactly as computed in advance. **The E045 caution is reinstated:** among about 120 meaningful texts measured so far,
only Indonesian (doubling grammar) reaches Voynich's back-to-back level; human gibberish (0.66) and the copy generator
(0.76–0.81) get most of the way; no ordinary prose does. Assamese at 0.75 is the highest real-language value outside
Indonesian and is noted (it has echo reduplication).

## What this audit changes in how the ledger should be read
- Of the three early links, one is gone (E031), one is reinstated as a standing caution against L (E045/C21), and one
  (E032) survives a fair re-test with the structure Voynich actually has.
- L still leads at the point values (0.94), but **at the range edges M leads (0.42 vs 0.33)**. The honest statement is
  now: *L is the best single explanation at our chosen starting point, and the ranking is not robust to the starting
  point.* The lower bound of L's honest range drops from 0.60 to about 0.33.
- Nothing here makes M likely on its own: its generators still fail on vocabulary, and its human-gibberish samples are
  too short to score. The symmetric work is to find a test M can *win*, as the forum's newer generator claims to.
