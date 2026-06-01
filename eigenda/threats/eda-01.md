# EDA-01: Unauthenticated GetChunks Cold-Miss Amplification Exhausts Operator CPU

{% hint style="warning" %}
**Severity**: High (8.6/10) · **Likelihood**: Very High · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

The operator Retrieval `GetChunks` endpoint can be driven to exhaust node CPU by an unauthenticated remote attacker through the combination of two defects. The gRPC interceptor passes every method except `StoreChunks`, so the Retrieval path enforces no authentication and no rate limit. On the cold-miss path, a LittDB lookup that finds no value returns immediately without debiting any rate-limit token. Together these let an attacker generate random 32-byte blob keys and call `GetChunks` repeatedly, triggering a `CacheAwareGet` on every request while never consuming a rate-limit token and never authenticating.

## Description

```mermaid
sequenceDiagram
    participant A as Attacker
    participant I as gRPC Interceptor
    participant S as validatorStore
    participant DB as LittDB
    A->>I: GetChunks(random 32-byte blobKey)
    Note over I: FullMethod != StoreChunks
    I->>S: pass through (no auth, no rate limit)
    S->>DB: CacheAwareGet(bundleKey)
    DB-->>S: exists = false
    Note over S: cold miss returns nil, no token debited
    S-->>A: not found
    A->>I: repeat at line rate
    Note over S,DB: CPU and disk I/O consumed each call;<br/>cold-read tokens never decrease
```

The vulnerability requires both defects; neither alone is exploitable from outside without privileges.

**Defect 1 — Retrieval path is uncovered by the interceptor.** The interceptor authenticates and rate-limits only `StoreChunks`, returning early for every other method, so all Retrieval calls reach the handler with no authentication and no rate limit.

```go
// node/grpc/middleware/storechunks_interceptor.go:51-53
// @audit any method other than StoreChunks bypasses auth and rate limiting on the Retrieval path
// https://github.com/Layr-Labs/eigenda/blob/61019b4/node/grpc/middleware/storechunks_interceptor.go
if info == nil || info.FullMethod != validatorpb.Dispersal_StoreChunks_FullMethodName {
    return handler(ctx, req)
}
```

**Defect 2 — cold miss returns without debiting tokens.** The store checks the cold-read limiter, but when the lookup finds no value it returns `nil` before any token is reserved, so a missing key costs the attacker nothing against the rate limiter.

```go
// node/validator_store.go:262-274
// @audit a random blob key yields exists=false and returns with no token debit, so cold reads are never throttled
// https://github.com/Layr-Labs/eigenda/blob/61019b4/node/validator_store.go
coldReadsExhausted := s.coldReadRateLimiter.Tokens() <= 0
bundle, exists, hot, err := s.chunkTable.CacheAwareGet(bundleKey, coldReadsExhausted)
if err != nil {
    return nil, false, fmt.Errorf("failed to get bundle: %v", err)
}
if exists && bundle == nil {
    return nil, false, fmt.Errorf("cold read rate limit exhausted")
}
if !exists {
    return nil, false, nil // returns before reserving any token
}
```

An attacker sends a 32-byte random blob key to `GetChunks`, producing a cold miss. Each request invokes `CacheAwareGet` and spends CPU and disk I/O, but Defect 2 leaves the rate-limit tokens untouched, so Defect 1 allows the unauthenticated call to repeat without bound.

## Proof of Concept

Reproduction was performed on an `inabox` local deployment of EigenDA at master commit `61019b4`, with the target operator running on a GCP `n2-standard-16` host of 16 vCPU and 64 GB, matching the Large operator class in the published system requirements.

- **Single request**: `grpcurl` to `validator.Retrieval/GetChunks` with a random key returns `Internal: failed to get chunks: not found`, confirming the cold-miss path is reached without authentication.
- **S3 — client max, 60 s**: at 82,029 requests per second the EigenDA process averaged 447.97 percent CPU with a peak of 463 percent.
- **S4 — client max, 10 min sustained**: at 83,490 requests per second the process averaged 458.35 percent CPU with a peak of 469 percent.
- **Asymmetry**: a single attacker consumed roughly 4.5 cores while client-side resource use converged toward zero. A 4 vCPU operator is fully saturated by one attacker; a 16 vCPU operator absorbs about 28 percent from one attacker and reaches saturation under parallel attackers.

See [Verification Evidence](../evidence.md#getchunks-cold-miss-cpu-exhaustion-eda-01) for the full reproduction environment, commands, and measurements.

## Impact

The attack targets the certificate verification threshold. The EigenDA certificate verifier requires signatures from 67 percent of stake, so saturating enough operators to pull the signing-stake fraction below that threshold halts certificate issuance for new batches. An L2 rollup that relies on EigenDA then has to pause sequencing or fall back to the more expensive L1 calldata path. The cost is borne almost entirely by the operators: a single unauthenticated attacker consumes about 4.5 cores while spending negligible client-side resources, the defining shape of an asymmetric denial-of-service condition.

### CVSS 3.1

**Score**: 8.6/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | `GetChunks` is reached over gRPC |
| AC (Attack Complexity) | L (Low) | Generating random blob keys and calling the endpoint is trivial |
| PR (Privileges Required) | N (None) | The Retrieval path requires no authentication |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | C (Changed) | Exhausting operators degrades certificate issuance relied on by downstream rollups |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | H (High) | Operator CPU saturation can drive signing stake below the certificate threshold |

## Recommendation

1. Attach a Retrieval-specific interceptor that applies a per-source-IP token bucket and a global limiter to all methods on the Retrieval listener. Retrieval is a public path, so the limiter bounds caller cost rather than authenticating callers.
2. In `getChunksLittDB`, reject cold reads before the lookup when no cold token remains, and debit a fixed cost on a cold miss so that requests for non-existent keys consume tokens and cannot be repeated without bound.
