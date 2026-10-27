# E087 amendment 2 (second bug fix before any scored decoding)

The v2 rerun stopped at the same first step: the copy generator cannot return 40,000 words
(`AssertionError: generator output too short`); every earlier experiment asked it for 28,841. `experiments/e087_spaceless_attack_v3.py`
requests 28,841 words (1,209 lines are needed; the generator gives them). Nothing else changes.

Before locking this amendment the pipeline was smoke-tested in-process on Aramaic with 2 restarts × 200 iterations
(not the registered effort): a crack decode reached accuracy 0.32 and COVER 0.46, a Voynich A decode COVER 0.53, and the
line-Markov controls built. These smoke numbers show that badly decoded text already scores about 0.5 COVER (short
dictionary words are easy to find in continuous strings), which the controls and threshold are there to absorb. No
scored run has produced any result.
