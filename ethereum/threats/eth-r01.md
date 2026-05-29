# ETH-R01: Blob/DataColumn Equivocation Detection Failure

{% hint style="info" %}
**Severity**: Low (1.1/10) · **STRIDE**: R (Repudiation) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

When a blob or data column with different content for the same (slot, index) pair is received, the second message is IGNORE-processed without generating slashing evidence. No mechanism exists to detect equivocation and preserve evidence. With Fulu making data columns the primary path, equivocation detection importance increases.

## Prerequisites

Malicious proposer distributing different blobs/columns for the same slot

## Attack Scenario

**Condition**: Different content blob/data column received for same (slot, index)

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.1/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:R/UI:N/S:U/C:N/CI:N/I:L/II:L/A:L/AI:L` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

*No specific code references provided.*

## Verification & Evidence

**Status**: code_verified

Confirmed IGNORE-only processing on equivocation, with no slashing evidence generation.

## Mitigations

Currently only IGNORE processing. Slashing evidence generation mechanism not implemented.
