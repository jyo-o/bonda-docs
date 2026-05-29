# AVL-E04: Technical Committee Runtime Upgrade (5/5 or 5/7 Consensus)

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: E · **Scope**: chain · **Status**: Verified
{% endhint %}

## Overview

The Technical Committee can upgrade the mainnet runtime with 5/5 or 5/7 consensus. Transparency Report 16 documents actual usage (block #1,095,300): a 5/5 consensus TC runtime upgrade was applied to fix a send_message logic bug. Full-scope impact: consensus rule changes, staking parameter changes, etc.

## Prerequisites

Obtain 5 of 7 Technical Committee member keys

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.7/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:C/C:N/I:H/A:H/CI:N/II:M/AI:M` |
| Likelihood | Unrated |
| Scope | chain |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:P -- TC 5/7 member key compromise requires physical/social engineering access. AC:H -- Requires 5/7 consensus. PR:R -- TC member credentials. S:C -- Chain-wide consensus rule changes. I:H/II:M -- Arbitrary staking/finality rule changes possible but detectable via Transparency Reports. A:H/AI:M -- Chain halt possible but strict TC consensus requirement.

## Code References


### PoC Notes

- 문서 기반 검증

### Other References

- Avail Forum Transparency Report 16 — block #1
- 095
- 300에서 5/5 합의로 실사용

## Verification & Evidence

**Status**: Verified

Avail Forum Transparency Report 16 confirms TC runtime upgrade usage. block #1,095,300.

**PoC References**: doc-TR16

## Mitigations

Requires 5/5 or 5/7 consensus. Transparency Reports are published.
