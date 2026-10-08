# Claim 6: K(n), O(n), C(n) for knight graphs of polyominoes, n = 1..18

## Exploration
- `exploration/knightpoly.c` — Redelmeier enumeration of fixed polyominoes (MODE 0) or polyknights (MODE 1), canonical filter to free,
  bitmask BFS for knight-graph connectivity, DFS for Hamiltonian path/cycle with connectivity and degree pruning; optional 2-way split.
  Build: `gcc -O3 -o knightpoly knightpoly.c`. Run: `./knightpoly N [MODE] [K r]`. Output: fixed, free, connfixed, conn (= K), open (= O), closed (= C).
- `exploration/recttest.c` — rectangle validator (3x4 open only, 4x4 none, 5x6 closed, ...).
- `outputs/r14.txt` .. `r18_1.txt` — runs for n = 14..18 (n = 17, 18 split in two halves; sum conn/open/closed across halves).

## Blind review
- `blind-review/poly.cpp` + `knight.h` — independent C++ implementation. `g++ -O2 -pthread -o poly poly.cpp`; `./poly free N` (A000105 check), `./poly knight N` (K, O, C).
  `outputs/review_big.log` — n up to 18. `blind-review/rect_test.cpp` — classical rectangle facts. `blind-review/brute.py` — unpruned Python, n <= 10.
- `blind-review/rev_kt.c`, `rev_poly.py`, `outputs/second_review_rev14.out` — a second, separate re-derivation to n = 14 (Python polyomino generator feeding a C knight-graph checker).

## Statement lines <-> outputs
- K, O, C for n = 14..18: `r14.txt`..`r18_*.txt` (exploration) and `review_big.log` (review); n <= 14 also in `second_review_rev14.out`.
- C(odd n) = 0 is a theorem (bipartite knight graph), reproduced by all runs.
