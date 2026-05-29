# AVL-E02: Multisig Key Holder Triple Overlap (Gov + Pauser + SP1)

{% hint style="info" %}
**Severity**: Low (0.5/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

Severe key holder overlap across 3 multisigs. Pauser Multisig (0x1a5b...8930, 3/5): 4 of 5 owners are identical to Governance Multisig 1. SP1VerifierGateway (0xCafE...6878, 2/3): 1 owner (0x72Ff...4f54) is identical across Gov + Pauser. 0x72Ff26D9517324eEFA89A48B75c5df41132c4f54 participates in all 3 multisigs (Gov #4, Pauser #4, SP1 #2). Pauser threshold 3/5: with 4 overlapping members, 3 governance keys can trigger pause.

## Prerequisites

Governance multisig compromise automatically impacts Pauser + SP1

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.5/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:L/A:L/CI:N/II:L/AI:L` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | ExternalEntity |

### BVSS Rationale

B:N -- No financial impact. AV:P -- Multisig key compromise required. AC:H -- Multiple simultaneous key compromises. PR:R -- Signer credentials. S:U -- Internal governance issue. I:L/II:L -- Pause independence lost but not a direct attack path. A:L/AI:L -- Emergency response delay.

## Code References


### Onchain Evidence

- `getOwners(Pauser)=5명`
- `getThreshold(Pauser)=3`

### PoC Notes

- poc_onchain_verification.md §11

### Other References

- 4/5=Gov 동일
- RoleGranted 이벤트 역추적
- 0x72Ff 3중 중복

## Verification & Evidence

**Status**: Verified

Pauser Multisig discovered via RoleGranted event tracing. getOwners cross-analysis. 4/5 overlap + 0x72Ff triple participation confirmed.

**PoC References**: onchain-§11

## Mitigations

Separate thresholds per multisig (4/7, 3/5, 2/3).
