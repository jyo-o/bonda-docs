# CEL-D10: Worst-case Memory Reservation for Empty Namespace Requests

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

When handling `NamespaceData` requests, the ShrEx server reserves memory for the full Original Data Square (ODS) size regardless of the actual response size. When the requested namespace contains no data but the block exists in the store, the server reserves up to 8 MiB per stream then returns an empty response. The per-peer cap limits this to 16 MiB of reservation, which is released almost instantly, resulting in minimal practical impact.

## Description

The memory reservation logic uses worst-case sizing:

```go
// celestia-node/share/shwap/namespace_data_id.go
// @audit ResponseSize calculation: odsLn * odsLn * ShareSize
// @audit With GovMaxSquareSize=128: 128 * 128 * 512 = 8 MiB per stream
```

```go
// celestia-node/share/shwap/p2p/shrex/server.go
// @audit Block not in store: returns NOT_FOUND immediately, no memory reservation
// @audit Block exists: calls ReserveMemory with worst-case ODS size, regardless of actual response
// @audit Empty namespace = full reservation + empty response
```

The per-peer stream limits bound the impact:

```go
// celestia-node/share/shwap/p2p/shrex/limits.go
// @audit servicePeerStreams = streamIncrease / minSimultaneousPeers = 8/4 = 2
// @audit peerStreamsPerProtocol for NamespaceDataID is 16
// @audit A single peer can trigger at most 2 concurrent streams = 16 MiB reservation
```

The `edsSize` value is looked up from the server's local block store rather than derived from the request. If the requested block is not in the store, the server returns `NOT_FOUND` immediately with no memory reservation. The problem only arises when the block exists but the requested namespace is empty.

Empty namespace responses complete almost instantly, causing the reservation to be released very quickly. This limits the practical impact to brief, small memory spikes. GovMaxSquareSize=128 confirmed via mainnet REST at `celestia-rest.publicnode.com`.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Temporary memory reservation of up to 16 MiB per attacking peer, released almost instantly. The resource manager budget could be briefly reduced, but the practical effect is minimal given the rapid release cycle and per-peer limits.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via P2P NamespaceData requests over the network |
| AC (Attack Complexity) | H (High) | Requires knowledge of block heights held by the target and namespaces that are empty in those blocks |
| PR (Privileges Required) | N (None) | No privileges required beyond P2P network access |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted node's memory reservation budget |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | L (Low) | 16 MiB temporary reservation released almost instantly; minimal practical impact |

## Recommendation

1. Check the actual namespace data size before reserving memory, using the real response size instead of worst-case ODS size.
2. Change `ReserveMemory` to use actual response size when the namespace data is known to be empty, avoiding unnecessary reservation.
