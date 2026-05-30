# AVL-T02: Bridge Upgrade Protected by 24-Hour Timelock

{% hint style="info" %}
**Severity**: Low (0.3/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

Avail's Bridge contract upgrades are routed through a TimelockController (0x45828180bbE489350D621d002968A0585406d487) that enforces a mandatory 24-hour delay on all upgrade operations. The `getMinDelay` function returns 86,400 seconds, confirming this one-day waiting period. The TimelockController holds the DEFAULT_ADMIN role over the bridge, meaning all administrative changes must pass through the timelock.

The proposer and executor roles on the TimelockController are assigned to the Governance Multisig (0x7F2f...), which requires 4 of 7 signatures to approve any action. This means a malicious bridge upgrade would require both the compromise of 4 multisig keys and a 24-hour public waiting period before the upgrade takes effect.

This is a relatively safe design. The 24-hour window gives users, monitoring systems, and the broader community time to detect a suspicious upgrade proposal and withdraw funds before it executes. Combined with the 4-of-7 multisig requirement, the practical risk of a successful malicious upgrade through this path is low.

## Prerequisites

- Compromise 4 of the 7 Governance Multisig signing keys to propose an upgrade
- Wait 24 hours for the timelock to expire before execution
- Avoid detection by users and monitoring systems during the waiting period

## Attack Scenario

1. The attacker compromises 4 of the 7 Governance Multisig signing keys and proposes a malicious bridge upgrade through the TimelockController. The proposal is recorded on-chain and begins the 24-hour countdown.
2. During the 24-hour waiting period, the malicious proposal is publicly visible on-chain. Monitoring systems, security researchers, or community members can detect the suspicious upgrade and raise the alarm. Users are notified to withdraw their funds from the bridge.
3. If the proposal goes undetected for the full 24 hours, the attacker executes the upgrade, and the malicious code takes effect. However, the probability of a malicious upgrade surviving 24 hours of public scrutiny is low, especially with active monitoring in place.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.3/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:L/A:N/CI:N/II:L/AI:N` |
| Scope | bridge |

### Scoring Rationale

There is no direct financial impact under normal operation because the timelock and multisig provide strong safeguards. The attack vector requires physical or social engineering access to 4 of the 7 key holders. Attack complexity is high due to the combined requirement of compromising the 4-of-7 multisig and waiting 24 hours without detection. The attacker needs proposer credentials on the TimelockController. The scope is constrained by the timelock to a limited window of impact. Integrity impact is low because users have a full 24-hour window to exit the bridge before any malicious upgrade takes effect. Infrastructure integrity impact is similarly low for the same reason.

## Evidence

### On-Chain Verification

- `cast call 0x4582...d487 "hasRole(bytes32,address)(bool)" <DEFAULT_ADMIN_ROLE> <TimelockController>` returns `true`, confirming the TimelockController holds admin authority.
- `cast call 0x4582...d487 "getMinDelay()(uint256)"` returns `86400`, confirming the 24-hour delay.
- Proposer and executor roles are assigned to the Governance Multisig (0x7F2f...).

### PoC Testing

- Documented in poc_onchain_verification.md, sections 1 and 5.

## Mitigations

The 24-hour timelock provides a guaranteed exit window for users to withdraw funds before any upgrade takes effect. The 4-of-7 multisig threshold prevents any single compromised key from proposing upgrades. Together, these mechanisms make the Bridge upgrade path significantly more secure than contracts that can be upgraded immediately.
