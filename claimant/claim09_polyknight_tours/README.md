# Claim 9: polyknights (A030446 objects) admitting an open / closed knight's tour, n = 1..10

## Exploration (single implementation)
- `exploration/knightpoly.c` in MODE 1 enumerates polyknights (cells connected by knight moves) instead of polyominoes. `gcc -O3 -o knightpoly knightpoly.c; ./knightpoly N 1`.
- `outputs/polyknight_tours_1_10.txt` — free (must equal A030446), open (= PO), closed (= PC) per n.

## Statement lines <-> outputs
- PO(1..10), PC(1..10): `open=` and `closed=` fields; A030446 side condition: `free=` field.
