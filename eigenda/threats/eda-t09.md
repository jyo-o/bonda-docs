# EDA-T09: Ejector Role Abuse Can Force-Remove Honest Operators

{% hint style="warning" %}
**Severity**: High (7.0/10) · **STRIDE**: T · **Status**: Verified
{% endhint %}

## Overview

The EigenDA `EjectionManager` contract (`0x130d8E...`) is owned by the same multisig (`0x002721...`) that controls the other core contracts. However, the active ejector is a single EOA (`0x864247...`), not a multisig. This means a single private key controls the ability to eject operators from the network.

The ejection parameters are configured with a `rateLimitWindow` of 259,200 seconds (3 days) and an `ejectableStakePercent` of 3,333 (33.33%). This allows the ejector to force-remove up to 33.33% of a quorum's total stake within any 3-day window. If the ejector key is compromised, an attacker could systematically remove honest operators, manipulating quorum composition to undermine data availability guarantees.

On-chain data shows 528 ejection events total, with a peak of 178 events in August 2024. Two active ejector EOAs have collectively been responsible for 150 ejection calls over 16 months, accounting for 100% of all ejection activity.

## Prerequisites

- Compromise of the ejector EOA private key, or abuse by the authorized ejector.

## Attack Scenario

1. An attacker compromises the ejector EOA private key (`0x864247...`).
2. The attacker calls the ejection function on the `EjectionManager` contract, targeting honest operators.
3. Within a 3-day window, the attacker can eject operators representing up to 33.33% of a quorum's total stake.
4. The removal of honest operators shifts the quorum composition, potentially allowing colluding operators to reach the safety or liveness thresholds.
5. The remaining operators may be unable to meet the 55% confirmation threshold, disrupting data availability.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 7.0/10 (High) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:R/UI:N/S:U/C:N/I:L/A:H/CI:N/II:M/AI:H` |
| Scope | Bridge |

### Scoring Rationale

Blockchain Impact (B) is None because no direct fund theft is possible through ejection alone. Attack Vector (AV) is Network because ejection is executed via on-chain transactions. Attack Complexity (AC) is Low because the ejector is a single EOA key, and 150 active uses have been observed over 16 months, demonstrating routine access. Privileges Required (PR) is Reserved because the ejector role is needed. Availability impact (A) is High and Availability Infrastructure impact (AI) is also High because up to 33.33% of quorum stake can be force-ejected within 3 days, which could push the quorum below its operating threshold.

## Evidence

### On-Chain Verification

- `EjectionManager.owner()` returns `0x002721B4` at block 25101686.
- `RegistryCoordinator.ejector()` returns `0x130d8EA0`.
- Active ejector is `0x8642` (EOA), with `isEjector=true`.
- `rateLimitWindow` = 259,200 seconds (3 days).
- `ejectableStakePercent` = 3,333 (33.33%).
- 528 total ejection events observed, peaking at 178 in 2024-08.
- 2 active ejector EOAs called 150 ejections over 16 months (100% of all ejection activity).

### Source Code

- [`contracts/src/periphery/ejection/EigenDAEjectionManager.sol`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/periphery/ejection/EigenDAEjectionManager.sol) -- Ejection manager contract with rate limiting parameters.

### PoC Testing

- `poc/06-*/evidence.yaml` confirmed ejection parameters and activity.
- Blockscout shows 150 ejection events as the primary source (Dune query 7461036 tracks `OperatorStakeUpdate`, not ejections).

**PoC References**: #05, #28

## Mitigations

The `EjectionCooldown` rate limit provides some protection by capping ejections at 33.33% of quorum stake per 3-day window. However, the ejector being a single EOA rather than a multisig is a centralization risk. Upgrading the ejector to a multisig or implementing a time-delay mechanism would reduce the risk of rapid abuse.
