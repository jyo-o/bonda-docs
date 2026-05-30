# AVL-E03: Deployer EOA Retains Admin Role Enabling Solo VectorX Upgrade

{% hint style="warning" %}
**Severity**: High (8.2/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

The deployer EOA still holds DEFAULT_ADMIN_ROLE on the VectorX bridge contract. Because this role controls all other roles, the deployer can grant itself upgrade authority and replace the entire contract implementation in just two transactions, bypassing all governance protections. The root cause is that the revocation code in the deployment script was commented out and never executed.

## Description

VectorX uses OpenZeppelin's AccessControl system to manage permissions across roles including DEFAULT_ADMIN_ROLE, TIMELOCK_ROLE, and GUARDIAN_ROLE. The deployment script Guardian.s.sol contains code to revoke DEFAULT_ADMIN_ROLE from the deployer, but that code is commented out and was never executed on-chain.

```solidity
// Guardian.s.sol — deployment script
// @audit DEFAULT_ADMIN_ROLE revocation from deployer is commented out.
//        The deployer retains full admin authority, enabling a 2-transaction
//        upgrade path: grantRole(TIMELOCK_ROLE) then upgradeTo(malicious).
//
// Intended but never executed:
// sp1Vector.revokeRole(sp1Vector.DEFAULT_ADMIN_ROLE(), msg.sender);
```

The deployer at 0xDEd0000E...E18e is a regular externally owned account rather than a smart contract, confirmed by `eth_getCode` returning empty code. Its nonce of 1107 indicates it is an actively used account. Since DEFAULT_ADMIN_ROLE is the admin of TIMELOCK_ROLE as confirmed by getRoleAdmin returning 0x00, the deployer can unilaterally grant itself upgrade authority.

## Proof of Concept

On-chain state was queried on Ethereum mainnet. See [Verification Evidence](../evidence.md#id-4.-deployer-admin-role-verification-avl-e03) for full commands and results.

- `hasRole(DEFAULT_ADMIN_ROLE, 0xDEd...)` returns `true` — deployer still holds admin
- `getRoleAdmin(TIMELOCK_ROLE)` returns `0x00` (DEFAULT_ADMIN_ROLE) — confirms the deployer can grant itself TIMELOCK_ROLE
- Deployer is an EOA (nonce 1107), confirming a 2-transaction upgrade path that bypasses the 4-of-7 governance multisig

## Impact

If the deployer's private key is compromised, an attacker gains full unilateral control over the VectorX bridge contract. The attacker can replace the entire VectorX implementation with arbitrary code in two transactions (grantRole + upgradeTo), enabling false attestations, fund theft from the bridge, or a complete bridge halt. No multisig approval, no timelock delay, and no community detection window exists for this path.

### CVSS 3.1
**Score**: 8.2/10 (High)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Attack is executed via direct calls on the Ethereum network |
| AC | H (High) | Requires compromising the deployer's private key |
| PR | L (Low) | Attacker needs the deployer's specific credentials (single EOA key) |
| UI | N (None) | No user interaction required |
| S | C (Changed) | Impact extends beyond VectorX to the entire bridge ecosystem and dependent L2s |
| C | N (None) | No confidentiality impact |
| I | H (High) | Arbitrary implementation replacement enables false attestations, bypasses governance multisig |
| A | H (High) | A single compromised key can halt the entire bridge, bypassing all governance protections |

## Recommendation

1. **Execute the commented-out revocation code**: Uncomment and execute the DEFAULT_ADMIN_ROLE revocation from the deployer EOA in Guardian.s.sol, as originally intended by the deployment script.
2. **Transfer DEFAULT_ADMIN_ROLE to the Governance Multisig**: Ensure the admin role is held by the same 4-of-7 multisig that controls other critical governance functions, eliminating single-key risk.
3. **Verify revocation on-chain**: After execution, confirm that `hasRole(DEFAULT_ADMIN_ROLE, 0xDEd...)` returns `false`.
