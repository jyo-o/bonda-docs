# CEL-P01: Double Sign Flat 2% Slashing — Absence of Correlation Penalty (Protocol Design Gap)

{% hint style="info" %}
**Severity**: Informational · **STRIDE**: P (Protocol Design) · **Scope**: protocol · **Status**: verified
{% endhint %}

## Overview

Celestia's double_sign slashing is a flat 2% (slash_fraction_double_sign=0.02), using the standard Cosmos SDK x/slashing module implementation without a correlation penalty. Whether 1 validator or 28 validators double sign simultaneously, each is slashed exactly 2%. Ethereum PoS applies a correlation penalty that effectively reaches 100% slashing for coordinated attacks -- roughly 50x more expensive at equivalent scale. A practical attack scenario (2/3+ collusion) is unrealistic due to coordination costs (orchestrating 28 independent entities, whistleblower risk, timing synchronization) and the absence of a revenue mechanism (double signing itself yields no direct profit). However, this design choice indicates structurally weaker on-chain deterrence against coordinated safety violations compared to Ethereum PoS.

## Core Invariants Affected

`consensus_safety`

Common Cosmos SDK design characteristic. A protocol design observation, not a Celestia-specific vulnerability. No realistic attack potential due to coordination costs and absence of revenue mechanism.

## Prerequisites

N/A -- no practical attack scenario. Note: top 28 validators (67.02%, ~340.6M TIA) colluding would face only ~$3.19M in on-chain costs (at TIA $0.468), but coordination costs and absence of revenue path make this economically irrational.

## Attack Scenario

**Condition**: N/A -- no clear attack path identified. Classified as a design gap.

**Example**: Mainnet (2026-05-26): slash_fraction_double_sign=0.02, slash_fraction_downtime=0.0 (on-chain confirmed), TIA=$0.468 (CoinGecko), top 28 cumulative ~340.6M TIA (67.02%). Theoretical on-chain cost: ~$3.19M. Comparison: Ethereum PoS coordinated attack -> ~100% slashing (correlation penalty), ~50x cost at equivalent scale.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Informational |
| Likelihood | Unrealistic (2/3 collusion premise + coordination cost > financial gain + no revenue mechanism) |
| Scope | protocol |
| Target | Process |
| Core Invariants | consensus_safety |

## Code References

- On-chain: `cosmos/slashing/v1beta1/params (slash_fraction_double_sign=0.02, slash_fraction_downtime=0.0, 2026-05-26)`
- On-chain: `cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED (top-28=67.02%, ~340.6M TIA)`
- Source: CoinGecko (TIA=$0.468, 2026-05-26)
- Source: Cosmos SDK x/slashing README ('flat per-validator slashing, no correlation mechanism')

## Verification & Evidence

**Status**: verified

Slashing parameters confirmed directly from celestia-rest.publicnode.com (2026-05-26). TIA price confirmed via CoinGecko API. Correlation penalty absence confirmed in Cosmos SDK x/slashing source. slash_fraction_downtime=0 additionally confirmed.

## Mitigations

Recommendations: (1) Introduce correlation penalty to Cosmos SDK (ref EIP-7002), (2) Raise slash_fraction_double_sign to 10%+ via governance, (3) Implement weighted slashing for simultaneous multi-validator double signs, (4) Set slash_fraction_downtime>0 (currently 0, no liveness penalty).
