#!/bin/bash
set -e
cd ~/avl03_work
R=~/avl03_results
H=0x433d1c5913a5bd694152194b4b0518fadb62bb77c4b3331b5cdbec870e194401

echo "===== M6 idle victim latency ====="
node harness.mjs latency system_health 6 | tee $R/m6_idle_system_health.json
node harness.mjs latency chain_getHeader 6 | tee $R/m6_idle_chain_getHeader.json

echo "===== M6 under N=50 attack ====="
node harness.mjs conc $H 1 50 30 > /tmp/m6_attack.json 2>/dev/null &
AP=$!
sleep 4
node harness.mjs latency system_health 8 | tee $R/m6_under_system_health.json
node harness.mjs latency chain_getHeader 8 | tee $R/m6_under_chain_getHeader.json
wait $AP
cp /tmp/m6_attack.json $R/m6_attack_load.json
echo "===== DONE M6 ====="
