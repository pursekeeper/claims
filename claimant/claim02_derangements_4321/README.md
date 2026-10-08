# Claim 2: derangements avoiding 4321 (n = 1..24)

## Exploration
- `exploration/der4321.cpp` — same DP as the 1234 case with decreasing piles. `g++ -O2 -o der4321 der4321.cpp; ./der4321 N 1`.
- `exploration/brute.c` — brute force (prints the der&LDS<=3 column). `outputs/der4321_21.txt` — DP run to n = 21.

## Blind review
- `blind-review/dp.cpp`: `./dp 24 3 1 1` (decreasing mode) -> `outputs/got4321.txt` (~26 s). `blind-review/brute.c`: second column of `outputs/brute12.txt`.
- `outputs/claim4321.txt` — the 21 claimed terms diffed by the reviewer.

## Statement lines <-> outputs
- b(1..21): `der4321_21.txt` and `got4321.txt`, identical; b(22..24): `got4321.txt` only.
