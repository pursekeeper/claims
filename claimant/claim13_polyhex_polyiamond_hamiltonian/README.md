# Claim 13: P6, C6 (polyhexes, n <= 15), P3, C3 (polyiamonds, n <= 22)

## Exploration
- `exploration/hamform.c` — Redelmeier enumeration of fixed polyhexes (`-DLAT=6`) or polyiamonds (`-DLAT=3`) in axial coordinates, canonical form under the
  12 symmetries, bitmask DFS for Hamiltonian path/cycle with reachability and degree pruning; also counts shapes whose inner dual is a path (`snake`, = A003104 / A151518)
  or a cycle (`ouroboros`). Build: `gcc -O3 -DLAT=6 -o hamhex hamform.c` and `gcc -O3 -DLAT=3 -o hamtri hamform.c`. Run: `./hamhex N [K r [depth]]`.
  Output fields: fixed (A001207 / A001420), free (A000228 / A000577), hamcycle (= C6 / C3), hampath (= P6 / P3), snake, ouroboros.
- `exploration/check.py` — unpruned Python recheck of every canonical shape dumped with `DUMP=1` (`python3 check.py LAT`).
- `exploration/sap_honey.py`, `saw_honey.py` — independent method: enumerate honeycomb self-avoiding polygons / walks and count distinct free vertex sets (= C3 / P3 for n <= 16).
- `outputs/hex_runs.log`, `tri_runs.log` — the runs (split halves for large n; add fields across halves).

## Blind review
- `blind-review/hex.c`, `iam.c`, `ham.h`, `test.c` — independent C implementation (honeycomb vertices as integer points (x, y) with (x + y) mod 3 != 2).
  `gcc -O3 -o hex hex.c; ./hex n1 [n2]`; `gcc -O3 -o iam iam.c; ./iam n1 n2` (two runs for up/down origin, see `iam_up.txt`, `iam_down.txt`: add the two).
  `test.c` — Hamiltonian tester harness on K4, Q3, Petersen, etc.
- `outputs/hex_11_13.txt`, `hex_14_15.txt`, `iam_up.txt`, `iam_down.txt`.

## Statement lines <-> outputs
- P6, C6: `hampath`, `hamcycle` in `hex_runs.log` and `hex_*.txt`; P3, C3: same fields in `tri_runs.log` and `iam_up.txt` + `iam_down.txt` (sum).
