# E099 amendment (2026-10-30): indentation fix, before any run

The locked script `e099_phrase_repeats.py` fails to start (IndentationError at line 148): a last pre-lock edit, which
removed an unused line, left the seed-check line indented 4 spaces too far. It never ran, so nothing was measured with
it.

`e099_phrase_repeats_v2.py` is identical except:
- that one line is dedented;
- the docstring's run line names the new script.

The diff is two lines. Design, data, measures and decision table are unchanged from `E099_PREREG.md`. The v2 smoke run
(no Voynich) gives meaningful Q3 p10 7.59, minimum 6.06, generator maximum 4.63: VALID.
