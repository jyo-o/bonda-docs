# EigenDA Evidence Summary

This page summarizes the on-chain verification and data analysis evidence collected for EigenDA threat findings. All on-chain results are from Ethereum mainnet using `cast` (Foundry). Every conclusion traces to a raw on-chain response or data source.

**Verification date**: 2026-05-15 to 2026-05-24
**Tools**: cast (Foundry), grpcurl, Python scripts, ipinfo.io
**RPC endpoint**: `https://ethereum-rpc.publicnode.com`
**Reference block**: 25101686

---

## 1. Ejector Role Parameters (EDA-T09)

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

## 2. Governance Multisig Configuration (EDA-E02)

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

## 3. Operator Stake Distribution (EDA-E03)

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

## 4. Slashing Absence Verification (EDA-P01)

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

## 5. Relay Registry Single Point of Failure (EDA-D06)

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

## 6. Infrastructure Concentration Analysis (EDA-G01)

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

## 7. Dead Operator Measurement (EDA-D12)

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
