# E090 pre-registration (approach check 1 of 4): does our letter attack find a real text that is not Bible-like?

Written 2026-10-28, before the run. Script: `experiments/e090_power_check.py`. Output: `experiments/results/e090.json`,
`e090_run.log`, report `reports/POWER_CHECK.md`. Updates `LEDGER.md`. Arham asked (2026-10-28) to test the approach
itself, four checks one at a time; this is the first.

## Question
Every validated letter attack (E047, E049, E052, E053, E063, E080–E084) proved its power on ciphers of **held-out books of
the same Bible** its language model was built from. The Voynich plaintext, if any, would be a 15th-century technical
text (herbal, recipes, astrology), not Bible prose. The absence rule (m = 0.2) treated each "not found" as a search with
about 80% power. **What is the attack's power when the plaintext is a different kind of text from the model?**

## Data
Language models exactly as used on Voynich: Latin = Vulgate OT books (E047 `LM_BOOKS`), English = KJV OT books (E052/E063
`OT_LM`), Hebrew = WLC OT books (E047). Plaintexts:
| Language | In-genre (baseline) | Out-of-genre |
|---|---|---|
| Latin | Vulgate EZK, PSA, PRO, JOB, 1–2CH | Apicius (recipes) + Cato, Varro, Columella (agriculture, plants), Latin Library, footer lines removed |
| English | KJV same books | Culpeper, *Complete Herbal* (Gutenberg 49513, body only) |
| Hebrew | WLC same books | Talmud (Berakhot, Shabbat, Pesachim; Mishnaic Hebrew + Aramaic; Sefaria) |
No Voynich text is decoded. Voynich A (DEV) supplies only its length (8,794 words), sign inventory and frequencies, and
the pseudo-Voynich controls, exactly as E063. LOCKED_TEST leaves are excluded as always.

## Procedure
Per language: 10 VOY23 ciphers (fresh key each, E047 encoder, 12% spelling slips) of each text, Voynich-A length;
7 controls (2 generator, 5 pseudo-Voynich-A). E047 attack settings (32 restarts x 30,000 iterations, 4-gram KN with
spaces). Seed 90090. 81 attacks.
- **Validation and threshold exactly as E063**, from in-genre keys 0 and 1: VALIDATED iff both have accuracy >= 0.80 and
  agreement >= 0.95 and min lexrate > max control; T = midpoint.
- **FOUND** = the E063 Voynich-A claim rule: agreement >= 0.95, lexrate >= T, lexrate > max control + 0.05.
- **CRACKED** = accuracy >= 0.80 (the key was recovered whether or not the rule would claim it).
- **p_out** = mean over validated languages of the share of out-of-genre ciphers FOUND.

## Decision table
| Outcome | Rule | Ledger |
|---|---|---|
| **ABSENCE FACTORS STAND** | p_out >= 0.8 | none |
| **ABSENCE FACTORS TOO STRONG** | p_out < 0.8 | each letter-attack absence factor f (E049–E050 L 0.902 / C 0.92; E052 L 0.885; E053 L 0.958; E063 L 0.94 / C 0.96) is replaced by f' = 1 − s·p_out, where s = (1 − f)/0.8 is the share it searched; the ledger is multiplied by f'/f for each |
| **VOID** | no language validates | none |
Shares of forms inside L (L-alpha-known etc.) are recomputed in approach check 2 (ledger audit), not here. Hebrew-campaign
tests (E080–E089) applied no ledger factor, so none is corrected; per-language power is reported for reading them.

## Disclosed (seen before locking)
- Dry run: for each plaintext, the share of its own true words (3+ letters) that are in the model's vocabulary, i.e. the
  lexrate of a **perfect** decode: Latin in-genre 0.85, recipes/agriculture 0.56; English in-genre 0.96, Culpeper 0.71;
  Hebrew in-genre 0.75, Talmud 0.42. Past thresholds were about 0.5–0.6 (Hebrew 0.57 in E049), so low power on the
  Talmud is expected before running; Latin and English are open.
- Smoke run with 2 restarts x 300 iterations, 2 keys (pipeline check only; nothing validated, numbers meaningless).
