# AVL-T02: Bridge 24h Timelock -- Relatively Safe, Limited Risk

{% hint style="info" %}
**Severity**: Low (0.3/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

Bridge upgrades route through TimelockController (0x45828180bbE489350D621d002968A0585406d487) with getMinDelay=86400 (24h). DEFAULT_ADMIN=TimelockController. TimelockController proposer/executor=Multisig 1 (0x7F2f...). Users can exit within 24h.

## Prerequisites

TimelockController proposer (Multisig 1, 4/7) key compromise + 24h wait

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.3/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:L/A:N/CI:N/II:L/AI:N` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | DataStore |

### BVSS Rationale

B:N -- No direct financial impact. AV:P -- 4/7 key compromise required. AC:H -- 4/7 + 24h wait. PR:R -- Proposer credentials. S:U -- Timelock limits impact scope. I:L/II:L -- User exit possible within 24h, limiting practical risk.

## Code References


### Onchain Evidence

- `hasRole(DEFAULT_ADMIN`
- `getMinDelay=86400`

### PoC Notes

- poc_onchain_verification.md §1

### Other References

- TimelockController)=true
- §5

## Verification & Evidence

**Status**: Verified

TimelockController DEFAULT_ADMIN confirmed. getMinDelay=86400 (24h) confirmed.

**PoC References**: onchain-§1, onchain-§5

## Mitigations

24h timelock -- user exit time guaranteed. 4/7 multisig threshold.
