# E067: does human-written gibberish grow vocabulary like Voynich? — GIBBERISH LIKE VOYNICH, M × 3

Pre-registration `reports/E067_PREREG.md` (sha256 1b739781…2109c6), script `experiments/e067_gibberish_vocabulary.py`
(sha256 580ae474…47780a), locked in the commit before the run. Results `experiments/results/e067.json`,
`e067_run.log`. 25 s.

## Verdict
Gate passed (languages separated from Voynich: d_T −1.60). **Gibberish: d_T +0.28, d_H +0.59, inside the LIKE box
(≤ 0.5 and ≤ 1).** Not borderline. Pre-registered factor **M × 3**.

**Plain reading.** In a 150-word stretch, Voynich uses about 112 different words and 62% of its words occur once.
Thirty-six people asked to write gibberish produced, in their first 150 words, 115 different words on average with 67%
one-offs: the same richness as Voynich. The Bibles average 95 different words and 47% one-offs; the copy generator 94
and 46%. On vocabulary at this scale, human gibberish sits with Voynich, and the machine sits with the languages.

## Numbers (150-token windows)
| Group | Windows | Distinct words T | One-off share H | Growth BETA | d_T | d_H |
|---|---|---|---|---|---|---|
| **Voynich DEV** | 200 | **112.1 ± 11.0** | **0.615** | 0.86 | 0 | 0 |
| **Human gibberish** (36 writers, first 150 tokens) | 36 | **115.2** (sd 21.6, range 71–148) | **0.671** | 0.90 | **+0.28** | **+0.59** |
| 60 Bibles (mean of language means) | 1,200 | 94.5 (languages 63–132) | 0.469 | 0.79 | −1.60 | −1.58 |
| G&B meaningful texts (71) | 710 | 99.2 | | | −1.17 | −1.04 |
| Copy generator | 200 | 93.8 | 0.458 | 0.78 | −1.67 | −1.69 |

## Caveats, stated plainly
- **Some languages are as rich as Voynich at this length.** Fourteen of 60 lie within 0.5 sd of Voynich's mean T:
  Hebrew (132), Shi, Tamil, Arabic, Uyghur, Shona, Turkish, Slovak, Malayalam, Assamese, Croatian, Huichol, Azerbaijani,
  Polish, all heavily inflected or abjad-written. Among Gaskell & Bowern's meaningful texts, Sanskrit (134), Turkish and
  Arabic match too. The pre-registered gate was on the *mean* of languages, and it passed; but this measure does not
  separate Voynich from every language, only from the typical one. So the result says "humans scribbling reach Voynich's
  richness", not "only gibberish does".
- **The writers vary a lot** (71 to 148; only 11 of 36 fall inside Voynich's ±1 sd band; 25 are above Voynich's mean).
  Voynich is tightly consistent (sd 11 over 200 windows), as a long text by five scribes would be. The group mean
  matches; the individual writers scatter around it.
- **150 tokens is not 28,841.** Whether a human could keep up 68% one-offs and a flat frequency head over a whole book
  cannot be tested with these samples (the longest is 480 tokens). The generator's failure was at book scale; this test
  removes the objection only at the scale we can see.
- The writers are modern, wrote for minutes, and were asked for gibberish; this is a proxy.

## Ledger
| | M | L | C | O |
|---|---|---|---|---|
| Before (after E066) | 0.0739 | 0.8939 | 0.0281 | 0.0041 |
| **After E067** | **0.1932** | **0.7788** | **0.0245** | **0.0036** |

From the range edges (M 0.70, L 0.17 after E066): M 0.87, L 0.07, C 0.05. At the point values L still leads 0.78 to 0.19.

## What it changes
The one thing M could not do, make a Voynich-rich vocabulary, humans scribbling do at the scale we can measure, while
the machine does not. M's remaining gap is now the **book-scale** vocabulary (68% one-offs over 28,841 tokens) and the
line-level facts (E045: gibberish AS 0.66 vs Voynich 1.0; near-copies; endings), none of which has been tested on human
gibberish beyond AS. Per Arham's decision before the run, had M missed, the work would have stayed inside L; it did not
miss, so M stays a live contender and the next tests must treat M and L symmetrically.
