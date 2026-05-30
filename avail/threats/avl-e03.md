# AVL-E03: Deployer EOA Retains Admin Role Enabling Solo VectorX Upgrade

{% hint style="warning" %}
**Severity**: High (8.4/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX is the ZK light-client bridge contract that relays Avail block headers to Ethereum. Access to critical functions like contract upgrades is controlled by OpenZeppelin's AccessControl system, which organizes permissions into roles such as DEFAULT_ADMIN_ROLE, TIMELOCK_ROLE, and GUARDIAN_ROLE.

The deployer EOA (0xDEd0000E32f8F40414d3ab3a830f735a3553E18e) still holds DEFAULT_ADMIN_ROLE on VectorX. This role is the admin of all other roles, meaning the deployer can grant itself any role at will. In practice, the deployer can call `grantRole(TIMELOCK_ROLE, self)` and then `upgradeTo(malicious)` in just two transactions, replacing the entire VectorX implementation without any multisig approval.

This happened because the deployment script (Guardian.s.sol) contains code to revoke DEFAULT_ADMIN_ROLE from the deployer, but that code is commented out. The deployer address is a regular EOA with no contract code protection, and its nonce of 1107 confirms it is an actively used account. If the deployer's private key is compromised, an attacker gains full unilateral control over the VectorX bridge contract, bypassing all governance protections.

## Prerequisites

- Access to the deployer EOA private key (0xDEd0000E32f8F40414d3ab3a830f735a3553E18e)
- This is a single key, not a multisig

## Attack Scenario

1. An attacker compromises the deployer EOA private key. Since this is a single EOA, only one key needs to be obtained.
2. The attacker calls `grantRole(TIMELOCK_ROLE, deployer_address)` on VectorX, giving the deployer the upgrade permission. This succeeds because DEFAULT_ADMIN_ROLE is the admin of TIMELOCK_ROLE.
3. The attacker calls `upgradeTo(malicious_implementation)` using the newly granted TIMELOCK_ROLE. This replaces the entire VectorX contract logic with arbitrary code, enabling false attestations, fund theft from the bridge, or a complete bridge halt. The entire attack completes in two transactions with no timelock delay.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 8.4/10 (High) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:R/UI:N/S:C/C:N/I:H/A:H/CI:N/II:H/AI:H` |
| Scope | bridge |

### Scoring Rationale

No direct fund theft path has been proven, but bridge funds are at risk through a malicious upgrade (B:N). The attack is executed via direct calls on the Ethereum network (AV:N). Complexity is rated high because it requires compromising the deployer's private key (AC:H), and the attacker needs the deployer's specific credentials (PR:R). The scope is changed because impact extends beyond VectorX to the entire L2 and bridge ecosystem (S:C). Integrity impact is high because an arbitrary implementation replacement enables false attestations and completely bypasses the governance multisig (I:H, II:H). Availability impact is high because a single compromised key can halt the entire bridge, bypassing all governance protections (A:H, AI:H).

## Evidence

### On-Chain Verification

The following on-chain queries confirmed the vulnerability:

- `hasRole(DEFAULT_ADMIN_ROLE, 0xDEd...)` returns `true` -- deployer still holds admin
- `hasRole(TIMELOCK_ROLE, 0xDEd...)` returns `false` -- not yet granted, but grantable
- `getRoleAdmin(TIMELOCK_ROLE)` returns `0x00` (DEFAULT_ADMIN_ROLE) -- confirms admin can grant it
- `eth_getCode(0xDEd...)` returns `0x` -- confirms this is an EOA, not a contract
- `eth_getTransactionCount(0xDEd...)` returns `1107` -- actively used account

### Source Code

- [Guardian.s.sol](https://github.com/availproject/sp1-vector) -- deployment script contains commented-out code for revoking DEFAULT_ADMIN_ROLE from the deployer, confirming the revocation was intended but never executed

### PoC Testing

Exhaustive role verification across 3 roles and 2 principals confirmed that DEFAULT_ADMIN_ROLE is the only active role for the deployer. TIMELOCK_ROLE admin mapping to 0x00 was verified, confirming the grant-then-upgrade attack path.

References: poc_onchain_verification.md sections 8 and 9.

## Mitigations

No mitigations exist. The system is entirely dependent on the security of the deployer's private key. The Guardian.s.sol deployment script was supposed to revoke DEFAULT_ADMIN_ROLE from the deployer, but the revocation code is commented out and was never executed.
