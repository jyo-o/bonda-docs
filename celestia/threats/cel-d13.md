# CEL-D13: Pre-gas Commitment Computation with Unlimited Blob Count in CheckTx

{% hint style="warning" %}
**Severity**: High (7.5/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

In celestia-app, the `handleBlobCheckTx` function executes `ValidateBlobTx` and `CreateParallelCommitments` before any gas is deducted by the ante handler chain. Combined with the absence of a blob count limit in `ValidateBasic`, an attacker can force expensive NMT commitment computation on validator nodes at zero cost by submitting transactions with invalid signatures or zero fees.

## Description

The ante handler chain in `celestia-app/app/ante/ante.go` runs in the order: `SetUpContext` -> `DeductFee` -> `SigVerify` -> `MinGasPFB` -> `BlobShare`. However, commitment computation occurs before this entire chain:

```go
// celestia-app/app/check_tx.go
// @audit handleBlobCheckTx calls ValidateBlobTx before the ante handler chain
// @audit This triggers CreateParallelCommitments before any gas deduction
```

```go
// celestia-app/x/blob/types/payforblob.go
// @audit ValidateBasic has no maximum blob count check
// @audit Within MaxTxSize of 8 MiB, thousands of 1-byte blobs can be packed
```

```go
// celestia-app/x/blob/types/blob_tx.go
// @audit ValidateBlobTx calls CreateParallelCommitments
// @audit Each blob triggers NMT subtree and Merkle root computation
```

The attack flow is:

1. Attacker crafts a `BlobTx` containing thousands of 1-byte blobs (e.g., 1,000 blobs at approximately 70 KB total including metadata)
2. Attacker sets an invalid signature or zero fee to ensure rejection
3. Validator's `handleBlobCheckTx` runs `ValidateBlobTx` and `CreateParallelCommitments`, computing NMT commitments for all blobs
4. The ante chain runs afterward and rejects the transaction
5. Gas is never charged because the transaction was rejected before gas deduction

The attack is especially cheap because rejected transactions still trigger the full commitment computation at zero cost.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Validator CPU exhaustion leading to mempool processing delays and reduced consensus throughput. The attack requires no on-chain cost when using the rejected transaction path (invalid signature or zero fee). An attacker with RPC or P2P access can repeatedly submit crafted transactions to consume significant validator CPU resources.

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
| A (Availability) | H (High) | CPU exhaustion degrades mempool processing and consensus throughput |

## Recommendation

1. Add a `MaxBlobsPerPFB` cap to `ValidateBasic` to reject transactions with excessive blob counts before any computation occurs.
2. Move commitment computation to after signature verification in the ante chain, so invalid transactions are rejected before expensive computation.
3. Add blob count-based early rejection in `CheckTx` before any expensive computation is triggered.
