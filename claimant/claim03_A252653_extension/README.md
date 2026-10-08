# Claim 3: A252653 a(13..18)

## Exploration
- `exploration/hampoly.c` — Redelmeier enumeration + canonical form + bitmask DFS for Hamiltonian cycle (even n) and path.
  Build: `gcc -O3 -o hampoly hampoly.c`. Run: `./hampoly N [PRUNE] [K r]`; PRUNE=1 skips shapes with >2 leaf cells before canonicalisation
  (a symmetry-invariant necessary condition); `K r` splits the recursion at depth 5 into K parts, this process takes part r.
  Output line per run: fixed, free, cycle count, path count. Fixed counts should match A001168, free counts A000105 (unpruned).
- `exploration/verify.py` — independent Python (frozenset canonical forms, subset-DP Hamiltonicity). `python3 verify.py N` (n <= 12).
- `outputs/run_0.log`, `run_1.log` — the two halves of the n = 18 run (path counts sum to 2024680); `u15.log`, `u16.log` — unpruned validation runs (free counts = A000105).

## Blind review
- `blind-review/review_hampoly.c` — independent C implementation (lexicographic-minimum canonical form, leaf/parity/connectivity pruning).
  `gcc -O3 -o review_hampoly review_hampoly.c; ./review_hampoly N [nproc pid]`. `outputs/out0.txt`, `out1.txt` — the two halves for n up to 18.
- `blind-review/brute.py` — unpruned Python cross-check (`python3 brute.py N`, n <= 11).

## Statement lines <-> outputs
- a(13..18) = 14916, 39592, 106630, 283409, 761763, 2024680: sum of the path counts in `run_0.log`+`run_1.log` per n, and in `out0.txt`+`out1.txt`.
- The same runs also produce A361288 (cycle counts), which was used only as validation.
