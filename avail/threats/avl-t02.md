# AVL-T02: Bridge Upgrade Protected by 24-Hour Timelock

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: T · **Status**: Verified
{% endhint %}

## Summary

Avail's Bridge contract upgrades are routed through a TimelockController (0x45828180bbE489350D621d002968A0585406d487) enforcing a mandatory 24-hour delay. The TimelockController holds DEFAULT_ADMIN role over the bridge, and the proposer/executor roles are assigned to the Governance Multisig (4-of-7). This design gives users a 24-hour exit window before any upgrade takes effect, making a successful malicious upgrade through this path low-probability.

## Description

The Bridge upgrade path requires both a 4-of-7 multisig approval and a 24-hour timelock delay before execution.

```
// @audit — Bridge upgrade protection:
//          TimelockController: 0x4582...d487
//          getMinDelay(): 86,400 seconds (24 hours)
//          DEFAULT_ADMIN role: TimelockController
//          Proposer/Executor: Governance Multisig (0x7F2f..., 4-of-7)
//          Attack requires: 4/7 key compromise + 24h undetected waiting period.
```

The 24-hour window gives users, monitoring systems, and the broader community time to detect a suspicious upgrade proposal and withdraw funds before it executes. The proposal is publicly visible on-chain during the entire waiting period.

## Proof of Concept

On-chain verification confirmed the timelock configuration:

- `cast call 0x4582...d487 "hasRole(bytes32,address)(bool)" <DEFAULT_ADMIN_ROLE> <TimelockController>` returns `true`, confirming the TimelockController holds admin authority
- `cast call 0x4582...d487 "getMinDelay()(uint256)"` returns `86400`, confirming the 24-hour delay
- Proposer and executor roles are assigned to the Governance Multisig (0x7F2f...)

References: poc_onchain_verification.md, sections 1 and 5.

## Impact

A malicious bridge upgrade would require both the compromise of 4 multisig keys and surviving a 24-hour public waiting period without detection. If the proposal goes undetected for the full 24 hours, the attacker executes the upgrade and malicious code takes effect. However, the probability of a malicious upgrade surviving 24 hours of public on-chain scrutiny is low, especially with active monitoring in place. Users have a guaranteed exit window to withdraw funds before any upgrade executes.

### CVSS 3.1
**Score**: 1.8/10 (Low)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Requires physical or social engineering access to 4 of 7 key holders |
| AC | H (High) | Combined requirement of 4-of-7 multisig compromise and 24-hour undetected waiting period |
| PR | L (Low) | Attacker needs proposer credentials on the TimelockController |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact constrained by the timelock to a limited window |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Users have a full 24-hour window to exit the bridge before any malicious upgrade takes effect |
| A | N (None) | No direct availability impact; the timelock provides ample detection time |

## Recommendation

1. **Implement automated upgrade monitoring**: Deploy automated monitoring that detects and alerts on any TimelockController proposals immediately, ensuring the 24-hour window is actively utilized for detection.
2. **Establish an emergency pause procedure**: Define a clear procedure for the Pauser Multisig to halt bridge operations if a suspicious upgrade proposal is detected during the timelock period.
3. **Consider extending the timelock**: Evaluate whether a longer delay (e.g., 48 or 72 hours) would provide additional safety margin for detection and community response.
