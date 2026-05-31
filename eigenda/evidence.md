# EigenDA Evidence Summary

This page summarizes the on-chain verification and data analysis evidence collected for EigenDA threat findings. All on-chain results are from Ethereum mainnet using `cast` (Foundry). Every conclusion traces to a raw on-chain response or data source.

**Verification date**: 2026-05-15 to 2026-05-24
**Tools**: cast (Foundry), grpcurl, Python scripts, ipinfo.io
**RPC endpoint**: `https://ethereum-rpc.publicnode.com`
**Reference block**: 25101686

---

## Ejector Role Parameters (EDA-T09)

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

## Governance Multisig Configuration (EDA-E02)

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

## Operator Stake Distribution (EDA-E03)

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

**Quorum 0 (ETH)** — 58 operators, total stake `2.368e24`:

| Rank | Top-k Cumulative | Threshold |
|------|------------------|-----------|
| Top 3 | 39.80% | > 33% safety |
| Top 4 | 48.16% | > 45% liveness |
| Top 5 | 55.25% | > 55% confirmation |

**Quorum 1 (EIGEN)** — 62 operators, total stake `2.727e26`:

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

## Slashing Absence Verification (EDA-P01)

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

## Relay Registry Single Point of Failure (EDA-D06)

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

## Infrastructure Concentration Analysis (EDA-G01)

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

## Dead Operator Measurement (EDA-D12)

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

### DataAPI Limitations

The `signing-info` endpoint becomes unreliable beyond 24-hour windows. Requests with `interval=172800` (48h) and above consistently return HTTP 502/504/429 errors. This limits real-time monitoring to 24-hour snapshots, requiring external probers for longer-term observation.

---

## Proxy Admin and Upgrade Authority (EDA-E02 supplementary)

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

## Unpauser and Pauser Structure (EDA-E02 supplementary)

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

## Dispersal Client Centralization (EDA-D06 supplementary)

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

## Relay Latency Spike Observation (EDA-D06 supplementary)

A naturally occurring latency inflation event on the single relay was observed by the BONDA prober.

### Baseline vs Spike

| Period | Window (UTC) | Requests | Avg Latency | P95 Latency |
|---|---|---|---|---|
| Baseline | 06:30-06:37 | 472 | 599 ms | 999 ms |
| Spike | 06:40-06:47 | 471 | 2,449 ms | 4,076 ms |

Latency inflated 4.1x during the spike, with peak individual retrievals reaching 6,094 ms. The spike was not explained by blob size shift (average blob size identical in both windows) or local infrastructure issues.

### Spike Minute-Level Detail

| Minute (UTC) | Requests | Avg (ms) | P95 (ms) | >2s | >5s |
|---|---|---|---|---|---|
| 06:39 | 59 | 835 | 2,205 | 4 | 0 |
| 06:40 | 63 | 2,639 | 4,257 | 45 | 0 |
| 06:41 | 78 | 2,386 | 3,916 | 38 | 2 |
| 06:42 | 69 | 2,730 | 4,542 | 49 | 1 |
| 06:43 | 61 | 2,560 | 3,745 | 44 | 0 |
| 06:44 | 58 | 2,099 | 3,223 | 23 | 0 |
| 06:45 | 59 | 2,402 | 3,888 | 30 | 2 |
| 06:46 | 83 | 2,327 | 4,031 | 46 | 0 |

All 471 spike-window retrievals went through relay key 0 (the only registered relay). The proxy default relay timeout is 10 seconds, meaning sustained latency above this would cause complete retrieval failures.
