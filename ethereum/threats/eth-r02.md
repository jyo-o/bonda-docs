# ETH-R02: Prysm DataColumnsByRange Rate Limit Bypass

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D (DoS) · **Status**: code\_review
{% endhint %}

## Summary

Prysm's `DataColumnsByRange` RPC handler charges a **constant cost of 1** to the rate limiter regardless of request size. In contrast, `DataColumnsByRoot` (serving the same role) correctly charges the actual number of requested columns. This asymmetry allows any **unauthenticated P2P peer** to send requests with large slot ranges and all 128 columns, bypassing the rate limit while amplifying the target node's DB lookup and I/O workload. The leaky bucket does accumulate post-hoc charges during streaming, so the impact is not "infinite exhaustion" but rather **"initial uncharged work + amplification."**

## Description

### Vulnerable Code -- ByRange Handler (constant charge)

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_range.go:22
// https://github.com/prysmaticlabs/prysm
const rateLimitingAmount = 1  // @audit ignores request size (count x columns), always 1

// :57
if err := s.rateLimiter.validateRequest(stream, rateLimitingAmount); // @audit passes with cost=1
// @audit heavy work begins after this point: slot block-range iteration, batcher setup, DB lookup
// @audit per-column charging happens later via add() during streaming -- guard is at the back end
```

### Correct Pattern -- ByRoot Handler (for comparison)

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_root.go:58
// https://github.com/prysmaticlabs/prysm
totalRequested := 0
for _, ident := range requestedColumnIdents {
    totalRequested += len(ident.Columns)  // @audit sums actual requested column count
}
if err := s.rateLimiter.validateRequest(stream, uint64(totalRequested)); // @audit actual cost
```

### Root Cause

**Work/charge ordering problem.** After the initial `validateRequest(1)` passes, heavy work begins. Per-column charging only accumulates during the streaming phase via `add()`. The guard is at the **back end rather than the front end** of the work, and the work between the first `validateRequest` and the first `add()` is unmetered.

### Attack Trigger Method

1. Connect as an unauthenticated P2P peer
2. Send a `DataColumnsByRange` request with `count=MAX_SLOTS (within DA window), columns=[0..127]`
3. Pass rate limit with cost=1, triggering DB lookups for all slots
4. Multiply with concurrent streams
5. `MaxRequestDataColumnSidecars (16384)` only limits **response volume**, not **work performed**

### Critical Limitation

The leaky bucket accumulates per-column charges during streaming, so subsequent requests from the same peer are eventually throttled. The DA window upper-bounds the slot range. Therefore, the impact is **"amplification of uncharged work between validateRequest and the first add()"**, not unlimited exhaustion.

### STRIDE Detail

| Category | Relevance | Analysis |
|----------|-----------|----------|
| **D -- DoS** | **Primary** | Rate limit bypass amplifies DB lookup and I/O, exhausting node CPU/disk resources |

## Proof of Concept

No exploit reproduction was conducted. A devnet measurement was not performed in this review. If conducted, the key metric would be "CPU cycles ratio vs. baseline" comparing ByRange (constant charge) against ByRoot (accurate charge) under identical load.

**Recommended test scenario:**

| Scenario | Load | Target | Purpose |
|----------|------|--------|---------|
| S1: ByRange max request | count=MAX, cols=128, xN streams | Prysm node CPU/IO | Prove rate limit bypass |
| S2: ByRoot same load (control) | Same column count | Same node | Prove accurate charging blocks the load |

## Impact

1. **Attacker connects as P2P peer** -- no authentication required, fully automatable
2. **Rate limit bypassed** -- large requests pass with cost=1
3. **Single Prysm node CPU/disk I/O exhausted** -- attestation and sync performance degraded
4. **Cascade:** At Prysm's market share (~19%), simultaneous attacks on multiple nodes could reduce attestation participation rates, potentially delaying finality (not a consensus split)

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

> Availability is scored as Low conservatively due to the leaky bucket's post-hoc throttling. If devnet measurement proves sustained exhaustion, upgrade to A:H (7.5).

## Recommendation

### Patch 1 -- Replace constant charge with actual cost + overflow protection

```go
// [Before]
const rateLimitingAmount = 1
// ...
if err := s.rateLimiter.validateRequest(stream, rateLimitingAmount); err != nil { /* ... */ }

// [After] -- remove const, compute actual cost in handler body
cols := uint64(len(req.Columns))
cost := cols * req.Count
if req.Count != 0 && cost/req.Count != cols { // @audit overflow detection -- treat as max
    cost = math.MaxUint64
}
if err := s.rateLimiter.validateRequest(stream, cost); err != nil { /* ... */ }
```

### Patch 2 -- Move charging before work

If possible, move the charge to **before the first `add()`** to adopt a "charge before work" structure. The uncharged work gap between `validateRequest` and the first `add()` is the core issue; eliminating this gap resolves it.

**Note:** Multiplying `len(Columns) (<=128) x req.Count (attacker-controlled uint64)` without overflow protection causes wraparound, making the cost small and **re-enabling the bypass**. Saturating arithmetic is required.
