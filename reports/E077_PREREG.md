# E077 pre-registration: is a label word odd in its bridge (like a foreign name) or everywhere?

Written 2026-10-27, before the run, at Arham's direction (option 3 of three; working model: front = optional add-on,
middle = bridge that is never a word alone, ending = fixed set of about 20). Script
`experiments/e077_label_oddness.py`; output `experiments/results/e077.json`, `e077_run.log`; report
`reports/LABEL_ODDNESS.md`. Descriptive under the working assumption L; **no ledger factor**.

## Question
Labels carry five times more words that the kit cannot build (2026-10-27 count). If labels are names, the oddness
should sit in the **bridge** (a foreign or special stem) while the **ending** stays an ordinary ending, as names in a
herbal take normal endings. If labels are odd everywhere, they look less like names.

## Measure
- Lists from the text's ordinary words: 10 commonest fronts (0–3 characters), 20 commonest endings (0–4). Each word is
  cut into front (longest listed match), ending (longest listed match), bridge (the rest). A bridge is **known** if it
  is the bridge of ≥ 3 different ordinary word types.
- Normal rate per slot: front present, ending present, bridge known.
- Target vs control: control = rare ordinary words (frequency 1–2), drawn to match the target's word lengths.
- Excess oddness per slot = control normal rate − target normal rate; bootstrap (2,000) z for the bridge excess, the
  ending excess, and bridge excess − ending excess.
- Reading: **NAME-LIKE** if z(bridge) > 3 and z(bridge − ending) > 3; **ODD EVERYWHERE** if otherwise z(bridge) > 3
  or z(ending) > 3; **NOT ODD** otherwise.

## Texts
- Known answer: Latin Vulgate (latVUC, whole text, capitals kept). Names = word types that appear capitalised in the
  middle of a sentence and never in lower case (length ≥ 3; all-capital headings ignored). Target = all name tokens;
  ordinary = all other words. **Validity: Latin names must read NAME-LIKE; otherwise VOID.**
- Voynich: DEV, clean tokens, LOCKED_TEST excluded. Target = every label token (all sections). Ordinary = prose word
  types; control pool = prose types with frequency 1–2.

## Disclosed (seen beforehand)
2026-10-27 count: kit-misfit words per 1,000 tokens — labels 108, circle text 44, prose 19. E055/E073: same-label
drawings do not look alike. Toy check: planted foreign-stem names NAME-LIKE (z +63), random ordinary words NOT ODD.
No real text has been measured with this script. One attempt.
