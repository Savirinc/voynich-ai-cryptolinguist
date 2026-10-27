# E072 pre-registration: is ot/ok a detachable front piece? (layers q, ot/ok, qot/qok)

Written 2026-10-27, before the run. Script: `experiments/e072_front_pieces.py`. Output: `experiments/results/e072.json`,
`e072_run.log`, report `reports/FRONT_PIECES.md`. Updates `LEDGER.md`.
Label-class programme (`CLAUDE.md` §6), after step 0 and E071; Arham's question of 2026-10-27: *ot* and *ok* stay
constant while the rest of the word changes; are they root-like or marker-like?

## Question
Voynich words are built front to back as (q)(o)(tall letter)(short core)(ending). Take the front piece off a word.
Does the leftover stand as a word of its own more often than when an ordinary beginning of the same length is taken off
a matched word? If yes, the front piece is **detachable**, like Arabic *al-* ("the"), Hebrew *ha-*, Hungarian *meg-*:
a marker sitting on a separate word. If no, it is **fused** into the word, like part of a root.

## Earlier work (checked 2026-10-27)
- E038: *q±* pairs (86) share neighbours (t_nbr 0.87) and partly different pages; *t/k* almost one sign (t_nbr 1.13).
- E059: *q* is a junction form, mostly after a word ending in *-y*. Step 0 (2026-10-26): *qo*+tall-letter words follow
  *-y* words 0.746 vs 0.29–0.38.
- 2026-10-25 descriptive pass: label words with the *o* removed are text words only at chance.
- E061 stripped the *endings*, not the front. STRUCTURAL_FINDINGS P5 measured the *ot/ok* share of labels only.
- No earlier test strips *ot/ok* with matched controls.

## Measure
For a front piece P and a text: targets = word types with frequency ≥ 2 that start with P and are at least
len(P) + 1 long. REM = share of targets whose remainder (the word without P) is a word type with frequency ≥ 2.
Control: 1,000 draws; each target replaced by a random non-target type of the same length and log2 frequency bin
(E071's matching, including its bin and length fallback), stripped of len(P) leading glyphs. z = (REM − mean) / sd.
Ten seeds 1,001–1,010; median z reported; a side holds if ≥ 8 of 10 seeds agree (rule 8). Bar z = 3.

## Texts
- **Voynich:** DEV prose, clean tokens (28,841; LOCKED_TEST excluded). Control types exclude every word starting with
  *q* or o + t/k/p/f.
  - Layer 1, **internal check**: P = *q* on words starting *qo*.
  - Layer 2, **primary**: P = *ot* and *ok* pooled (targets start *ot* or *ok*).
  - Layer 3, reported: P = *qot* and *qok* pooled.
  - Reported: P = *op/of* pooled; P = *o* on o + t/k/p/f words; layer 2 restricted to DEV label types.
- **Known answers** (28,841-token windows from token 10,000, E064 tokenizer; Arabic and Hebrew with vowel and
  cantillation marks removed and ٱ written ا): Arabic arb-vd P = ال; Hebrew hboWLC P = ה; Hungarian hun P = meg;
  Indonesian indayt P = ber.
- **False-claim controls:** in each known-answer text and in Voynich, a pseudo-target set (the target set's size, drawn
  as matched non-target types) scored by the same procedure.
- **Generator (M comparison):** Timm & Schinner seeds 31–33, 28,841 tokens each, layer 2 exactly as for Voynich.

## Validity
VALID iff all four known answers give z > 3 (8/10 seeds), all five false-claim sets give |z| ≤ 3 (8/10), and the
Voynich layer 1 check gives z > 3 (8/10). Otherwise VOID, no factor.

## Decision table (layer 2)
| Outcome | Rule | Ledger |
|---|---|---|
| **DETACHABLE, beyond the generator** | Voynich z > 3, and the generator z ≤ 3 in all three seeds | **L × 2** (a front marker on separate words is a language habit the copy process does not produce) |
| **DETACHABLE, generator too** | Voynich z > 3 and any generator seed z > 3 | none; recorded as a structural fact both sides produce |
| **NOT DETACHABLE** | Voynich z ≤ 3 | none for M/L/C; *ot/ok* recorded as fused (root-like); reading 2 of the label programme loses its marker form |
| VOID | validity fails | none |

Why only × 2 and no factor against L: detachable front markers are common in languages but slot-built gibberish can
produce them too, and the generator is the only meaningless process tested here; a fused front piece is ordinary in
languages and says nothing against L.

## Disclosed (seen beforehand)
- Design counts (types with frequency ≥ 2): DEV 1,956; starting *q* 267, *qo*+gallows 178, *ot/ok* 188, *op/of* 35,
  *ch* 293, *sh* 161, *d* 124.
- While choosing known answers: raw REM shares without matched controls: Arabic ال 0.41 (392 targets), Hebrew ה 0.53
  (350), Hungarian meg 0.37 (129), Indonesian ber 0.40 (98); unmatched strip-1 and strip-2 baselines Arabic 0.26 /
  0.20, Hebrew 0.40 / 0.28. Pointed Arabic and Hebrew gave 0 (marks change at the join), hence consonant text.
  English *un-* and German *un-* have too few words in a window and were dropped.
- Five Voynich examples were shown to Arham (otal→al, otar→ar, otol→ol, okaiin→aiin, oky→y); no Voynich REM or z has
  been computed.
- One attempt (rule 9); the script is exercised on fabricated text before locking.
- Script exercise on fabricated text: a planted detachable prefix z +66 to +89, a fused prefix z −0.2, pseudo-targets
  z −1.4 to +0.1 on a Zipf-like toy. A first toy whose prefixed words were all longer than any other word made the
  matching fall back to a small fixed pool and gave pseudo z +35; the control matching therefore widens length step
  by step (same frequency bin ± 1), then takes the 20 nearest candidates by length and bin. The fallback is counted
  and reported only through E071's merged-bin logic; no real text was used in the exercise.
