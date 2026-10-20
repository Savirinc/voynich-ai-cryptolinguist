# E028: simple-syllable languages at the word level (Occam rung 1)

Pre-registration: `reports/E028_PREREG.md` (sha256 `3b9286c6860a029327fef57ba4b75d3ed847de760ec91c959fdd619f06f19137`,
locked before the run). Script: `experiments/e028_syllable_words.py`. Results: `experiments/results/e028.json`,
`e028_run.log`.

## Verdict: **RUNG 1 INCONSISTENT AT WORD LEVEL** (failing on one feature: top_word)
The gate passed: the Latin and English Bibles behave like the E019/E021 word twins.

| DEV (z of Voynich vs the family) | I_word | top_word | PERS_30 | COV_30 | |
|---|---|---|---|---|---|
| SIMPLE (Hawaiian, Tongan, Māori, Vietnamese, Mandarin pinyin) | +0.0 | **−3.6** | −2.3 | −1.3 | inconsistent |
| BIBLE_EU (Latin Vulgate, English KJV) | −0.8 | −2.5 | −1.5 | +0.0 | consistent |
| Latin Vulgate alone | −0.9 | −2.2 | −1.4 | +0.6 | |
| Vietnamese / Mandarin alone | −1.7 / −0.9 | −3.3 / −3.0 | −1.6 / −2.4 | −0.4 / −0.9 | |
| Hawaiian alone | +3.7 | −6.0 | −4.8 | −3.1 | |

- **Topic clustering (I_word):** Voynich matches the simple-syllable family exactly (z +0.0).
- **The failure is top_word:** the share of frequent types that are strongly concentrated. It is lower in Voynich
  than in any simple-syllable text, and in Currier B it is low against every family.
- **Hawaiian is the worst fit:** its common words are too evenly spread.

## Exploratory (not pre-registered): why top_word fails
Profile of the types in one DEV-sized sample:

| | Distinct words | Types ≥ 8 tokens | Share seen once |
|---|---|---|---|
| **Voynich** | **6,077** | 515 | **0.68** |
| Latin Vulgate | 6,380 | 492 | 0.62 |
| English KJV | 2,757 | 452 | 0.47 |
| Māori | 1,691 | 353 | 0.42 |
| Vietnamese (syllables) | 1,817 | 576 | 0.26 |
| Mandarin pinyin (syllables) | 866 | 491 | 0.12 |

Voynich's vocabulary is as large and as full of one-off forms as **inflected Latin**, three to seven times larger
than the simple-syllable languages. One Voynich word cannot be one syllable of a Vietnamese- or Mandarin-type
language: those have too few distinct syllables. Spreading the same tokens over many more types also leaves each
type rarer, which plausibly explains the low top_word.

## What this means (the Occam reading)
Together, E027 and E028 say two things:
- **Inside words**, Voynich is built like a language with simple, rigid syllables (E027).
- **Across words**, its vocabulary is rich, like an inflected language. This also fits E026's compact ending set.

Neither a plain monosyllabic language nor plain Latin-type spelling explains both. The single extra part this
forces is **rich word-building out of simple syllables**: polysyllabic words with prefixes and endings. That is the
profile of agglutinative languages with simple syllables (for example Swahili, Quechua, Japanese, Malay/Indonesian).
It is not yet a cipher. The next test should ask whether any such language matches the glyph-level *and*
vocabulary facts at the same time. Those facts must be pre-registered, since the vocabulary comparison above was
exploratory.
