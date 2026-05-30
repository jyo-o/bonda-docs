# EDA-D07: GetBlob Unauthenticated Access Relies Solely on Global Rate Limiting

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

The Relay's `GetBlob` endpoint has no authentication requirement, and the rate limiter lacks per-client fields, enforcing only a global limit. Any unauthenticated client can consume the shared rate limit budget, starving legitimate users. The root cause is the absence of per-client rate limiting and authentication on `GetBlob`, in contrast to `GetChunks` which requires operator authentication. Over a 7-day observation period, 31 instances of HTTP 429 (Too Many Requests) were observed, demonstrating the global rate limit is reached in practice.

## Description

The `GetBlob` endpoint exhibits two deficiencies.

**No authentication.** Mainnet testing confirmed that `GetBlob` accepts unauthenticated access. Calling the endpoint without credentials returns `NotFound` for non-existent blob keys, not `Unauthorized`. This means the server does not check caller identity at all.

**Global-only rate limiting.** The `BlobRateLimiter` struct contains only global operation and bandwidth limiters. There is no per-client map, client identifier field, or any mechanism to distinguish between callers:

```go
// relay/limiter/blob_rate_limiter.go
// @audit No per-client map or client identifier — rate limiting is purely global
type BlobRateLimiter struct {
    config             *Config
    opLimiter          *rate.Limiter      // global operation limiter
    bandwidthLimiter   *rate.Limiter      // global bandwidth limiter
    operationsInFlight int
    relayMetrics       *metrics.RelayMetrics
    lock               sync.Mutex
}
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/relay/limiter/blob_rate_limiter.go
```

In contrast, `GetChunks` requires operator authentication and returns `InvalidArgument` when called without credentials. This creates an asymmetric authentication policy between the two retrieval endpoints.

## Proof of Concept

Exploitation testing was conducted against the Relay `GetBlob` endpoint. Detailed reproduction steps and measurements will be added upon completion of the vulnerability report.

- Mainnet relay confirmed to accept unauthenticated `GetBlob` requests (returns `NotFound`, not `Unauthorized`)
- `GetChunks` requires operator authentication (returns `InvalidArgument`), confirming asymmetric access policies
- Prober observed 31 rate-limit 429 errors over a 7-day period

## Impact

A single abusive client can exhaust the global rate limit budget for all users by sending a high volume of unauthenticated `GetBlob` requests. This was confirmed by 31 HTTP 429 errors observed over a 7-day period affecting all clients equally. The impact is limited to read-path degradation (not data corruption or loss), and the global rate limit does provide a ceiling on total throughput. However, legitimate clients have no priority over attackers under the current global-only scheme. No authentication or privileges are required to mount this attack.

### CVSS 3.1

**Score**: 5.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | The Relay endpoint is publicly accessible without authentication |
| AC (Attack Complexity) | L (Low) | Unauthenticated access was directly confirmed on mainnet |
| PR (Privileges Required) | N (None) | No authentication required for `GetBlob` |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the Relay read path |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | N (None) | Read-only path; no data integrity impact |
| A (Availability) | L (Low) | Read-only path with global rate limit providing some protection; 429 errors observed but not catastrophic |

## Recommendation

1. Add per-client rate limiting to `GetBlob` to prevent a single client from exhausting the shared budget.
2. Require lightweight authentication (API key or client certificate) for `GetBlob` to match the authentication policy of `GetChunks`.
3. Implement priority queuing for authenticated clients to ensure legitimate users are served before anonymous traffic.
