# Claim 17: Grambank contingency tables (GB147 x GB155, GB302 x GB155)

Data: clone github.com/grambank/grambank and check out commit 37f73da55cf8b426c82383f46a972bc59ce6cf76; the file is cldf/values.csv (MD5 399c99b4fbf50c83eb6b6725028d2420).
Scripts refer to the data directory as `DATA/`.

## Deterministic tables (this is what the public claim asserts)
- `exploration/tables.py` — `python3 tables.py DATA/grambank/cldf/values.csv` prints Table A (n = 1748: 404 / 581 / 88 / 675) and Table B (n = 1449: 292 / 1009 / 80 / 68).
  `outputs/tables_out.txt` — its output.

## Context (not part of the pass criterion): the association analysis
- `exploration/claim_passive_causative.py`, `famtest.py` — original analysis (one-language-per-family resampling, within-family permutation, GEE with family clusters, morphology-richness index).
  `outputs/claim_output.txt` — its printed results.
- `blind-review/prep.py`, `core.py`, `family.py`, `confound.py`, `breaks.py`, `wals.py` — the blind reviewer's independent analysis (run in that order; `prep.py` writes pickles to `./`).
  Conclusion there: association confirmed (adjusted OR about 3-5) but the "passive is special" framing not supported (other valency affixes predict causative affixes equally well).
