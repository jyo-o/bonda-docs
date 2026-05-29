# AVL-T01: VectorX Instant Upgrade (4/7 Multisig, NO Timelock)

{% hint style="info" %}
**Severity**: Low (2.5/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

Avail Multisig 1 (4/7, 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666) can instantly upgrade VectorX. EIP-1967 admin slot=0x0 (UUPS pattern, upgrade within implementation). Bridge has 24h timelock applied, but VectorX does not. TimelockedUpgradeable class provides only an AccessControl wrapper without actual timelock (see AVL-S01).

## Prerequisites

Obtain 4 of 7 signer keys from Avail Multisig 1

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.5/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:H/CI:N/II:M/AI:M` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | DataStore, Process |

### BVSS Rationale

B:N -- Direct financial impact uncertain. AV:P -- Obtaining 4/7 multisig keys requires physical/social engineering access. AC:H -- Simultaneous compromise of 4 of 7 signer keys. PR:R -- Multisig signer credentials. S:U -- Within VectorX upgrade scope. I:H/II:M -- Malicious upgrade can forge data roots but community detection possible. A:H/AI:M -- Bridge halt possible but multisig protection exists.

## Code References


### Onchain Evidence

- `storage admin_slot=0x0`

### PoC Notes

- poc_onchain_verification.md §2

### Other References

- L2BEAT: avail — no delay
- TimelockedUpgradeable.sol delay 로직 없음
- §4

## Verification & Evidence

**Status**: Verified

EIP-1967 admin slot=0x0 confirmed (UUPS). L2BEAT cross-verified. TimelockedUpgradeable source code: delay logic absence confirmed.

**PoC References**: onchain-§2, onchain-§4

## Mitigations

4/7 multisig threshold. However, no timelock.
