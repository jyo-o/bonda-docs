# EDA-E03: Operator Stake Concentration Enables Minority Collusion Beyond Safety Thresholds

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

On-chain stake distribution analysis reveals that a small number of operators control enough stake to exceed both safety (33%) and liveness (45%) thresholds across all three quorums.

In Quorum 0 (ETH), the top 3 operators hold 39.8% of stake. In Quorum 2 (Custom), AltLayer alone holds 52.6%. The Nakamoto coefficient at the 33% threshold is just 3 for both Q0 and Q1.

If 3 operators in Q0 or Q1 collude, they can sign invalid data availability certificates that pass on-chain BLS aggregate signature verification.

## Description

![Stake concentration — top 3 operators exceed 33% safety threshold](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/eigenda/assets/eda-e03-stake-concentration.png)

Stake distribution was queried at block 25097183 using `StakeRegistry.getCurrentStake()` across 120 operators.

**Quorum 0 (ETH)** has a total stake of `2.368e24`:
- Top 3 operators hold 39.8%, exceeding the 33% safety threshold.
- Top 4 operators hold 48.2%, exceeding the 45% liveness threshold.
- Top 5 cumulative stake reaches 55.25%.

**Quorum 1 (EIGEN)** has a total stake of `2.727e26`:
- Top 3 operators hold 35.6%, exceeding the 33% safety threshold.
- Top 5 operators hold 51.7%, exceeding the 45% liveness threshold.
- Positions 4 through 8 are suspected to be controlled by Coinbase entities.

**Quorum 2 (Custom)** has a total stake of `8.064e23`:
- AltLayer alone holds 52.6%, exceeding all thresholds unilaterally.
- Q2 is not a required quorum.

**Concentration metrics**:
- Nakamoto coefficient (33%) = 3 for both Q0 and Q1
- Herfindahl-Hirschman Index (HHI): Q0 = 883, Q1 = 876
- Gini coefficients: Q0 = 0.79, Q1 = 0.82

The attack path requires collusion among 3 operators to sign invalid DA certificates. The aggregate BLS signature would meet the required threshold, and on-chain verification would pass because it only checks signature validity and stake weight. For full protocol impact, both required quorums (Q0 and Q1) must be simultaneously compromised.

## Proof of Concept

On-chain state was queried at block 25101686. See [Verification Evidence](../evidence.md#id-3.-operator-stake-distribution-eda-e03) for full commands and results.

- Q0 top 3 operators hold 39.8% of stake, exceeding the 33% safety threshold
- Q1 top 3 operators hold 35.6% of stake, also exceeding the 33% safety threshold
- Nakamoto coefficient at 33% = 3 for both Q0 and Q1

## Impact

If 3 operators in Q0 or Q1 collude, they can sign invalid data availability certificates that pass on-chain BLS signature verification. The aggregate signature would meet the required stake threshold, and rollups relying on EigenDA would accept these invalid certificates, potentially posting invalid state commitments.

For full protocol disruption, both Q0 and Q1 must be simultaneously compromised due to the dual-quorum requirement. No authentication beyond operator registration is needed; the attack exploits the existing stake distribution.

In Q2, AltLayer can unilaterally exceed all thresholds, though Q2 is not a required quorum.

### CVSS 3.1

**Score**: 6.5/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attestations and certificate signing occur over the network |
| AC (Attack Complexity) | H (High) | Organized collusion of 3 independent entities is required, and both Q0 and Q1 must be compromised simultaneously for full impact |
| PR (Privileges Required) | N (None) | Operators are already registered; no additional privileges needed for collusion |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the EigenDA protocol and dependent rollups |
| C (Confidentiality) | N (None) | No data exposure from stake concentration |
| I (Integrity) | L (Low) | Invalid certificate signing is possible but on-chain BLS verification remains functional; dual-quorum requirement limits impact |
| A (Availability) | H (High) | Top 3 operators in Q0 already exceed the 33% safety threshold, threatening quorum operation |

## Recommendation

1. Pursue stake redistribution by incentivizing delegation diversification to raise the Nakamoto coefficient above 3.
2. Onboard additional independent operators to dilute individual operator stake concentrations.
3. Investigate and address the suspected Coinbase entity concentration in Q1 positions 4 through 8.
4. Consider implementing maximum stake caps per operator or per entity to prevent future concentration.
