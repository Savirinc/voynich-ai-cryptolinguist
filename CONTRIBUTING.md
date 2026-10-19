# Contributing: the quest is open

Anyone may test a hypothesis here: a cipher class, a language, a reading, an anchor, or "it's meaningless". We
welcome negative results as much as positive ones: a well-run NO CLAIM narrows the space for everyone.

## What makes a result acceptable here
1. **Known answers first.** If you propose an attack or a reading method, show that it recovers synthetic texts
   of its own hypothesis class at Voynich length, with every hidden part kept hidden (key, tables, inventory).
2. **Controls.** Run the same procedure on meaningless twins (Rugg grille, self-citation, letter-shuffled; see
   `docs/USING.md` §4). The method must make no false claims on them.
3. **Pre-registration.** Fill in `docs/PREREG_TEMPLATE.md` *before* looking at the Voynich result. Lock it
   (`chmod 444`), record its sha256, and commit it before or together with the run script.
4. **Whole text.** A reading must cover the text it is applied to, not selected words.
5. **LOCKED_TEST leaves stay closed.** They are reserved for one final, frozen confirmation decode. Do not load them
   during development (`E.voynich_lines()` already excludes them).
6. **Report everything.** Add your numbers to `experiments/LEDGER.csv`, and any failure or protocol slip to
   `experiments/FAILURES.md`.

## How to submit
- **Open an issue** describing the hypothesis and the planned test. That's the cheapest way to get feedback
  before you spend compute.
- **Send a pull request** with:
  - `experiments/eNNN_<name>.py`
  - `reports/ENNN_PREREG.md` (locked) and `reports/<NAME>.md`
  - result files under `experiments/results/`
  - any new tests under `tests/`
- Keep code in the style of the surrounding modules, and make sure `pytest -q` passes.
- Use experiment numbers above the current highest. Prefix them with your handle if you like (e.g. `E1xx`).

## Using it elsewhere
You're free to fork and build your own version under the MIT licence. If you publish anything that uses this
code, its methods, data or results, **please cite us** (see `CITATION.cff` or the BibTeX in the README), and cite
the third-party sources in `THIRD_PARTY.md`.

## Conduct
Be precise and kind. Criticise methods and results, not people. Claims are judged by the rules above, not by who
makes them, us included.
