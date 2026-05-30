# EDA-E03: Operator Stake Concentration Enables Minority Collusion Beyond Safety Thresholds

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

On-chain stake distribution analysis reveals that a small number of operators control enough stake to exceed both safety (33%) and liveness (45%) thresholds across all three quorums. In Quorum 0 (ETH), the top 3 operators hold 39.8% of stake, and in Quorum 2 (Custom), AltLayer alone holds 52.6%. The root cause is insufficient stake decentralization, as evidenced by a Nakamoto coefficient of just 3 at the 33% threshold. If 3 operators in Q0 or Q1 collude, they can sign invalid data availability certificates that pass on-chain BLS aggregate signature verification.

## Description

Stake distribution was queried at block 25097183 using `StakeRegistry.getCurrentStake()` across 120 operators:

**Quorum 0 (ETH)** -- total stake `2.368e24`:
- Top 3 operators = 39.8% > 33% safety threshold
- Top 4 operators = 48.2% > 45% liveness threshold
- Top 5 cumulative = 55.25%

**Quorum 1 (EIGEN)** -- total stake `2.727e26`:
- Top 3 = 35.6% > 33% safety threshold
- Top 5 = 51.7% > 45% liveness threshold
- Positions 4 through 8 are suspected to be controlled by Coinbase entities

**Quorum 2 (Custom)** -- total stake `8.064e23`:
- AltLayer alone = 52.6%, exceeding all thresholds unilaterally
- Q2 is not a required quorum

**Concentration metrics**:
- Nakamoto coefficient (33%) = 3 for both Q0 and Q1
- Herfindahl-Hirschman Index (HHI): Q0 = 883, Q1 = 876
- Gini coefficients: Q0 = 0.79, Q1 = 0.82

The attack path requires collusion: 3 operators sign invalid DA certificates, the aggregate BLS signature meets the required threshold, and on-chain verification passes because it only checks signature validity and stake weight. For full protocol impact, both required quorums (Q0 and Q1) must be simultaneously compromised.

## Proof of Concept

### On-Chain Verification

- `StakeRegistry.getCurrentStake()` queried across 120 operators at block 25101686.
- Q0 total stake: `2.368e24`, Q1: `2.727e26`, Q2: `8.064e23`.
- Q0 top 3 = 39.8% > safety 33%; top 4 = 48.2% > liveness 45%.
- Q1 top 3 = 35.6% > safety 33%; top 5 = 51.7% > liveness 45%.
- Q2 AltLayer alone = 52.6%.
- Nakamoto coefficient (33%) = 3; HHI Q0 = 883, Q1 = 876; Gini = 0.79 / 0.82; Top 5 cumulative Q0 = 55.25%.

### Reproduction

- `poc/16-*/evidence.yaml` confirmed stake concentration figures.

**PoC References**: #14

## Impact

If 3 operators in Q0 or Q1 collude, they can sign invalid data availability certificates that pass on-chain BLS signature verification, because the aggregate signature meets the required stake threshold. Rollups relying on EigenDA would accept these invalid certificates, potentially posting invalid state commitments. For full protocol disruption, both Q0 and Q1 must be simultaneously compromised (dual-quorum requirement). No authentication beyond operator registration is needed; the attack exploits the existing stake distribution. In Q2, AltLayer can unilaterally exceed all thresholds, though Q2 is not a required quorum.

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
