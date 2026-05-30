# EDA-P02: Absence of Data Availability Sampling Forces Full Quorum Trust

{% hint style="warning" %}
**Severity**: Medium (5.9/10) · **STRIDE**: P · **Status**: Code Verified
{% endhint %}

## Overview

EigenDA does not implement Data Availability Sampling (DAS). The official specification explicitly states this, and the client retrieval path contains no sampling interface. This represents a fundamentally different trust model compared to Celestia (which uses namespaced Merkle trees with random sampling) and Ethereum PeerDAS (which uses column sampling).

On-chain certificate verification checks only BLS aggregate signatures and a 55% stake threshold. The client-side random shuffle used during retrieval is for load balancing purposes only, not cryptographic sampling. This means clients cannot independently verify that data was actually made available by operators; they must trust that the quorum honestly stored the data they attested to.

The 8 free-rider candidate operators identified in PoC #02 illustrate the direct attack scenario: operators can sign BLS attestations claiming they received data without actually storing it, and there is no sampling mechanism for clients to detect this dishonesty.

## Prerequisites

- EigenDA's design decision not to adopt DAS, which is a conscious architectural choice rather than an oversight.

## Attack Scenario

1. One or more operators register with EigenDA and receive data chunks for storage.
2. The operators sign BLS attestations confirming data receipt but discard the actual data.
3. The aggregate BLS signature meets the 55% stake threshold, producing a valid certificate.
4. On-chain certificate verification passes because it only checks signatures and stake thresholds, not actual data availability.
5. When a client later attempts to retrieve the data, the request fails because the operators no longer have it.
6. The client has no sampling mechanism to detect this ahead of time and relied entirely on quorum trust.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.9/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L/CI:N/II:M/AI:M` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because there is no direct financial impact from the absence of DAS. Attack Complexity (AC) is High because the non-adoption of DAS is a design decision and exploitation requires operator collusion to withhold data. Integrity impact (I) is High because clients are entirely dependent on quorum trust with no independent verification, but Integrity Infrastructure impact (II) is Medium because KZG opening proofs provide partial verification capability. Availability impact (A) is Low because clients cannot independently verify data availability, but Availability Infrastructure impact (AI) is Medium because the protocol itself continues to function normally.

## Evidence

### Source Code

- [`EigenDACertVerificationLib.sol:232-246`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L232-L246) -- Certificate verification checks only BLS aggregate signatures and 55% stake threshold.
- `docs/spec/src/introduction.md:27` -- Specification explicitly states DAS is not used.
- Code search for sampling interfaces returns zero results.

### PoC Testing

- `poc/34-das-absence/evidence.yaml` confirmed the absence of sampling interfaces.
- Verified from specification and code, not from mainnet measurement.

**PoC References**: #31

## Mitigations

KZG opening proofs provide partial verification capability through `ValidateBatchV2`, but this is not a sampling-based mechanism. Clients can verify individual chunks they retrieve but cannot proactively sample the network to check data availability. Whether DAS will be introduced in future EigenDA versions (v2/v3) is not specified in current documentation.
