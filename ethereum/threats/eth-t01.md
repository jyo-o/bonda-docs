# ETH-T01: Blob Fee Denominator Fork-dependent Formula

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: T (Tampering) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

In BPO2, updateFraction is set to 11684671. The blob fee calculation formula uses different denominators depending on the fork. Code paths confirmed and covered by consensus-spec-tests.

## Prerequisites

*None specified.*

## Attack Scenario

*No specific attack scenario detailed.*

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:L/II:L/A:N/AI:N` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

*No specific code references provided.*

## Verification & Evidence

**Status**: code_verified

Confirmed BPO2 updateFraction=11684671 setting and fork-dependent formula.

## Mitigations

Fork-specific fee calculation formulas are covered by consensus-spec-tests.
