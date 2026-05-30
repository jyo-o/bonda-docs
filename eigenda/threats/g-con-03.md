# G-CON-03: Operator Infrastructure Concentrated in Few Cloud Providers

{% hint style="warning" %}
**Severity**: Medium (5.3/10) · **STRIDE**: CON · **Status**: Verified
{% endhint %}

## Overview

An analysis of 78 EigenDA operator host classes (mapped from 72 raw IPs) through ASN aggregation reveals that operator infrastructure is heavily concentrated in a small number of hosting providers. In Quorum 0 (ETH), AWS accounts for 21.78% of stake, OVH for 15.67%, and the top 5 providers collectively host 82.7% of stake-weighted infrastructure. In Quorum 1 (EIGEN), a single provider, Herd SaaS, accounts for 41.87% of stake alone.

This concentration creates a systemic risk: a single cloud region or provider outage could take offline enough operators to approach or breach the 55% quorum confirmation threshold. While such outages are typically transient, they could temporarily prevent EigenDA from producing valid certificates, disrupting all dependent rollups.

The geographic and provider diversity is insufficient for a protocol-critical infrastructure layer. The concentration metrics mirror the stake concentration findings in EDA-E03, but this threat focuses specifically on the infrastructure layer rather than the economic layer.

## Prerequisites

- Multiple operators using the same cloud provider or ASN, which is the current observed state of the network.

## Attack Scenario

1. A major cloud provider (such as AWS or Herd SaaS) experiences an outage in a region hosting multiple EigenDA operators.
2. Operators hosted on the affected infrastructure go offline simultaneously.
3. With AWS at 21.78% of Q0 stake and top 5 at 82.7%, a significant provider outage could push available stake below the 55% confirmation threshold.
4. EigenDA temporarily cannot produce valid certificates because the remaining operators cannot reach the required quorum.
5. Rollups depending on EigenDA experience delayed or failed data availability confirmations until the outage is resolved.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because there is no financial impact from infrastructure concentration. Attack Complexity (AC) is High because this requires a specific provider failure event. Availability impact (A) is High because a single provider outage could affect a significant portion of stake (AWS 21.78% Q0, Herd SaaS 41.87% Q1, top 5 cumulative 82.7%), approaching the quorum confirmation threshold of 55%. Availability Infrastructure impact (AI) is Medium because such outages are typically transient and services recover once the provider restores operations.

## Evidence

### On-Chain Verification

- 78 operator host classes extracted, 72 raw IP mappings completed.
- ASN aggregation via ipinfo.io lookup.
- Q0 stake by provider: AWS 21.78%, OVH 15.67%, top 5 cumulative 82.7%.
- Q1 stake by provider: Herd SaaS 41.87% alone.

### PoC Testing

- `poc/18-cloud-asn-concentration/evidence.yaml` confirmed all provider concentration figures.

**PoC References**: #16

## Mitigations

Encouraging geographic and provider diversity through incentive mechanisms would reduce concentration risk. Supplementing cloud-hosted nodes with on-premises infrastructure would add resilience. Operators should be incentivized to deploy across different cloud providers and regions to prevent correlated failures.
