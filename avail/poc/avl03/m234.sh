#!/bin/bash
set -e
cd ~/avl03_work
R=~/avl03_results
H_4MB=0x433d1c5913a5bd694152194b4b0518fadb62bb77c4b3331b5cdbec870e194401
H_1KB=0xb9d8b9c5a2ea4bd3e567af03e84ae48b5cbaee19e09dd71b431f04d64e20e0e5
H_100KB=0x0933c3bf93ee6188e8b913f2c1484e8dccce7949c7d2bb9333c1da3fb5e37593
H_1MB=0xa2ec427b40d6078f06a2f881bffd6ead8ed5aa9165aca11a3f622f02caf5399c
PID=$(pgrep -f 'avail-node --dev' | head -1)

echo "===== M2: cost vs cell count on 4MB block ====="
: > $R/m2_cellcount.json
for nc in 1 8 32 64; do
  node harness.mjs single $H_4MB $nc 8 | tee -a $R/m2_cellcount.json
done

echo "===== M3: cache absence (repeat same vs different cells, 4MB) ====="
# harness already randomizes cells each iter (cold every time). Run twice to show stability.
: > $R/m3_cache.json
echo '{"note":"harness randomizes cell coords each iteration -> every request is a cold/distinct cell"}' >> $R/m3_cache.json
node harness.mjs single $H_4MB 1 8 | tee -a $R/m3_cache.json
node harness.mjs single $H_4MB 1 8 | tee -a $R/m3_cache.json

echo "===== M4: cost vs block size (wall + perf core-seconds each) ====="
: > $R/m4_sizescale.json
run_size () {
  local label=$1 hash=$2
  echo "--- $label ($hash) ---"
  node harness.mjs single $hash 1 12 > /tmp/m4_$label.json 2>/dev/null &
  LP=$!
  sudo perf stat -e task-clock,context-switches -p $PID -- sleep 12 2> /tmp/m4_${label}_perf.txt
  wait $LP
  local reqs=$(jq -r '.reqs' /tmp/m4_$label.json)
  local p50=$(jq -r '.latencyMs.p50' /tmp/m4_$label.json)
  local taskns=$(grep task-clock /tmp/m4_${label}_perf.txt | awk '{gsub(",","",$1); print $1}')
  local coresec=$(echo "scale=6; ($taskns/1000000000)/$reqs" | bc)
  echo "{\"label\":\"$label\",\"hash\":\"$hash\",\"reqs\":$reqs,\"p50WallMs\":$p50,\"taskClockNs\":$taskns,\"coreSecPerReq\":$coresec}" | tee -a $R/m4_sizescale.json
  cat /tmp/m4_${label}_perf.txt >> $R/m4_${label}_perf_raw.txt
  cp /tmp/m4_${label}_perf.txt $R/m4_${label}_perf.txt
}
run_size 1KB   $H_1KB
run_size 100KB $H_100KB
run_size 1MB   $H_1MB
run_size 4MB   $H_4MB
echo "===== DONE M2-M4 ====="
