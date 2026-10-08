# Claim 14: Hamiltonian induced subgraphs of the honeycomb lattice: unique cycle up to 36 vertices, first double at 38

## Exploration
- `exploration/sap_honey.py` — enumerates honeycomb self-avoiding polygons by length, reduces to free polygons and to distinct free vertex sets, and reports both counts
  (equal through length 30 in the original run). `python3 sap_honey.py L`.

## Blind review
- `blind-review/poly.c` + `ham.h` — C enumeration of honeycomb SAPs up to L vertices (distance pruning), free reduction, then Hamiltonian-cycle count of the induced
  subgraph on each vertex set that has chords; prints, per length, the number of free polygons, of vertex sets, and the maximum cycle count. `gcc -O3 -o poly poly.c; ./poly 40`.
  Result: max cycle count 1 for every length <= 36; at 38 exactly one vertex set has 2 cycles; at 40 further multi-cycle sets appear (the exact count at 40 was not settled
  consistently in the original run and is deliberately excluded from the public claim).
- `blind-review/verify38.py` — independent check of the 38-vertex set with a different embedding (Z^3, a+b+c in {0,1}): prints 49 edges, degree multiset, and
  "directed Hamiltonian cycles from 0: 4 => undirected: 2". `python3 verify38.py` (a few minutes, unpruned DFS with reachability cut).

## Statement lines <-> outputs
- Part (b) (49 edges, 16 x degree 2 + 22 x degree 3, exactly 2 undirected Hamiltonian cycles): `verify38.py` output.
- Part (a) (uniqueness through 36, exactly one double at 38): `poly.c` run output; the vertex-set counts 97 .. 53793 for lengths 24..36 appear in the same output.
- The coordinates in the public statement are the Z^3 image of the (x, y) list in `verify38.py` under the map used there.
