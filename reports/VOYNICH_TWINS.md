# E011: Voynich twins (known-answer generators fitted to Voynich's fingerprint)

**Scope.** This is structural only (Gate 4 level). It ranks mechanisms by how well they reproduce Voynich statistics.
It decodes nothing and makes no semantic claim. **No decipherment.**

Code: `src/vcl/synthetic/twins.py`, `experiments/e011_twin_search.py`, `tests/test_twins.py`.
Results: `experiments/results/e011.json`. Twin specs: `data/derived/twins_v1/specs.json`.
Logs: `experiments/results/e011_run.log` (search) and `experiments/results/e011_reanalysis.log` (final analysis).

## 1. Families and sources

All five families build EVA words from the same **glyph-chunk pools**: prefix, middle and suffix pieces of Voynich
DEV words, split by one fixed regex (`twins.split_word`). They also share one line-wrapping rule (target line width
taken from the DEV mean, 49.7 ± 18.2 glyphs). So every family gets the same glyph-shape prior, and the families
differ only in the mechanism that strings the chunks together.

| family | meaningful? | mechanism | source | citation check (WebSearch, 2026-10-17) |
|---|---|---|---|---|
| `naibbe` | yes (exact decode) | Plaintext is randomly respaced into unigrams and bigrams (p_bigram). Each unigram becomes one whole word; each bigram becomes prefix(1st letter) + suffix(2nd letter). There are 6 tables, chosen per letter with weights 5:2:2:2:1:1^skew. Plaintext spaces are dropped. | Greshko, *Cryptologia* 2025, doi:10.1080/01611194.2025.2566408 | **Verified**: paper, author, DOI and high-level design. The design details (respacing ~47:53, 6 tables, 5:2:2:2:1:1 ratio, no nulls, no line mechanism) come only from secondary sources (press, voynich.ninja posts by the author and his critics). The table *contents* were not available (paywalled), so ours are drawn from the chunk pools. **This is an approximation, labelled "Naibbe-style".** |
| `abbreviation` | yes (exact to the abbreviated text; expansion is lossy) | Medieval-style shorthand: brevigraphs for frequent words, prefix and suffix signs, suspension and contraction. Each unit then gets a positional prefix-free glyph code. | Cappelli, *Lexicon abbreviaturarum* (practice). Newbold 1921 and Feely 1943 are background for the idea. | Cappelli not re-verified. Newbold and Feely **unverified**. The sign inventory is data-driven (most frequent affixes of the source text), so it approximates a real system. |
| `syllabary` | yes (exact decode) | Onset-maximal syllabification. The top-N syllables get glyph clusters; rare syllables are spelled letter by letter. Optional `units_per_word` splits plaintext words into several ciphertext words; when set, plaintext spaces are not encoded. | Generic syllabary/abugida hypothesis | No single source (n/a) |
| `rugg_grille` | no (decoy) | A table of prefix/middle/suffix cells read through moving three-hole grilles | Rugg, *Cryptologia* 28(1), 2004, "An elegant hoax?" | **Verified via secondary sources** (Wikipedia, press). Table size and grille shapes are search parameters. |
| `self_citation` | no (decoy) | Words copied from the previous line (near the same position) or from a recent window, then mutated: similar-glyph substitution, prefix add/drop, combining two words, suffix swap | Timm & Schinner, *Cryptologia* (online 2019-05-25; vol. 44, 2020) | Title, authors and date **verified via secondary sources**. DOI 10.1080/01611194.2019.1596999 **unverified**. The mutation rules approximate the published description. |

The three meaningful families are deterministic given (params, seed, plaintext). Their decode functions are
round-trip tested in `tests/test_twins.py` (Latin and Italian, several seeds and parameter corners).

**Plaintexts** come only from role=tune books (used in the search) and role=ref books (the held-out text check);
role=test books are never used. Languages: Latin, Italian, German, Middle English, French, Spanish, Czech and
Hebrew. Book ids are in `e011.json["plaintext"]`. A chunk filter drops English front matter and other scripts; for
example, the Greek inside a Latin Homer edition is excluded.

## 2. Target and method
- **Voynich target:** DEV leaves only. The LOCKED_TEST leaves (1, 8, 9, 30, 35, 38, 51, 52, 56, 75, 86, 87, 102,
  105, 114) are excluded, and an assertion checks this. Prose and clean tokens are used, with lines kept in
  manuscript order. The text is cut at line boundaries into **14 blocks of about 12,000 symbols**.
- **Fingerprint:**
  - **FIT** (used by the search): h1, h_cond, glyph types, ioc×types, mean word length, **word-length CV**, word
    TTR, initial-glyph entropy, final-glyph entropy, never-initial mass. These are the e006/e007 features; the
    window features are averaged over four 3,000-symbol windows.
  - **HELD-OUT** (never seen by the search): double rate, top-word share, 1-glyph-word share, h3_cond, share of
    hapax word types, Zipf slope, adjacent identical words, edit-distance-1 neighbour share, **y→q log-OR,
    line-final m-vs-iin log-OR** and q→o share.
- **Distance:** RMS z, standardised by the SD across the 14 Voynich blocks (floored at 2% of |mean|).
- **Noise floor:** the leave-one-out distance of each Voynich block to the mean of the others. Median is
  **0.99 (fit) / 0.97 (held-out)**; the 90th percentile is 1.29 / 1.22.
- **Currier A vs B** as a scale: the distance between the A-block mean and the B-block mean is **1.43 (fit) /
  1.20 (held-out)**. Distances of 2 to 3 are therefore larger than the difference between Voynich's own two
  "languages".
- **Search:** for each family × language there were 420 random evaluations and 480 refinement evaluations (perturb
  the best). Each evaluation scores one sampled block on tune text. Decoys got 3× that budget (2,700 evaluations).
- **Final evaluation:** each combo's best parameters were regenerated 20 times with fresh seeds on tune text, and
  20 times on ref books (held-out text). The tables below report these re-evaluations. Search-time best values
  (1.0 to 1.9) are optimistic because of the winner's curse on a noisy single-block objective.

## 3. Results (final re-evaluation, mean of 20 regenerations)

Best combo per family:

| family | best language | fit dist (±sd) | held-out dist | held-out without type_hapax | ref-text fit / held | features missed (abs z ≥ 2) |
|---|---|---|---|---|---|---|
| naibbe | it | **2.11** ± 0.49 | 4.23 | **1.81** | 2.12 / 3.98 | types, word_ttr, type_hapax, y→q, line-final m |
| rugg_grille | – | 2.43 ± 0.38 | 9.77 | 3.87 | – | h_cond, types, wl_mean, never_init_mass, word_top_share, wl_1, type_hapax (z −30), Zipf slope, adj_repeat, ED1, y→q, m-final, q→o |
| self_citation | – | 2.55 ± 0.31 | 5.53 | 5.41 | – | h_cond, types, wl_mean, wl_cv, word_ttr, never_init_mass, double_rate, h3_cond, type_hapax, Zipf, adj_repeat (z +8), y→q, m-final, q→o (z −13) |
| syllabary | cs | 2.57 ± 0.20 | 5.72 | 4.32 | 2.53 / 5.42 | h1, h_cond (z +4.5), ioc, ttr, init/final entropy, type_hapax, q→o, line effects |
| abbreviation | enm | 4.78 ± 0.88 | 6.51 | 6.79 | 5.08 / 5.97 | **wl_mean (z +11), wl_cv (z +7)**, h_cond, ED1 (z −21), line effects |

Naibbe-style by language (all 8 languages were searched; fit / held-out / held-out on ref text):
it 2.11 / 4.23 / 3.98; de 2.19 / 3.52 / 3.47; **la 2.22 / 2.37 / 2.30** (best held-out combo overall); cs 2.32 /
3.75 / 3.67; he 2.36 / 3.01 / 3.61; fr 2.40 / 3.71 / 3.91; es 2.90 / 3.74 / 4.61; enm 2.94 / 3.59 / 3.93. The full
26-row table is `e011.json["combos"]`. The held-out-text numbers stay close to the tune-text numbers, so the fits do
not depend on the particular book used.

Observations:
- **Low h_cond (≈2.11) is still the core obstacle.** Every family ends up above it: Naibbe-style +1.8 z, Rugg
  +2.8, self-citation +3.0, syllabary +4.5. This matches e006.
- **Word-length CV 0.35 is reachable.** Naibbe-style (0.377), Rugg (0.372) and syllabary (0.363) get close, while
  plaintext in all 36 languages is above 0.42 (e007). Low dispersion is a property of these mechanisms, so it does
  not argue against language underneath. Abbreviation keeps whole plaintext words and inherits their long, variable
  lengths (CV 0.46).
- **Rare word types (type_hapax) are the strongest held-out discriminator.** Voynich: 0.71 of the word types in a
  block occur once. Naibbe-style 0.42, self-citation 0.56, syllabary 0.40, Rugg 0.00 (a finite table emits a closed
  vocabulary). Abbreviation is the only family that matches this feature, because it writes one ciphertext word per
  plaintext word, but it fails on length.
- **Line-position effects (y→q, line-final m) are missed by every family** (z ≈ −2 to −3.5), as expected: none has
  a line mechanism. Greshko reports the same gap for Naibbe. Line-wrapping alone does not create them.

## 4. Identifiability verdict

**NO TWIN.** None of the five families reaches Voynich's own block-to-block variation on the fit features. The best
is Naibbe-style/Italian at 2.11, against a noise floor of 0.99 (median) and 1.29 (90th percentile). It is also
further from Voynich than Currier A is from B. So the question "are meaningful and meaningless twins equally good?"
cannot be settled at the level of an exact twin. Within this library, the near-misses can be ranked:

| held-out comparison (20 vs 20 regenerations) | meaningful | meaningless | Mann–Whitney p |
|---|---|---|---|
| naibbe/it vs rugg_grille, all held-out | 4.23 | 9.77 | 7e-8 |
| naibbe/it vs rugg_grille, without type_hapax | 1.81 | 3.87 | 2e-7 |
| naibbe/it vs self_citation, all held-out | 4.23 | 5.53 | 0.018 (not < 0.01) |
| naibbe/it vs self_citation, without type_hapax | 1.81 | 5.41 | 8e-8 |

- The Naibbe-style verbose cipher is the closest family on the fit features *and* on features it was never fitted to.
  It beats the Rugg grille robustly. It beats self-citation clearly once the type_hapax feature is set aside
  (type_hapax dominates the RMS), but only marginally with that feature included. The script's automatic verdict is
  therefore **"held-out comparisons are mixed"**. The ranking favours a verbose homophonic mechanism over the two
  hoax mechanisms as implemented here. It does **not** show that Voynich encodes language. All three meaningful
  families would also need a line mechanism and a richer rare-word vocabulary before they could count as twins.
- Fit-feature differences between the families are small (2.1 to 2.6 for the top four families). On the e006/e007
  feature set alone, meaningful and meaningless mechanisms are close to **non-identifiable**: the separation
  appears only in the held-out word-level and line-level statistics.
- **Classifier check.** A logistic classifier separates the twin families from each other perfectly (pooled 5-fold
  AUC 1.0). However, its "language vs non-language" boundary does not transfer to an unseen mechanism: the
  leave-one-family-out AUC is 0.0, meaning it is systematically inverted. Its output for Voynich (p = 1.0
  "meaningful") is therefore not interpretable and is not used in the verdict.

## 5. Caveats
- **These are approximations.** Naibbe-style uses our tables, not Greshko's. The Rugg and Timm–Schinner rules are
  re-implementations from published descriptions. A failure of our version is not a refutation of the original
  proposal.
- **Shared glyph prior.** The chunk pools are taken from Voynich DEV. This makes glyph-level fit easier for every
  family equally, and it means that glyph unigram statistics (h1, entropies) are weak evidence.
- **Winner's curse.** The search scored single blocks, so the best re-evaluated distances are about 1 higher than
  the search-time best. A search that averages over several blocks per evaluation might reach lower distances. The
  budget was within the cap: 55 min search wall time on 3 workers. The syllabary family was the slowest, because
  building its prefix-free codes is expensive.
- **Thin held-out text for two languages.** enm/ref has 2 chunks and cs/ref has 7. The first run's English filter
  contained the word "to", which is a common Czech word, so cs/ref had 0 chunks. The filter was fixed and the final
  evaluation and analysis were rerun with `--reuse-search` (same searched parameters). Ledger rows exist for both
  runs; the rerun rows are marked REANALYSIS.
- The SD estimates come from 14 blocks, so z-scores on rare-event features (line-final m) are noisy. The Currier
  A/B comparison is used only as a scale; no variety-conditioned twins were fitted.
- LOCKED_TEST leaves were not read. No solver was applied to Voynich.

## 6. Using the twin specs
`data/derived/twins_v1/specs.json` holds the following: the chunk pools, the line-width layout, and, for all 26
family × language combos, the best parameters with their fit and held-out distances and the tune/ref book ids.
Usage:
`twins.generate(spec["family"], spec["params"], seed, pools, n_words, plain=<normalised tune/ref book text>,
width_mean=..., width_sd=...)`.
This returns the lines plus the key and the plaintext, so a later solver experiment can generate an unlimited number
of known-answer Voynich twins. For the meaningful families, the matching `decode` function gives the ground truth.

Commands (seed 11011):
`caffeinate -ims .venv/bin/python experiments/e011_twin_search.py --scale 3` (search, 3,296 s), then
`... --scale 3 --reuse-search` (final evaluation and analysis, 74 s).
