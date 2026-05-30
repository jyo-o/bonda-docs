# CEL-P01: Flat 2% Double Sign Slashing Without Correlation Penalty

{% hint style="success" %}
**Severity**: Informational · **STRIDE**: P · **Status**: verified
{% endhint %}

## Overview

Celestia uses the standard Cosmos SDK x/slashing module, which applies a flat 2% penalty (slash_fraction_double_sign=0.02) for double signing regardless of how many validators double sign simultaneously. Whether one validator or twenty-eight validators double sign at the same time, each is slashed exactly 2% of their bonded stake.

This contrasts with Ethereum PoS, which applies a correlation penalty that effectively reaches 100% slashing for coordinated attacks, making coordinated safety violations roughly 50 times more expensive at equivalent scale. Celestia's flat penalty means the on-chain deterrence against coordinated attacks is structurally weaker.

However, a practical attack requiring two-thirds collusion is unrealistic. Coordinating 28 independent institutional validators introduces enormous operational costs including internal decision-making, whistleblower risk, and precise timing synchronization. Additionally, double signing itself generates no direct revenue for the attackers. This is a protocol design observation rather than an exploitable vulnerability.

## Prerequisites

- No practical attack scenario exists
- Theoretical scenario: collusion of the top 28 validators (67.02%, approximately 340.6M TIA) would face only approximately $3.19M in on-chain costs at TIA $0.468, but coordination costs and absence of a revenue mechanism make this economically irrational

## Attack Scenario

1. This is classified as a design gap rather than a concrete attack. No clear attack path has been identified.
2. In theory, a coordinated group controlling more than two-thirds of voting power could double sign to finalize conflicting blocks.
3. Each participating validator would lose only 2% of bonded stake regardless of the coordination scale.
4. In practice, the coordination cost among 28 independent institutions far exceeds the on-chain penalty, and there is no mechanism by which the attackers profit.

## Impact

A structural weakness in economic deterrence against coordinated safety violations compared to correlation-penalty systems like Ethereum PoS. The flat 2% penalty does not scale with attack size, but the practical likelihood of such coordination is negligible.

## Evidence

### On-Chain / Network

- Mainnet slashing parameters (2026-05-26): slash_fraction_double_sign=0.02, slash_fraction_downtime=0.0
- Confirmed via celestia-rest.publicnode.com/cosmos/slashing/v1beta1/params
- Mainnet staking: top 28 validators hold 67.02% (approximately 340.6M TIA)
- TIA price: $0.468 (CoinGecko, 2026-05-26)
- Cosmos SDK x/slashing README confirms flat per-validator slashing with no correlation mechanism

## Mitigations

Recommended fixes include introducing a correlation penalty to the Cosmos SDK (referencing Ethereum's EIP-7002 approach), raising slash_fraction_double_sign to 10% or higher via governance, implementing weighted slashing that scales with the number of simultaneous double signers, and setting slash_fraction_downtime above zero (currently zero, providing no liveness penalty).
