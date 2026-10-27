# E078 pre-registration: Voynich's word skeleton counted, and which languages share it

Written 2026-10-27, before the run, at Arham's direction (option 1 of three). Script
`experiments/e078_skeleton_traits.py`; output `experiments/results/e078.json`, `e078_run.log`; report
`reports/SKELETON_TRAITS.md`. Descriptive under the working assumption L; **no ledger factor**.

## Question
The working model: optional front pieces, bridges that are never words alone, about 20 fixed endings, some of which
are also words on their own. Which languages have a skeleton like that?

## Traits (identical recipe for every text, 28,841 tokens; lists from the text's own word types: 10 commonest fronts of
1–2 characters, 20 commonest endings of 1–4 characters)
| Trait | Definition |
|---|---|
| PFRONT | number of productive fronts: ≥ 15 front-words (frequency ≥ 2) and ≥ 30% of them leave a word when the front is removed |
| PEND | number of productive endings: ≥ 15 bridges X with X+e a word and X+e2 a word for another listed ending |
| BOUND | share of running words whose bridge (after removing longest listed front and ending) is not itself a word |
| FREEEND | share of productive endings that are also words on their own (frequency ≥ 10) |
| BARE | share of running words that are a listed ending standing alone |
| FILL | E074 fill rate (10 fronts, 30 middles, 20 endings) |

## Texts and comparison
Voynich DEV prose (LOCKED_TEST excluded); every Bible on disk as in E076 (28,841 tokens from token 10,000; Arabic
script, Hebrew, Yiddish with marks removed; Persian included). Closeness: Euclidean distance to Voynich after scaling
each trait by its standard deviation across the languages; all languages ranked. Copy generator seeds 31–33 reported
beside the ranking (included because the model must be checked against it once, as agreed 2026-10-27), not ranked.

## Reported
Every text's six traits; Voynich's position on each trait among the languages; the ranking; generator distances.

## Disclosed
E074, E076 and the 2026-10-27 counts (Voynich bare endings 9.2% of tokens; middles almost never words alone). Toy
check: a pure slot text gave PFRONT 4, PEND 9, BOUND 0.93, FREEEND 0.67, BARE 0.09. No real text has been measured with
this script. One attempt.
