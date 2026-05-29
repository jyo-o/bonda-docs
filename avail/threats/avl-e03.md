# AVL-E03: Deployer EOA Retains DEFAULT_ADMIN_ROLE -- Solo VectorX Upgrade Possible

{% hint style="info" %}
**Severity**: High (8.4/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX deployer EOA 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e still holds DEFAULT_ADMIN_ROLE (0x00). TIMELOCK_ROLE/GUARDIAN_ROLE have been revoked (false). However, since DEFAULT_ADMIN_ROLE is the admin of both roles, the deployer can single-handedly execute grantRole(TIMELOCK_ROLE, self) -> upgradeTo(malicious) in 2 transactions to take over VectorX. The deployment script (Guardian.s.sol) has the DEFAULT_ADMIN_ROLE revoke code commented out. Deployer is an EOA (code=0x), nonce=1107 (active account).

## Prerequisites

Deployer EOA private key compromise (1 key)

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 8.4/10 (High) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:R/UI:N/S:C/C:N/I:H/A:H/CI:N/II:H/AI:H` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | DataStore, Process |

### BVSS Rationale

B:N -- Direct fund theft path unproven but bridge funds at risk. AV:N -- Direct call from Ethereum network. AC:H -- Requires deployer EOA private key compromise. PR:R -- Deployer credentials. S:C -- Impact extends beyond VectorX to entire L2/Bridge. I:H/II:H -- Arbitrary implementation replacement -> false attestation, complete multisig bypass. A:H/AI:H -- Complete bridge halt possible; single key bypasses entire governance.

## Code References


### Onchain Evidence

- `hasRole(DEFAULT_ADMIN`
- `hasRole(TIMELOCK_ROLE`
- `getRoleAdmin(TIMELOCK_ROLE)=0x00`
- `code 0xDEd...=0x`
- `nonce 0xDEd...=1107`

### PoC Notes

- poc_onchain_verification.md §8

### Other References

- 0xDEd...)=true
- 0xDEd...)=false
- github.com/availproject/sp1-vector Guardian.s.sol revoke 주석처리

## Verification & Evidence

**Status**: Verified

3 roles x 2 principals exhaustive verification. DEFAULT_ADMIN=true for deployer confirmed. TIMELOCK_ROLE admin=0x00 confirmed. Guardian.s.sol source code: revoke commented out confirmed.

**PoC References**: onchain-§8, onchain-§9

## Mitigations

None -- entirely dependent on deployer key security. Guardian.s.sol revoke is commented out.
