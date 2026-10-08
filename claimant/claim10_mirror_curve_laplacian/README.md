# Claim 10: mirror-curve loop number = GF(2) nullity of the Laplacian; A397065 = odd spanning-tree count

## Part (a): L(P) = nul(P) for all free polyominoes with n <= 11
- `blind-review/rev_loops.py` — generates free polyominoes, traces the mirror curve (edge-midpoint nodes, diagonal moves, reflection at unshared sides) to get L(P),
  computes the GF(2) nullity of the Laplacian of the cell graph, and reports mismatches (0) and the distribution of L. `python3 rev_loops.py` (n <= 11, ~1 min).
- `outputs/rev_polys12.txt` — polyomino list used by the reviewer's scripts (if present).

## Part (b): number of free n-ominoes with tau odd, n = 1..17
- `exploration/polyphys.c` — enumerates free polyominoes and computes tau (exact Bareiss determinant in 128-bit integers, optionally double LU with cross-check).
  Build: `gcc -O3 -o polyphys polyphys.c`. Run: `./polyphys N [K r tag mode show]`; `mode` bit 0 = use double determinant, bit 1 = cross-check against Bareiss.
  The `tau_odd=` field of the summary line is the count. `exploration/runbig.sh` — the 2-way split used for n = 15..17; `exploration/merge.py N` merges the halves.
- `blind-review/rev_tau.py` — independent Python (numpy determinants) giving the odd-tau counts for n <= 12.
- `outputs/run_small.txt` (n = 1..13), `run_14.txt`, `big_15_*.txt`, `big_16_*.txt`, `big_17_*.txt` (halves; add `tau_odd` across the two halves).

## Statement lines <-> outputs
- Part (a): `rev_loops.py` output (0 mismatches, max L = 4 for n <= 11).
- Part (b): `tau_odd` fields for n = 1..17 = 1, 1, 2, 4, 11, 28, 86, 273, 915, 3126, 10948, 38782, 138719, 499351, 1808081, 6576500, 24013937.
