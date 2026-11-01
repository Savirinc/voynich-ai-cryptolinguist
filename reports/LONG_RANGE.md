# X115 (Arham, move 1): how far does the link between parts of the text reach? (exploratory, unscored)

Script `experiments/e115_long_range.py`. Control results `experiments/results/e115_smoke.json`; Voynich values
`experiments/results/x115_voynich.json`. Not pre-registered, because no valid yardstick was found (below).

## The idea (Shannon; Lin & Tegmark)
In real language a word or letter still says a little about text far away, because the topic stays the same. That
link fades slowly. In machine gibberish it should die fast.

**Measure:** shuffle-corrected mutual information between letters d characters apart (spaces kept). The scored range
was to be the mean over d = 48–512.

**Groups:** 69 meaningful texts (the E099/E104 set), 60 copy-generator stretches and 10 dice books (E114's best set).
All are 28,841 tokens, cut into blocks the size of the Voynich's five scribes' texts.

## Development (controls only, before any Voynich value was computed)
1. **Word repeats at distance:** the share of the short-range link left at 256–2,048 words. Languages p10–p90
   −0.03..0.23, generators −0.07..0.18. The bands overlap: no yardstick.
2. **Letter-level link at 48–512 characters (×10⁻⁴):**

   | Group | p10 | median | p90 | max |
   |---|---|---|---|---|
   | Meaningful | −0.07 | 1.29 | 3.21 | 8.22 |
   | Generator | 1.67 | 16.5 | 32.6 | 54.0 |

   The bands overlap (3.21 > 1.67), so no valid yardstick either. A pre-registered test would have been VOID, so it was
   not locked.

**The surprise:** the prediction is reversed at this text size. Real languages lose the letter link within about
30 characters. The copy generator and the dice books keep a faint link out to hundreds of characters, because their
vocabulary drifts locally.

**Family closed (rule 9):** two variants were tried; no third will be.

## Voynich (computed after the family was closed; unscored)
- **Overall:** letter link at 48–512 characters = **11.9 ×10⁻⁴**.
  - Above all 69 meaningful texts: the highest is Tod 8.2; Culpeper's herbal catalogue is 1.4, Avicenna 1.9, Pliny
    −0.5.
  - In the middle of the generators: 46% of generator stretches are lower.
- **Per scribe:**

  | Scribe | ×10⁻⁴ |
  |---|---|
  | 3 | 8.6 |
  | 2 | 13.4 |
  | 1 | 13.4 |

  So it is not caused by joining scribes.
- **Word-repeat version:** 0.13 (inside both bands).

## What it means (cautiously)
The Voynich has a long, faint letter link, like text whose spelling habits or vocabulary drift locally, page by page.
Meaningful texts, including the herbal catalogue, do not.

This fits:
- copying-based gibberish;
- a writer whose glyph habits shift page by page (C24 sheets, E113 sections);
- a cipher whose tables change.

A meaningful text in a fixed spelling fits it poorly.

**Caveat:** texts with very strong letter-to-letter structure (the Voynich's 1.77 bits at d = 1, generators 1.7,
English 0.91) may carry more mid-range link. Scaled by the d = 1 value, the Voynich is still above every language.

Unscored lean towards M or changing tables. No factor; ledger unchanged.
