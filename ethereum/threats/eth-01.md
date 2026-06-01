# ETH-01: Prysm DataColumnsByRange Rate Limit Bypass

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **Category**: Vulnerability · **Status**: verified
{% endhint %}

## Summary

Prysm's `DataColumnsByRange` RPC handler charges a constant cost of 1 to the rate limiter regardless of request size. The equivalent `DataColumnsByRoot` handler correctly charges the actual number of requested columns. This asymmetry allows any unauthenticated P2P peer to send requests with large slot ranges and all 128 columns, bypassing the rate limit while amplifying the target node's DB lookup and I/O workload.

## Description

The ByRange handler uses a hardcoded constant for rate limiting, while the ByRoot handler sums the actual requested column count:

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_range.go:22
// https://github.com/prysmaticlabs/prysm
const rateLimitingAmount = 1  // @audit ignores request size (count x columns), always 1

// :57
if err := s.rateLimiter.validateRequest(stream, rateLimitingAmount); // @audit passes with cost=1
// @audit heavy work begins after this point: slot block-range iteration, batcher setup, DB lookup
// @audit per-column charging happens later via add() during streaming -- guard is at the back end
```

For comparison, the ByRoot handler charges accurately:

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_root.go:58
// https://github.com/prysmaticlabs/prysm
totalRequested := 0
for _, ident := range requestedColumnIdents {
    totalRequested += len(ident.Columns)  // @audit sums actual requested column count
}
if err := s.rateLimiter.validateRequest(stream, uint64(totalRequested)); // @audit actual cost
```

After the initial `validateRequest(1)` passes, heavy work begins. Per-column charging only accumulates during the streaming phase via `add()`, meaning the guard is at the back end rather than the front end of the work. An attacker can connect as an unauthenticated P2P peer, send `count=MAX_SLOTS` with all 128 columns, and multiply with concurrent streams. The leaky bucket does accumulate post-hoc charges during streaming, so subsequent requests from the same peer are eventually throttled. The impact is amplification of uncharged work between `validateRequest` and the first `add()`, not unlimited exhaustion.

## Proof of Concept

No exploit reproduction was conducted. A devnet measurement was not performed in this review.

## Impact

An attacker connecting as a P2P peer can bypass the rate limit and exhaust a single Prysm node's CPU/disk I/O, degrading attestation and sync performance. At Prysm's market share (~19%), simultaneous attacks on multiple nodes could reduce attestation participation rates, potentially delaying finality.

### CVSS 3.1

**Score**: 5.3/10 (Medium, conservative)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Triggered via P2P message |
| AC | L (Low) | No special conditions required |
| PR | N (None) | Unauthenticated peer |
| UI | N (None) | Fully automated |
| S | U (Unchanged) | Impact limited to the targeted node's availability |
| C | N (None) | No confidentiality impact |
| I | N (None) | No integrity impact |
| A | L (Low) | Conservative; could be High (7.5) if exhaustion is proven via PoC |

## Recommendation

1. Replace the constant `rateLimitingAmount = 1` with actual cost calculation: `cols * req.Count` with overflow protection.
2. Move the charge to before the first `add()` to adopt a charge-before-work structure.
3. Ensure the cost multiplication uses saturating arithmetic to prevent uint64 wraparound from re-enabling the bypass.
