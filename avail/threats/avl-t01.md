# AVL-T01: VectorX Can Be Upgraded Instantly Without Timelock

{% hint style="info" %}
**Severity**: Medium (5.6/10) · **STRIDE**: T · **Status**: Verified
{% endhint %}

## Summary

VectorX uses the UUPS proxy pattern and can be upgraded instantly by the Governance Multisig with no timelock delay. Unlike the Avail Bridge which enforces a 24-hour delay before upgrades take effect, VectorX upgrades execute immediately, giving the community no window to detect and respond to a malicious upgrade.

## Description

VectorX is the ZK light-client bridge contract that verifies Avail block headers on Ethereum. It uses the UUPS proxy pattern where upgrade logic lives inside the implementation contract. The EIP-1967 admin slot is set to `0x0`, confirming this UUPS design.

```solidity
// TimelockedUpgradeable.sol
// @audit Misleadingly named — no actual timelock logic exists.
//        The modifier only checks role membership, not time delay.
//        VectorX upgrades execute immediately upon authorization,
//        unlike the Avail Bridge which enforces a 24-hour delay.
modifier onlyTimelock() {
    if (!hasRole(TIMELOCK_ROLE, msg.sender)) {
        revert OnlyTimelock();
    }
    _;
}
```

The Governance Multisig, a 4-of-7 Safe at 0x7F2f...3666, holds the TIMELOCK_ROLE and can upgrade VectorX in a single transaction with no delay. This creates an inconsistency in governance protections between VectorX and the Avail Bridge.

## Proof of Concept

No exploit reproduction was conducted. This finding is based on on-chain state verification and source code analysis.

- EIP-1967 admin slot reads `0x0`, confirming the UUPS proxy pattern where upgrade logic lives in the implementation
- Source code review of `TimelockedUpgradeable.sol` confirmed the `onlyTimelock` modifier performs only `hasRole(TIMELOCK_ROLE, msg.sender)` with no delay, queue, or schedule logic

## Impact

A compromised 4-of-7 multisig could replace the VectorX implementation with arbitrary code in a single transaction. The malicious implementation can forge data roots to produce false block header attestations, redirect bridge operations, or halt the bridge entirely. The community has no time window to detect the upgrade and respond before damage is done, unlike the Avail Bridge which provides a 24-hour detection window for the same operation.

### CVSS 3.1
**Score**: 5.6/10 (Medium)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Requires physical or social engineering access to obtain 4 of 7 multisig signer keys |
| AC | H (High) | Simultaneously compromising 4 of 7 independent signers is difficult |
| PR | L (Low) | Attacker needs multisig signer credentials specifically |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact stays within the VectorX upgrade scope |
| C | N (None) | No confidentiality impact |
| I | H (High) | Malicious upgrade can forge data roots; community detection is possible only after the fact |
| A | H (High) | Bridge halt is possible, though 4-of-7 multisig threshold provides meaningful protection |

## Recommendation

1. **Add a timelock delay to VectorX upgrades**: Implement a TimelockController for VectorX upgrades matching the 24-hour delay used by the Avail Bridge contract, giving the community a detection window.
2. **Rename or replace TimelockedUpgradeable**: Either implement actual timelock logic in the base contract or rename it to accurately reflect its AccessControl-only functionality (e.g., `RoleBasedUpgradeable`).
3. **Standardize governance protections**: Ensure all critical bridge contracts (VectorX, Bridge, SP1VerifierGateway) have consistent upgrade protection levels.
