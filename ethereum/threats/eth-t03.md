# ETH-T03: Gloas Data Column Inclusion Proof Omission

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: T (Tampering) · **Scope**: protocol · **Status**: partial
{% endhint %}

## Overview

In Gloas (future feature), data column inclusion proofs are omitted by design. Gloas is currently unscheduled, so there is no immediate impact. Re-evaluation required when Gloas is activated.

## Prerequisites

Gloas fork must be scheduled and activated

## Attack Scenario

**Condition**: When Gloas fork is activated

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:M/II:M/A:N/AI:N` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

*No specific code references provided.*

## Verification & Evidence

**Status**: partial

Gloas-related code paths confirmed. Currently unscheduled.

## Mitigations

Currently unscheduled. Proof mechanism implementation required before activation.
