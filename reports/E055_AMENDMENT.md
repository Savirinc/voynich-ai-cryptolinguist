# E055 amendment (before any rating): label-mask size fix

Written 2026-10-24. The original pre-registration and script stay locked. The run uses
`experiments/e055_same_label_pairs_v2.py`.

## Bug
The paper-coloured boxes that blank out labels were sized as 2.2% of the *canvas width*. Several Beinecke canvases
hold 2–3 pages side by side (fold-outs), so on those the boxes came out about 3× too large and covered parts of the
drawings. This was seen in the one pair image inspected (P01).

## Fix (v2)
The half-height of each box is now 1.6% of the canvas *height*, which is about 2.2% of one page's width on every
canvas. **Nothing else changed:** same items, same pairs, same seed, same judges' prompt, same decision rule.

## Disclosed
- One pair image (P01, from the v1 build) was viewed to check the masking. Its pair type was not looked up.
- Some drawing boxes from the mapping agents are imprecise; P01's right crop is mostly text. This is a property of
  the maps fixed before the test, and is left as is: it adds noise to all pair types alike.
