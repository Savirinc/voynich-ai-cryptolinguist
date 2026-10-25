# E062 pre-registration (campaign step 2): a verbose cipher with one table per scribe

Written 2026-10-25, before the run. Script: `experiments/e062_scribe_tables.py`. Output: `experiments/results/e062.json`,
`e062_run.log`, report `reports/SCRIBE_TABLES.md`. Updates `LEDGER.md`.

## Question
E020 left one cipher class open: a verbose cipher whose glyph inventory changes by section. E059 showed that glyph
habits change with the scribe and the sheet, and Currier A/B follows the scribes. So the natural form of that class is
**a verbose cipher where each of the five scribes used his own table set**. Does such a cipher reproduce Voynich's
measured facts where the copy-and-change generator failed (E032: distinct words, words seen once, Zipf head,
persistence and coverage of the common words, concentrated types, word length)?

**Terms.** A *verbose* cipher writes one plaintext letter (or letter pair) as several glyphs; Greshko's Naibbe is the
published example (E013–E018). A *table* is the list saying which glyph string stands for which letter. *Per-scribe
tables* means the same cipher design, but the assignment of glyph strings to letters is re-drawn for each scribe.

## Construction (no tuning; everything fixed here)
- **Base cipher:** the faithful Naibbe port (`vcl.synthetic.naibbe_exact`, published tables, card weights, 17/36
  respacing, 3% space removal).
- **Per-scribe tables:** for scribe h (1–5), within every (state, table) group of the published tables, the glyph
  strings are permuted among the letters with seed 1000·h + sample seed. Structure, weights and glyph strings are
  unchanged; only who stands for whom changes.
- **Who writes which line:** the DEV prose lines in manuscript order carry their scribe (hand) from the ZL headers.
  The plaintext is enciphered run by run: consecutive lines of the same scribe are enciphered with that scribe's
  tables, consuming the plaintext in order, and cut into lines of exactly the Voynich line lengths. Lines whose hand
  is unassigned ('@') take scribe 3's tables (they sit in his quire).
- **Single-table comparison:** the same, with one table set (the published one) for all scribes.
- **Plaintexts (4):** Latin (latVUC), German (deu1912), Turkish (turytc), Hebrew (hboWLC, consonants transliterated
  one-to-one to Latin letters), windows from token 10,000 onward, as much text as the cipher consumes.
- **Samples:** 10 seeds per language per variant = 80 twins of 28,841 tokens.
- **Sanity check:** for one sample per language, decoding the unmerged cipher words with the right tables must recover
  ≥ 95% of plaintext characters; otherwise VOID.

## Battery and judging (exactly E032's)
The 13 features of E032 (`e032_copy_generator.features`: R, NR, wl_mean, types, h2, I_word, top_word, PERS_30, COV_30,
type_hapax, zipf_slope, NSUF95, DIST), Voynich DEV against each twin set's mean and sd (floor 2% of the Voynich value),
a feature **fails** when |z| > 3.

| Outcome (best per-scribe set over the 4 languages) | Rule | Ledger |
|---|---|---|
| **C REPRODUCES** | ≤ 1 fail | **C × 3** (a cipher class with no tuning reproduces the facts the generator could not) |
| PARTIAL | 2–4 fails | none; the failing features are recorded as what the class still lacks |
| **CLASS FAILS** | ≥ 5 fails for every language | **C × 1/3** (the one open verbose class fails the same way the generator did) |
| VOID | sanity check fails | none |

Also reported, not scored: the single-table sets (what the per-scribe tables add), and per feature which of the
E032 generator failures the per-scribe cipher fixes.

Why ×3 and not E032's ×10: E013 showed that a verbose twin *with tweaks fitted to Voynich* can match a static battery;
matching here is untuned but still necessary rather than sufficient for C, so the weak factor is used in both
directions.

## Seed rule
A feature with |z| within 0.5 of 3 for the deciding set is re-judged with 10 further sample seeds (≥ 8 of 10 agree).

## Disclosed
- E032's Voynich values and generator failures (in `COPY_GENERATOR.md`); E013's result that single-table Naibbe plus
  fitted tweaks matched 22 static features for la/it/fr/de; E061's stem result (word-level attack).
- The number of DEV lines per scribe is known from E059's design counts.
- No per-scribe or single-table twin has been generated or measured.
- One attempt (standing rule 9). The script's functions will be exercised on fabricated text before locking.
