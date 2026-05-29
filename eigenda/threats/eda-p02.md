# EDA-P02: DAS (Data Availability Sampling) Absent -- Clients Rely Entirely on Quorum Trust

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: P · **Scope**: protocol · **Status**: Code Verified
{% endhint %}

## Overview

The official EigenDA spec explicitly states DAS is not used, and the client retrieval path has no sampling interface. Onchain cert verification only checks BLS aggregate signatures and stake threshold (55%); the client's random shuffle is for load balancing, not cryptographic sampling. This is a different trust model from Celestia (namespaced Merkle + sampling) and Ethereum PeerDAS (column sampling). The 8 free-rider gap from PoC #02 is a direct attack scenario.

## Prerequisites

EigenDA's design decision not to adopt DAS (different trust model from Celestia et al.)

## Attack Scenario

Operator signs BLS claiming data received -> cert valid -> retrieval actually fails for data.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.9/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L/CI:N/II:M/AI:M` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process, Datastore |

### BVSS Rationale

B:N -- No direct financial impact. AC:H -- Non-adoption of DAS is a design decision; exploitation requires operator collusion. I:H/II:M -- Entirely dependent on quorum trust, but KZG opening proof provides partial verification. A:L/AI:M -- Clients cannot independently verify, but the protocol itself operates normally.

## Code References

### Source Code

- [`EigenDACertVerificationLib.sol:232-246`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/EigenDACertVerificationLib.sol#L232-L246) -- BLS aggregate + 55% stake threshold만

### PoC Notes

- poc/34-das-absence/evidence.yaml

### Other References

- docs/spec/src/introduction.md:27 [VERIFIED]

## Verification & Evidence

**Status**: Code Verified

Spec docs/spec/src/introduction.md:27 explicitly states DAS is not used. Code has zero sampling interfaces. Verified from spec/code, not mainnet measurement.

**PoC References**: #31

## Mitigations

KZG opening proof enables partial verification (ValidateBatchV2), but is not sample-based. Whether DAS will be introduced in EigenDA v2/v3 is unspecified.
