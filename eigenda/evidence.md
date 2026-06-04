# EigenDA Evidence Summary

This page summarizes the on-chain verification and data analysis evidence collected for EigenDA threat findings. All on-chain results are from Ethereum mainnet using `cast` (Foundry). Every conclusion traces to a raw on-chain response or data source.

**Verification date**: 2026-05-15 to 2026-05-24
**Tools**: cast (Foundry), grpcurl, Python scripts, ipinfo.io
**RPC endpoint**: `https://ethereum-rpc.publicnode.com`
**Reference block**: 25101686

---

## Ejector Role Parameters (EDA-08)

The `EjectionManager` contract delegates ejection authority to EOA addresses with rate-limited parameters.

### On-Chain State

```bash
# EjectionManager owner
cast call 0x130d8EA0052B45554e4C99079B84df292149Bd5E \
  "owner()(address)" --rpc-url $RPC
# Result: 0x002721B4790d97dC140a049936aA710152Ba92D5

# RegistryCoordinator ejector slot
cast call 0x0BAAc79acD45A023E19345c352d8a7a83C4e5656 \
  "ejector()(address)" --rpc-url $RPC
# Result: 0x130d8EA0052B45554e4C99079B84df292149Bd5E

# Rate limit parameters (Quorum 0)
cast call 0x130d8EA0052B45554e4C99079B84df292149Bd5E \
  "quorumEjectionParams(uint8)(uint32,uint16)" 0 --rpc-url $RPC
# Result: rateLimitWindow = 259200 (3 days), ejectableStakePercent = 3333 (33.33%)

# Ejection cooldown per operator
cast call 0x0BAAc79acD45A023E19345c352d8a7a83C4e5656 \
  "ejectionCooldown()(uint256)" --rpc-url $RPC
# Result: 259200 (3 days)

# Active ejector status
cast call 0x130d8EA0052B45554e4C99079B84df292149Bd5E \
  "isEjector(address)(bool)" 0xd2ee81cf07b12140c793fce5b26313cdd9d78ea8 --rpc-url $RPC
# Result: true (EOA)

cast call 0x130d8EA0052B45554e4C99079B84df292149Bd5E \
  "isEjector(address)(bool)" 0x8642473a123fe33b0aae90bd8604ea1029417236 --rpc-url $RPC
# Result: true (EOA)

cast call 0x130d8EA0052B45554e4C99079B84df292149Bd5E \
  "isEjector(address)(bool)" 0x338477ffaf63c04ac06048787f910671ec914b34 --rpc-url $RPC
# Result: true (SafeProxy — registered but never called ejectOperators)
```

### Ejection Activity

| Metric | Value |
|---|---|
| Total `ejectOperators` calls | 150 |
| Caller `0xD2Ee...eA8` (EOA) | 89 calls |
| Caller `0x8642...236` (EOA) | 61 calls |
| Observation period | 2025-01 to 2026-03 (~16 months) |
| Call cadence | ~1-14 day intervals, 9-day periodic pattern |

Source: Blockscout transaction history for EjectionManager (`0x130d8E...`).

---

## Governance Multisig Configuration (EDA-07)

A single Gnosis Safe controls eight core EigenDA contracts with no timelock.

### On-Chain State

```bash
# Multisig threshold
cast call 0x002721B4790d97dC140a049936aA710152Ba92D5 \
  "getThreshold()(uint256)" --rpc-url $RPC
# Result: 3

# Multisig owners
cast call 0x002721B4790d97dC140a049936aA710152Ba92D5 \
  "getOwners()(address[])" --rpc-url $RPC
# Result: [0xA3e302..., 0x1b6cC4..., 0x403F4d..., 0x891bbC...]

# Safe version
cast call 0x002721B4790d97dC140a049936aA710152Ba92D5 \
  "VERSION()(string)" --rpc-url $RPC
# Result: "1.4.1"

# Verify all 4 owners are EOAs (no contract code)
cast code 0xA3e302a6Ea0cf79B8580d94e92Eb5514292daacE --rpc-url $RPC
# Result: 0x (EOA)
# ... same for all 4 owners
```

### Contract Ownership Verification

All eight core contracts return the same owner:

```bash
# ServiceManager
cast call 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  "owner()(address)" --rpc-url $RPC
# Result: 0x002721B4790d97dC140a049936aA710152Ba92D5

# RegistryCoordinator
cast call 0x0BAAc79acD45A023E19345c352d8a7a83C4e5656 \
  "owner()(address)" --rpc-url $RPC
# Result: 0x002721B4790d97dC140a049936aA710152Ba92D5

# EjectionManager, ThresholdRegistry, RelayRegistry,
# DisperserRegistry, PaymentVault, CertVerifierRouter
# — all return 0x002721B4790d97dC140a049936aA710152Ba92D5
```

The CertVerifier at `0x61692e...` is an exception: `owner()` reverts, confirming it is an immutable contract. Certificate verification logic changes must go through the CertVerifierRouter, which is owned by the multisig.

---

## Operator Stake Distribution (EDA-09)

Stake distribution was queried at block 25101686 to measure concentration against safety and liveness thresholds.

### On-Chain Thresholds

```bash
# Adversary (safety) threshold per quorum
cast call 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  "quorumAdversaryThresholdPercentages()(bytes)" --rpc-url $RPC
# Result: 0x212121 → [33, 33, 33] (Q0, Q1, Q2)

# Confirmation (liveness) threshold per quorum
cast call 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  "quorumConfirmationThresholdPercentages()(bytes)" --rpc-url $RPC
# Result: 0x373737 → [55, 55, 55] (Q0, Q1, Q2)

# Active quorum count
cast call 0x0BAAc79acD45A023E19345c352d8a7a83C4e5656 \
  "quorumCount()(uint8)" --rpc-url $RPC
# Result: 3
```

### Stake Distribution Analysis

Data source: EigenDA DataAPI `signing-info` endpoint (120 operator-quorum pairs, 84 unique operators).

**Quorum 0 (ETH)** — 58 operators, total stake `2.368 × 10²⁴` (≈ 2.37 million units at 18-decimal stake weight):

| Rank | Top-k Cumulative | Threshold |
|------|------------------|-----------|
| Top 3 | 39.80% | > 33% safety |
| Top 4 | 48.16% | > 45% liveness |
| Top 5 | 55.25% | > 55% confirmation |

**Quorum 1 (EIGEN)** — 62 operators, total stake `2.727 × 10²⁶` (≈ 272.7 million units at 18-decimal stake weight):

| Rank | Top-k Cumulative | Threshold |
|------|------------------|-----------|
| Top 3 | 35.65% | > 33% safety |
| Top 5 | 51.68% | > 45% liveness |
| Top 6 | 58.68% | > 55% confirmation |

### Concentration Metrics

| Metric | Q0 | Q1 |
|---|---|---|
| Nakamoto coefficient (33%) | 3 | 3 |
| HHI | 883 | 876 |
| Gini coefficient | 0.79 | 0.82 |

---

## Slashing Absence Verification (EDA-11)

A comprehensive audit confirmed that EigenDA has no active slashing mechanism.

### On-Chain State

```bash
# ServiceManager does not expose slasher interface
cast call 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  "slasher()(address)" --rpc-url $RPC
# Result: execution reverted (0x)

# ServiceManager does not expose AllocationManager handle
cast call 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  "allocationManager()(address)" --rpc-url $RPC
# Result: execution reverted (0x)

# EigenLayer AllocationManager — operatorSet count for EigenDA AVS
cast call 0x948a420b8CC1d6BFd0B6087C2E7c344a2CD0bc39 \
  "getOperatorSetCount(address)(uint32)" \
  0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 --rpc-url $RPC
# Result: 0 (no operator sets registered = slashing inactive)

# Rewards are wired (asymmetry)
cast call 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  "rewardsInitiator()(address)" --rpc-url $RPC
# Result: 0x178eeeA9E0928dA2153A1d7951FBe30CF8371b8A
```

### Event Scan

A scan of 500,000 blocks (~70 days) on the ServiceManager found zero slashing-related events:

| Event Signature | Topic0 | Hits |
|---|---|---|
| `OperatorSlashed(address,bytes32)` | `0x6886bb...` | 0 |
| `OperatorFrozen(address)` | `0x4991f3...` | 0 |
| `Slashed(address,uint256)` | `0x4ed05e...` | 0 |
| `Freeze(address)` | `0xaf85b6...` | 0 |

### Code-Level Verification

A `grep` across all EigenDA core Solidity contracts (`contracts/src/core/`) found zero `slash()` or `freeze()` function definitions. The only match was a NatSpec comment on line 26 of `EigenDAServiceManager.sol` describing intended future functionality.

---

## Relay Registry Single Point of Failure (EDA-04)

The RelayRegistry confirms only one relay is registered on mainnet.

### On-Chain State

```bash
# Next relay key (number of registered relays)
cast call 0xD160e6C1543f562fc2B0A5bf090aED32640Ec55B \
  "nextRelayKey()(uint32)" --rpc-url $RPC
# Result: 1

# Relay key 0 (the only registered relay)
cast call 0xD160e6C1543f562fc2B0A5bf090aED32640Ec55B \
  "relayKeyToAddress(uint32)(address)" 0 --rpc-url $RPC
# Result: 0xe8437B66E834B7CdC90cC5D98B8DD6e636b37D7a

# Keys 1-5 all unregistered
cast call 0xD160e6C1543f562fc2B0A5bf090aED32640Ec55B \
  "relayKeyToAddress(uint32)(address)" 1 --rpc-url $RPC
# Result: 0x0000000000000000000000000000000000000000
# (same for keys 2, 3, 4, 5)

# Registry owner
cast call 0xD160e6C1543f562fc2B0A5bf090aED32640Ec55B \
  "owner()(address)" --rpc-url $RPC
# Result: 0x002721B4790d97dC140a049936aA710152Ba92D5
```

The registered relay URL is `relay-0-mainnet-ethereum.eigenda.xyz`. DNS resolves to Cloudflare IPs (`104.18.0.169`, `104.18.1.169`).

---

## Infrastructure Concentration Analysis (EDA-14)

ASN aggregation analysis of 78 operator host classes reveals systemic provider concentration.

### Methodology

1. Extracted 78 operator socket addresses from `SocketRegistry` via `getOperatorSocket()`.
2. Resolved 72 raw IPs from socket hostnames (6 operators had no socket registered).
3. Performed ASN lookup via `ipinfo.io` for each IP.
4. Correlated ASN providers with stake weight from `signing-info` data.

### Quorum 0 (ETH) — Provider Stake Distribution

| Provider | Operators | Stake % |
|---|---|---|
| Amazon AWS | 10 | 21.78% |
| P2P.org | 5 | 20.43% |
| OVH SAS | 11 | 15.67% |
| DigitalOcean | 3 | 13.67% |
| No socket | 6 | 11.18% |
| Google Cloud | 6 | 8.46% |
| **Top 5 cumulative** | — | **82.7%** |

### Quorum 1 (EIGEN) — Provider Stake Distribution

| Provider | Operators | Stake % |
|---|---|---|
| Herd SaaS | 6 | 41.87% |
| No socket | 6 | 22.11% |
| P2P.org | 5 | 13.71% |
| Cherry Servers | 2 | 8.49% |
| Google Cloud | 6 | 5.55% |

### Impact Scenarios

| Scenario | Q0 Loss | Q1 Loss | Threshold Status |
|---|---|---|---|
| AWS region outage | 21.78% | 0.68% | Q0 confirmation 55% passes |
| Herd SaaS outage | 0.16% | 41.87% | Q1 confirmation 55% margin: 3.1pp |
| AWS + OVH combined | 37.45% | 1.23% | Q0 confirmation passes; margin thin |

---

## Dead Operator Measurement (EDA-06)

A 24-hour prober measurement of 79 EigenDA operators identified chronic non-serving behavior.

### Data Sources

- **Prober DB** (`operator_probes` table): Direct `GetChunks` calls to each operator, measuring chunk-serving success rate.
- **DataAPI** (`signing-info`, `interval=86400`): BLS signing percentage from the EigenDA DataAPI.

### Results

| Window | Source | Dead (0%) | Degraded | Healthy |
|---|---|---|---|---|
| 24h | Prober (chunk serving) | 11 | 2 | 66 |
| 24h | DataAPI (BLS signing) | 3 | 1 | 80 |
| **Gap** | — | **8** | — | — |

The 8-operator gap between prober and signing-info indicates operators that sign BLS attestations but do not serve data chunks, consistent with free-riding behavior.

### Chronic Dead Operators (Signing-Info)

Three operators showed 0% signing rate across both 1h and 24h windows (47,502 batches with zero signatures):

| Address | Q0 Signing | Q1 Signing | Max Stake % |
|---|---|---|---|
| `0x3F98...5272` | 0.0% | 0.0% | 0.725% |
| `0x46b3...AB82` | 0.0% | 0.0% | 0.668% |
| `0x0141...31c7` | N/A | 0.0% | 0.003% |

### Measurement Window

BLS signing data is reliable only over 24-hour windows; longer intervals are not available, so real-time monitoring relies on 24-hour snapshots and external probers for longer-term observation.

---

## Proxy Admin and Upgrade Authority (EDA-07 supplementary)

All 12 upgradeable proxy contracts share a single ProxyAdmin, which is owned by the same DA Ops Multisig.

### On-Chain State

```bash
# EIP-1967 admin slot for ServiceManager
cast storage 0x870679E138bCdf293b7Ff14dD44b70FC97e12fc0 \
  0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 \
  --rpc-url $RPC
# Result: 0x0000000000000000000000008247ef5705d3345516286b72bfe6d690197c2e99

# ProxyAdmin owner
cast call 0x8247ef5705d3345516286b72bfe6d690197c2e99 \
  "owner()(address)" --rpc-url $RPC
# Result: 0x002721B4790d97dC140a049936aA710152Ba92D5 (DA Ops Multisig)
```

### Proxy Classification

| Contract | Proxy? | Admin |
|---|---|---|
| SERVICE_MANAGER | Yes | 0x8247...2e99 |
| REGISTRY_COORDINATOR | Yes | 0x8247...2e99 |
| EJECTION_MANAGER | Yes | 0x8247...2e99 |
| RELAY_REGISTRY | Yes | 0x8247...2e99 |
| DISPERSER_REGISTRY | Yes | 0x8247...2e99 |
| THRESHOLD_REGISTRY | Yes | 0x8247...2e99 |
| PAYMENT_VAULT | Yes | 0x8247...2e99 |
| CERT_VERIFIER_ROUTER | Yes | 0x8247...2e99 |
| BLS_APK_REGISTRY | Yes | 0x8247...2e99 |
| INDEX_REGISTRY | Yes | 0x8247...2e99 |
| STAKE_REGISTRY | Yes | 0x8247...2e99 |
| SOCKET_REGISTRY | Yes | 0x8247...2e99 |
| **PAUSER_REGISTRY** | **No** | N/A (immutable) |
| **CERT_VERIFIER** | **No** | N/A (immutable) |
| **ACCESS_CONTROL** | **No** | N/A (immutable) |

All 12 proxies share a single ProxyAdmin (`0x8247ef...2e99`), owned by the DA Ops Multisig. The 3-of-4 multisig can upgrade any proxy implementation in a single `execTransaction` call with no timelock delay.

---

## Unpauser and Pauser Structure (EDA-07 supplementary)

The pause/unpause authority is separated from the DA Ops Multisig via a dedicated PauserRegistry.

### On-Chain State

```bash
# PauserRegistry unpauser
cast call 0x0c431C66F4dE941d089625E5B423D00707977060 \
  "unpauser()(address)" --rpc-url $RPC
# Result: 0x369e6F597e22EaB55fFb173C6d9cD234BD699111

# Unpauser Safe threshold and owners
cast call 0x369e6F597e22EaB55fFb173C6d9cD234BD699111 \
  "getThreshold()(uint256)" --rpc-url $RPC
# Result: 1

cast call 0x369e6F597e22EaB55fFb173C6d9cD234BD699111 \
  "getOwners()(address[])" --rpc-url $RPC
# Result: [0xC06Fd4F821eaC1fF1ae8067b36342899b57BAa2d,
#          0xFEA47018D632A77bA579846c840d5706705Dc598]

# Owner A: TimelockController (10-day delay)
cast call 0xC06Fd4F821eaC1fF1ae8067b36342899b57BAa2d \
  "getMinDelay()(uint256)" --rpc-url $RPC
# Result: 864000 (10 days)

# Owner B: 9-of-13 Gnosis Safe
cast call 0xFEA47018D632A77bA579846c840d5706705Dc598 \
  "getThreshold()(uint256)" --rpc-url $RPC
# Result: 9

cast call 0xFEA47018D632A77bA579846c840d5706705Dc598 \
  "getOwners()(address[])" --rpc-url $RPC
# Result: [13 addresses]

# Active pausers (3 SafeProxy addresses)
cast call 0x0c431C66F4dE941d089625E5B423D00707977060 \
  "isPauser(address)(bool)" 0x369e6F597e22EaB55fFb173C6d9cD234BD699111 --rpc-url $RPC
# Result: true

cast call 0x0c431C66F4dE941d089625E5B423D00707977060 \
  "isPauser(address)(bool)" 0xbe1685c81aA44FF9FB319dD389addd9374383e90 --rpc-url $RPC
# Result: true

cast call 0x0c431C66F4dE941d089625E5B423D00707977060 \
  "isPauser(address)(bool)" 0x5050389572f2d220ad927ccbea0d406831012390 --rpc-url $RPC
# Result: true

# DA Ops Multisig is NOT a pauser (separation confirmed)
cast call 0x0c431C66F4dE941d089625E5B423D00707977060 \
  "isPauser(address)(bool)" 0x002721B4790d97dC140a049936aA710152Ba92D5 --rpc-url $RPC
# Result: false

# Current pause bitmap (all functions active)
cast call 0x0BAAc79acD45A023E19345c352d8a7a83C4e5656 \
  "paused()(uint256)" --rpc-url $RPC
# Result: 0 (all unpaused)
```

### Governance Separation Summary

| Role | Entity | Scheme |
|---|---|---|
| Contract owner | DA Ops Multisig | 3-of-4 EOA |
| ProxyAdmin owner | DA Ops Multisig | 3-of-4 EOA |
| Pauser | 3 SafeProxy contracts | Any one can pause |
| Unpauser | Unpauser Safe | 1-of-2: TimelockController (10d) OR 9-of-13 Safe |

The Unpauser Safe has never executed an `execTransaction` (nonce = 30 from setup, 0 actual user transactions), confirming its emergency-only design.

---

## Dispersal Client Centralization (EDA-04 supplementary)

Analysis of 3,695 blobs from the DataAPI `blobs/feed` endpoint reveals extreme dispersal concentration.

### Distribution

```bash
# Query DataAPI feed
curl -s "https://dataapi.eigenda.xyz/api/v2/blobs/feed?limit=1000" > feed.json
# Paginate via cursor until exhaustion
```

| Metric | Value |
|---|---|
| Unique dispersing accounts | 10 |
| Top 1 account share | 98.65% |
| Top 1 address | `0x41fa832fad553c3b92976344d44b3548517679ac` |
| HHI (Herfindahl-Hirschman) | 9,731 (monopoly territory) |
| Effective number of dispersers | 1.03 |
| Sample window | ~1 hour (3,695 blobs) |

All 10 accounts are anonymous EOAs with no Blockscout public tags, ENS names, or other identifiers.

### PaymentVault Reservation

```bash
# Dominant account reservation
cast call 0xb2e7ef419a2A399472ae22ef5cFcCb8bE97A4B05 \
  "getReservations(address[])((uint64,uint64,uint64,bytes,bytes)[])" \
  "[0x41fa832fad553c3b92976344d44b3548517679ac]" --rpc-url $RPC
# Result: symbolsPerSecond=163840, start=2025-06-25, end=2027-02-08, quorums=[0,1]
```

The reservation was set by the DA Ops Multisig via `setReservation()` on PaymentVault. The DA Ops Safe can revoke this reservation at any time (no timelock), which would instantly halt 98.65% of EigenDA mainnet traffic.

---

## Relay Bandwidth Starvation Test (EDA-05)

A controlled bandwidth-starvation test was run against the Relay `GetBlob` path at commit `61019b4e9f91cbbb3dc05ed758674e4bdfeee20e` to confirm that the global-only rate limiter lets one client starve another.

### Test Setup

The Relay charges the global bandwidth bucket before the cache lookup, so an attacker repeatedly requesting an already-cached blob consumes the shared budget at near-zero backend cost.

```go
// relay/server.go:245-250
// @audit bandwidth charged before the cache lookup — cached reads still drain the global bucket
err = s.blobRateLimiter.RequestGetBlobBandwidth(uint32(len(data)))
if err != nil {
    return nil, err
}
data, err = s.blobProvider.GetBlob(ctx, blobKey)
// https://github.com/Layr-Labs/eigenda/blob/61019b4e9f91cbbb3dc05ed758674e4bdfeee20e/relay/server.go#L245-L250
```

### Results

`TestPoCVariantABandwidthStarvation`: one attacker at 6 requests/second and one legitimate victim at 1 request/second, both requesting a cached blob, sharing one global bucket.

| Client | Rate | Requests | Rejected | Rejection Rate |
|---|---|---|---|---|
| Victim | 1 RPS | 11 | 6 | 55% |
| Attacker | 6 RPS | 84 | 30 | 36% |

The bucket was scaled down 20x for the test (1 MiB/s versus the 20 MiB/s production default). The same starvation holds at production scale, requiring proportionally more attacker throughput. The victim losing more than half of its requests confirms that legitimate clients have no priority over anonymous traffic under the global-only scheme.

---

## GetChunks Cold-Miss CPU Exhaustion (EDA-01)

A load test was run against the operator Retrieval `GetChunks` path on an `inabox` local deployment to confirm that unauthenticated random-key requests drive a cold-miss lookup on every call and saturate operator CPU.

### Test Setup

The operator ran on a GCP host matching the Large operator class in the published system requirements. The deployment was the EigenDA `inabox` harness with four validators, one disperser, one encoder, one controller, one relay, one churner, and one proxy, all built from the EigenDA master branch at commit `61019b4`.

| Component | Value |
|---|---|
| Instance | GCP `n2-standard-16` (16 vCPU / 64 GB) |
| Boot disk | pd-ssd 200 GB |
| OS | Ubuntu 24.04 LTS |
| Runtime | Docker 29.1.3, docker-compose v2.40 |
| Go | 1.24.13 |
| forge | 1.4.4 |
| grpcurl | 1.9.3 |
| EigenDA | master branch, commit `61019b4` |

The interceptor passes every method except `StoreChunks`, so Retrieval calls reach the handler without authentication or rate limiting, and a cold-miss lookup returns before any rate-limit token is debited.

```go
// node/validator_store.go:262-274
// @audit a random blob key yields exists=false and returns with no token debit, so cold reads are never throttled
coldReadsExhausted := s.coldReadRateLimiter.Tokens() <= 0
bundle, exists, hot, err := s.chunkTable.CacheAwareGet(bundleKey, coldReadsExhausted)
if !exists {
    return nil, false, nil // returns before reserving any token
}
// https://github.com/Layr-Labs/eigenda/blob/61019b4/node/validator_store.go
```

A single request with a random 32-byte blob key reaches the cold-miss path and returns the `not found` error mapped through `validator_store.go` → `server_v2.go` → `api/errors.go` to a gRPC `Internal` code:

```bash
# Single GetChunks call with a random 32-byte blob key
grpcurl -plaintext -max-time 5 \
  -d "{\"blob_key\":\"$B64KEY\",\"quorum_id\":0}" \
  $TARGET validator.Retrieval/GetChunks
# Result:
#   Code: Internal
#   Message: failed to get chunks: failed to get chunks: not found
```

### Results

Scenarios were run sequentially against operator `opr0` with a 30-second gap between each:

| ID | Load | Duration | Purpose |
|---|---|---|---|
| BL-idle | none | 60 s | baseline |
| BL-1 | 100 sequential RPCs (1 conn, 1 worker) | ~30 ms | single-request RTT |
| S1 | 100 req/s rate cap | 60 s | normal-user level |
| S2 | 1,000 req/s rate cap | 60 s | first saturation check |
| S3 | client max (200 inflight) | 60 s | saturation point |
| S4 | client max | 10 min | sustained load |

CPU was exhausted while disk I/O showed little change:

| Scenario | RPS | Process CPU avg (max) % | Δ GetChunks (Prometheus) |
|---|---|---|---|
| BL-idle | 0 | 2.7 (4.0) | 0 |
| BL-1 | 100 sequential | — | 0 |
| S1 (100 rps) | 102 | 5.0 (7.0) | 6,094 |
| S2 (1k rps) | 1,017 | 21.1 (23.0) | 60,953 |
| S3 (max, 60 s) | 82,029 | 447.97 (463) | 4,850,103 |
| S4 (max, 10 min) | 83,490 | 458.35 (469) | 50,023,312 |

| Resource | S3 measured | BL-idle |
|---|---|---|
| Disk read | 0 kB/s | 0 kB/s |
| Disk write | 662 kB/s | 25 kB/s |
| Disk IOPS | 3.4 | 0.6 |

A single attacker drove the EigenDA process to an average of 447.97 percent CPU and a peak of 469 percent, roughly 4.5 cores, while client-side resource use converged toward zero. A 4 vCPU operator with a 400 percent ceiling is fully saturated by one attacker; a 16 vCPU operator absorbs about 28 percent from one attacker and reaches saturation under parallel attackers.

---

## GetBlobCommitment Unauthenticated Compute (EDA-02)

Two layers of verification confirm that the Disperser V2 `GetBlobCommitment` endpoint performs unauthenticated KZG (MSM) work: an in-process measurement of the KZG cost an attacker can trigger, and a live-endpoint check across operational environments.

### Test Setup

The compute cost was measured in-process by directly invoking `committer.GetCommitmentsForPaddedLength`, the same function the handler at `server_v2.go:309` calls, with the mainnet SRS configuration of `SRSNumberToLoad = 524288` (2^19).

| Item | Value |
|---|---|
| OS / Arch | darwin / arm64 |
| CPU | Apple M5, 10 cores (GOMAXPROCS=10) |
| Go | 1.26.1 |
| EigenDA source | commit `61019b4e9f91cbbb3dc05ed758674e4bdfeee20e` |
| KZG library | gnark-crypto (BN254 curve) |
| SRS files | `g1.point` (16 MiB), `g2.point` (32 MiB), `g2.trailing.point` (32 MiB) |
| `SRSNumberToLoad` | 524,288 (2^19, mainnet limit) |
| SRS load time | 13.5 s (one-time at startup) |

`GetCommitments` runs G1 MSM x1 + G2 MSM x2 sequentially, and each MSM alone saturates all cores:

```go
// encoding/v2/kzg/committer/committer.go:159-176
// @audit G1 + 2xG2 MSM computed sequentially — each saturates all cores
commit, err := c.computeCommitmentV2(inputFr)
lengthCommitment, err := c.computeLengthCommitmentV2(inputFr)
lenProof, err := c.computeLengthProofV2(inputFr)
// https://github.com/Layr-Labs/eigenda/blob/61019b4e9f91cbbb3dc05ed758674e4bdfeee20e/encoding/v2/kzg/committer/committer.go#L123-L177
```

### Results

Single-request KZG cost scales nearly linearly with the symbol count, reaching about 14 core-seconds at the 16 MiB mainnet limit:

| Blob | N (symbols) | run1 | run2 | run3 | avg wall | core-seconds (x10 cores) |
|---|---|---|---|---|---|---|
| 2 MiB | 65,536 (2^16) | 214 ms | 219 ms | 216 ms | 216 ms | 2.16 |
| 8 MiB | 262,144 (2^18) | 737 ms | 753 ms | 745 ms | 745 ms | 7.45 |
| 16 MiB | 524,288 (2^19) | 1.393 s | 1.418 s | 1.407 s | 1.406 s | 14.06 |

Concurrent 16 MiB requests scale almost linearly in per-request wall time, confirming that requests serialize because one MSM occupies every core:

| Concurrency | per-request avg wall | max wall | vs concurrency 1 |
|---|---|---|---|
| 1 | 1.431 s | 1.431 s | 1.0x (baseline) |
| 2 | 2.675 s | 2.76 s | 1.87x |
| 4 | 5.556 s | 5.611 s | 3.88x |

A live-endpoint check confirmed the endpoint is active and anonymously callable. The probe sends a 32-byte payload only to check liveness; a real attack would send a 16 MiB blob:

```bash
# Liveness probe (32-byte payload, no credentials)
B64=$(head -c 32 /dev/zero | base64)
grpcurl -max-time 15 -d "{\"blob\":\"$B64\"}" <endpoint>:443 \
    disperser.v2.Disperser/GetBlobCommitment
# Result: blobCommitment returned (commitment, lengthCommitment, lengthProof, length=1)
```

| Environment | Endpoint | Status |
|---|---|---|
| Mainnet | `disperser.eigenda.xyz:443` | active |
| Testnet (Sepolia) | `disperser-testnet-sepolia.eigenda.xyz:443` | active |
| Testnet (Hoodi) | `disperser-hoodi.eigenda.xyz:443` | active |
| Preprod (Hoodi v2) | `disperser-v2-preprod-hoodi.eigenda.xyz:443` | active |

A disabled endpoint would instead return `Unimplemented: GetBlobCommitment is deprecated and has been disabled`, confirming the `DISABLE_GET_BLOB_COMMITMENT` flag is inactive in all four environments. All four endpoints resolve to Cloudflare IPs (`104.18.0.169`, `104.18.1.169`), but Cloudflare does not block algorithmic-complexity DoS, so there is no effective protection against this vector. The request context is not propagated into `GetCommitmentsForPaddedLength`, so a short client deadline or early disconnect does not abort the server-side MSM work.

---

## DisperseBlob Commitment-Before-Payment (EDA-02)

The second surface of EDA-02: `DisperseBlob` recomputes the KZG commitment inside `validateDispersalRequest` before `AuthorizePayment`, so an attacker with only a self-signed EOA and no payment authorization forces full KZG work that is discarded at commitment rejection. A live `inabox` reproduction measured the rejection wall time, which equals the KZG cost, confirming KZG runs before payment.

### Test Setup

| Item | Value |
|---|---|
| Cloud / instance | GCP n2-standard-16 (16 vCPU, 62 GB, 96 GB SSD), Ubuntu 24.04.4 LTS |
| Harness | EigenDA `inabox` full stack: disperser V2 API + controller + encoder + relay + operator in-process; anvil + LocalStack (S3/DynamoDB) + Graph node in Docker |
| EigenDA source | commit `61019b4` |
| Tools | Go 1.24.0, Node v20.20.2, Foundry anvil v1.7.1, Docker 29.5.2, LocalStack 2026.5.0 |

The attacker generates a random EOA, signs a 16 MiB random blob carrying a valid-but-mismatched commitment, and calls `DisperseBlob`. `AuthenticateBlobRequest` only checks that the signature matches the header `AccountID`, not that the account has payment authorization, so the request passes auth and the server runs the full KZG recomputation before rejecting at `commitments.Equal` (`disperse_blob_v2.go:262`).

### Single Request (raw)

```text
Round 1: wall=1.582s  code=InvalidArgument
Round 2: wall=1.596s  code=InvalidArgument
Round 3: wall=1.563s  code=InvalidArgument
avg=1.58s
msg="failed to validate request: invalid blob commitment: commitments are different:
     [238 93 184 21 ...]   <- server-recomputed commitment
     vs
     [64 0 0 0 ...]"       <- attacker's fake commitment
```

The ~1.58 s rejection wall time equals the KZG cost (G1 MSM x1 + G2 MSM x2, each saturating all cores), confirming the commitment is recomputed before payment is checked.

### Concurrency (one attacker degrades legitimate dispersal)

A legitimate victim issuing a real `DisperseBlob` while N attackers flood fake-commitment 16 MiB blobs:

| Attackers | Victim wall | vs baseline | Attacker ops in 8 s |
|---|---|---|---|
| 0 | 1.572 s | 1.0x | — |
| 1 | 2.893 s | 1.8x | 3 |
| 2 | 4.430 s | 2.8x | 4 |
| 4 | 7.398 s | 4.7x | 8 |

### CPU Utilization (16 vCPU)

| Phase | avg CPU% | cores (of 16) | max CPU% |
|---|---|---|---|
| Baseline (no attacker, 5 s) | 2.6% | 0.03 | — |
| Attack (1 attacker, 60 s) | 1,343.2% | 13.4 (84%) | 1,504% (15/16, 94%) |

A single attacker drove the disperser to 516x baseline CPU and pinned 13 to 15 of 16 cores with nothing but self-signed ECDSA requests. The attacker cost is one ECDSA signature per request, the server cost is several core-seconds of KZG, an extreme asymmetry; a short client gRPC deadline does not abort the server-side work.
