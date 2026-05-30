# EDA-D07: GetBlob Unauthenticated Access Relies Solely on Global Rate Limiting

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

The Relay's `GetBlob` endpoint has no authentication requirement, and the rate limiter lacks per-client fields, enforcing only a global limit. Any unauthenticated client can consume the shared rate limit budget, starving legitimate users. The root cause is the absence of per-client rate limiting and authentication on `GetBlob`, in contrast to `GetChunks` which requires operator authentication. Over a 7-day observation period, 31 instances of HTTP 429 (Too Many Requests) were observed, demonstrating the global rate limit is reached in practice.

## Description

The `GetBlob` endpoint exhibits two deficiencies:

**No authentication**: Mainnet testing confirmed that `GetBlob` accepts unauthenticated access, returning `NotFound` (not `Unauthorized`) for non-existent blob keys.

**Global-only rate limiting**: The rate limiter has no per-client field, only global limits.

**Source**: [`relay/limiter/blob_rate_limiter.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/relay/limiter/blob_rate_limiter.go) -- Rate limiter has no per-client field, only global limits.

In contrast, `GetChunks` requires operator authentication and returns `InvalidArgument` when called without credentials, revealing an asymmetric authentication policy between the two retrieval endpoints.

## Proof of Concept

### Reproduction

- `grpcurl relay-0-mainnet-ethereum.eigenda.xyz:443 GetBlob` returned `NotFound` (not `Unauthorized`), confirming unauthenticated access.
- `grpcurl GetChunks` returned `InvalidArgument` (auth required), confirming asymmetric authentication policies.
- `grpcurl` without auth headers achieved 50/50 retrieval success rate.

### Results

- Prober observed 31 rate-limit 429 errors over 7 days, reduced to 0 in a subsequent 24-hour window.
- 8 failures out of 122,745 total retrieval probes.
- `poc/08-*/evidence.yaml` confirmed the finding.

**PoC References**: #07

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
