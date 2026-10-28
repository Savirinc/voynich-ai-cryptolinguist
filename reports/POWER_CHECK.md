# E090: power of the validated letter attack on texts unlike its model (approach check 1)

Pre-registration `E090_PREREG.md` (sha256 1ad15612…), script `experiments/e090_power_check.py` (sha256 43929b82…),
results `experiments/results/e090.json`, log `e090_run.log`. Run 2026-10-28, 1,709 s.

## Question
Every letter attack proved itself on ciphers of held-out books of the same Bible its model came from. Would it have
found a real *technical* text (recipes, a herbal, rabbinic writing) written in a Voynich-style cipher?

## Result (10 ciphers per text, Voynich-A length, E063 claim rule)
| Language | Threshold T | Controls max | Bible text: found / cracked | Technical text: found / cracked | Technical lexrate |
|---|---|---|---|---|---|
| Latin | 0.476 | 0.216 | 10/10 / 10/10 | recipes + agriculture **10/10** / 10/10 | 0.49–0.56 |
| English | 0.590 | 0.324 | 10/10 / 10/10 | Culpeper herbal **4/10** / 10/10 | 0.55–0.69 |
| Hebrew | 0.573 | 0.538 | 10/10 / 10/10 | Talmud **0/10** / 10/10 | 0.33–0.45 |

p_out = (1.0 + 0.4 + 0.0) / 3 = **0.467 → ABSENCE FACTORS TOO STRONG.**

## What it shows
- **The decoder itself is not the weak part.** It recovered the key of all 30 technical-text ciphers (accuracy 0.97–1.00,
  agreement 1.00), with a Bible model. Decodes read correctly, e.g. Culpeper: "pound sage wormwood costmary … sallad oil
  twenty pounds yellow wa four pounds malaga wine"; Talmud: "אמר רבי יהושע בנ לוי כתוב אחד אומר חצות לילה אקומ להודות".
- **The claim gate is the weak part.** It counts decoded words found in the Bible vocabulary. A correct decode of a
  technical text has fewer Bible words, so it can fall under the threshold.
- **Hebrew is worst:** the correctly decoded Talmud scores 0.33–0.45, *below* the meaningless pseudo-Voynich controls
  (0.54). Under this gate a correctly decoded rabbinic-style Hebrew text is indistinguishable from, in fact scores lower
  than, gibberish. The Bible-model Hebrew searches (E049, E050, E080, H5 in E082) could therefore exclude only Bible-like
  Hebrew. E084 used a Talmud model (in-genre for the Talmud); medieval technical or medical Hebrew is covered by neither.

## Ledger (pre-registered correction, f' = 1 − s·p_out)
| Entry | L old → new | C old → new |
|---|---|---|
| E049–E050 | 0.902 → 0.9428 | 0.92 → 0.9533 |
| E052 | 0.885 → 0.9329 | – |
| E053 | 0.958 → 0.9755 | – |
| E063 | 0.94 → 0.965 | 0.96 → 0.9767 |
Combined: L × 1.1518, C × 1.0542. **M 0.1005 → 0.0887, L 0.8682 → 0.8824, C 0.0273 → 0.0254, O 0.004 → 0.0035.**
Shares of forms inside L are recomputed in approach check 2 (ledger audit).

## Not covered
Three languages, one technical text each; p_out is a mean of very different values (1.0, 0.4, 0.0) and depends on how
far the text's vocabulary is from the Bible. A 15th-century technical text with period spelling would likely be further
away than Apicius or Culpeper, so the true power is plausibly lower still.
