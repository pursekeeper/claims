# Claim 7: 9-cell open-tourable boards: 57 boards / 94 tours / 14 unique-tour boards in the 4x4 frame

## Exploration
- `exploration/nine.py` — pure-Python re-derivation: grows free polyominoes, enumerates undirected Hamiltonian paths of the knight graph,
  canonicalises each path under the board's automorphisms, prints every tourable board with its tour count, frame and hole flag. `python3 nine.py 9` -> `outputs/nine9.txt`.
- `exploration/knightcount.c` — C implementation counting geometrically distinct tours by Burnside over Aut(board). `gcc -O3 -o knightcount knightcount.c; ./knightcount 9`.

## Blind review
- `blind-review/poly.cpp` + `knight.h`: `./poly detail 9` -> `outputs/detail9.txt` (per board: bounding box, |Aut|, directed paths, undirected paths, tours up to symmetry, ASCII picture).
- `blind-review/brute.py`: `python3 brute.py 9 detail` -> `outputs/brute9.txt` (independent canonicalisation method; same 57 boards and counts).
- `blind-review/rev_nine.py` — a third, separate re-derivation (novelty reviewer) giving the per-frame breakdown 3x4 7/11, 3x5 12/17, 4x4 26/49, 4x5 11/16, 5x5 1/1.

## Statement lines <-> outputs
- 57 boards, 94 tours: totals in `nine9.txt`, `detail9.txt`, `brute9.txt`.
- Distribution 34/15/4/3/1 by tour count, per-frame table, and the fourteen 4x4-frame boards with exactly one tour: read off `detail9.txt` (boards labelled `w=4 h=4 ... toursUpToSym=1`).
