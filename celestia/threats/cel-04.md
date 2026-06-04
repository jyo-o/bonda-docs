# CEL-04: Pre-gas Commitment Computation with Unlimited Blob Count in CheckTx

{% hint style="warning" %}
**Severity**: High (7.5/10) · **Likelihood**: Moderate · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

In celestia-app, the `handleBlobCheckTx` function executes `ValidateBlobTx` and `CreateParallelCommitments` before any gas is deducted by the ante handler chain. Combined with the absence of a blob count limit in `ValidateBasic`, an attacker can force expensive NMT commitment computation on validator nodes at zero cost by submitting transactions with invalid signatures or zero fees.

## Description

![CEL-04 data flow — Celestia Consensus path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/celestia/assets/dfd/celestia-consensus.png)

*Data flow — Celestia Consensus: Mempool / CheckTx.*

The ante handler chain in `celestia-app/app/ante/ante.go` runs in the order: `SetUpContext` -> `DeductFee` -> `SigVerify` -> `MinGasPFB` -> `BlobShare`. However, commitment computation occurs before this entire chain:

```go
// celestia-app/app/check_tx.go — handleBlobCheckTx
// @audit ValidateBlobTx runs BEFORE the ante handler chain (forwardCheckTx)
// @audit Commitment computation happens before any gas deduction or signature check
// https://github.com/celestiaorg/celestia-app/blob/main/app/check_tx.go
func (app *App) handleBlobCheckTx(req *abci.RequestCheckTx, btx *blobtx.BlobTx) (*abci.ResponseCheckTx, error) {
    baseReq := &abci.RequestCheckTx{Tx: btx.Tx, Type: req.GetType()}
    case abci.CheckTxType_New:
        if err := blobtypes.ValidateBlobTx(app.encodingConfig.TxConfig, btx, ...); err != nil {
            return responseCheckTxWithEvents(err, ...), err
        }
        app.txCache.Set(btx.Tx, btx.Blobs)
    // ...
    return app.forwardCheckTx(baseReq, sdkTx) // @audit ante chain runs here, AFTER ValidateBlobTx
}
```

```go
// celestia-app/x/blob/types/blob_tx.go — ValidateBlobTx
// @audit CreateParallelCommitments computes NMT roots for ALL blobs using NumCPU*2 goroutines
// https://github.com/celestiaorg/celestia-app/blob/main/x/blob/types/blob_tx.go
func ValidateBlobTx(txcfg client.TxEncodingConfig, bTx *tx.BlobTx, ...) error {
    msgPFB, err := ValidateBlobTxSkipCommitment(txcfg, bTx)
    if err != nil {
        return err
    }
    calculatedCommitments, err := inclusion.CreateParallelCommitments(
        bTx.Blobs, merkle.HashFromByteSlices, subtreeRootThreshold, runtime.NumCPU()*2,
    )
    // ...
}
```

```go
// celestia-app/x/blob/types/payforblob.go — ValidateBasic
// @audit No maximum blob count check — only validates arrays are non-empty and consistent
// https://github.com/celestiaorg/celestia-app/blob/main/x/blob/types/payforblob.go
func (msg *MsgPayForBlobs) ValidateBasic() error {
    if len(msg.Namespaces) == 0 { return ErrNoNamespaces }
    if len(msg.Namespaces) != len(msg.ShareVersions) || len(msg.Namespaces) != len(msg.BlobSizes) || ... {
        return ErrMismatchedNumberOfPFBComponent.Wrapf(...)
    }
    // @audit No cap on len(msg.Namespaces) — thousands of 1-byte blobs accepted
    return nil
}
```

The attack flow is:

1. Attacker crafts a `BlobTx` containing thousands of 1-byte blobs, for example 1,000 blobs at approximately 70 KB total
2. Attacker sets an invalid signature or zero fee to ensure rejection
3. Validator's `handleBlobCheckTx` runs `ValidateBlobTx` and `CreateParallelCommitments`, computing NMT commitments for all blobs
4. The ante chain runs afterward and rejects the transaction
5. Gas is never charged because the transaction was rejected before gas deduction

The attack is especially cheap because rejected transactions still trigger the full commitment computation at zero cost.

The single global `CheckTx` mutex turns this into a head-of-line-blocking attack rather than a pure CPU drain: every `CheckTx` is serialized behind the one holding the lock, so a single many-blob transaction stalls all other mempool admission until its commitment computation finishes.

```go
// celestia-app/app/check_tx.go — CheckTx
// @audit a single global mutex serializes every CheckTx; the lock is held through commitment computation
// https://github.com/celestiaorg/celestia-app/blob/main/app/check_tx.go
func (app *App) CheckTx(req *abci.RequestCheckTx) (*abci.ResponseCheckTx, error) {
    app.checkStateMu.Lock()
    defer app.checkStateMu.Unlock() // held through ValidateBlobTx / CreateParallelCommitments
    // ...
}
```

## Proof of Concept

A live single-attacker reproduction on an 8 vCPU victim confirmed the head-of-line-blocking DoS. See [Verification Evidence](../evidence.md#cel-04-blobtx-pre-ante-cpu-exhaustion-poc_verified) for the full setup and measurements.

- **Single free attacker**: a zero-fee BlobTx with thousands of 1-byte blobs forced full commitment computation before ante rejection, returning RPC `-32603 invalid commitment for share`.
- **Legitimate CheckTx latency rose 127x**: a concurrent normal 1-blob probe went from 1.15 ms to 146 ms p50 while node CPU rose from ~2% to 534% (5.34 cores), at zero attacker cost.
- **Core scaling does not help**: the global CheckTx mutex caps parallelism near ~700%, and legitimate latency stays degraded (340x at 16 cores under a scaled attack), confirming the serialized lock, not raw CPU, is the bottleneck.

## Impact

A single free attacker holds the global `CheckTx` lock while the node computes NMT commitments, head-of-line-blocking all other mempool admission. The measured effect on an 8 vCPU victim was a 127x rise in legitimate CheckTx latency (1.15 ms to 146 ms p50) and node CPU from ~2% to 534%, at zero attacker cost. A public RPC or bridge node becomes a direct denial of service to its users; a validator cannot fill its mempool and proposes near-empty blocks while transaction propagation stalls, reducing network throughput and validator fee income. The node recovers immediately once the attack stops, so the impact is a sustained denial while the attack is active rather than a crash.

Affects the **Liveness** axis, where it produces a Layer 3 deduction while unpatched.

### CVSS 3.1

**Score**: 7.5/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via RPC or P2P transaction submission over the network |
| AC (Attack Complexity) | L (Low) | Crafting a BlobTx with many 1-byte blobs and an invalid signature is straightforward |
| PR (Privileges Required) | N (None) | No privileges required; any node with RPC or P2P access can submit transactions |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted validator node's CPU |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact; the attack targets availability only |
| A (Availability) | H (High) | A single free attacker sustains a 127x CheckTx latency increase and head-of-line-blocks all mempool admission for the duration of the attack; the node recovers when the attack stops |

## Recommendation

1. Add a `MaxBlobsPerPFB` cap to `ValidateBasic` to reject transactions with excessive blob counts before any computation occurs.
2. Move commitment computation to after signature verification in the ante chain, so invalid transactions are rejected before expensive computation.
3. Add blob count-based early rejection in `CheckTx` before any expensive computation is triggered.
