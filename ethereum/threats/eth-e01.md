# ETH-E01: Reconstruction Failure Mode Inconsistency (Lighthouse vs. Prysm)

{% hint style="info" %}
**Severity**: High (8.2/10) · **STRIDE**: E (Elevation of Privilege) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

Lighthouse deletes all columns on reconstruction failure, while Prysm marks reconstructed columns as verified without re-verification. This cross-client behavioral inconsistency can cause network-level consensus issues. With Fulu making reconstruction the core DA mechanism (primary path), impact is elevated.

## Prerequisites

Receipt of bad data columns that trigger reconstruction failure

## Attack Scenario

**Condition**: Data column reconstruction failure occurs

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 8.2/10 (High) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:C/C:N/CI:N/I:M/II:M/A:M/AI:M` |
| Likelihood | Medium |
| Scope | protocol |
| Target | Process |

## Code References

*No specific code references provided.*

## Verification & Evidence

**Status**: code_verified

LH: deletes all columns. Prysm: marks reconstructed columns as verified without re-verification. PRIMARY PATH in Fulu -- reconstruction is a core DA mechanism.

## Mitigations

Each client handles failure independently. However, cross-client consistency is absent.
