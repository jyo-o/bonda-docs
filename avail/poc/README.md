# Avail PoC Scripts

Runnable reproduction code for the Avail runtime and RPC findings. Each script targets a **self-hosted Avail node**, never the public mainnet. Raw outputs and measured numbers are summarized in [Verification Evidence](../evidence.md).

## Mapping

| Finding | Script | What it does |
|---|---|---|
| **AVL-01** | `poc_multiaddr_index.js` | Submits `send_message` as `Address::Id` (baseline) then as byte-swapped `Address::Index(0)` (attack); checks `kate_queryDataProof` for each. |
| **AVL-02** | `run_poc.js` | Submits `submitData` directly (baseline) then wrapped in `Proxy::proxy` with `AppId=0` (attack); checks `kate_queryDataProof` for each. |
| **AVL-02 (scope)** | `poc_bridge1_proxy_sendmessage.js` | Shows the proxy path **rejects** wrapped `send_message` (`1010 custom error 141`), so only `submit_data` slips through. Negative result. |
| **AVL-03** | `avl03/` | Native x86 CPU measurement: fill a 4 MB block, then measure single-request core-seconds (`perf`), cost vs cell count, cache absence, cost vs block size, concurrency CPU saturation, and victim latency. |

## Environment

| Item | Value |
|---|---|
| Node | `availj/avail:v2.3.4.3` (avail-node 2.3.4, commit `510ee26`, specVersion 51) |
| Flags | dev chain with Kate RPC enabled (`--dev --enable-kate-rpc`) |
| Runtime | node.js v20+, deps in `package.json` (`avail-js-sdk`, `@polkadot/api`) |

```bash
cd avail/poc && npm install
```

## Run — AVL-01 / AVL-02 (functional, any Avail dev node)

```bash
# AVL-02: proxy-wrapped submitData DA bypass
node run_poc.js

# AVL-01: MultiAddress::Index bridge proof omission
node poc_multiaddr_index.js

# AVL-02 scope: proxy-wrapped send_message is rejected
node poc_bridge1_proxy_sendmessage.js
```

Each prints a BASELINE block (proof exists) and an ATTACK block (event fires, proof missing). The node may run under emulation for these functional checks; only correctness is asserted, not timing.

## Run — AVL-03 (CPU measurement, native x86)

Run on a native x86 host (the published numbers are from a GCP n2-standard-16, 16 vCPU, not emulated). Start the node as a host process so `perf` can attach:

```bash
avail-node --dev --rpc-port 9944 --rpc-methods unsafe --enable-kate-rpc --tmp &
sudo sysctl kernel.perf_event_paranoid=-1

cd avl03
node fill.mjs            # fill blocks (1 KB / 100 KB / 1 MB / 4 MB), prints block hashes
./dims.sh               # read actual grid dims from the header V3 commitment
./m1.sh                 # M1: perf core-seconds for a single 1-cell queryProof
bash m234.sh            # M2 cell-count, M3 cache, M4 block-size scaling
bash m5.sh              # M5 concurrency CPU saturation (pidstat/mpstat)
bash m6.sh              # M6 victim co-tenant latency during attack
```

`harness.mjs` is the load driver (`single` / `conc` / `latency` modes). The `m*.sh` scripts contain a block hash from the measurement run; replace it with a hash printed by `fill.mjs` on your own node.
