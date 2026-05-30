# CEL-D12: Nil Pointer Panic in GetProposal During Block Sync

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

The `GetProposal` function in celestia-core can trigger a nil pointer dereference panic when `getAllState` returns `cb=nil` with `has=true`. This occurs when a block exists in `BlockStore` but not in the proposal cache, breaking the function contract. The `syncData` path uses the return value and can trigger the crash, as confirmed by tests in PR #3060.

## Description

The root cause is in `getAllState`'s stored-block branch:

```go
// celestia-core/consensus/propagation/commitment_state.go:191
// @audit getAllState stored-block branch returns cb=nil with has=true
// @audit Function contract is broken: signals "found" via has=true while returning nil compact block
// @audit Returns (nil, cparts, bitarray, true) when block exists in BlockStore but not in proposal cache
```

```go
// celestia-core/consensus/propagation/commitment_state.go:95
// @audit GetProposal dereferences &cb.Proposal without nil check
// @audit Triggers nil pointer panic when cb is nil
```

The primary caller at `consensus/state.go:2920` discards the first return value using an underscore (`_`), so the panic does not occur on most code paths. However, the `syncData` path is vulnerable:

```go
// celestia-core/consensus/state.go:2929
// @audit syncData calls GetProposal and uses the return value
// @audit This path CAN trigger the nil pointer panic
```

The timing window occurs during normal block sync: when a block is written to `BlockStore` but before the proposal cache is populated with the corresponding compact block. A malicious peer could potentially increase the probability by manipulating block propagation timing.

## Proof of Concept

PR `celestia-core#3060` (OPEN, 2026-05-21) includes tests that confirm the panic can be triggered via the `syncData` path. The PR adds a nil guard to prevent the panic.

## Impact

Consensus node crash via nil pointer panic. The trigger requires specific sync timing that is difficult to exploit reliably but can occur during normal operation. A malicious peer could potentially increase the probability by manipulating block propagation timing to create the window between `BlockStore` write and proposal cache population.

### CVSS 3.1

**Score**: 5.9/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | A malicious peer can attempt to trigger the timing window via manipulated block propagation |
| AC (Attack Complexity) | H (High) | Requires hitting a specific timing window between BlockStore write and proposal cache population |
| PR (Privileges Required) | N (None) | No privileges required; any peer participating in block propagation can attempt to trigger the condition |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the crashing consensus node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | H (High) | Nil pointer panic crashes the consensus node, halting participation until restart |

## Recommendation

1. Merge PR #3060 which adds a nil guard to `GetProposal` to check for `nil` before dereferencing the compact block.
2. Fix the `getAllState` function contract so that `has=true` is never returned with a `nil` compact block, preventing the inconsistent state from propagating to callers.
