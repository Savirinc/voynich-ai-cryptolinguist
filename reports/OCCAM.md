# Occam reset (2026-10-20)

**Why.** Since E016 every step has added another layer: a verbose cipher, sandhi, nulls, codebooks, a stem + ending
code, a learned split, a self-null. Each layer adds free parameters. A key with thousands of free parameters can fit
gibberish as well as it fits Latin, which is exactly what the Rugg control showed in Stage B. Adding more layers to
fix that is the loop we are in.

**Rule from now on.** Explain *all* the measured facts at once, with the fewest moving parts. A new part (a cipher
layer, a code, nulls, drift) is allowed only when a specific fact cannot be explained without it, and that has been
shown. Hypotheses are tested from the simplest upwards.

## The facts every hypothesis must explain (all measured on DEV)
| # | Fact | Source |
|---|---|---|
| F1 | Glyphs are very predictable inside words: h2 2.10–2.48, against ≥ 2.79 for our 34 languages | E002, E024 |
| F2 | Word-sized units carry topic | E019 |
| F3 | Common words persist the way grammar words do | E021 |
| F4 | A compact set of ~28 endings, only partly written with their own glyphs | E026 |
| F5 | Strong line-start and line-end conventions | E025 |
| F6 | No glyph grouping behaves like an alphabet of our 34 languages | E012, E024 |
| F7 | Ruled out as tested: fixed-key letter cipher, Naibbe × la/it/fr/de, Rugg, self-citation, European syllables | E011–E021 |

## The ladder, simplest first
| Rung | Hypothesis | Moving parts | Tested properly? |
|---|---|---|---|
| 0 | **A natural language written plainly in its own script**, one Voynich word per spoken word or syllable | 1 (the script) | **No.** F1/F6 rule it out only against European-type languages with complex syllables. Languages with rigid, simple syllables (Vietnamese, Mandarin pinyin, Hawaiian, Māori, Japanese kana) were never compared |
| 1 | As rung 0, but some sounds are written with fixed glyph groups (e.g. *ch*, *aiin*) | 2 | Partly (E012/E024), and against the same European set only |
| 2 | Meaningless text made by a human habit | 1–2 | Only for the generators we wrote |
| 3 | A cipher or code over a known language | 3+ | This is where almost all our effort went (E016–Stage B) |

**The gap.** We jumped to rung 3 before rung 0 had been tested against the right comparison languages. Rigid
syllable structure is the plainest explanation for F1 (low h2), F4 (a small set of word endings: the "rhymes" of a
syllable language) and the slot-like word structure that earlier researchers have described. It needs no key at all.

## Next test (E027, to be pre-registered)
Question: is Voynich's within-word predictability (F1) and ending profile (F4) inside the range of natural
languages with rigid, simple syllables, written plainly?

- Comparison languages: Vietnamese, Mandarin pinyin, Hawaiian, Māori, Samoan, Japanese romanised kana. These are
  added to the 34, with the same cleaning and size-matching as E024 and E026.
- Statistics: E024's h1, h2 and word length; E026's SPLIT, NSUF95 and DIST.
- Decision: rung 0 or 1 **survives** if any simple-syllable language contains Voynich within its range on all of
  them. It is **out** if none does, which would then justify going up the ladder.
- The test has no key and no search, so it has nothing to overfit.
