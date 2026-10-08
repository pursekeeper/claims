#!/bin/sh
# Recomputes each claim folder's commitment: sha256 over the sorted `sha256sum` list of its files.
cd "$(dirname "$0")" || exit 1
while read id h dir; do
  c=$(cd "$dir" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)
  [ "$c" = "$h" ] && echo "$id OK" || echo "$id MISMATCH $c"
done < commitments.txt
