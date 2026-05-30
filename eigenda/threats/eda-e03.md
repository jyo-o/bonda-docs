# EDA-E03: Operator Stake Concentration Enables Minority Collusion Beyond Safety Thresholds

{% hint style="warning" %}
**Severity**: Medium (6.5/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Overview

On-chain stake distribution analysis at block 25097183 reveals that a small number of operators control enough stake to exceed both safety and liveness thresholds across all three quorums. In Quorum 0 (ETH), the top 3 operators hold 39.8% of stake, exceeding the 33% safety threshold, and the top 4 hold 48.2%, exceeding the 45% liveness threshold. In Quorum 1 (EIGEN), the top 3 hold 35.6% (above safety) and the top 5 hold 51.7% (above liveness). Quorum 1 positions 4 through 8 are suspected to be controlled by Coinbase entities.

The most extreme case is Quorum 2 (Custom), where AltLayer alone holds 52.6% of stake, exceeding all thresholds by itself. While Q2 is not a required quorum, this demonstrates how stake concentration can enable unilateral control.

Concentration metrics confirm the severity: the Nakamoto coefficient at 33% is just 3 for both Q0 and Q1, the Herfindahl-Hirschman Index (HHI) is 883 for Q0 and 876 for Q1, and Gini coefficients are 0.79 and 0.82 respectively. The top 5 operators in Q0 hold a cumulative 55.25% of stake.

## Prerequisites

- Q0/Q1: Collusion of 3 operators to exceed the safety threshold.
- Q2: AltLayer alone can exceed all thresholds.

## Attack Scenario

1. Three operators in Q0 or Q1 collude, collectively controlling over 33% of quorum stake.
2. The colluding operators sign invalid data availability certificates, attestating to data that was never made available.
3. On-chain BLS signature verification passes because the aggregate signature meets the required threshold.
4. For full protocol impact, both required quorums (Q0 and Q1) must be simultaneously compromised.
5. Rollups relying on EigenDA accept the invalid certificates, potentially posting invalid state commitments.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 6.5/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:M/A:H/CI:N/II:M/AI:M` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because stake concentration itself has no direct financial impact; actual harm only occurs if collusion is executed. Attack Complexity (AC) is High because organized collusion of 3 independent entities is required, and both Q0 and Q1 must be compromised simultaneously. Integrity impact (I) is Medium because invalid certificate signing is possible but on-chain BLS verification remains functional. Availability impact (A) is High because the top 3 operators in Q0 already exceed the 33% safety threshold. Availability Infrastructure impact (AI) is Medium because both required quorums (Q0 + Q1) must be compromised for full protocol disruption; single-quorum compromise alone cannot halt the protocol.

## Evidence

### On-Chain Verification

- `StakeRegistry.getCurrentStake()` queried across 120 operators at block 25101686.
- Q0 total stake: `2.368e24`, Q1: `2.727e26`, Q2: `8.064e23`.
- Q0 top 3 = 39.8% > safety 33%; top 4 = 48.2% > liveness 45%.
- Q1 top 3 = 35.6% > safety 33%; top 5 = 51.7% > liveness 45%.
- Q2 AltLayer alone = 52.6%.
- Nakamoto coefficient (33%) = 3; HHI Q0 = 883, Q1 = 876; Gini = 0.79 / 0.82; Top 5 cumulative Q0 = 55.25%.

### PoC Testing

- `poc/16-*/evidence.yaml` confirmed stake concentration figures.

**PoC References**: #14

## Mitigations

EigenDA uses 3 independent quorums, and both Q0 and Q1 are required for certificate validity. This means an attacker must compromise operators across both quorums simultaneously. Q2 is not a required quorum. However, the low Nakamoto coefficient of 3 means that stake redistribution or additional operator onboarding is needed to strengthen decentralization.
