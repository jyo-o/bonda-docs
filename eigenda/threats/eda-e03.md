# EDA-E03: Operator Stake Concentration -- Minority Collusion Exceeds Safety/Liveness Thresholds

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: E · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

Onchain verification (block 25097183): Q0 (ETH) top 3 = 39.8% > safety 33%, top 4 = 48.2% > liveness 45%. Q1 (EIGEN) top 3 = 35.6% > safety 33%, top 5 = 51.7% > liveness 45%. Q2 (Custom) AltLayer alone = 52.6%, exceeding all thresholds individually. Q1 top 4-8 contains 5 Coinbase (suspected) entities.

## Prerequisites

Q0/Q1: Collusion of 3 operators. Q2: AltLayer alone.

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 6.5/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:M/A:H/CI:N/II:M/AI:M` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | ExternalEntity |

### BVSS Rationale

B:N -- Stake concentration itself has no direct financial impact; actual impact only occurs upon collusion execution. AC:H -- Requires organized collusion of 3 independent entities (Q0/Q1 simultaneous). I:M/II:M -- Invalid cert signing possible but onchain BLS verification remains. A:H -- Q0 top3=39.8% exceeds safety 33% confirmed. AI:M -- Both required quorums Q0+Q1 must be compromised simultaneously; single quorum compromise alone cannot halt the entire protocol.

## Code References


### Onchain Evidence

- `StakeRegistry.getCurrentStake() × 120 operators`
- `block 25097183`

### PoC Notes

- block=25101686
- poc/16-*/evidence.yaml [VERIFIED]

### Other References

- Q0 totalStake=2.368e24
- Q1=2.727e26
- Q2=8.064e23

## Verification & Evidence

**Status**: Verified

Nakamoto(33)=3, HHI Q0=883/Q1=876, Gini 0.79/0.82. Top5 cumulative Q0=55.25%.

**PoC References**: #14

## Mitigations

3 independent quorums -- all must fail simultaneously (required quorums = Q0+Q1). However Q2 is not required.
