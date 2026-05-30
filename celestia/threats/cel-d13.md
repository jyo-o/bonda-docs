# CEL-D13: Pre-gas Commitment Computation with Unlimited Blob Count in CheckTx

{% hint style="warning" %}
**Severity**: High · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

In celestia-app, the handleBlobCheckTx function executes ValidateBlobTx followed by CreateParallelCommitments before any gas is deducted. The ante handler chain runs in the order SetUpContext, DeductFee, SigVerify, MinGasPFB, and BlobShare, but commitment computation happens before this entire chain. This means an attacker can force expensive cryptographic computation (NMT subtree roots and Merkle root calculations) on validator nodes without paying any gas.

MsgPayForBlobs.ValidateBasic() does not enforce a blob count limit. Within the MaxTxSize of 8 MiB, an attacker can pack thousands of 1-byte blobs into a single BlobTx. Each blob triggers NMT subtree and Merkle root computation regardless of whether the transaction will ultimately be rejected for invalid signatures, insufficient fees, or wrong nonces.

The attack is especially cheap because rejected transactions still trigger the full commitment computation. An attacker can submit transactions with invalid signatures or zero fees that cost nothing but force significant CPU work on every validator that receives them.

## Prerequisites

- RPC or P2P access to submit transactions to a validator node
- No fees required for the rejected transaction path (invalid signature or insufficient fees)

## Attack Scenario

1. The attacker crafts a BlobTx containing thousands of 1-byte blobs (e.g., 1,000 blobs at approximately 70 KB total including metadata).
2. The attacker sets an invalid signature or zero fee to ensure the transaction will be rejected.
3. The attacker submits the transaction to a validator's RPC endpoint.
4. The validator's handleBlobCheckTx runs ValidateBlobTx and CreateParallelCommitments, computing NMT commitments for all 1,000 blobs.
5. Only after this computation does the ante chain run, rejecting the transaction for the invalid signature.
6. Gas is never charged because the transaction was rejected before gas deduction.
7. The attacker repeats, consuming significant validator CPU at zero cost.

## Impact

Validator CPU exhaustion leading to mempool processing delays and reduced consensus throughput. The attack requires no on-chain cost when using the rejected transaction path.

## Evidence

### Source Code

- `celestia-app/app/check_tx.go` -- handleBlobCheckTx calls ValidateBlobTx before the ante handler chain
- `celestia-app/x/blob/types/blob_tx.go` -- ValidateBlobTx calls CreateParallelCommitments
- `celestia-app/x/blob/types/payforblob.go` -- ValidateBasic has no maximum blob count check
- `celestia-app/app/ante/ante.go` -- ante chain order confirms gas deduction happens after commitment computation

## Mitigations

Recommended fixes include adding a MaxBlobsPerPFB cap to ValidateBasic, moving commitment computation to after signature verification in the ante chain, and adding blob count-based early rejection in CheckTx before any expensive computation.
