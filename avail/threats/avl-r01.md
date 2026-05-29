# AVL-R01: Slashing Infrastructure Exists but Not Triggered in 688 Eras

{% hint style="info" %}
**Severity**: Low (0.3/10) · **STRIDE**: R · **Scope**: chain · **Status**: Verified
{% endhint %}

## Overview

Avail NPoS slashing infrastructure exists in code but has never been triggered. Runtime metadata has 67 references to 'slash'. SlashDeferDuration=27 eras, BondingDuration=28 eras, SessionsPerEra=6. ActiveEra=688 (long-running). UnappliedSlashes(era=688)=empty (not triggered). Zero slashing events across 688 eras means no practical sanctions for validator misbehavior.

## Prerequisites

Internal validator behavior concern -- not a direct external attack

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.3/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:L/PR:R/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Likelihood | Unrated |
| Scope | chain |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:P -- Internal validator behavior concern. AC:L -- Non-triggering is the permanent state. PR:R -- Validator credentials. S:U -- Within incentive scope. A:L/AI:L -- Indirect incentive weakening impact.

## Code References


### Onchain Evidence

- `state_getStorage ActiveEra=688`
- `UnappliedSlashes(688)=null`

### PoC Notes

- poc_onchain_verification.md §10

### Other References

- Runtime metadata 'slash' 67건

## Verification & Evidence

**Status**: Verified

ActiveEra SCALE decode=688. UnappliedSlashes=null (empty). Runtime constants confirmed.

**PoC References**: onchain-§10

## Mitigations

Slashing infrastructure code exists. BondingDuration=28 eras.
