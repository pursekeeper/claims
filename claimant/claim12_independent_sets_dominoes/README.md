# Claim 12: independent-set and domino-tiling statistics of free polyominoes (single implementation + Python cross-check to n = 9)

- `exploration/polyphys.c` as in claim 10. Summary fields: `min_is` (= IMIN), `max_is` (= IMAX), `sum_is` (= ISUM), `sum_pm` (= MSUM for even n), `max_pm` (= MMAX for even n).
  IDIST(n) = number of lines in `outputs/hist/hist_is_<n>_x.txt`. The domino histograms `hist_pm_<n>_x.txt` give the number of polyominoes with 0, 1, 2, ... tilings;
  the 0- and 1-columns reproduce A213376 and A213377 for even n <= 16.
- `exploration/xcheck.py` — independent Python check for n <= 9.
- `outputs/*` — same run files as claim 11.

## Statement lines <-> outputs
- IMIN, IMAX, ISUM: summary fields; IDIST: line counts of `hist_is_<n>_x.txt`; MSUM, MMAX: `sum_pm`, `max_pm` fields for n = 2, 4, ..., 16 (k = n/2).
