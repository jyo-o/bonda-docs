# EDA-D04: Encoding Failure Transitions Blob to Failed (No Fallback Path)

{% hint style="info" %}
**Severity**: Low (0.6/10) · **STRIDE**: D · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

After 3 retries with exponential backoff (2^i seconds), encoder failure transitions blob to Failed state. No alternative encoding path exists. Probe measurements found 32 Failed blobs out of 491,479 total. All were from the same account (0x41fa...) during mass dispersal.

## Prerequisites

Encoder failure or overload

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.6/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:R/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process |

### BVSS Rationale

B:N -- No financial impact. AC:H -- Only occurs under encoder overload conditions; measured at 0.024%. PR:R -- Dispersal permission required. A:L/AI:L -- 3 retries + exponential backoff exist; limited to individual blob failures.

## Code References

### Source Code

- [`disperser/controller/encoding_manager.go:362-408`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/controller/encoding_manager.go#L362-L408)

### PoC Notes

- prober — Failed blobs: 32건 (전체 532
- poc/17-*/evidence.yaml [VERIFIED]

### Other References

- Prober: observed_blobs — Failed 32건
- 전부 account 0x41fa832f / 2026-05-14
- 823건 중 0.006%)

## Verification & Evidence

**Status**: Verified

8307 blob sample showed 0.024% Failed (2 blobs). Corrected to 4 attempts (initial + 3 retries).

**PoC References**: #15

## Mitigations

3 retries + exponential backoff.
