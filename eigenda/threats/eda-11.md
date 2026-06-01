# EDA-11: Operator Slashing Not Implemented Creates Asymmetric Honesty Incentives

{% hint style="success" %}
**Category**: Design Note · **Status**: verified
{% endhint %}

## Summary

EigenDA has no slashing mechanism for dishonest or non-performing operators. A comprehensive search across all EigenDA core contracts found zero slash or freeze functions, zero slash-related events, and the EigenLayer `AllocationManager` returns `getOperatorSetCount=0` for the EigenDA AVS.

The root cause is that slashing integration with EigenLayer has not been activated. This creates an incentive asymmetry where operators receive rewards but face no economic penalty for free-riding. Operators can sign BLS attestations without storing or serving data chunks, which directly enables the 8 free-rider candidates observed in EDA-06.

## Description

A comprehensive search across all EigenDA core contracts found:

- Zero slash or freeze functions
- Zero slash-related events
- Zero slashing incidents over 500,000 blocks (approximately 70 days)
- `AllocationManager.getOperatorSetCount()` returns 0 for the EigenDA AVS
- All quorum strategies return empty arrays
- `ServiceManager.slasher()` and `ServiceManager.allocationManager()` both revert

Meanwhile, rewards are fully wired: a `rewardsInitiator` EOA distributes rewards to operators.

This finding is directly connected to the 8 free-rider candidate operators identified in EDA-06 and the dead operator observations. Without slashing, ejection by the two authorized EOA addresses is the only recourse against misbehaving operators.

The degradation path is:
1. Operators sign BLS attestations to earn rewards but do not store or serve data chunks.
2. Other operators observe this profitable strategy and may adopt it.
3. As the proportion of free-riders grows, data availability guarantees weaken.
4. Eventually the Reed-Solomon reconstruction threshold is threatened.
5. The only response available is manual ejection by the two authorized EOA ejector addresses.

## Proof of Concept

On-chain state was queried at block 25101686. See [Verification Evidence](../evidence.md#slashing-absence-verification-eda-11) for full commands and results.

- Zero slash or freeze functions found across all EigenDA core contracts
- `AllocationManager.getOperatorSetCount()` returns 0 for the EigenDA AVS
- `ServiceManager.slasher()` and `ServiceManager.allocationManager()` both revert
- Zero slashing events over 500,000 blocks (approximately 70 days)

## Impact

Without slashing, operators face zero economic penalty for free-riding behavior. This creates a rational incentive to sign attestations without actually storing data, degrading the network's data availability guarantees over time.

The 8 free-rider candidates already observed in EDA-06 demonstrate this is not theoretical. As the proportion of non-serving operators grows, the system approaches the Reed-Solomon erasure coding reconstruction threshold. No authentication is needed to exploit this; any registered operator can free-ride. KZG proofs and erasure coding provide partial mitigation but cannot fully compensate for widespread non-serving behavior.

Sets the Verifiability Design Baseline through the dishonesty-deterrent sub-property. The absence of slashing is a documented design property, not an exploitable defect, so it carries no score.

## Recommendation

1. Integrate with the EigenLayer `AllocationManager` to activate slashing for the EigenDA AVS.
2. Deploy a dedicated EigenDA slasher contract to enforce economic penalties for non-serving operators.
3. Until slashing is implemented, strengthen the ejection mechanism to provide faster response against identified free-riders (related to EDA-08).
4. Consider implementing on-chain proof-of-custody or periodic data availability challenges to detect free-riding behavior proactively.
