# E099 pre-registration (Arham, 2026-10-30; Reddit idea R3): does the Voynich reuse multi-word phrases?

Script `experiments/e099_phrase_repeats.py` (sha256 in the commit). Locked before the Voynich is measured.

## Question
A Reddit post (w2esca) says the Voynich has almost no repeated multi-word sequences. Real languages reuse phrases
("and he said unto"); a copy-and-change generator repeats words but not whole phrases. Which is the Voynich like?

## Data
- **Voynich:** DEV clean prose tokens (28,841), in their own lines.
- **Meaningful texts (69):**
  - 61 eBible translations (E067 set);
  - Pliny and abbreviated Pliny, Avicenna, the Quran, the Mahabharata, Lojban *Alice* (G&B corpus);
  - Culpeper;
  - Latin farming prose (Cato, Varro, Columella).
- **Meaningless:** the E032 copy generator, 10 disjoint stretches.
- **Not testable here:** human gibberish (G&B samples are 79–480 tokens, too short for phrase counts). Disclosed.

## Measure
- **Shape:** every text is cut to 28,841 tokens (seeded offset) and poured into the Voynich line lengths.
- **Counting:** 3-, 4- and 5-word sequences are counted within lines. Sequences containing a back-to-back repeated word
  are excluded, so C9 does not count as a phrase.
- **RP_n:** number of sequence tokens whose sequence occurs at least twice.
- **Q_n = (RP_n + 1) / (shuffle mean + 1):** the shuffle mean is over 20 word-order shuffles of the same tokens. This
  is phrase reuse beyond what word frequencies alone give.
- **Primary measure:** Q3. Q4 and Q5 are reported only.

## Decision table
| Outcome | Rule | Factor |
|---|---|---|
| VOID | meaningful 10th percentile ≤ generator maximum | none |
| PHRASES LIKE LANGUAGE | Voynich Q3 ≥ meaningful p10 and > generator max | M × 1/3 |
| NO PHRASES (GENERATOR-LIKE) | Voynich Q3 ≤ generator max and < meaningful minimum | M × 3 |
| BETWEEN | otherwise | none |

- **Rule 8:** if the Voynich is within 0.5 shuffle-sd of a boundary, 10 fresh shuffle seeds must give the same verdict
  in ≥ 8, else BETWEEN.
- **Symmetry:** M can win this test (GENERATOR-LIKE), and so can L/C (meaning-preserving ciphers keep phrase
  reuse).

## Seen beforehand
- **Reddit claim:** "only two 4-word repeats" (w2esca); no ratio or control was given.
- **Smoke run** (14 meaningful texts, generator; no Voynich):
  - meaningful Q3 6.1–626, p10 7.6;
  - generator 2.0–4.7.
  - A first version without the +1 smoothing gave unstable Q4/Q5 (division by near-zero shuffle counts), so the +1 was
    added before locking.
