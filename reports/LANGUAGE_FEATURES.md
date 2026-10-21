# E033 (ledger test 4): real languages on E032's spelling-independent features — PARTIAL

Pre-registration: `reports/E033_PREREG.md` (sha256 ebd8be58…de79, locked before the run). Script
`experiments/e033_language_features.py`. Results: `experiments/results/e033.json`, `e033_run.log`.

## Plain-language result
No real-language Bible matches Voynich on all 8 spelling-independent features. The best ones, **Swahili** and
**Latin**, fail 2 each:
- **word repeats (R):** they almost never put a word next to itself;
- **Zipf slope:** the most common words in Voynich are less dominant than in any language here.

**Indonesian**, the language that matches the repeats, fails 3: it has too few distinct words, too few words seen
once, and too steep a Zipf slope. The authors' generator (E032) fails 6.

By the pre-registered rule (best text fails exactly 2): **PARTIAL**, so **no update**.

| Text | Fails (of 8) | Which |
|---|---|---|
| Swahili | 2 | R, zipf |
| Latin Vulgate | 2 | R, zipf |
| Indonesian | 3 | types, hapax, zipf |
| English, Cebuano | 4 | |
| Tagalog | 5 | |
| Malay, Yoruba, Hausa, Hawaiian, Tongan, Māori | 6 | |
| *E032 generator* | *6* | *types, top_word, PERS_30, COV_30, hapax, zipf* |

Topic clustering (I_word, top_word) matches every language. Persistence (PERS_30) matches most of the larger-vocabulary
ones.

## The two things nobody matches yet
1. **Repeats and rich vocabulary together.**
   - Languages with Voynich's rich vocabulary (Latin 6,542 types; Swahili 5,344; Voynich 6,077) don't repeat
     words.
   - The languages that do repeat (Indonesian 3,049 types; Malay 3,209) have poor vocabularies in these Bibles.
2. **A flat Zipf head.** Voynich's slope over its 100 most common words is −0.65. Every text here is steeper:
   - all 12 languages: −0.79 to −1.12;
   - the generator: −0.82.

   In Voynich no handful of words (like *et*, *the*, *and*) dominates as strongly as in real prose. This is a new
   measured fact (C11). It counts against L (as prose) and against M (as this generator).

## What it means for the ledger
- No change (PARTIAL).
- L's 0.87 now has a clear, honest status: L survived a test it could have failed (3+ fails), but no language
  actually matches.
- The best explanation so far: a language with a rich, Latin-like vocabulary that *also* doubles words, written in
  a text type where function words are weak, such as lists, recipes or notes. That is a hypothesis to test, not a
  finding.
