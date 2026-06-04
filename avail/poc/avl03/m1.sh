#!/bin/bash
# M1: perf core-seconds per single queryProof request on the 4MB block.
set -e
H=0x433d1c5913a5bd694152194b4b0518fadb62bb77c4b3331b5cdbec870e194401
WIN=${1:-25}
PID=$(pgrep -f 'avail-node --dev' | head -1)
cd ~/avl03_work
echo "avail-node pid=$PID, window=${WIN}s"
RESDIR=~/avl03_results
# Start the tight loop in background, capture its JSON
node harness.mjs single $H 1 $WIN > $RESDIR/m1_loop.json 2>$RESDIR/m1_loop.err &
LOOP=$!
# perf stat attached to node for the same window
sudo perf stat -e task-clock,cycles,instructions -p $PID -- sleep $WIN 2> $RESDIR/m1_perf.txt
wait $LOOP
echo "=== loop result ==="
cat $RESDIR/m1_loop.json
echo "=== perf ==="
cat $RESDIR/m1_perf.txt
