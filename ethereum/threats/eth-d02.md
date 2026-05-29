# ETH-D02: Reconstruction Failure Discards All Verified Columns (Lighthouse)

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

In Lighthouse overflow_lru_cache.rs L1360-1396, when data column reconstruction fails, a single bad column causes all 64+ already-verified valid columns to be discarded, requiring O(N/2) scale re-download. With Fulu making reconstruction the core DA mechanism (primary path), impact is elevated.

## Prerequisites

Malicious peer intentionally propagating bad data columns

## Attack Scenario

**Condition**: One or more bad columns present during data column reconstruction

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:N/II:N/A:M/AI:M` |
| Likelihood | Medium |
| Scope | protocol |
| Target | Process |

## Code References

- [`lighthouse/overflow_lru_cache.rs:1360-1396`](https://github.com/sigp/lighthouse/blob/main/overflow_lru_cache.rs#L1360-L1396)

## Verification & Evidence

**Status**: code_verified

Confirmed in Lighthouse overflow_lru_cache.rs that reconstruction failure discards all columns. PRIMARY PATH in Fulu.

## Mitigations

LRU cache eviction provides memory bounding. However, no mechanism to preserve verified columns exists.
