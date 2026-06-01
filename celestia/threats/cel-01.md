# CEL-01: TxCache Key Mismatch Causing Permanent Memory Leak in Validators

{% hint style="warning" %}
**Severity**: High (7.5/10) · **Likelihood**: Moderate · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

celestia-app's `TxCache` uses different keys for storing and deleting blob transaction entries, causing entries to accumulate permanently and eventually crash validator nodes via OOM. During `CheckTx`, entries are stored using `sha256(inner SDK tx)`, but during `FinalizeBlock`, deletion attempts use `sha256(full BlobTx wire bytes)`. Since these keys never match, cache deletion always fails silently, and entries accumulate irreversibly.

## Description

The key mismatch originates from the re-serialization of blob transactions during block building:

```go
// celestia-app/app/check_tx.go — handleBlobCheckTx
// @audit txCache.Set(btx.Tx, btx.Blobs) stores using sha256 of inner SDK tx as key
// https://github.com/celestiaorg/celestia-app/blob/main/app/check_tx.go
case abci.CheckTxType_New:
    if err := blobtypes.ValidateBlobTx(app.encodingConfig.TxConfig, btx, appconsts.SubtreeRootThreshold, appconsts.Version); err != nil {
        return responseCheckTxWithEvents(err, 0, 0, []abci.Event{}, false), err
    }
    app.txCache.Set(btx.Tx, btx.Blobs) // @audit key = sha256(btx.Tx) = sha256(inner SDK tx)
```

```go
// celestia-app/app/app.go — FinalizeBlock
// @audit RemoveTransaction uses sha256 of full BlobTx wire bytes, not inner SDK tx
// https://github.com/celestiaorg/celestia-app/blob/main/app/app.go
func (app *App) FinalizeBlock(req *abci.RequestFinalizeBlock) (*abci.ResponseFinalizeBlock, error) {
    res, err := app.BaseApp.FinalizeBlock(req)
    if err != nil {
        return nil, err
    }
    for _, tx := range req.Txs {
        app.txCache.RemoveTransaction(tx) // @audit key = sha256(tx) = sha256(full BlobTx wire bytes)
    }
    return res, nil
}
```

```go
// celestia-app/app/tx_cache.go — getTxKey
// @audit sha256-based key generation — sha256(full BlobTx) != sha256(inner SDK tx)
// https://github.com/celestiaorg/celestia-app/blob/main/app/tx_cache.go
func (c *TxCache) getTxKey(tx []byte) string {
    hash := sha256.Sum256(tx)
    return string(hash[:])
}
```

The `TxCache` is implemented as a `sync.Map` with no capacity limit, no TTL, and no separate cleanup mechanism. The only recovery is a node restart.

The problem is worsened by the rejected transaction path: `txCache.Set()` executes before `BaseApp.CheckTx()` in the `CheckTx` handler. Transactions with valid blob structure but invalid nonce, fee, or gas are rejected by `BaseApp` but still persist in the cache. An attacker can exploit this at zero cost since no fees are charged for rejected transactions.

Note: `process_proposal.go:251` correctly queries using the inner tx key via `Exists`, confirming the intended key type is the inner SDK tx.

## Proof of Concept

End-to-end reproduction confirmed the key mismatch. See [Verification Evidence](../evidence.md#cel-01-txcache-key-mismatch-poc_verified) for full test results.

- **TestTxCacheLeakProductionPath**: `CheckTx` followed by `FinalizeBlock(wrappedTx)` confirmed `fromCache` still returns `true`. Cache entry was not deleted.
- **Rejected transaction persistence verified**: future sequence blob tx and zero-fee blob tx both leave permanent cache entries.
- **Per-entry memory**: approximately 204 bytes.
- **Projected leak rate**: approximately 1 GB per 160 seconds at 100 Mbps rejected transaction rate.
- **Existing test suite gap**: existing tests do not reproduce the production path because they pass `blobTx.Tx` directly to `FinalizeBlock` instead of the wrapped `BlobTx`.

## Impact

Validator and consensus node memory exhaustion leading to OOM crash and consensus participation halt. The accumulation is irreversible without a restart. Simultaneous attacks on multiple validators could cause one-third departure from the validator set, threatening chain liveness. The rejected transaction path enables the attack at zero cost.

### CVSS 3.1

**Score**: 7.5/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via RPC or P2P blob transaction submission |
| AC (Attack Complexity) | L (Low) | Submitting blob transactions with invalid nonces or zero fees is straightforward |
| PR (Privileges Required) | N (None) | No privileges required; any node with RPC or P2P access can submit transactions |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted validator/consensus node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact; the attack targets availability only |
| A (Availability) | H (High) | OOM crash halts consensus participation; accumulation is irreversible without restart |

## Recommendation

1. Re-parse blob transactions via `UnmarshalBlobTx` in `FinalizeBlock` to extract the inner tx key for deletion, ensuring the same key type is used for both storage and removal.
2. Call `txCache.Set` only after `BaseApp.CheckTx` succeeds, preventing rejected transactions from persisting in the cache.
3. Add a maximum size cap or TTL to the `TxCache` to bound memory growth even if other fixes are not immediately applied.
