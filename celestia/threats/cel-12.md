# CEL-12: ShrEx Client-side Unbounded Response Size

{% hint style="success" %}
**Category**: Design Note · **Status**: verified
{% endhint %}

## Summary

The ShrEx client reads peer responses using `bytes.Buffer.ReadFrom` without `io.LimitReader`, allowing a malicious peer to stream an arbitrarily large response. Four code-level defects are identified in the client-side read path, the namespace data accumulation loop, the server-side request validation, and the bitswap blockstore stubs. Existing defenses including stream deadlines, peer blacklisting, and peer scoring reduce practical exploitability to near zero.

## Description

The ShrEx protocol handles share exchange between Celestia nodes. While the server side applies `ReserveMemory`, per-peer stream caps, and rate limits, the client side has no byte ceiling beyond stream deadlines of 60 to 120 seconds. Four code defects are identified:

**Defect 1: Unbounded `bytes.Buffer` in GetEDS**

```go
// share/shwap/p2p/shrex/shrex_getter/shrex.go — GetEDS method
// @audit buff has no size cap; ReadFrom reads until EOF with no io.LimitReader
// https://github.com/celestiaorg/celestia-node/blob/388cc825/share/shwap/p2p/shrex/shrex_getter/shrex.go
func (sg *Getter) GetEDS(ctx context.Context, header *header.ExtendedHeader) (*rsmt2d.ExtendedDataSquare, error) {
    var (
        buff     = bytes.NewBuffer(make([]byte, 0)) // @audit no size limit
        response = &eds.Rsmt2D{}
    )
    req := func(ctx context.Context, peer libpeer.ID) error {
        buff.Reset()
        return sg.client.Get(ctx, &request, buff, peer)
    }
    // ...
}
```

Inside the client `doRequest` method, the response is consumed via `resp.ReadFrom(stream)` with no `io.LimitReader` wrapping the stream:

```go
// share/shwap/p2p/shrex/client.go — doRequest
// @audit ReadFrom reads from stream until EOF — no size limit applied
// https://github.com/celestiaorg/celestia-node/blob/388cc825/share/shwap/p2p/shrex/client.go
bytesRead, err := resp.ReadFrom(stream)
st := statusSuccess
if err != nil {
    err = fmt.Errorf("%w: %w", ErrInvalidResponse, err)
    st = statusReadRespErr
}
```

Normal maximum EDS size is approximately 32 MiB (MaxSquareSize=512). At 100 Mbps, malicious streaming for 60 seconds could cause a roughly 750 MB transient spike, but bridge node recommended specs of 8 to 32 GB make OOM improbable and GC reclaims immediately after the stream deadline fires.

**Defect 2: Unbounded Frame Accumulation in NamespaceData.ReadFrom**

```go
// share/shwap/namespace_data.go — NamespaceData.ReadFrom
// @audit Loop collects RowNamespaceData frames until EOF with no count limit
// @audit Individual frames have a serde 1 MiB cap, but the number of frames is unlimited
// https://github.com/celestiaorg/celestia-node/blob/388cc825/share/shwap/namespace_data.go
func (nd *NamespaceData) ReadFrom(reader io.Reader) (int64, error) {
    var ndNew []RowNamespaceData
    var n int64
    for {
        var rnd RowNamespaceData
        nn, err := rnd.ReadFrom(reader)
        n += nn
        if errors.Is(err, io.EOF) {
            break
        }
        if err != nil {
            return n, err
        }
        ndNew = append(ndNew, rnd) // @audit unbounded append — no frame count cap
    }
    *nd = ndNew
    return n, nil
}
```

**Defect 3: Server Validates Without Bounds Checking**

```go
// share/shwap/p2p/shrex/server.go — handleDataRequest
// @audit Server calls Validate() only, never Verify(edsSize)
// @audit Validate() checks only Height > 0; Verify() checks RowIndex < edsSize
// https://github.com/celestiaorg/celestia-node/blob/388cc825/share/shwap/p2p/shrex/server.go
err = requestID.Validate()
if err != nil {
    logger.Warnw("validate request", "err", err)
    return statusBadRequest, 0
}
```

The distinction between `Validate()` and `Verify(edsSize)`:

- `SampleID.Validate()`: checks only `ShareIndex >= 0` and `Height > 0`
- `SampleID.Verify(edsSize)`: additionally checks `ShareIndex < edsSize` and `RowIndex < edsSize`

The server never calls `Verify(edsSize)` to reject out-of-bounds requests early. It later calls `file.Size(ctx)` for memory reservation but does not perform bounds rejection before processing.

**Defect 4: Bitswap Blockstore Panic Stubs**

```go
// share/shwap/p2p/bitswap/block_store.go — unimplemented methods
// @audit Five methods panic — any code path triggering these crashes the node
// @audit These are client receive paths, not serving paths (Get/Has/GetSize work normally)
// https://github.com/celestiaorg/celestia-node/blob/388cc825/share/shwap/p2p/bitswap/block_store.go
func (b *Blockstore) Put(context.Context, blocks.Block) error {
    panic("not implemented")
}

func (b *Blockstore) PutMany(context.Context, []blocks.Block) error {
    panic("not implemented")
}

func (b *Blockstore) DeleteBlock(context.Context, cid.Cid) error {
    panic("not implemented")
}

func (b *Blockstore) AllKeysChan(context.Context) (<-chan cid.Cid, error) {
    panic("not implemented")
}

func (b *Blockstore) HashOnRead(bool) { panic("not implemented") }
```

These are dead code under normal operation because bridge nodes only use the serving paths (`Get`, `Has`, `GetSize`). However, if any code path from a remote peer's Bitswap message triggers `Put` or `PutMany`, the node crashes.

## Proof of Concept

No exploit reproduction was conducted. This finding is based on source code analysis of the celestia-node codebase at commit `388cc825`.

## Impact

Transient memory spike on DA serving nodes. Practical exploitation requires a malicious peer in the victim's peer table who is selected for a ShrEx request. Peers are blacklisted after one failure, limiting attacks to single attempts per peer identity. The memory spike is reclaimed by GC after the stream deadline expires. With bridge node recommended specs of 8 to 32 GB RAM, OOM is improbable from a single malicious response.

Sets the Liveness Design Baseline through the read-path resilience sub-property. This is a documented protocol property and carries no score.

## Recommendation

1. Apply `io.LimitReader(stream, maxResponseSize)` on the client side in `client.go` before calling `ReadFrom`, where `maxResponseSize` is derived from the expected EDS size for the requested height.
2. Add a frame count cap to `NamespaceData.ReadFrom` based on the maximum possible number of rows in a data square.
3. Call `requestID.Verify(edsSize)` on the server side before processing, to reject out-of-bounds requests early with a clean error.
4. Replace `panic("not implemented")` stubs in `block_store.go` with `ErrNotSupported` error returns to prevent node crashes from unexpected code paths.
