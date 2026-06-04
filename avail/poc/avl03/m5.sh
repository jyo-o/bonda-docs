#!/bin/bash
set -e
cd ~/avl03_work
R=~/avl03_results
H=0x433d1c5913a5bd694152194b4b0518fadb62bb77c4b3331b5cdbec870e194401
PID=$(pgrep -f 'avail-node --dev' | head -1)
echo "pid=$PID"

echo "===== IDLE BASELINE ====="
pidstat -u -p $PID 1 3 > $R/m5_idle_pidstat.txt 2>&1
mpstat 1 3 > $R/m5_idle_mpstat.txt 2>&1
echo "idle pidstat:"; tail -4 $R/m5_idle_pidstat.txt
echo "idle mpstat:"; tail -4 $R/m5_idle_mpstat.txt

: > $R/m5_sweep.json
DUR=20
for N in 1 2 4 8 16 32 50; do
  echo "===== M5 N=$N for ${DUR}s ====="
  # start concurrent load
  node harness.mjs conc $H 1 $N $DUR > /tmp/m5_N$N.json 2>/dev/null &
  LP=$!
  sleep 2  # let it ramp
  # sample process CPU% for ~15 samples (1s each) during the burst
  pidstat -u -p $PID 1 15 > $R/m5_N${N}_pidstat.txt 2>&1
  mpstat 1 3 > $R/m5_N${N}_mpstat.txt 2>&1
  wait $LP
  # extract node CPU% avg + peak from pidstat (%CPU column, drop Average row)
  AVGCPU=$(grep -E "avail-node|[0-9]:[0-9]" $R/m5_N${N}_pidstat.txt | grep -v Average | awk '{print $(NF-1)}' | grep -E '^[0-9.]+$' | awk '{s+=$1;n++} END{if(n>0)printf "%.1f", s/n}')
  PEAKCPU=$(grep -E "avail-node|[0-9]:[0-9]" $R/m5_N${N}_pidstat.txt | grep -v Average | awk '{print $(NF-1)}' | grep -E '^[0-9.]+$' | sort -nr | head -1)
  RPS=$(jq -r '.rps' /tmp/m5_N$N.json)
  WALL=$(jq -r '.perReqAvgWallMs' /tmp/m5_N$N.json)
  CORES=$(echo "scale=2; $AVGCPU/100" | bc)
  echo "{\"N\":$N,\"perReqAvgWallMs\":$WALL,\"rps\":$RPS,\"nodeCpuAvgPct\":$AVGCPU,\"nodeCpuPeakPct\":$PEAKCPU,\"coresBusyAvg\":$CORES}" | tee -a $R/m5_sweep.json
  cp /tmp/m5_N$N.json $R/m5_N${N}_load.json
done
echo "===== DONE M5 ====="
