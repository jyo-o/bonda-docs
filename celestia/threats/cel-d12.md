# CEL-D12: GetProposal Nil Pointer Panic — Node Crash via Block Sync Timing

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

GetProposal at celestia-core consensus/propagation/commitment_state.go:95 can trigger a nil pointer dereference panic when getAllState returns cb=nil, has=true. The stored-block branch of getAllState (line 190-196) returns (nil, cparts, bitarray, true) when the block exists in BlockStore but not in the proposal cache. The primary caller at consensus/state.go:2920 discards the first return value (_), so panic does not occur on most paths. However, the syncData path (state.go:2929) can trigger it, as confirmed in PR #3060 tests. The function contract itself is broken, creating panic risk for future callers.

## Core Invariants Affected

`consensus_liveness`

Potential for consensus node panic, but only triggers on specific sync paths. PR #3060 adds nil guard.

## Prerequisites

Can occur during normal operation. Intentional trigger: malicious peer induces proposal request immediately after block store write.

## Attack Scenario

**Condition**: Block exists in BlockStore but not in proposal cache during sync timing + syncData path entry

**Example**: getAllState returns (nil, cparts, bitarray, true) causing &cb.Proposal to panic.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Medium |
| Likelihood | Low (triggers only on specific sync timing; primary caller discards return value) |
| Scope | implementation |
| Target | Process |
| Core Invariants | consensus_liveness |

## Code References

- [`celestia-core/consensus/propagation/commitment_state.go:95 (GetProposal: &cb.Proposal nil deref)`](https://github.com/celestiaorg/celestia-core/blob/main/consensus/propagation/commitment_state.go#L95)
- [`celestia-core/consensus/propagation/commitment_state.go:191 (getAllState stored-block branch returns cb=nil, has=true)`](https://github.com/celestiaorg/celestia-core/blob/main/consensus/propagation/commitment_state.go#L191)
- [`celestia-core/consensus/state.go:2929 (syncData calls GetProposal)`](https://github.com/celestiaorg/celestia-core/blob/main/consensus/state.go#L2929)
- [PR #3060: 2026-05-21 OPEN, 'guard GetProposal against nil compact block'](https://github.com/celestiaorg/celestia-core/pull/3060)

## Verification & Evidence

**Status**: code_verified

celestia-core main branch commitment_state.go code confirmed. PR #3060 existence and open status confirmed via gh api.

## Mitigations

PR #3060 (open): adds nil guard. No defense before merge.
