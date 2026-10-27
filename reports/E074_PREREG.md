# E074 pre-registration: how much of the text is front piece + middle + ending? (measurement, no ledger factor)

Written 2026-10-27, before the run, at Arham's direction ("can we make the entire script of voynich by using
permutation and combination of front piece, middle and ending - what %age of entire script can be written like that").
Script `experiments/e074_slot_coverage.py`; output `experiments/results/e074.json`, `e074_run.log`; report
`reports/SLOT_COVERAGE.md`.

## Question
If every word is built as **front piece + middle + ending**, each taken from a short list, what share of the
Voynich text can be written that way? And how does that share compare with real languages and the copy generator
when the same recipe builds their lists?

## Recipe (identical for every text; characters are EVA letters for Voynich, letters for languages)
1. Text: 28,841 tokens (Voynich DEV prose, clean; languages from token 10,000 with the E064 tokenizer, Hebrew with marks
   removed as in E072; generator seeds 31–33). First half = **build half**, second half = **check half**.
2. From the build half's word types:
   - **front list**: the kF most common word beginnings of 0–2 characters (the empty front always included), ranked by
     the number of word types that start with them;
   - **ending list**: the kE most common word endings of 0–4 characters (empty always included), ranked the same way;
   - **middle list**: every way of writing a build-half type as front + middle + ending with front and ending from the
     lists and a middle of 0–4 characters; the kM middles used by the most types are kept (the empty middle always
     allowed).
3. A word is **written by the system** if it splits as front + middle + ending with all three in the lists.
4. Sizes: (kF, kM, kE) = (5, 15, 10), **(10, 30, 20) primary**, (20, 60, 40). 60 pieces in the primary system.

## Reported
- **Coverage**: share of check-half tokens (running words) and of check-half word types the system writes. Build-half
  coverage also reported (in-sample).
- **Fill rate**: of all kF × kM × kE combinations, the share that are actual word types in the whole 28,841-token text
  (how freely the pieces combine).
- The three lists for Voynich in full.
- Texts: Voynich; latVUC, hboWLC (consonants), turytc, deu1912, eng-kjv, indayt, hun, tglulb; generator seeds 31–33.

## Reading (descriptive, set before the run)
- Voynich coverage above every language's → "the slot system fits Voynich better than any language tested".
- Inside the language range → "slot-built like ordinary languages".
- The generator's coverage is reported beside it; it is built from Voynich, so similarity there is expected and is not
  evidence for M on its own.
No ledger factor: a high coverage is predicted by an agglutinative language, a verbose cipher and a slot table alike.

## Disclosed (seen beforehand)
- 2026-10-27 descriptive count (shown to Arham): front pieces l, y, d, q, ot, o, ok, ch, sh come off leaving a word
  50–95% of the time; endings come off far less cleanly; families such as *kaiin / okaiin / qokaiin / lkaiin*.
- Literature: slot or "crust-mantle-core" word grammars (Stolfi; later forum slot grammars) report that most Voynich
  word types fit a slot pattern; STRUCTURAL_FINDINGS listed a slot_grammar model. No figure from those was used here.
- No coverage has been computed for any text with this recipe. One attempt.
- Script exercise on fabricated text: a true 5×5×5 slot text 100% written at the primary size; random letter strings 17%.
