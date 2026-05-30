# CEL-D17: TxCache Key Mismatch Causing Permanent Memory Leak in Validators

{% hint style="warning" %}
**Severity**: High · **STRIDE**: D · **Status**: poc_verified
{% endhint %}

## Overview

celestia-app's TxCache uses different keys for storing and deleting blob transaction entries, causing entries to accumulate permanently and eventually crash validator nodes via OOM.

During CheckTx, entries are stored using sha256(inner SDK tx) as the key. During FinalizeBlock, entries are deleted using sha256(full BlobTx wire bytes) as the key. Because PrepareProposal re-serializes blob transactions via MarshalBlobTx(innerTx, blobs...), the full BlobTx bytes in FinalizeBlock differ from the inner SDK tx bytes used in CheckTx. Since sha256(full BlobTx) never equals sha256(inner SDK tx), cache deletion always fails silently.

The TxCache is implemented as a sync.Map with no capacity limit, no TTL, and no separate cleanup mechanism. Entries accumulate irreversibly, and the only recovery is a node restart.

The problem is worsened by the fact that txCache.Set() executes before BaseApp.CheckTx() in the CheckTx handler. This means transactions with valid blob structure but invalid nonce, fee, or gas are rejected by BaseApp but still persist in the cache. An attacker can exploit this rejected transaction path at zero cost, since no fees are charged for rejected transactions.

## Prerequisites

- RPC or P2P access to submit blob transactions to any celestia-app node
- The rejected transaction path requires no fees (invalid nonce or zero fee is sufficient)
- The valid transaction path requires only minimum gas fees

## Attack Scenario

1. The attacker crafts blob transactions with valid blob structure but invalid signatures or zero fees.
2. The attacker submits these transactions via RPC or P2P to a validator node.
3. handleBlobCheckTx calls txCache.Set(btx.Tx) using sha256 of the inner SDK tx as key.
4. BaseApp.CheckTx rejects the transaction (e.g., code=32 for future sequence, code=11 for zero fee).
5. The cache entry persists because there is no cleanup path for rejected transactions.
6. When valid blob transactions are finalized, FinalizeBlock attempts to delete using sha256 of the full BlobTx wire bytes, which never matches the stored key.
7. Both rejected and finalized entries accumulate indefinitely in the sync.Map.
8. At approximately 204 bytes per entry and 100 Mbps rejected transaction rate, memory leaks at roughly 1 GB every 160 seconds.

## Impact

Validator and consensus node memory exhaustion leading to OOM crash and consensus participation halt. The accumulation is irreversible without a restart. Simultaneous attacks on multiple validators could cause one-third departure from the validator set, threatening chain liveness.

## Evidence

### Source Code

- `celestia-app/app/check_tx.go:63` -- txCache.Set(btx.Tx) stores using inner SDK tx key
- `celestia-app/app/app.go:589` -- txCache.RemoveTransaction(tx) deletes using full BlobTx key
- `celestia-app/app/tx_cache.go:23-27` -- sha256-based key generation
- `celestia-app/app/filtered_square_builder.go:193-197` -- encodeBlobTxs re-serializes via MarshalBlobTx
- `celestia-app/app/process_proposal.go:251` -- Exists correctly queries using inner tx key

### PoC Testing

- TestTxCacheLeakProductionPath: CheckTx followed by FinalizeBlock(wrappedTx), confirmed fromCache still returns true (cache not deleted). Test passed.
- Rejected transaction persistence verified: future sequence blob tx (checktx_code=32) and zero-fee blob tx (checktx_code=11) both leave cache entries.
- Per-entry memory measured at approximately 204 bytes.
- Existing test suite identified as not reproducing the production path because tests pass blobTx.Tx directly to FinalizeBlock instead of the wrapped BlobTx.

## Mitigations

No current defense exists. Recommended fixes include re-parsing blob transactions via UnmarshalBlobTx in FinalizeBlock to extract the inner tx key for deletion, calling txCache.Set only after BaseApp.CheckTx succeeds, and adding a maximum size cap or TTL to the TxCache.
