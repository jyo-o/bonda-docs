# EDA-P01: Operator Slashing Not Implemented Creates Asymmetric Honesty Incentives

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: P · **Status**: Verified
{% endhint %}

## Summary

EigenDA has no slashing mechanism for dishonest or non-performing operators. A comprehensive search across all EigenDA core contracts found zero slash or freeze functions, zero slash-related events, and the EigenLayer `AllocationManager` returns `getOperatorSetCount=0` for the EigenDA AVS.

The root cause is that slashing integration with EigenLayer has not been activated. This creates an incentive asymmetry where operators receive rewards but face no economic penalty for free-riding. Operators can sign BLS attestations without storing or serving data chunks, which directly enables the 8 free-rider candidates observed in EDA-D12.

## Description

A comprehensive search across all EigenDA core contracts found:

- Zero slash or freeze functions
- Zero slash-related events
- Zero slashing incidents over 500,000 blocks (approximately 70 days)
- `AllocationManager.getOperatorSetCount()` returns 0 for the EigenDA AVS
- All quorum strategies return empty arrays
- `ServiceManager.slasher()` and `ServiceManager.allocationManager()` both revert

Meanwhile, rewards are fully wired: a `rewardsInitiator` EOA distributes rewards to operators.

This finding is directly connected to the 8 free-rider candidate operators identified in EDA-D12 and the dead operator observations. Without slashing, ejection by the two authorized EOA addresses is the only recourse against misbehaving operators.

The degradation path is:
1. Operators sign BLS attestations to earn rewards but do not store or serve data chunks.
2. Other operators observe this profitable strategy and may adopt it.
3. As the proportion of free-riders grows, data availability guarantees weaken.
4. Eventually the Reed-Solomon reconstruction threshold is threatened.
5. The only response available is manual ejection by the two authorized EOA ejector addresses.

## Proof of Concept

On-chain state was queried at block 25101686. See [Verification Evidence](../evidence.md#4-slashing-absence-verification-eda-p01) for full commands and results.

- Zero slash or freeze functions found across all EigenDA core contracts
- `AllocationManager.getOperatorSetCount()` returns 0 for the EigenDA AVS
- `ServiceManager.slasher()` and `ServiceManager.allocationManager()` both revert
- Zero slashing events over 500,000 blocks (approximately 70 days)

## Impact

Without slashing, operators face zero economic penalty for free-riding behavior. This creates a rational incentive to sign attestations without actually storing data, degrading the network's data availability guarantees over time.

The 8 free-rider candidates already observed in EDA-D12 demonstrate this is not theoretical. As the proportion of non-serving operators grows, the system approaches the Reed-Solomon erasure coding reconstruction threshold. No authentication is needed to exploit this; any registered operator can free-ride. KZG proofs and erasure coding provide partial mitigation but cannot fully compensate for widespread non-serving behavior.

### CVSS 3.1

**Score**: 6.5/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Operators participate over the network; free-riding occurs through network-based attestation signing |
| AC (Attack Complexity) | H (High) | Organized operator free-riding or collusion is needed; exploitation requires a multi-step chain from no slashing to free-riding to data withholding |
| PR (Privileges Required) | N (None) | Any registered operator can free-ride; operator registration is open |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the EigenDA protocol |
| C (Confidentiality) | N (None) | No data exposure from free-riding |
| I (Integrity) | H (High) | The DA guarantee has an integrity gap where data withholding goes undetected; KZG and erasure coding provide compensating but incomplete mechanisms |
| A (Availability) | L (Low) | Service quality degradation is gradual rather than immediate; accumulated over time |

## Recommendation

1. Integrate with the EigenLayer `AllocationManager` to activate slashing for the EigenDA AVS.
2. Deploy a dedicated EigenDA slasher contract to enforce economic penalties for non-serving operators.
3. Until slashing is implemented, strengthen the ejection mechanism to provide faster response against identified free-riders (related to EDA-T09).
4. Consider implementing on-chain proof-of-custody or periodic data availability challenges to detect free-riding behavior proactively.
