# ETH-T02: KZG Trusted Setup File Replacement

{% hint style="info" %}
**Severity**: Medium (4.2/10) · **STRIDE**: T (Tampering) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

The KZG trusted setup file is protected by go:embed + sync.Once. An attacker would need local filesystem access to replace it. Since the file is embedded at build time, runtime replacement is impossible.

## Prerequisites

Access to the build environment or binary distribution chain

## Attack Scenario

**Condition**: Local filesystem access required

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 4.2/10 (Medium) |
| BVSS Vector | `B:N/AV:P/AC:H/PR:R/UI:N/S:C/C:N/CI:N/I:H/II:H/A:N/AI:N` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

*No specific code references provided.*

## Verification & Evidence

**Status**: code_verified

Confirmed go:embed + sync.Once protection mechanism. Runtime file replacement impossible.

## Mitigations

go:embed embeds the file at build time + sync.Once prevents runtime re-initialization.
