# CEL-D05: ShrEx Client-side Unbounded Response Size

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

The ShrEx client (`shrex_getter`) reads responses using `bytes.Buffer.ReadFrom` without `io.LimitReader`, imposing no byte ceiling on the client side. While server-side defenses (`ReserveMemory`, per-peer stream caps, rate limits) and client-side defenses (stream deadlines, peer blacklisting, peer scoring, GC) make practical exploitation unrealistic, four specific code defects exist that deviate from defense-in-depth best practices.

## Description

**Case #1: Unbounded GetEDS Buffer**

```go
// celestia-node/share/shwap/p2p/shrex/client.go:142
// @audit resp.ReadFrom called without io.LimitReader
```

```go
// celestia-node/share/shwap/p2p/shrex/shrex_getter/shrex.go:221-249
// @audit GetEDS uses unbounded bytes.Buffer allocation
```

**Case #2: Unlimited NamespaceData Frame Count**

```go
// celestia-node/share/shwap/namespace_data.go:60-80
// @audit Frame collection until EOF with no frame count limit
// @audit Individual frames have 1 MiB serde cap, but number of frames is unlimited
```

**Case #3: Missing Verify Call on Server**

```go
// celestia-node/share/shwap/p2p/shrex/server.go:202
// @audit Calls Validate() only, omits Verify(odsSize)
// @audit Could return abnormal ResponseSize values
// @audit However, libp2p resource manager rejects oversized reservations under default settings
```

**Case #4: Dead Code Panics in Bitswap Block Store**

```go
// celestia-node/share/shwap/p2p/bitswap/block_store.go:88-101
// @audit Put, PutMany, DeleteBlock, AllKeysChan, HashOnRead implement panic("not implemented")
// @audit These are client receive paths on bridge nodes — dead code under normal operation
```

Despite these defects, existing defenses neutralize practical exploitation:
- Stream deadlines: 60-120 seconds bound data ingestion time
- Peer blacklisting after failure (though disabled by default, see CEL-D06)
- Peer scoring-based selection
- Server-side `ReserveMemory` with rate limiting (85 RPS, burst 256)
- Garbage collection reclaims temporary memory spikes

At 100 Mbps, a malicious peer could stream up to approximately 750 MB over a 60-second deadline window. With bridge node recommended specs of 8-32 GB RAM, OOM is unlikely. The normal maximum EDS size is approximately 32 MiB (`MaxSquareSize=512`).

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

A transient memory spike on DA serving nodes that is automatically recovered through garbage collection and peer blacklisting. The peer is blacklisted after a single failed request, preventing repeat attacks from the same identity. The impact is limited to a brief resource allocation spike with no lasting effect on node operation.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via P2P ShrEx data responses over the network |
| AC (Attack Complexity) | H (High) | Requires Sybil infrastructure to place a malicious peer in the victim's peer table and be selected for requests |
| PR (Privileges Required) | N (None) | No privileges required beyond P2P network participation |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted node's memory |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | L (Low) | Transient memory spike only; automatically recovered via GC and peer blacklisting |

## Recommendation

1. Apply `io.LimitReader(stream, maxResponseSize)` on the client side in the ShrEx getter to enforce a byte ceiling on responses.
2. Add a frame count cap to `NamespaceData` collection to prevent unlimited frame accumulation.
