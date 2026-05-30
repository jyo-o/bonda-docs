# ETH-D02: Reconstruction Failure Discards All Verified Columns

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D (Denial of Service) · **Status**: code_verified
{% endhint %}

## Summary

The Lighthouse consensus client discards all data columns for a slot when reconstruction fails, including the 64 or more columns that were already individually verified as valid. This all-or-nothing failure mode, found in `overflow_lru_cache.rs` at lines 1360-1396, creates an amplification vector where a single malicious column forces a full re-download of approximately half the total columns for the affected slot.

## Description

When data column reconstruction fails due to a single bad column, the Lighthouse implementation evicts the entire column set for the affected slot from cache.

```rust
// @audit — reconstruction failure discards all columns including verified ones
// Lighthouse: overflow_lru_cache.rs, lines 1360-1396
// On reconstruction failure:
//   → ALL columns for the slot are evicted from cache
//   → This includes 64+ individually verified valid columns
//   → No mechanism to selectively preserve verified columns
//   → Node must re-download ~N/2 columns from network
```

With the Fulu fork, data column reconstruction becomes the primary mechanism for data availability, making this a core path rather than an edge case. An attacker who can inject one corrupted column forces the victim node to perform O(N/2) additional network requests, wasting bandwidth and delaying data availability confirmation. The attack can be repeated across multiple slots for sustained impact.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

A single corrupted data column triggers re-download of approximately half the total columns for the affected slot. Repeated across multiple slots, this causes sustained bandwidth waste and delayed data availability confirmation. The amplification factor is significant: one bad column causes O(N/2) additional network requests. With reconstruction as the primary mechanism in Fulu, this directly impacts timely data availability confirmation.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Corrupted columns propagated through PeerDAS network |
| AC | H (High) | Corrupted column must pass initial validation checks to reach reconstruction |
| PR | N (None) | Any peer can propagate data columns |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Impact limited to the Lighthouse node performing reconstruction |
| C | N (None) | No confidentiality impact |
| I | N (None) | No integrity impact; attack targets availability only |
| A | L (Low) | Re-download overhead and delayed data availability confirmation |

## Recommendation

1. **Selectively preserve verified columns on reconstruction failure**: Retain individually verified columns and only discard columns produced during the failed reconstruction attempt, reducing re-download requirements from O(N/2) to just the specific bad column.
2. **Identify and exclude the bad column before reattempt**: Implement logic to identify which specific column caused the reconstruction failure and exclude it from subsequent attempts, reusing the valid columns already cached.
3. **Maintain LRU cache eviction for memory bounding**: The LRU cache eviction mechanism for overall memory management should remain in place, but should not be triggered by reconstruction failure for valid columns.
