# Claim 15: polyhexes whose inner dual is exactly a cycle, n = 1..13 (single implementation)

- `exploration/hamform.c` built with `-DLAT=6` (see claim 13); the `ouroboros=` field counts shapes whose inner dual is a cycle graph, the `snake=` field those whose inner dual is a path (= A003104).
- `outputs/hex_ouroboros_1_13.txt` — one line per n = 1..13.

## Statement lines <-> outputs
- R6(1..13) = `ouroboros` field; A003104 side condition = `snake` field.
