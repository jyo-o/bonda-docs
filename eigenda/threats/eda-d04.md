# EDA-D04: Encoding Failure Permanently Marks Blob as Failed With No Fallback

{% hint style="info" %}
**Severity**: Low (0.6/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Overview

When the EigenDA encoder fails to process a blob, it retries up to 3 times with exponential backoff (2^i seconds). If all retries are exhausted, the blob transitions to a permanent `Failed` state with no alternative encoding path available. Once a blob reaches this state, it cannot be recovered or re-encoded.

Mainnet probe measurements found 32 Failed blobs out of 491,479 total (0.006%). All failures were from the same account (`0x41fa...`) during a mass dispersal event on 2026-05-14. A separate 8,307 blob sample showed a 0.024% failure rate (2 blobs), confirming that failures are rare and concentrated during high-load scenarios.

## Prerequisites

- Encoder failure or overload conditions. The encoder must fail on the initial attempt plus all 3 retries.

## Attack Scenario

1. An attacker or heavy user submits a large volume of blobs simultaneously, creating encoder overload conditions.
2. The encoder's processing queue grows beyond its capacity.
3. Some blobs fail the initial encoding attempt and enter the retry loop with exponential backoff.
4. After 4 total attempts (initial + 3 retries), the blob is permanently marked as `Failed`.
5. The submitter must re-submit the blob from scratch, as no fallback or alternative encoding path exists.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.6/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:R/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because there is no financial impact from encoding failures. Attack Complexity (AC) is High because this only occurs under encoder overload conditions, and the measured failure rate is just 0.024%. Privileges Required (PR) is Reserved because dispersal permission is needed to submit blobs. Availability impact (A) is Low because the 3-retry mechanism with exponential backoff handles most transient failures, and the impact is limited to individual blob failures without cascading effects.

## Evidence

### Source Code

- [`disperser/controller/encoding_manager.go:362-408`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/controller/encoding_manager.go#L362-L408) -- Retry logic with 3 retries and exponential backoff; blob transitions to `Failed` on exhaustion.

### On-Chain Verification

- Prober observed 32 Failed blobs out of 532,823 total (0.006%), all from account `0x41fa832f` on 2026-05-14.
- Separate 8,307 blob sample showed 0.024% failure rate (2 blobs).
- Total attempts corrected to 4 (initial + 3 retries).

### PoC Testing

- `poc/17-*/evidence.yaml` confirmed the failure behavior and rate.

**PoC References**: #15

## Mitigations

The encoder performs 3 retries with exponential backoff before marking a blob as Failed. This handles transient failures effectively, as demonstrated by the very low observed failure rate. However, there is no alternative encoding path or fallback mechanism for persistent failures. Adding a secondary encoder or a re-queue mechanism could improve resilience.
