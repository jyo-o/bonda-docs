# EDA-05: GetBlob Unauthenticated Access Relies Solely on Global Rate Limiting

{% hint style="warning" %}
**Severity**: High · **Category**: Operational Risk · **Status**: poc_verified
{% endhint %}

## Summary

The Relay's `GetBlob` endpoint has no authentication requirement, and the rate limiter lacks per-client fields, enforcing only a global limit. Any unauthenticated client can consume the shared rate limit budget, starving legitimate users. The root cause is the absence of per-client rate limiting and authentication on `GetBlob`, in contrast to `GetChunks` which requires operator authentication.

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

**Bandwidth charged before the cache lookup.** The bandwidth bucket is debited at the start of request handling, before the blob is fetched:

```go
// relay/server.go:245-250
// @audit RequestGetBlobBandwidth charges the global bucket BEFORE the cache lookup below
err = s.blobRateLimiter.RequestGetBlobBandwidth(uint32(len(data)))
if err != nil {
    return nil, err
}
data, err = s.blobProvider.GetBlob(ctx, blobKey)
// https://github.com/Layr-Labs/eigenda/blob/61019b4e9f91cbbb3dc05ed758674e4bdfeee20e/relay/server.go#L245-L250
```

Because the charge precedes the cache lookup, repeatedly requesting the same cached blob drains the shared global bandwidth bucket at near-zero backend cost to the attacker: there is no S3 fetch, yet the global budget is consumed on every call. An attacker therefore competes for the same bucket as legitimate clients while paying almost nothing for it.

## Proof of Concept

A bandwidth-starvation test (`TestPoCVariantABandwidthStarvation`) was run against the Relay `GetBlob` path at commit `61019b4e9f91cbbb3dc05ed758674e4bdfeee20e`. A single attacker issuing 6 requests per second for a cached blob ran concurrently with one legitimate victim issuing 1 request per second:

- The victim saw a 55% rejection rate (6 of 11 requests rejected) once the shared global bucket was contended.
- The attacker itself absorbed a 36% rejection rate (30 of 84) but still crowded the bucket, since cached requests cost the attacker no backend work.
- The test bucket was scaled down 20x; at production scale (1 MiB/s test vs 20 MiB/s production) the same starvation holds, only requiring proportionally more attacker throughput.

Separately, on-network checks confirmed the access asymmetry:

- Mainnet relay accepts unauthenticated `GetBlob` requests (returns `NotFound`, not `Unauthorized`).
- `GetChunks` requires operator authentication (returns `InvalidArgument`), confirming asymmetric access policies.

## Impact

A single abusive client can exhaust the global rate limit budget for all users by sending a high volume of unauthenticated `GetBlob` requests, degrading the read path for every other client equally. The bandwidth-starvation test showed a legitimate victim losing more than half of its requests (55% rejection) while the attacker spent almost no backend resources, because cached-blob reads are charged against the global bucket before the cache lookup. The impact is limited to read-path degradation, not data corruption or loss, and the global rate limit does provide a ceiling on total throughput. However, legitimate clients have no priority over attackers under the current global-only scheme. No authentication or privileges are required to mount this attack.

Affects the Liveness axis. As an operational condition rather than an exploitable defect, it is tracked as an Operational Indicator shown alongside the risk pentagon, not as a deduction from the structural score.

## Recommendation

1. Add per-client rate limiting to `GetBlob` to prevent a single client from exhausting the shared budget.
2. Require lightweight authentication (API key or client certificate) for `GetBlob` to match the authentication policy of `GetChunks`.
3. Implement priority queuing for authenticated clients to ensure legitimate users are served before anonymous traffic.
