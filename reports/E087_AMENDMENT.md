# E087 amendment (bug fix before any decoding)

The locked script stopped at its first step, before any language model was built or any text decoded: the generator
directory arrived as a string (argparse) and `e032_copy_generator.generate` needs a `Path`
(`TypeError: unsupported operand type(s) for /: 'str' and 'str'`). `experiments/e087_spaceless_attack_v2.py` differs
only by wrapping the argument in `Path(...)` (and a comment). Pre-registration, data, settings, seed and rules are
unchanged. No result of any kind was produced by the failed run.
