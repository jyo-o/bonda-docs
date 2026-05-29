# ETH-T05: Gloas Column Proof Verification

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: T (Tampering) · **Scope**: protocol · **Status**: partial
{% endhint %}

## Overview

Analysis of column proof verification mechanism in Gloas. Gloas is currently unscheduled with no immediate impact. Verification logic re-evaluation required upon activation.

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

Currently unscheduled. Verification mechanism must be complete before activation.
