# Claim 16: PHOIBLE contingency tables (ejectives x velar nasal)

Data: clone github.com/phoible/dev and check out commit adc867f4dd2be1bf4262395c69c33fe8c4a7e75e; the file is data/phoible.csv (MD5 866d36bc83ab21bdb5837ffa63dc5993).
Scripts refer to the data directory as `DATA/`.

## Deterministic tables (this is what the public claim asserts)
- `exploration/tables.py` — `python3 tables.py DATA/phoible/data/phoible.csv` prints Table A (all 3,020 inventories) and Table B (lowest InventoryID per Glottocode, NA glottocode dropped).
  `outputs/tables_out.txt` — its output: A = 39 / 226 / 1841 / 914, B = 31 / 147 / 1354 / 643.

## Context (not part of the pass criterion): the association analysis
- `exploration/00_load.py`, `10_final.py` — original analysis (one inventory per Glottocode by a source-preference rule, marginal segments excluded, family/macroarea joins,
  Mantel-Haenszel by family/area/grid, nearest-neighbour matching, logistic models). Requires pandas/numpy/statsmodels.
- `blind-review/build.py`, `analyse.py`, `analyse2.py` — the blind reviewer's independent analysis (random inventory per language, own family harmonisation, own controls).
  `outputs/out.txt`, `out2.txt` — its printed results (odds ratio 0.105 raw; 0.15-0.3 after family/area controls; effect absent in South America).
