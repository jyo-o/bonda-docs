# EDA-T09: Ejector Role Abuse Can Force-Remove Honest Operators

{% hint style="warning" %}
**Severity**: High (7.1/10) · **STRIDE**: T · **Status**: Verified
{% endhint %}

## Summary

The `EjectionManager` contract grants a single EOA (`0x864247...`) the power to force-eject operators representing up to 33.33% of a quorum's total stake within any 3-day window. The root cause is that the active ejector is a single private key rather than a multisig, despite the contract owner being the core multisig (`0x002721...`).

If this key is compromised, an attacker could systematically remove honest operators, manipulating quorum composition to push it below the 55% confirmation threshold and undermine data availability guarantees.

## Description

The `EjectionManager` contract (`0x130d8E...`) is owned by the multisig (`0x002721...`), but delegates ejection authority to a single EOA. The on-chain parameters are:

- `rateLimitWindow` = 259,200 seconds (3 days)
- `ejectableStakePercent` = 3,333 (33.33%)

This means the ejector can remove up to one-third of a quorum's stake in a rolling 3-day window. On-chain data shows 528 ejection events total, with a peak of 178 events in August 2024. Two active ejector EOAs have collectively been responsible for 150 ejection calls over 16 months, accounting for 100% of all ejection activity.

```solidity
// contracts/src/periphery/ejection/EigenDAEjectionManager.sol
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/periphery/ejection/EigenDAEjectionManager.sol
// @audit Ejection manager with rate limiting — ejector is a single EOA, not a multisig
contract EigenDAEjectionManager is ImmutableEigenDAEjectionsStorage, IEigenDASemVer {
    // ...
    modifier onlyEjector(address sender) {
        _onlyEjector(sender);
        _;
    }

    function setDelay(uint64 delay) external onlyOwner(msg.sender) {
        EigenDAEjectionLib.setDelay(delay);
    }

    function setCooldown(uint64 cooldown) external onlyOwner(msg.sender) {
        EigenDAEjectionLib.setCooldown(cooldown);
    }
}
```

The attack flow is:

1. Attacker compromises the ejector EOA private key (`0x864247...`).
2. Attacker calls the ejection function targeting honest operators.
3. Within a 3-day window, up to 33.33% of quorum stake is force-ejected.
4. The remaining operators may be unable to meet the 55% confirmation threshold.

## Proof of Concept

On-chain state was queried at block 25101686. See [Verification Evidence](../evidence.md#id-1.-ejector-role-parameters-eda-t09) for full commands and results.

- `rateLimitWindow` = 259,200 seconds (3 days), `ejectableStakePercent` = 3,333 (33.33%)
- 3 active ejector addresses confirmed, 2 of which are EOAs responsible for 100% of ejection activity
- 150 `ejectOperators` calls observed over 16 months via Blockscout transaction history

## Impact

Compromise of the ejector EOA allows an attacker to force-remove up to 33.33% of a quorum's total stake within a 3-day window. This can shift quorum composition enough to prevent the remaining operators from reaching the 55% confirmation threshold, disrupting data availability for all dependent rollups.

The attack requires only a single private key compromise with no multisig coordination, making it a concentrated point of failure. The `EjectionCooldown` rate limit provides some ceiling on the damage rate but does not prevent the attack.

### CVSS 3.1

**Score**: 7.1/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Ejection is executed via on-chain transactions accessible over the network |
| AC (Attack Complexity) | L (Low) | The ejector is a single EOA key with 150 active uses observed over 16 months, demonstrating routine access |
| PR (Privileges Required) | L (Low) | The ejector role is needed, but it is held by a single EOA rather than a multisig |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is contained within the EigenDA protocol |
| C (Confidentiality) | N (None) | No direct data exposure from ejection |
| I (Integrity) | L (Low) | Quorum composition is manipulated, but no direct fund theft is possible through ejection alone |
| A (Availability) | H (High) | Up to 33.33% of quorum stake can be force-ejected within 3 days, potentially pushing the quorum below its operating threshold |

## Recommendation

1. Upgrade the ejector from a single EOA to a multisig to eliminate single-key compromise risk.
2. Implement a time-delay mechanism (timelock) on ejection calls to allow community observation and response before ejections take effect.
3. Consider reducing the `ejectableStakePercent` parameter or shortening the `rateLimitWindow` to limit the blast radius of any abuse.
