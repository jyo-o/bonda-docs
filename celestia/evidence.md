# Celestia Evidence Summary

This page summarizes the on-chain verification and parameter measurement evidence collected for Celestia threat findings. On-chain bridge results use `cast` (Foundry) against Ethereum mainnet. Chain-level parameters use Celestia's REST API. Every conclusion traces to a raw response or measured data point.

**Verification date**: 2026-05-20 to 2026-06-03
**Tools**: cast (Foundry), curl (Celestia REST API), Go load harness (BlobTx flood), pidstat / mpstat
**RPC endpoints**: `https://ethereum-rpc.publicnode.com` (Ethereum), `https://celestia-rest.publicnode.com` (Celestia)

---

## SP1Blobstream Bridge Verification (CEL-09)

The SP1Blobstream contract assigns all three access control roles to a single 4-of-6 Gnosis Safe, with no timelock on critical upgrade functions.

### On-Chain State

```bash
# Gnosis Safe: 0x8bF34D8df1eF0A8A7f27fC587202848E528018E6
# SP1Blobstream proxy: 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe

# Check DEFAULT_ADMIN_ROLE assignment
cast call 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe \
  "hasRole(bytes32,address)(bool)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 --rpc-url $ETH_RPC
# Result: true

# Check TIMELOCK_ROLE assignment
cast call 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe \
  "hasRole(bytes32,address)(bool)" \
  "<TIMELOCK_ROLE_HASH>" \
  0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 --rpc-url $ETH_RPC
# Result: true

# Check GUARDIAN_ROLE assignment
cast call 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe \
  "hasRole(bytes32,address)(bool)" \
  "<GUARDIAN_ROLE_HASH>" \
  0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 --rpc-url $ETH_RPC
# Result: true

# Gnosis Safe threshold and owners
cast call 0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 \
  "getThreshold()(uint256)" --rpc-url $ETH_RPC
# Result: 4

cast call 0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 \
  "getOwners()(address[])" --rpc-url $ETH_RPC
# Result: 6 addresses (all EOAs)
# 0x0449...56a9, 0x7939...E899, 0x1358...7caf,
# 0x4587...1b0, 0x4983...cE4d, 0x91D4...e15
```

### Role Grant History

All three `RoleGranted` events were emitted at block 20027685 with zero subsequent `RoleRevoked` events. The `initialize(_guardian, _guardian)` pattern in `SP1Blobstream.sol:89` is the root cause, assigning the same address for both `_timelock` and `_guardian` parameters.

### Bridge Usage

| Metric | Value |
|---|---|
| Total contract transactions | 12,109 |
| Transaction type | 100% `commitHeaderRange` (relayer calls) |
| Internal transactions | 0 |
| `verifyAttestation` calls | 0 |
| Active users | None observed |

Etherscan proxy at `0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe` shows zero user-facing calls. Molten Network and Rari Chain `SequencerInbox` contracts point to `0xa8973B...` for their `BLOBSTREAM` getter, which returns bytecode `0x` (dead pointer).

---

## Validator Set and Slashing Parameters (CEL-08, CEL-10)

### Slashing Parameters

Queried via `celestia-rest.publicnode.com/cosmos/slashing/v1beta1/params`:

```json
{
  "slash_fraction_double_sign": "0.020000000000000000",
  "slash_fraction_downtime": "0.000000000000000000",
  "min_signed_per_window": "0.001000000000000000",
  "signed_blocks_window": "10000",
  "downtime_jail_duration": "60s"
}
```

Key findings:
- `slash_fraction_downtime=0`: validators face zero penalty for missed blocks
- `min_signed_per_window=0.001`: validators must sign only 10 of 10,000 blocks (0.1%) to avoid jail
- `downtime_jail_duration=60s`: jail lasts only 60 seconds

These parameters were updated in PR `celestia-app#7090` (merged 2026-04-17) with the description "to match mainnet governance."

### Documentation Discrepancy (CEL-10)

The public documentation at `docs.celestia.org/operate/consensus-validators/slashing` states "25% of 5,000 blocks" while mainnet shows 0.1% of 10,000 blocks. This is a 250x discrepancy in the documented liveness threshold.

### Validator Set Composition (CEL-08)

Mainnet staking data as of 2026-05-24:

| Metric | Value |
|---|---|
| Total registered validators | 301 |
| Bonded validators | 94 |
| Unbonding validators | 192 |
| `max_validators` | 100 |
| Top 8 voting power | 35.77% (>1/3 threshold) |
| Top 28 voting power | 67.02% (>2/3 threshold) |
| Largest validator | Anchorage Digital (11.08%) |
| KYC entities in top 8 | 6 of 8 |

Data cross-verified across three independent endpoints: publicnode, polkachu, pops.one.

---

## Gas and Blockspace Parameters (CEL-05, CEL-04)

```bash
# Minimum gas price
# celestia-rest.publicnode.com/cosmos/base/node/v1beta1/config
# minimum_gas_price: "0.002000000000000000utia"
```

### Blockspace Cost Calculation

| Parameter | Value | Source |
|---|---|---|
| `BlockMaxBytes` | 32 MiB | `celestia-app/pkg/appconsts/app_consts.go` |
| `MaxTxSize` | 8 MiB | `celestia-app/pkg/appconsts/app_consts.go` |
| `GasPerBlobByte` | 8 | `celestia-app/pkg/appconsts/app_consts.go` |
| `minimum_gas_price` | 0.002 utia/gas | Celestia REST API |

At mainnet prices as of 2026-05-26:
- Single 8 MiB PFB cost: approximately 0.134 TIA (~$0.063)
- Full block fill (4 max-size PFBs): approximately $0.25
- One hour sustained attack (600 blocks): approximately $151 before fee market response

---

## PoC Test Results

### CEL-01: TxCache Key Mismatch (poc_verified)

| Test | Result |
|---|---|
| **TestTxCacheLeakProductionPath** | `CheckTx` followed by `FinalizeBlock(wrappedTx)` confirmed `fromCache` still returns `true` — cache entry not deleted |
| **Rejected tx persistence** | Future sequence blob tx (checktx_code=32) and zero-fee blob tx (checktx_code=11) both leave permanent cache entries |
| **Per-entry memory** | Approximately 204 bytes |
| **Projected leak rate** | ~1 GB per 160 seconds at 100 Mbps rejected tx rate |
| **Existing test gap** | Production tests pass `blobTx.Tx` directly to `FinalizeBlock` instead of wrapped `BlobTx`, masking the key mismatch |

### CEL-03: blacklistedHashes Growth (poc_verified)

Local unit PoC confirmed: N unique fake hashes injected via shrexsub, after `cleanUp` the `blacklistedHashes` map length increases by N while pools are correctly deleted. The cleanup function is the only write path that sets `blacklistedHashes[h]=true`, and no deletion path exists anywhere in the codebase.

### CEL-04: BlobTx Pre-Ante CPU Exhaustion (poc_verified)

A live single-attacker reproduction confirmed that an unauthenticated, zero-fee BlobTx packed with many 1-byte blobs forces full NMT commitment computation under the global `CheckTx` lock, head-of-line-blocking all other CheckTx processing. The attacker needs no valid account, funds, or signature.

#### Test Setup

| Item | Value |
|---|---|
| Victim | GCP c2-standard-8 (8 vCPU, 32 GB, 80 GB SSD), Debian 12 |
| Attacker | GCP e2-standard-8 (8 vCPU, 32 GB, 40 GB SSD), Debian 12 |
| celestia-app | commit `cfb01626` |
| go-square | v4.0.0-rc4 |
| celestia-core | v0.40.2 |
| Probe | normal 1-blob PFB every 300 ms, measuring legitimate CheckTx latency |

#### Single Run (raw)

```text
# invalid commitment, no key, 3000 blobs/tx, 1 worker, 3 s
$ ./poca -node http://<victim>:26657 -blobs 3000 -workers 1 -dur 3s
duration_s=3.0 sent=91 rejected=0 rps=30.3 blobs_per_tx=3000 wire_bytes=306129
  [90x] RPC error -32603 - Internal error: invalid commitment for share
```

The node runs `CreateParallelCommitments` for all 3,000 blobs before the ante chain rejects the invalid commitment, so the CPU cost is already paid at rejection time.

#### Load Results (8 vCPU victim, 1-byte blobs x 5,000, 8 workers, 60 s)

| Scenario | tx rps | proc CPU avg | probe p50 | probe p90 / max |
|---|---|---|---|---|
| baseline (probe only) | ~3 | ~5% | 1.15 ms | 1.39 / 5.1 ms |
| Case #1 attack | 39.9 | 534% (5.34 cores) | 146 ms (127x) | 291 / 387 ms |

A free, keyless flood raised legitimate CheckTx latency 127x (1.15 ms to 146 ms) and node CPU from ~2% to 534%, at zero attacker cost. Per rejected tx: ~0.125 CPU-seconds (~3.9x10^8 cycles); per 1-byte blob commitment: ~2.5x10^4 cycles.

#### Core Scaling (the serialized lock, not raw CPU, is the bottleneck)

| Metric | 8 cores (ceiling 800%) | 16 cores, same attack (1600%) | 16 cores, scaled attack |
|---|---|---|---|
| Attack params | 8w x 5,000 | 8w x 5,000 | 16w x 10,000 |
| proc CPU avg | 534% | 699% | 703% |
| probe p50 during attack | 146 ms (127x) | 82 ms (71x) | 390 ms (340x) |

`CheckTx` processes one tx's commitment at a time under a single global mutex, so parallel efficiency caps near ~700% (7 cores). Adding cores does not relieve the serialized lock, and legitimate latency stays degraded (340x at 16 cores under a scaled attack). The defect is the serial lock delay, not CPU exhaustion alone.
