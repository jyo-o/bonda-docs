# CEL-D15: blob.Subscribe Infinite Retry — CPU 100% Burn Without Backoff

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

The Subscribe method in celestia-node blob/service.go runs an infinite retry loop without time.Sleep when getAll fails. Unless ctx is cancelled, the pattern 'for { getAll(); if err==nil break }' consumes 100% CPU. If a malicious full node returns intermittent errors for a specific namespace's data requests, a light node subscribed to that namespace enters a tight busy-loop.

## Core Invariants Affected

`data_recoverability`

Light node CPU exhaustion stops DAS sampling, disabling DA verification for that node.

## Prerequisites

One malicious full node that can connect as a peer to the target light node.

## Attack Scenario

**Condition**: Light node has active subscription for a namespace where peers return intermittent errors

**Example**: for { blobs, err = s.getAll(ctx, header, []Namespace{ns}); if err == nil { break } } -- no sleep, no backoff.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Medium |
| Likelihood | Conditional (malicious full node + specific namespace subscriber) |
| Scope | implementation |
| Target | Process, Dataflow |
| Core Invariants | data_recoverability |

## Code References

- [`celestia-node/blob/service.go (Subscribe: infinite retry loop without backoff)`](https://github.com/celestiaorg/celestia-node/blob/main/blob/service.go)

## Verification & Evidence

**Status**: code_verified

celestia-node main branch blob/service.go Subscribe method code directly confirmed.

## Mitigations

Recommendations: (1) Add exponential backoff, (2) Max retry count, (3) time.Sleep between retries (minimum 100ms).
