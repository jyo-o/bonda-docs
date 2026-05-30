# CEL-P01: Flat 2% Double Sign Slashing Without Correlation Penalty

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: P · **Status**: verified
{% endhint %}

## Summary

Celestia uses the standard Cosmos SDK `x/slashing` module which applies a flat 2% penalty (`slash_fraction_double_sign=0.02`) for double signing regardless of how many validators double sign simultaneously. This contrasts with Ethereum PoS's correlation penalty that effectively reaches 100% for coordinated attacks. While this is a structural design gap in economic deterrence, no practical attack scenario exists because the coordination cost among 28 independent institutional validators far exceeds the on-chain penalty and there is no revenue mechanism for attackers.

## Description

The flat slashing mechanism applies identically regardless of attack scale:

Mainnet slashing parameters (2026-05-26) confirmed via `celestia-rest.publicnode.com/cosmos/slashing/v1beta1/params`:
- `slash_fraction_double_sign=0.02` (flat 2%)
- `slash_fraction_downtime=0.0` (zero liveness penalty)

Whether one validator or twenty-eight validators double sign at the same time, each is slashed exactly 2% of their bonded stake. This makes coordinated safety violations roughly 50x cheaper at equivalent scale compared to Ethereum PoS's correlation penalty.

Theoretical scenario analysis:
- Collusion of the top 28 validators (67.02% of voting power, approximately 340.6M TIA) would face only approximately $3.19M in on-chain costs at TIA $0.468
- However, coordinating 28 independent institutional validators introduces enormous operational costs: internal decision-making, whistleblower risk, and precise timing synchronization
- Double signing itself generates no direct revenue for attackers
- Cosmos SDK `x/slashing` README confirms flat per-validator slashing with no correlation mechanism

Mainnet staking data: top 28 validators hold 67.02% (approximately 340.6M TIA). TIA price: $0.468 (CoinGecko, 2026-05-26).

## Proof of Concept

No proof of concept was conducted for this threat. This is classified as a protocol design observation rather than an exploitable vulnerability.

## Impact

A structural weakness in economic deterrence against coordinated safety violations compared to correlation-penalty systems like Ethereum PoS. The flat 2% penalty does not scale with attack size. However, the practical likelihood of such coordination is negligible due to the absence of a revenue mechanism and the enormous coordination costs among independent institutional validators.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Double signing is executed over the consensus network |
| AC (Attack Complexity) | H (High) | Requires coordinating 28+ independent institutional validators with no revenue incentive |
| PR (Privileges Required) | N (None) | No special privileges beyond being a bonded validator (low minimum stake) |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to Celestia's economic security model |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | The under-penalized coordinated double sign could theoretically finalize conflicting blocks |
| A (Availability) | N (None) | No direct availability impact from the slashing design itself |

## Recommendation

1. Introduce a correlation penalty to the Cosmos SDK slashing module (referencing Ethereum's approach) so that simultaneous double signs by multiple validators incur proportionally higher penalties.
2. Raise `slash_fraction_double_sign` to 10% or higher via governance to increase the base deterrent.
3. Implement weighted slashing that scales with the number of simultaneous double signers to make coordinated attacks exponentially more expensive.
4. Set `slash_fraction_downtime` above zero (currently zero) via governance to provide at least minimal liveness penalty.
