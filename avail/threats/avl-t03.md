# AVL-T03: AVAIL Token Mint via Bridge Upgrade -- Unlimited Minting Possible

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

AVAIL token (0xeeb4d8400aeefafc1b2953e0094134a887c76bd8) is immutable, but mint/burn authority resides in Bridge proxy (0x054f...). totalSupply ~791M AVAIL, owner() reverts (immutable). Via Bridge upgrade (24h timelock) or VectorX upgrade (NO timelock), a malicious upgrade could enable unlimited minting.

## Prerequisites

Bridge upgrade (TimelockController + 4/7) or VectorX upgrade (4/7 direct)

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | DataStore |

### BVSS Rationale

B:N -- No direct financial impact (multisig premise). AV:P -- 4/7 key compromise required. AC:H -- 24h timelock (Bridge) or 4/7 multisig (VectorX). PR:R -- Multisig signer or timelock proposer credentials. S:U -- Within token mint scope. I:H/II:M -- Unlimited minting possible but timelock/multisig protection exists.

## Code References


### Onchain Evidence

- `totalSupply(0xeeb4...)=~791M`
- `owner(0xeeb4...)=revert(immutable)`

### PoC Notes

- poc_onchain_verification.md §6

### Other References

- mint/burn=bridge only

## Verification & Evidence

**Status**: Verified

totalSupply, owner() revert, mint/burn authority limited to Bridge confirmed.

**PoC References**: onchain-§6

## Mitigations

Bridge: 24h timelock. VectorX: no timelock but 4/7 multisig.
