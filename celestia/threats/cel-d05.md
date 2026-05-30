# CEL-D05: ShrEx Client-side Unbounded Response Size

{% hint style="success" %}
**Severity**: Informational · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

The ShrEx client (shrex_getter) reads responses using bytes.Buffer.ReadFrom without io.LimitReader, meaning there is no byte ceiling on the client side. The server side applies ReserveMemory, per-peer stream caps, and rate limits, but the client relies solely on stream deadlines of 60 to 120 seconds to bound data ingestion.

Four specific code defects have been identified. First, GetEDS uses an unbounded bytes.Buffer at client.go line 142, calling ReadFrom without io.LimitReader. Second, NamespaceData.ReadFrom collects frames until EOF with no frame count limit; individual frames have a 1 MiB serde cap but the number of frames is unlimited. Third, server.go calls Validate() without calling Verify(odsSize), which could return abnormal ResponseSize values, but the libp2p resource manager rejects oversized reservations under default settings, neutralizing the impact. Fourth, the bitswap block_store implements Put, PutMany, DeleteBlock, AllKeysChan, and HashOnRead with panic("not implemented"), but these are client receive paths on bridge nodes and constitute dead code under normal operation.

Despite these defects, existing defenses including stream deadlines, peer blacklisting after failure, peer scoring, and garbage collection make practical exploitation unrealistic. A malicious peer would be blacklisted after a single failed attempt, and any temporary memory spike would be reclaimed by the garbage collector.

## Prerequisites

- Sybil peer infrastructure to place a malicious node in the victim's peer table
- The victim must select the malicious peer for a ShrEx request
- After one failure, the peer is blacklisted, requiring many peer IDs for sustained attacks

## Attack Scenario

1. The attacker deploys a malicious peer that enters the victim node's peer table.
2. The victim selects this peer for a ShrEx data request.
3. The malicious peer streams an oversized response, exploiting the lack of io.LimitReader on the client.
4. At 100 Mbps, the malicious peer could stream up to approximately 750 MB over a 60-second deadline window.
5. The peer is blacklisted after the failed request, preventing repeat attacks from the same identity.
6. The temporary memory spike is reclaimed by the garbage collector. With bridge node recommended specs of 8-32 GB, OOM is unlikely.

## Impact

A transient memory spike on DA serving nodes that is automatically recovered through garbage collection and peer blacklisting. The normal maximum EDS size is approximately 32 MiB (MaxSquareSize=512), so legitimate responses are well within memory bounds.

## Evidence

### Source Code

- `celestia-node/share/shwap/p2p/shrex/client.go:142` -- resp.ReadFrom called without io.LimitReader
- `celestia-node/share/shwap/p2p/shrex/shrex_getter/shrex.go:221-249` -- GetEDS buffer allocation
- `celestia-node/share/shwap/namespace_data.go:60-80` -- frame collection with no count limit
- `celestia-node/share/shwap/p2p/shrex/server.go:202` -- calls Validate() only, omits Verify(odsSize)
- `celestia-node/share/shwap/p2p/bitswap/block_store.go:88-101` -- panic("not implemented") on dead code paths

## Mitigations

Existing defenses include stream deadlines (60-120 seconds), peer blacklisting on failure, peer scoring-based selection, and server-side ReserveMemory with rate limiting (85 RPS, burst 256). Recommended fixes include applying io.LimitReader(stream, maxResponseSize) on the client side and adding a frame count cap to NamespaceData.
