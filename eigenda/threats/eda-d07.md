# EDA-D07: GetBlob Unauthenticated Access Relies Solely on Global Rate Limiting

{% hint style="info" %}
**Severity**: Low (2.0/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Overview

The Relay's `GetBlob` endpoint has no authentication requirement, and the rate limiter lacks per-client fields, enforcing only a global limit. This means any unauthenticated client can consume the shared rate limit budget, potentially starving legitimate users. Mainnet testing confirmed that `GetBlob` accepts unauthenticated access, returning `NotFound` (not `Unauthorized`) for non-existent blob keys.

Over a 7-day observation period, 31 instances of HTTP 429 (Too Many Requests) were observed in retrieval probes, demonstrating that the global rate limit is being reached in practice and affecting all clients equally. In contrast, `GetChunks` requires operator authentication and returns `InvalidArgument` when called without credentials, revealing an asymmetric authentication policy between the two retrieval endpoints.

## Prerequisites

- Access to the Relay gRPC endpoint, which is publicly reachable.

## Attack Scenario

1. An attacker connects to the Relay at `relay-0-mainnet-ethereum.eigenda.xyz:443` without any authentication credentials.
2. The attacker sends a high volume of `GetBlob` requests, consuming the global rate limit budget.
3. Legitimate clients begin receiving 429 (Too Many Requests) responses as the shared rate limit is exhausted.
4. Blob retrieval service quality degrades for all users, even though the attacker accesses only a read-only path.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.0/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:M` |
| Scope | Rollup |

### Scoring Rationale

Blockchain Impact (B) is None because there is no financial impact from this read-path abuse. Attack Vector (AV) is Network because the Relay endpoint is publicly accessible without authentication. Attack Complexity (AC) is Low since the unauthenticated access was directly confirmed on mainnet. Availability impact (A) is Low because this is a read-only path and the rate limiter does provide some protection. Availability Infrastructure impact (AI) is Medium because legitimate users also receive 429 errors when the global rate limit is reached, as observed in 31 incidents over 7 days.

## Evidence

### On-Chain Verification

- `grpcurl relay-0-mainnet-ethereum.eigenda.xyz:443 GetBlob` returned `NotFound` (not `Unauthorized`), confirming unauthenticated access.
- `grpcurl GetChunks` returned `InvalidArgument` (auth required), confirming asymmetric authentication policies.

### Source Code

- [`relay/limiter/blob_rate_limiter.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/relay/limiter/blob_rate_limiter.go) -- Rate limiter has no per-client field, only global limits.

### PoC Testing

- `grpcurl` without auth headers achieved 50/50 retrieval success rate.
- Prober observed 31 rate-limit 429 errors over 7 days, reduced to 0 in a subsequent 24-hour window.
- 8 failures out of 122,745 total retrieval probes.
- `poc/08-*/evidence.yaml` confirmed the finding.

**PoC References**: #07

## Mitigations

A global rate limit exists and provides basic protection against abuse. However, the absence of per-client rate limiting means a single abusive client can exhaust the budget for all users. Adding per-client rate limiting or requiring lightweight authentication for `GetBlob` would address this asymmetry.
