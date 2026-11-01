# Open-web sweep, 2026-11-01 (Arham: "one last time … anything out there we have missed")

Five research agents, one area each, public pages only:
- recent computational papers;
- community forums;
- physical evidence;
- gibberish generators;
- decipherment claims.

There were no downloads and no logins; one cached PDF was deleted unopened. Most voynich.ninja replies sit behind a
login, so usually only a thread's opening posts were read. These are leads, not verified results. Each needs our own
pre-registered test before it can enter the ledger.

## New to the programme (ranked)
| # | Source | Claim | Bears on | Our test |
|---|---|---|---|---|
| 1 | Zhang & Sheng, arXiv 2610.34499 (Oct 2026) | 16 accounts fitted on 22 statistics, checked on 15 held out. Copying (Copy-T) misses no held-out statistic by more than 5 sd; one-key ciphers miss by 100–200 sd. **A two-key cipher, a word-class cipher and a two-key nomenclator with heavy miscopying are not excluded.** The glyph link across word boundaries (0.204 bits) is reproduced by nothing. | M vs C | A two-key (A/B) word-class cipher on our battery; measure boundary coupling on our generators |
| 2 | Rozanova & Temerev, arXiv 2608.17096 (Aug 2026; code lrozanova/voynich-units) | Edge-glyph MI ≈ 0.2 bits; one word predicts the next by under 1%; uncertain spaces are physically narrower (AUC 0.905). Naibbe and self-citation reproduce low entropy but not the edge coupling or the rich vocabulary. | M (against current generators) | Edge-glyph MI on the Voynich, our generators and Naibbe |
| 3 | Layfield & Fagin Davis, *Digital Medievalist* 19 (2026), doi 10.4000/16k0a; thread-5896/5911/6219 | Written on loose single bifolios ("singulions"), sewn later out of order. Conjoint leaves are more similar than facing pages (Q6 0.448 vs 0.166), but Q2 is reversed. quimqu: Quire 20 ordering agreement 0.95 on the real text, above 5 generator runs. | M vs L; confirms C24 | Per-quire conjoint/facing similarity and ordering against generator nulls (check locked leaves first) |
| 4 | Parisel, arXiv 2604.25979 (2026; code labyrinthinesecurity/currier-models) | Each folio switches between cho and che (ΔAIC 2,549; 195/197 folios assigned). An order-2 Markov model gives 3–11× too little variance between folios. | M (a habit switch); A/B | Adopted in E120's two habit tables; switch by sheet vs scribe |
| 5 | Parisel, arXiv 2604.19762 / 2509.10573 (2025–26; Kaggle notebook) | Within words the order is optimised right-to-left, across words left-to-right; not seen in English, French, Hebrew or Arabic. A slot generator and a Cardan grille fail its four-signature joint test. | C (reversed words?) / M | LTR−RTL cross-entropy within words on languages, generators and Naibbe |
| 6 | Steckley & Steckley, arXiv 2404.13069 (Histocrypt 2024) | The word before a drawing is about 7.5% shorter and behaves like a line-final word; the word after behaves like a line-initial word; some words prefer or avoid drawing edges. | M (layout-driven) | "Before a drawing" as a second line end: herbal DEV vs generator |
| 7 | Hermes, VOY2022 paper 7 (R code hermesj/R_Voynich_Stats) | A Trithemius-style codebook (Polygraphia III) is closer to the Voynich than languages on word length, entropy and minimal pairs. | C | A word-per-letter code class (R4) on the battery |
| 8 | Bowern & Gaskell, VOY2022 paper 6 | Simple cipher manipulations reproduce the Voynich's odd word-level metrics, so those metrics do not prove gibberish. | C | Their transforms on our Bibles, on our battery |
| 9 | quimqu generator, thread-6219 (2026) | Rules: per-sheet habits; copies from nearby or the word above (~35%); half of copies changed; new words from a template plus a 2-letter chain; q- after -y; line-start and line-end forms; paragraph gallows. 58/64 measures within ±25%; held out 51/64 (real vs real 55/64). No public code. | M | Used to design E120 |
| 10 | Hauer–Kondrak alphagrams; Zattera slots read as in-word sorting; Schiffer 2024 | Words could be letter-sorted. | C (partly untested: E098 rated in-word sorting PARTIAL) | Sort real texts; compare slot conformity and glyph predictability |
| 11 | Physical: Pelling's slip lists (f111r, f26r, f115r); Stolfi's eye-skip on f105r (**locked leaf, not used**); retouching on f3v, f26v, f57v, f67r2, f71r, f72v; ink re-dip cycles (f31r) | Starting points for a correction census. No published count of corrections exists, and the Beinecke is not allowing new imaging. | L/C (exemplar copying) vs M | Correction census (step 2) |
| 12 | Timm 2026 ("One Hand, Five Labels"; "Dynamic Text") with rebuttals | One evolving hand rather than five scribes; slot shares constant while members drift. | Scribe facts | Scribe effect with book position controlled |

## Checked: nothing new
- No decipherment claim from 2017–2026 has made a held-out prediction that held up.
- No crib has independent agreement. Plant IDs have consensus for two or three plants at most; the Pleiades label
  fails as a crib.
- Recent self-published claims (Sinhala, Tironian, Italian anagram) are low value.
- Period chancery ciphers (three homophones on vowels, nulls, small nomenclators) fall in classes E098 already tested.
- There is no new physical finding about meaning.
