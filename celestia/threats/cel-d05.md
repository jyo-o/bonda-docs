# CEL-D05: ShrEx Client-side Unbounded Response Size — Defensive Coding Gap

{% hint style="info" %}
**Severity**: Informational · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

The ShrEx client (shrex_getter) reads responses using bytes.Buffer.ReadFrom without io.LimitReader. While the server side applies ReserveMemory, per-peer stream cap, and rate limits, the client side has no byte ceiling -- only stream deadlines (60-120 seconds). Four code defects are identified: (1) GetEDS uses an unbounded bytes.Buffer, calling ReadFrom without io.LimitReader at client.go:142. (2) NamespaceData.ReadFrom collects frames until EOF with no frame count limit; individual frames have a serde 1 MiB cap but the number is unlimited. (3) server.go calls Validate() only without Verify(odsSize), potentially returning abnormal ResponseSize values, but the libp2p resource manager rejects reservations under default settings so practical impact is nil. (4) bitswap block_store's Put/PutMany/DeleteBlock/AllKeysChan/HashOnRead panic with 'not implemented', but these are client receive paths (not serving paths Get/Has/GetSize) on bridge nodes and are dead code under normal operation.

## Core Invariants Affected

Unrelated to consensus nodes. Only transient memory spike possibility on DA serving nodes; automatic recovery via existing defenses.

## Prerequisites

Sybil peer infrastructure. However, peers are blacklisted after one failure, so sustained attacks require many peer IDs.

## Attack Scenario

**Condition**: Malicious peer must enter victim's peer table, and victim must select that peer for a ShrEx request

**Example**: Normal maximum EDS size is ~32 MiB (MaxSquareSize=512). At 100 Mbps, malicious streaming for 60 seconds could cause a ~750 MB transient spike, but with bridge node recommended specs (8-32 GB), OOM probability is low and GC reclaims immediately.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Informational |
| Likelihood | Unrealistic (requires malicious peer in victim's peer table + victim selecting that peer; one-shot then blacklisted; transient memory spike then GC reclaims) |
| Scope | protocol |
| Target | Process |

## Code References

- [`celestia-node/share/shwap/p2p/shrex/client.go:142 (resp.ReadFrom unbounded)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/client.go#L142)
- [`celestia-node/share/shwap/p2p/shrex/shrex_getter/shrex.go:221-249 (GetEDS buffer)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/shrex_getter/shrex.go#L221-L249)
- [`celestia-node/share/shwap/namespace_data.go:60-80 (frame count 무제한)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/namespace_data.go#L60-L80)
- [`celestia-node/share/shwap/p2p/shrex/server.go:202 (Validate only)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/server.go#L202)
- [`celestia-node/share/shwap/p2p/bitswap/block_store.go:88-101 (panic dead code)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/bitswap/block_store.go#L88-L101)

## Verification & Evidence

**Status**: code_verified

Full code audit completed. All 4 defects are confirmed code-level issues, but existing defenses (timeout, blacklist, peer scoring, GC) make practical exploitation impossible. Defensive coding improvement recommended.

## Mitigations

Existing defenses: stream deadlines (60-120s), peer blacklisting on failure, peer scoring-based selection, server-side ReserveMemory with rate limit (85 RPS, burst 256). Recommendations: Apply io.LimitReader(stream, maxResponseSize) on client side, add frame count cap to NamespaceData.
