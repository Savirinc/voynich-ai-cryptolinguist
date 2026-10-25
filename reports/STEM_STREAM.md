# E061 (campaign step 1): stems versus padding — VOID (the decision rule could not be won), stems look word-like

Pre-registration `reports/E061_PREREG.md` (sha256 f62bd71f…0055, commit 15c33b6). Script
`experiments/e061_stem_stream.py` (sha256 69da0163…4e68). Results: `experiments/results/e061.json`, `e061_run.log`.
Runtime 104 s. **No ledger factor.** One attempt only, as pre-registered: no v2.

## Verdict (pre-registered rule): VOID
| Control | Rule | Result |
|---|---|---|
| Padding controls, leave-one-out | ≥ 8 of 10 PADDING-LIKE | **0 of 10** |
| Caesar (held-out Latin) | WORD-LIKE | WORD-LIKE (z within 1.4 on all four) PASS |

**Why the control failed (design, not bug).** PADDING-LIKE required a text to sit beyond 3 sd of the 22 languages on
3 of 4 measures. The languages are so spread out (stems covering 95% of tokens: Tamil 205 to Arabic 3,200; collapse
0.48 to 0.91) that nothing is 3 sd away from them, not even a pure padding cipher. The rule was set without a feel
for that spread, which I had declared I would not look at. The test could not have returned PADDING-LIKE for anything.

## The numbers (unscored)
The segmenter is the E026 one; the top Voynich suffixes it found are y, (none), ol, dy, aiin, edy, ar, or, ain, al, o,
iin, and the top stems qok, ch, qoke, ok, che, ol, daiin, ched, ot, sh, she, qot.

| | Word types | Stem types | Stems covering 95% | Collapse | Stem hapax | Stem Zipf |
|---|---|---|---|---|---|---|
| **Voynich DEV** | 6,077 | **2,228** | **892** | **0.367** | **0.553** | −0.81 |
| 22 languages (range) | 1,046–7,204 | 667–4,642 | 205–3,200 | 0.484–0.908 | 0.285–0.567 | −1.16 to −0.65 |
| 10 padding ciphers | 2,902–4,286 | **288–985** | **156–442** | **0.099–0.282** | **0.062–0.214** | −0.95 to −0.81 |
| 10 generator samples | 3,167–4,338 | 1,195–1,515 | 365–545 | 0.325–0.377 | 0.366–0.409 | −1.01 to −0.81 |

| Voynich z against | Stems 95% | Collapse | Stem hapax | Stem Zipf |
|---|---|---|---|---|
| languages | −0.3 | −2.3 | +2.6 | +0.4 |
| padding ciphers | **+5.8** | +3.0 | **+7.8** | +1.2 |
| generator | **+7.6** | +1.4 | **+11.2** | +2.1 |

## Plain reading (descriptive; the verdict is VOID)
1. **The stems are not a small code alphabet.** A cipher that hides one or two letters in each stem and pads it with
   a null ending leaves 150–450 distinct stems doing 95% of the work, with few one-off stems. Voynich's stems number
   2,228, 892 of them cover 95%, and 55% of stem types occur once, more than any language except Swahili. On the two
   measures that matter most, Voynich is 6–8 sd from the padding ciphers and inside the language range. The "message
   in the stems, endings are padding" picture is not what the text looks like.
2. **The stems are also far from the generator** (z +7.6, +11.2): the generator's copying makes too few, too repeated
   stems. This is E032's vocabulary failure again, now at stem level.
3. **One oddity stands:** collapse. Removing the endings cuts Voynich's distinct forms to 37% of the word types; no
   language falls below 48%. The endings account for more of the word variety than in any language measured, though
   far less than in a padding cipher (10–28%). Together with C14 (free stem–ending combination), this still says the
   endings are *more* independent of the stems than grammar usually is, without making them nulls.
4. Had the control passed, Voynich would have been WORD-LIKE by the rule (3 of 4 within 3 sd of the languages), which
   would have applied C × 0.8. It is not applied.

## Consequence for the campaign
The step-3 attack is built on **words**, not stems: the stem stream behaves like a language's stem stream, not like a
code alphabet. The surviving cipher class is the per-scribe verbose cipher of E062, whose units are letter groups
spread across whole words, not stems alone.
