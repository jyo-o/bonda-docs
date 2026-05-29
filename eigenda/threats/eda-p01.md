# EDA-P01: EigenDA Operator Slashing Not Implemented -- Asymmetric Honesty Incentives

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: P · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

Zero slash/freeze functions or events across all EigenDA core contracts. EigenLayer AllocationManager shows getOperatorSetCount=0 for EigenDA AVS, with empty arrays for all quorum strategies. ServiceManager slasher()/allocationManager() calls revert. Zero slash events over 500k blocks (~70 days). Only Rewards are wired (rewardsInitiator is an EOA), creating an incentive asymmetry -- operators receive rewards without punishment for dishonest behavior. Directly linked to 8 free-rider candidates in PoC #02.

## Prerequisites

EigenLayer slashing not activated + EigenDA's own slasher not implemented

## Attack Scenario

Operator only signs BLS but does not serve chunks (free-rider) -> zero punishment; only ejection by 2 EOA authorities is available.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.9/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L/CI:N/II:M/AI:M` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process, ExternalEntity |

### BVSS Rationale

B:N -- Absence of slashing alone does not prove direct fund theft/freeze path; requires multi-step chain (no slashing -> free-riding -> data withholding -> rollup impact). AC:H -- Requires organized operator free-riding or collusion. S:U -- EigenDA protocol design decision with impact within the same system, not external scope change. I:H/II:M -- DA guarantee integrity gap (undetected data withholding) but KZG proof/erasure coding compensating mechanisms exist. A:L/AI:M -- Gradual service quality degradation possible but not immediate availability disruption.

## Code References

### Source Code

- [`contracts/src/core/`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/core/) -- slash 0건

### PoC Notes

- poc/33-slashing-absence/evidence.yaml

### Other References

- AllocationManager onchain [VERIFIED]

## Verification & Evidence

**Status**: Verified

EigenDA core .sol has zero slash/freeze instances. AllocationManager OperatorSetCount=0. Zero slash events over 500k blocks. Only rewards are wired.

**PoC References**: #30

## Mitigations

EigenLayer AllocationManager integration, dedicated slasher contract. Ejection is the only current alternative (PoC #02).
