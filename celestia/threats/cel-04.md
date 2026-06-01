# CEL-04: Pre-gas Commitment Computation with Unlimited Blob Count in CheckTx

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **Category**: Vulnerability · **Status**: verified
{% endhint %}

## Summary

In celestia-app, the `handleBlobCheckTx` function executes `ValidateBlobTx` and `CreateParallelCommitments` before any gas is deducted by the ante handler chain. Combined with the absence of a blob count limit in `ValidateBasic`, an attacker can force expensive NMT commitment computation on validator nodes at zero cost by submitting transactions with invalid signatures or zero fees.

## Description

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

## Proof of Concept

No exploit reproduction was conducted. This finding is based on source code analysis of the celestia-app CheckTx handler and ante chain execution order. See [Verification Evidence](../evidence.md#gas-and-blockspace-parameters-cel-05-cel-04) for gas parameter data.

## Impact

Validator CPU exhaustion leading to mempool processing delays and reduced consensus throughput. The attack requires no on-chain cost when using the rejected transaction path (invalid signature or zero fee). An attacker with RPC or P2P access can repeatedly submit crafted transactions to consume significant validator CPU resources.

### CVSS 3.1

**Score**: 5.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via RPC or P2P transaction submission over the network |
| AC (Attack Complexity) | L (Low) | Crafting a BlobTx with many 1-byte blobs and an invalid signature is straightforward |
| PR (Privileges Required) | N (None) | No privileges required; any node with RPC or P2P access can submit transactions |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted validator node's CPU |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact; the attack targets availability only |
| A (Availability) | L (Low) | A single oversized transaction causes temporary processing degradation but does not crash the node; the system recovers after the affected block is processed |

## Recommendation

1. Add a `MaxBlobsPerPFB` cap to `ValidateBasic` to reject transactions with excessive blob counts before any computation occurs.
2. Move commitment computation to after signature verification in the ante chain, so invalid transactions are rejected before expensive computation.
3. Add blob count-based early rejection in `CheckTx` before any expensive computation is triggered.
