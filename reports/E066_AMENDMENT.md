# E066 amendment (before the rerun): a bug fix, with no change to the method or rules

Written 2026-10-25. The original pre-registration (`E066_PREREG.md`, sha256 b1d00ba2…b28405) and script
(`e066_word_individuality_v3.py`, sha256 d9708d04…f158ee) stay locked and unchanged. The rerun uses
`experiments/e066_word_individuality_v3_v2.py`.

## What went wrong
After all 81 statistics had been computed, the script crashed while filing the language results: the result dictionary
has a key `languages`, and the job kind is `language` (`KeyError: 'language'`, line 83). Nothing had been written to
disk; no statistic was seen (the log holds only the job count line and the traceback).

## The fix
One line: results of kind `language` are filed under `languages`. Everything else is byte-identical (see the diff in the
commit). Seeds, texts, statistic, gate and decision table are unchanged.
