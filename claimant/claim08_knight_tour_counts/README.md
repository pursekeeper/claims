# Claim 8: geometrically distinct open/closed knight's tours over all n-cell boards, n = 7..16

## Exploration
- `exploration/knightcount.c` — enumerates free polyominoes, counts all undirected Hamiltonian paths/cycles of the knight graph (raw), applies Burnside over Aut(board)
  for geometrically distinct tours, and counts symmetric tours (orbits fixed by a non-identity automorphism). `gcc -O3 -o knightcount knightcount.c; ./knightcount N`.
- `outputs/knightcount_7_16.txt` — one line per n: openboards, opentours_geom (= T_open), opentours_raw (= R_open), closedboards, closedtours_geom (= T_closed), closedtours_raw (= R_closed), opensym (= S_open), closedsym (= S_closed).

## Partial independent checks
- `blind-review/rev_closed.py` — separate re-derivation of the 12-cell closed-tour table (190 boards / 236 tours / 27 symmetric / 58 holey) and the 10-cell counts (18 boards, 19 tours). `python3 rev_closed.py 12`.
- `blind-review/rev_nine.py` — separate re-derivation of the 9-cell open counts.
- Board counts for all n are covered by the blind review of claim 6. Tour totals for n >= 13 (open) and n >= 14 (closed) rest on `knightcount.c` alone.

## Statement lines <-> outputs
- All six sequences: `knightcount_7_16.txt`, columns as named above.
