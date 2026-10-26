# E071 pre-registration: are the label words abbreviations (truncations) of longer words?

Written 2026-10-26, before the run. Script: `experiments/e071_label_truncation.py`. Output:
`experiments/results/e071.json`, `e071_run.log`, report `reports/LABEL_TRUNCATION.md`. Updates `LEDGER.md` (forms of L).
Label-class programme reading 3 (`CLAUDE.md` §6); step 0 (`LABEL_STEP0.md`) left readings 2 and 3 alive.

## Question
Medieval scribes shortened words mostly by cutting the end off (suspension: "op" for opus, "Ioh" for Iohannes). If the
label words of the Voynich manuscript (o + tall letter + short core + ending, 4–6% of running text) are such
shortenings of words that also appear in full, then a label word should be the **beginning of longer text words**
more often than an ordinary word of the same length and frequency is. Is it?

**Terms.** *Extension* of a word w: a different prose word type that begins with w (at least one glyph longer).
EXT(w) = number of distinct extensions. *Prefix score* of a set T: S(T) = mean over w in T of log2(1 + EXT(w)).

## Data
- Voynich: DEV prose types and counts (ZL 3b, clean tokens, LOCKED_TEST leaves excluded; 28,841 tokens, 6,077 types).
  Label types: DEV tokens with mode `label`, any section, clean.
  - **T1 (primary):** label types starting o + t/k/p/f with prose frequency ≥ 2 (design count 95).
  - **T2 (secondary):** all label types with prose frequency ≥ 2 (design count 280).
- Known answers: Gaskell & Bowern's abbreviated Pliny (`Historical - Latin (Abbreviated) - Technical`) aligned line by
  line with its full version; three windows of 28,841 tokens (starting at tokens 0, 100,000, 200,000 of the aligned
  stream). Target = abbreviated types of length ≥ 2 and frequency ≥ 2 that are proper prefixes of their full form
  (truncations). Planted truncations in latVUC, deu1912, turytc (28,841-token windows from token 10,000): 150 types of
  length ≥ 6 and frequency ≥ 4 chosen at random; each cut to its first 3–5 letters (random per type); half of its
  tokens (random) replaced by the cut form. Target = the cut forms with frequency ≥ 2.
- False-claim controls: in each of the six known-answer texts, a pseudo-label set of the target's size drawn from
  non-target types matched on length and frequency; Timm & Schinner generator seeds 31–33 (28,841 tokens) with 95
  random pseudo-labels of length 3–6 and frequency ≥ 2.

## Procedure
1. For a target set T in a text, 1,000 control draws: each member replaced by a random non-target type of the same
   glyph length and the same log2 frequency bin (bins with fewer than 5 candidates merge with the next bin). z =
   (S(T) − mean S(draw)) / sd S(draw). Ten seeds (1,001–1,010); the median z is reported; a verdict side holds only if
   ≥ 8 of 10 seeds fall on that side of the bar (standing rule 8).
2. Voynich T1 is scored twice: against all non-label prose types (**general**), and against non-label o-gallows types
   (**class-internal**, design count 128), both matched as in 1. T2 against general only.
3. Reported, not scored: the share of the commonest extension among all extension tokens (a truncated word should have
   one dominant full form; a stem with many endings should not); the same for the known answers.

## Known-answer and false-claim bars (all before Voynich is scored)
- Every known-answer target (3 Pliny windows, 3 planted languages) must give z > 3 (8/10 seeds).
- Every false-claim set (6 pseudo-label sets, 3 generator sets) must give |z| ≤ 3 (8/10 seeds).
- Otherwise **VOID**, no factor.

## Decision table (bar z = 3)
| Outcome | Rule | Ledger (within L; M/L/C unchanged) |
|---|---|---|
| **ABBREVIATION-LIKE** | T1 z > 3 general **and** z > 3 class-internal, and T2 z > 0 | L-abbrev × 3 (renormalise forms of L) |
| **CLASS MORPHOLOGY** | T1 z > 3 general, z ≤ 3 class-internal | INCONCLUSIVE, no factor; recorded as a fact about the o-gallows class |
| **NOT ABBREVIATION-LIKE** | T1 z ≤ 3 general | absence rule: the "suspensions of words also written in full" form is taken as s = 0.5 of L-abbrev, m = 0.2 → L-abbrev × 0.6 |
| VOID | any bar above fails | none |

Scope note: a word that is *always* abbreviated leaves no full form to extend it; that form of L-abbrev is not
searched here and keeps its share. T1 z < −3 (labels less prefix-like than matched words) counts as NOT
ABBREVIATION-LIKE and is recorded.

## Disclosed (seen beforehand)
- Step 0 (`LABEL_STEP0.md`): label words avoid line starts, no neighbour lock. Yesterday's descriptive facts: 69 cores
  for 135 zodiac o-gallows labels; labels carry the same 19 endings in the same ratio as text (this leans against
  truncation and is disclosed as such).
- Design counts only: 788 DEV label types, 280 with prose frequency ≥ 2, 95 o-gallows among them, 128 non-label
  o-gallows types with frequency ≥ 2; Pliny abbreviated 407,547 words vs full 409,868.
- No extension count has been computed for any Voynich word, any label, or any control text.
- One attempt (standing rule 9); the script is exercised on fabricated text before locking.
