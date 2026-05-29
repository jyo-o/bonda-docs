# CEL-D10: NamespaceData Request — Worst-case Memory Reservation for Empty Namespace

{% hint style="info" %}
**Severity**: Low · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

server.go's handleDataRequest reserves memory via ResponseSize(edsSize) before responding. edsSize is looked up from the server's local store rather than from the request. If the block is not in the store, it returns NOT_FOUND immediately (no memory reservation). If the block exists but namespace data is empty, it reserves memory for the full ODS size regardless of actual data size, then returns an empty response. On mainnet with GovMaxSquareSize=128 (ODS), ResponseSize = 128x128x512 = 8 MiB/stream. Service scope per-peer cap = 2, so a single peer can trigger 2 concurrent streams for 16 MiB reservation. Empty namespace responses complete immediately, causing quick reservation release.

## Core Invariants Affected

`data_recoverability`

Potential to exhaust resource manager budget, but at 16 MiB per peer with immediate release for empty responses, practical impact is minimal.

## Prerequisites

One node with P2P network access. Knowledge of block heights held by the target node.

## Attack Scenario

**Condition**: P2P peer requests NamespaceData for an empty namespace in an existing block. Service scope limits to 2 streams per peer.

**Example**: Mainnet GovMaxSquareSize=128 (ODS, on-chain confirmed): edsSize=256, odsLn=128, ResponseSize=8 MiB/stream. Service scope per-peer cap=2 yields 16 MiB from a single peer. Empty namespace responses complete immediately, releasing reservations instantly.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Low |
| Likelihood | Low (possible with 1 P2P peer but only 16 MiB/peer level, released immediately) |
| Scope | implementation |
| Target | Dataflow |
| Core Invariants | data_recoverability |

## Code References

- [`celestia-node/share/shwap/namespace_data_id.go (ResponseSize: odsLn*odsLn*ShareSize)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/namespace_data_id.go)
- [`celestia-node/share/shwap/p2p/shrex/server.go (block not in store → early return; block exists → ReserveMemory worst-case)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/server.go)
- [`celestia-node/share/shwap/p2p/shrex/limits.go (servicePeerStreams = streamIncrease/minSimultaneousPeers = 8/4 = 2; peerStreamsPerProtocol[NamespaceDataID]=16)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/limits.go)

## Verification & Evidence

**Status**: code_verified

Code verification completed. Confirmed edsSize comes from server local store lookup (not from request) in server.go. GovMaxSquareSize=128 confirmed via mainnet REST (celestia-rest.publicnode.com). Service scope per-peer cap=2 confirmed in limits.go.

## Mitigations

Recommendations: (1) Check namespace data size first and reserve based on actual size, (2) Change ReserveMemory to actual response size-based allocation.
