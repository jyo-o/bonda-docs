# EDA-P01: Operator Slashing Not Implemented Creates Asymmetric Honesty Incentives

{% hint style="warning" %}
**Severity**: Medium (5.9/10) · **STRIDE**: P · **Status**: Verified
{% endhint %}

## Overview

EigenDA has no slashing mechanism for dishonest or non-performing operators. A search across all EigenDA core contracts found zero slash or freeze functions, zero slash-related events, and zero slashing incidents over 500,000 blocks (approximately 70 days). The EigenLayer `AllocationManager` shows `getOperatorSetCount=0` for the EigenDA AVS, with empty arrays for all quorum strategies. Calls to `ServiceManager.slasher()` and `ServiceManager.allocationManager()` both revert.

Meanwhile, rewards are fully wired: a `rewardsInitiator` EOA distributes rewards to operators. This creates an incentive asymmetry where operators receive rewards for participation but face no economic penalty for dishonest behavior such as free-riding (signing BLS attestations without storing or serving data chunks).

This finding is directly connected to the 8 free-rider candidate operators identified in PoC #02 (EDA-D12) and the dead operator observations. Without slashing, ejection by the two authorized EOA addresses is the only recourse against misbehaving operators.

## Prerequisites

- EigenLayer slashing not activated for the EigenDA AVS.
- EigenDA has not implemented its own slasher contract.

## Attack Scenario

1. An operator registers with EigenDA and begins participating in the network.
2. The operator signs BLS attestations to earn rewards but does not store or serve data chunks.
3. The operator faces zero economic penalty for this free-riding behavior because no slashing mechanism exists.
4. Other operators observe this profitable strategy and may adopt it, gradually increasing the number of non-serving operators.
5. As the proportion of free-riders grows, data availability guarantees weaken, eventually threatening the Reed-Solomon reconstruction threshold.
6. The only response available is manual ejection by the two authorized EOA ejector addresses.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.9/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L/CI:N/II:M/AI:M` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because the absence of slashing alone does not create a direct fund theft or freeze path; exploitation requires a multi-step chain from no slashing to free-riding to data withholding to rollup impact. Attack Complexity (AC) is High because organized operator free-riding or collusion is needed. Scope (S) is Unchanged because this is an EigenDA protocol design decision with impact within the same system, not an external scope change. Integrity impact (I) is High because the DA guarantee has an integrity gap where data withholding goes undetected, but Integrity Infrastructure impact (II) is Medium because KZG proof and erasure coding provide compensating mechanisms. Availability impact (A) is Low because service quality degradation is gradual rather than immediate, and Availability Infrastructure impact (AI) is Medium because the degradation can accumulate over time.

## Evidence

### On-Chain Verification

- All EigenDA core Solidity contracts contain zero slash/freeze functions or events.
- `AllocationManager.getOperatorSetCount()` returns 0 for the EigenDA AVS.
- All quorum strategies return empty arrays.
- `ServiceManager.slasher()` and `ServiceManager.allocationManager()` both revert.
- Zero slash events over 500,000 blocks (approximately 70 days).
- Rewards are wired through a `rewardsInitiator` EOA.

### Source Code

- [`contracts/src/core/`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/core/) -- No slash or freeze functions found across the entire core contract directory.

### PoC Testing

- `poc/33-slashing-absence/evidence.yaml` confirmed all findings.
- AllocationManager on-chain state verified.

**PoC References**: #30

## Mitigations

Ejection is currently the only available mechanism to remove misbehaving operators, controlled by two EOA addresses (PoC #02). Integration with the EigenLayer `AllocationManager` for slashing and deployment of a dedicated EigenDA slasher contract would restore incentive symmetry. KZG proofs and erasure coding provide partial mitigation by enabling data verification and recovery even with non-serving operators.
