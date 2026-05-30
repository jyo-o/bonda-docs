# ETH-E01: Reconstruction Failure Mode Inconsistency Across Clients

{% hint style="info" %}
**Severity**: Medium (5.4/10) · **STRIDE**: E (Elevation of Privilege) · **Status**: code_verified
{% endhint %}

## Summary

Lighthouse and Prysm handle data column reconstruction failures in fundamentally different ways: Lighthouse deletes all columns for the affected slot, while Prysm marks reconstructed columns as verified without re-verification. This behavioral divergence means the same failure event produces contradictory outcomes — Lighthouse reports data as unavailable while Prysm treats potentially corrupted data as verified. This violates a core consensus invariant: all honest nodes should reach the same conclusion about data availability.

## Description

The reconstruction failure path diverges between the two major consensus clients.

**Case #1: Lighthouse (conservative — delete all)**

```rust
// @audit — Lighthouse deletes all columns on reconstruction failure
// On reconstruction failure:
//   → ALL columns for the slot evicted from cache
//   → Includes previously verified valid columns
//   → Node reports data as UNAVAILABLE
//   → Initiates full re-download from network
```

**Case #2: Prysm (permissive — trust reconstructions)**

```
# @audit — Prysm marks unverified reconstructions as verified
# On reconstruction failure:
#   → Reconstructed columns marked as VERIFIED without re-check
#   → Node reports data as AVAILABLE
#   → Potentially corrupted data treated as trustworthy
```

With the Fulu fork, data column reconstruction becomes the primary mechanism for data availability, elevating this from an edge-case recovery path to a core protocol function. The opposing failure modes mean the same network event produces contradictory outcomes across client implementations, threatening both consensus safety and data recoverability.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

After a reconstruction failure triggered by a corrupted column, Lighthouse nodes see the data as unavailable and initiate re-download, while Prysm nodes treat potentially corrupted data as verified and available. This creates a network-wide split view that propagates to attestation behavior: Lighthouse validators may vote against data availability while Prysm validators vote in favor, creating conflicting consensus signals. The inconsistency affects two core invariants — consensus safety (nodes disagree on data availability) and data recoverability (corrupted data may be served as verified).

### CVSS 3.1
**Score**: 5.4/10 (Medium)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Corrupted column injected through the network triggers divergent behavior |
| AC | H (High) | Corrupted column must pass initial validation and trigger reconstruction failure |
| PR | N (None) | Any peer or malicious proposer can inject a corrupted column |
| UI | N (None) | No user interaction needed |
| S | C (Changed) | Inconsistency crosses client trust boundaries, affecting network-wide consensus |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Prysm treats unverified reconstructions as verified, compromising data integrity |
| A | L (Low) | Lighthouse forces unnecessary re-downloads; network inconsistency can delay finality |

## Recommendation

1. **Define unified reconstruction failure semantics in the consensus specification**: The specification should explicitly define expected client behavior on reconstruction failure to prevent implementation-level divergence.
2. **Preserve verified columns while requiring re-verification of reconstructed columns**: The recommended behavior is to retain individually verified columns while requiring re-verification of any columns produced during a failed reconstruction — combining Lighthouse's safety with Prysm's efficiency.
3. **Add cross-client integration tests for reconstruction failure**: Implement multi-client test scenarios that verify consistent behavior under reconstruction failure conditions, ensuring both clients reach the same data availability conclusion.
