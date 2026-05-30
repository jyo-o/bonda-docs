# CEL-D10: Worst-case Memory Reservation for Empty Namespace Requests

{% hint style="info" %}
**Severity**: Low · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

When handling NamespaceData requests, server.go's handleDataRequest reserves memory using ResponseSize(edsSize) before sending the response. The edsSize value is looked up from the server's local block store rather than derived from the request. If the requested block is not in the store, the server returns NOT_FOUND immediately with no memory reservation.

The problem arises when the block exists in the store but the requested namespace contains no data. In this case, the server reserves memory for the full Original Data Square (ODS) size regardless of the actual response size, then returns an empty response. On mainnet with GovMaxSquareSize=128, this means reserving 128 x 128 x 512 = 8 MiB per stream. The service scope per-peer cap is 2 concurrent streams, so a single peer can trigger at most 16 MiB of memory reservation.

However, empty namespace responses complete almost instantly, causing the reservation to be released very quickly. This limits the practical impact to brief, small memory spikes that do not meaningfully affect node stability.

## Prerequisites

- One node with P2P network access to the target
- Knowledge of block heights held by the target node

## Attack Scenario

1. The attacker connects to the target node via P2P.
2. The attacker sends NamespaceData requests for namespaces known to be empty in blocks the target holds.
3. The server looks up the block from its local store and finds it exists.
4. The server reserves memory for the full ODS size (8 MiB per stream) despite the namespace being empty.
5. The per-peer cap limits this to 2 concurrent streams, totaling 16 MiB reservation.
6. The empty response completes immediately and the reservation is released.

## Impact

Temporary memory reservation of up to 16 MiB per attacking peer, released almost instantly. The resource manager budget could be briefly reduced, but the practical effect is minimal given the rapid release cycle and per-peer limits.

## Evidence

### Source Code

- `celestia-node/share/shwap/namespace_data_id.go` -- ResponseSize calculation: odsLn * odsLn * ShareSize
- `celestia-node/share/shwap/p2p/shrex/server.go` -- block not in store triggers early return; block exists triggers ReserveMemory with worst-case size
- `celestia-node/share/shwap/p2p/shrex/limits.go` -- servicePeerStreams = streamIncrease / minSimultaneousPeers = 8/4 = 2; peerStreamsPerProtocol for NamespaceDataID is 16

### On-Chain / Network

- GovMaxSquareSize=128 confirmed via mainnet REST at celestia-rest.publicnode.com

## Mitigations

Recommended fixes include checking the actual namespace data size before reserving memory and changing ReserveMemory to use actual response size instead of the worst-case ODS size.
