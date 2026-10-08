# Claim 1: derangements avoiding 1234 (n = 1..24)

## Exploration
- `exploration/der1234.cpp` — exact DP (state = used-value bitmask + patience-sorting pile tops, 128-bit counts).
  Build: `g++ -O2 -o der1234 der1234.cpp`. Run: `./der1234 N MODE` with MODE 1 = derangements avoiding 1234,
  0 = all 1234-avoiders (should give A005802), 2 = derangements only (A000166). Prints one line per n <= N.
  n = 21 needs ~10 GB RAM with this implementation (hash maps); n <= 20 fits in ~4 GB.
- `exploration/brute.c` — brute force over all n! permutations (LIS/LDS/fixed points computed directly). `gcc -O2 -o brute brute.c; ./brute` (n <= 12, ~3 min).
- `exploration/cand1.py` — generic Python pattern-containment brute force used for the first screen (n <= 9). `python3 cand1.py 9`.
- `exploration/analyze.py` — recurrence search (no linear recurrence with small polynomial coefficients found); not part of the claim.
- `outputs/der1234_out.txt` — DP output n <= 20 (MODE 1); `outputs/der1234_21.txt` — n = 21 run.

## Blind review (independent re-derivation, different algorithm)
- `blind-review/brute.c` — Heap's-algorithm brute force printing der&LIS<=3, der&LDS<=3, LIS<=3, derangements per n. `gcc -O2 -o brute brute.c; ./brute 12` -> `outputs/brute12.txt`.
- `blind-review/dp.cpp` — rank-compressed transfer DP. `g++ -O2 -o dp dp.cpp; ./dp 24 3 0 1` = (nmax, max LIS, 0 = increasing, 1 = derangements) -> `outputs/got1234.txt` (n = 1..24, ~96 s). `./dp 11 3 0 0` reproduces A005802; `./dp 9 99 0 1` reproduces A000166.
- `outputs/claim1234.txt` — the claimed 21 terms that the reviewer diffed against `got1234.txt`.

## Statement lines <-> outputs
- a(1..21): `der1234_out.txt` + `der1234_21.txt` (exploration) and `got1234.txt` (review), identical.
- a(22..24): `got1234.txt` only (review DP).
- Side conditions A005802 / A000166: MODE 0 / MODE 2 of `der1234`, and the third/fourth columns of `brute12.txt`.
