# Voynich Experiment 063: original-image and independent-transcription audit

**Date:** 14 October 2026  
**Source:** User-provided ZL3b EVA IVTFF transcription (13 May 2025), plus public folio photographs and independent EVA transcriptions (Currier, Takahashi, First Study Group and Stolfi, where checked).  
**Conclusion:** There is a real positional pattern involving EVA `m`, but **no demonstrated identity** between `-m` and `-iin`; an exclusive phonetic, minim, or line-saving interpretation would be premature.

## Visual comparisons and transcription checks

| Folio | Exact loci | Candidate forms | Review outcome |
|---|---|---|---|
| f46v | lines 1 and 3 | `daiin` / `dam` | Strong transcription cross-check: Currier, Takahashi, and Stolfi agree; both appear at **line ends**. No visual proof of stroke identity from reduced B&W scan. |
| f34v | lines 2 and 9 | `oldam` / `oldaiin` | Both at line ends; several transcribers agree, but Stolfi reads **`oldaiiin`** instead of `oldaiin`. |
| f3r | line 20 | `aiin` / `am` | Occur in the same manuscript line; transcribers disagree on the boundary near `s.aiin`, while `am` is stable. Position also differs: `am` closes the paragraph. |
| f8r | line 19 | `kaiin` / proposed `kam` | **Do not treat as a clean pair:** original ZL gives `dai,kam`; the boundary is unclear. |
| f6r | lines 2 and 3 | `daiin` / `dam` | Candidate contrast is transcribed, but positions differ. |

### What the photographs themselves show
The published black-and-white scans permit identifying the text bands and individual line locations. They are not sufficient to prove that the ending stroke of EVA `m` is physically composed from the ink strokes used in `iin`, or to adjudicate all connected-character boundaries. The 2014 color scans from Yale would be required for a decisive microscopic paleography study, ideally with independent human reviewers. **This audit does not claim to have completed a native-resolution pixel/stroke segmentation.**

## Recalculation from the full running-text transcription

- Total unambiguously parsed running-text tokens: **32,132**.
- Tokens ending in EVA `m`: **848**, distributed across **319** distinct forms.
- **617/848 (72.76%)** occurrences of `-m` words have a same-preceding-characters `-iin` counterpart *somewhere* in the running corpus.
- Only **121/319 (37.93%)** distinct `-m` word spellings have such a counterpart.

### Important specificity controls

For each `...m` word, ask whether `...X` is attested, with the same preceding written characters:

| Replacement | Fraction of `-m` occurrences with a corresponding `...X` form |
|---|---:|
| `iin` | **72.76%** |
| `in` | 64.62% |
| `r` | **80.54%** |
| `l` | **78.07%** |
| `n` | 46.70% |
| `id` | 8.96% |

Some alternative endings have an even higher lexical overlap than `iin`. These are **not** controlled for suffix frequency or independent semantic meaning, and therefore **cannot** be taken as a decisive ranking of competing allograph hypotheses. They *do* show the original 72.76% overlap is not by itself specific evidence for `m = iin`.

The 2022 peer-reviewed Matlach, Janečková and Dostál paper presents the distinct possibility that `m` is graphically an `i+d`-like ligature and `n` a word-final variant of `i`, as hypotheses rather than verified values. The sparse literal `...id` overlaps do not refute a ligature model because a ligature need not coexist with its decomposed form in normal writing.

## Decision and next experiment

1. Keep EVA `m`, `n`, `i` and composite minim runs as **separate observed written categories** until image-based evidence demonstrates a relationship.
2. Continue treating the line-final bias of `m` as a real positional phenomenon, but not proof of synonymy or a replacement cipher.
3. Obtain native-resolution 2014 color images for five prioritized examples (and wider controls), precisely crop the glyphs, assign pen-stroke and word-boundary judgments by two independent readers, and measure inter-annotator agreement.
4. If a well-supported graphical identity emerges, train a reversible contextual-allograph encoder on held-out folios and test exact-word prediction with frequency-matched placebo mergers.

## Sources
- User-uploaded `IVTFF Eva.txt.docx` (ZL3b, 2025-05-13), inspect with `voynich_experiment_063.py`.
- Independent f46v transcription: https://vib.tamagothi.de/index.php?id=f46v&show=page
- Independent f34v transcription: https://vib.tamagothi.de/index.php?id=f34v&show=page
- Independent f3r transcription: https://vib.tamagothi.de/index.php?id=f3r&show=page
- Public folio photographs: https://www.voynich.com/folios/
- Yale source digital viewer: https://collections.library.yale.edu/catalog/2002046
- Matlach et al., PLOS ONE (2022): https://doi.org/10.1371/journal.pone.0260948
