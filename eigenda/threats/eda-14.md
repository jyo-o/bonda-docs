# EDA-14: Infrastructure Concentration

{% hint style="success" %}
**Category**: Design Note · **Status**: verified
{% endhint %}

## Summary

An analysis of 78 EigenDA operator host classes (mapped from 72 raw IPs) through ASN aggregation reveals that operator infrastructure is heavily concentrated in a small number of hosting providers.

In Quorum 0 (ETH), the top 5 providers collectively host 82.7% of stake-weighted infrastructure, with AWS at 21.78% and OVH at 15.67%. In Quorum 1 (EIGEN), Herd SaaS alone accounts for 41.87% of stake.

A single cloud region or provider outage could take offline enough operators to approach the 55% quorum confirmation threshold.

## Description

ASN aggregation analysis of operator infrastructure reveals systemic provider concentration.

**Quorum 0 (ETH)** stake by provider:
- AWS: 21.78% of stake
- OVH: 15.67% of stake
- Top 5 providers cumulative: 82.7% of stake-weighted infrastructure

**Quorum 1 (EIGEN)** stake by provider:
- Herd SaaS: 41.87% of stake alone

The concentration creates a systemic risk. A single cloud region or provider outage could simultaneously take offline enough operators to approach or breach the 55% quorum confirmation threshold. While such outages are typically transient, they could temporarily prevent EigenDA from producing valid certificates, disrupting all dependent rollups.

The geographic and provider diversity is insufficient for a protocol-critical infrastructure layer. This threat focuses specifically on the infrastructure layer rather than the economic layer, which is covered by the stake concentration findings in EDA-09.

## Proof of Concept

Infrastructure analysis of 78 operator host classes was conducted via ASN aggregation. See [Verification Evidence](../evidence.md#infrastructure-concentration-analysis-eda-14) for full data.

- 72 raw IPs resolved and mapped to ASN providers via ipinfo.io
- Q0: AWS hosts 21.78% of stake, top 5 providers host 82.7% cumulatively
- Q1: Herd SaaS alone accounts for 41.87% of stake

## Impact

A major cloud provider outage affecting a region hosting multiple EigenDA operators would cause simultaneous operator failures. With the top 5 providers hosting 82.7% of Q0 stake, a significant provider outage could push available stake below the 55% confirmation threshold.

EigenDA would temporarily be unable to produce valid certificates, and rollups depending on EigenDA would experience delayed or failed data availability confirmations. Such outages are typically transient and services recover once the provider restores operations, but the impact window could be significant.

No attacker action is required. Natural infrastructure failures suffice.

Sets the Decentralization Design Baseline through the software and infrastructure diversity sub-property. This is a documented structural property and carries no score.

## Recommendation

1. Encourage geographic and provider diversity through incentive mechanisms that reward operators using underrepresented providers.
2. Supplement cloud-hosted nodes with on-premises infrastructure to add resilience against cloud provider outages.
3. Operators should be incentivized to deploy across different cloud providers and regions to prevent correlated failures.
4. Consider implementing provider-diversity requirements or caps on stake concentration per hosting provider.
