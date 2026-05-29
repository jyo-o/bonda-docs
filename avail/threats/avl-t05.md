# AVL-T05: KZG Trusted Setup (Filecoin PoT, 1-of-N Honest Assumption)

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: T · **Scope**: chain · **Status**: Unverified
{% endhint %}

## Overview

Avail KZG uses the Filecoin Powers of Tau ceremony (challenge_19, BLS12-381). Relies on the 1-of-N honest participant assumption. If all ceremony participants were dishonest, validity proof forgery would be possible, but the practical probability is extremely low.

## Prerequisites

All ceremony participants dishonest (1-of-N assumption violation)

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | chain |
| Target | DataStore |

### BVSS Rationale

B:N -- No direct financial impact. AV:N -- Network. AC:H -- Requires all ceremony participants to be dishonest (1-of-N assumption). PR:N -- Ceremony participant. S:U -- Within KZG verification scope. I:H/II:M -- Validity proof forgery theoretically possible but practical probability extremely low.

## Code References


### Other References

- Filecoin Powers of Tau challenge_19
- BLS12-381

## Verification & Evidence

**Status**: Unverified

SRS parameter source confirmation needed. Theoretical threat.

## Mitigations

1-of-N honest participant assumption -- Filecoin PoT ceremony had many participants.
