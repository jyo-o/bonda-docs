# EDA-D04: Encoding Failure Permanently Marks Blob as Failed With No Fallback

{% hint style="info" %}
**Severity**: Low (3.1/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

When the EigenDA encoder fails to process a blob, it retries up to 3 times with exponential backoff (2^i seconds). If all retries are exhausted, the blob transitions to a permanent `Failed` state with no alternative encoding path. The root cause is the absence of a fallback encoding mechanism or re-queue capability. Mainnet measurements found 32 Failed blobs out of 491,479 total (0.006%), all from the same account during a mass dispersal event, confirming failures are rare and concentrated during high-load scenarios.

## Description

The encoder retry and failure logic:

**Source**: [`disperser/controller/encoding_manager.go:362-408`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/controller/encoding_manager.go#L362-L408) -- Retry logic with 3 retries and exponential backoff; blob transitions to `Failed` on exhaustion.

The flow is:
1. Initial encoding attempt fails.
2. Up to 3 retries with exponential backoff (2^i seconds).
3. After 4 total attempts (initial + 3 retries), the blob is permanently marked as `Failed`.
4. No alternative encoding path or re-queue mechanism exists.
5. The submitter must re-submit the blob from scratch.

## Proof of Concept

### Results

- Prober observed 32 Failed blobs out of 532,823 total (0.006%), all from account `0x41fa832f` on 2026-05-14 during a mass dispersal event.
- Separate 8,307 blob sample showed 0.024% failure rate (2 blobs).
- Total attempts corrected to 4 (initial + 3 retries).
- `poc/17-*/evidence.yaml` confirmed the failure behavior and rate.

**PoC References**: #15

## Impact

Encoding failures result in permanent blob loss with no recovery path. The submitter must re-submit the blob from scratch. However, the measured failure rate is extremely low (0.006% to 0.024%), and failures are concentrated during high-load scenarios from single accounts. Individual blob failures do not cascade to affect other blobs or the protocol. The 3-retry mechanism with exponential backoff handles most transient failures effectively. Dispersal permission is required to submit blobs, limiting who can trigger the failure path.

### CVSS 3.1

**Score**: 3.1/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Blob dispersal occurs over the network |
| AC (Attack Complexity) | H (High) | Failures occur only under encoder overload conditions; measured failure rate is just 0.006% to 0.024% |
| PR (Privileges Required) | L (Low) | Dispersal permission is needed to submit blobs |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is limited to individual blob failures |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | N (None) | No data integrity impact |
| A (Availability) | L (Low) | The 3-retry mechanism handles most transient failures; impact is limited to individual blobs without cascading effects |

## Recommendation

1. Add a secondary encoder or failover encoding path to handle persistent failures.
2. Implement a re-queue mechanism that allows failed blobs to be retried after a longer cooldown period rather than permanently marking them as failed.
3. Add monitoring and alerting for encoding failure rates to detect encoder overload conditions early.
