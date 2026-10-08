#!/bin/bash
cd ./
for n in 15 16 17; do
  ./polyphys $n 2 0 s0 1 1 > big_${n}_0.txt 2>&1 &
  ./polyphys $n 2 1 s1 1 1 > big_${n}_1.txt 2>&1 &
  wait
  echo "done $n $(date)" >> big_progress.txt
done
