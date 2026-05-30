# CEL-D12: Nil Pointer Panic in GetProposal During Block Sync

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

The GetProposal function in celestia-core at consensus/propagation/commitment_state.go line 95 can trigger a nil pointer dereference panic. This happens when getAllState returns cb=nil with has=true, and the caller attempts to access &cb.Proposal on the nil value.

The root cause is in getAllState's stored-block branch (lines 190-196). When a block exists in BlockStore but not in the proposal cache, getAllState returns (nil, cparts, bitarray, true). The function contract is broken because it signals "found" via has=true while returning a nil compact block.

The primary caller at consensus/state.go line 2920 discards the first return value using an underscore, so the panic does not occur on most code paths. However, the syncData path at state.go line 2929 does use the return value and can trigger the panic, as confirmed by tests in PR #3060. The broken function contract also creates risk for any future callers.

## Prerequisites

- Can occur during normal node operation at specific sync timing windows
- Intentional trigger: a malicious peer could induce a proposal request immediately after a block store write completes but before the proposal cache is populated

## Attack Scenario

1. A block is written to BlockStore during normal sync operations.
2. Before the proposal cache is populated with the corresponding compact block, a syncData call is triggered.
3. syncData calls GetProposal, which calls getAllState.
4. getAllState finds the block in BlockStore but not in the proposal cache, returning (nil, cparts, bitarray, true).
5. GetProposal attempts to dereference &cb.Proposal on the nil compact block, causing a panic.
6. The consensus node crashes and must be restarted.

## Impact

Consensus node crash via nil pointer panic. The trigger requires specific sync timing that is difficult to exploit reliably, but can occur during normal operation. A malicious peer could potentially increase the probability by manipulating block propagation timing.

## Evidence

### Source Code

- `celestia-core/consensus/propagation/commitment_state.go:95` -- GetProposal dereferences &cb.Proposal without nil check
- `celestia-core/consensus/propagation/commitment_state.go:191` -- getAllState stored-block branch returns cb=nil with has=true
- `celestia-core/consensus/state.go:2929` -- syncData calls GetProposal and uses the return value
- PR celestia-core#3060 (OPEN, 2026-05-21): adds nil guard to prevent the panic

## Mitigations

PR #3060 (open) adds a nil guard to GetProposal. Until this PR is merged, there is no defense against this panic. The fix is straightforward: check for nil before dereferencing the compact block.
