# Claim 11: spanning-tree statistics of free polyominoes, n = 1..17 (single implementation + Python cross-check to n = 9)

- `exploration/polyphys.c` as in claim 10. Summary line fields: `max_tau` (= M), `max_tau_cnt` (= NM), `sum_tau` (= SUM), `unicyclic` (= UNI).
  DIST(n) = number of lines in `outputs/hist/hist_tau_<n>_x.txt` (histogram "value count", one line per distinct tau; for n = 15..17 produced by `merge.py` from the two halves).
- `exploration/xcheck.py` — independent Python generator + numpy determinants reproducing all statistics for n <= 9.
- `outputs/run_small.txt`, `run_14.txt`, `big_15_*.txt` .. `big_17_*.txt` — summary lines (halves must be merged with `merge.py`: sums add, maxima combine).
- The k = 1 column of the tau histograms reproduces A131482 (tree polyominoes) for n <= 12.

## Statement lines <-> outputs
- M, NM, SUM, UNI: summary fields per n; DIST: line counts of `hist_tau_<n>_x.txt`.
