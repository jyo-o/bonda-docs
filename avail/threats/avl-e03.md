# AVL-E03: Deployer EOA Retains Admin Role Enabling Solo VectorX Upgrade

{% hint style="warning" %}
**Severity**: High (8.2/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

The deployer EOA (0xDEd0000E32f8F40414d3ab3a830f735a3553E18e) still holds DEFAULT_ADMIN_ROLE on the VectorX bridge contract. This role is the admin of all other roles, meaning the deployer can grant itself TIMELOCK_ROLE and immediately upgrade the contract to an arbitrary implementation in just two transactions, bypassing all governance protections. The root cause is commented-out revocation code in the Guardian.s.sol deployment script that was intended to remove this role but was never executed.

## Description

VectorX uses OpenZeppelin's AccessControl system to manage permissions across roles including DEFAULT_ADMIN_ROLE, TIMELOCK_ROLE, and GUARDIAN_ROLE. The deployment script (`Guardian.s.sol`) contains code to revoke DEFAULT_ADMIN_ROLE from the deployer, but that code is commented out and was never executed on-chain.

```solidity
// @audit — Guardian.s.sol: revocation of DEFAULT_ADMIN_ROLE from deployer
//          is commented out, leaving the deployer with full admin authority.
//          The deployer can call grantRole(TIMELOCK_ROLE, self) followed by
//          upgradeTo(malicious) in two transactions.
```

The deployer address is a regular EOA (not a contract), confirmed by `eth_getCode` returning `0x`. Its nonce of 1107 indicates it is an actively used account. Since DEFAULT_ADMIN_ROLE is the admin of TIMELOCK_ROLE (getRoleAdmin returns 0x00), the deployer can unilaterally grant itself upgrade authority.

## Proof of Concept

Exhaustive role verification across 3 roles and 2 principals confirmed that DEFAULT_ADMIN_ROLE is the only active role for the deployer. The following on-chain queries established the attack path:

- `hasRole(DEFAULT_ADMIN_ROLE, 0xDEd...)` returns `true` -- deployer still holds admin
- `hasRole(TIMELOCK_ROLE, 0xDEd...)` returns `false` -- not yet granted, but grantable
- `getRoleAdmin(TIMELOCK_ROLE)` returns `0x00` (DEFAULT_ADMIN_ROLE) -- confirms admin can grant it
- `eth_getCode(0xDEd...)` returns `0x` -- confirms this is an EOA, not a contract
- `eth_getTransactionCount(0xDEd...)` returns `1107` -- actively used account

TIMELOCK_ROLE admin mapping to 0x00 was verified, confirming the grant-then-upgrade attack path.

References: poc_onchain_verification.md sections 8 and 9.

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
