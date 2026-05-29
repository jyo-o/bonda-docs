# CEL-D13: CheckTx Pre-gas Commitment Computation — Unlimited Blob Count

{% hint style="info" %}
**Severity**: High · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

celestia-app's handleBlobCheckTx executes ValidateBlobTx followed by CreateParallelCommitments before gas deduction. MsgPayForBlobs.ValidateBasic() has no blob count limit, so a BlobTx containing thousands of 1-byte blobs forces NMT subtree + Merkle root computation for each blob. If the signature is invalid or fees insufficient, computation is wasted but gas is not charged. Within the MaxTxSize=8 MiB limit, thousands of tiny blobs are possible. The ante chain order is: SetUpContext > ... > DeductFee > SigVerify > MinGasPFB > BlobShare, so commitment computation executes before this chain.

## Core Invariants Affected

`consensus_liveness`

Validator CheckTx CPU exhaustion leads to mempool processing delays and consensus throughput degradation.

## Prerequisites

RPC access. Invalid signature transactions can also force commitment computation.

## Attack Scenario

**Condition**: Attacker submits BlobTx with many tiny blobs repeatedly

**Example**: 1-byte blob x 1000 = ~70KB tx (including metadata). NMT commitment x 1000 = significant CPU. Gas ~4M but uncharged with invalid signature.

## Impact

| Metric | Value |
|--------|-------|
| Severity | High |
| Likelihood | Immediate (send BlobTx; gas is normally charged but can force computation with invalid tx at zero cost) |
| Scope | implementation |
| Target | Process |
| Core Invariants | consensus_liveness |

## Code References

- [`celestia-app/app/check_tx.go (handleBlobCheckTx calls ValidateBlobTx before ante chain)`](https://github.com/celestiaorg/celestia-app/blob/main/app/check_tx.go)
- [`celestia-app/x/blob/types/blob_tx.go (ValidateBlobTx → CreateParallelCommitments)`](https://github.com/celestiaorg/celestia-app/blob/main/x/blob/types/blob_tx.go)
- [`celestia-app/x/blob/types/payforblob.go (ValidateBasic: no max blob count)`](https://github.com/celestiaorg/celestia-app/blob/main/x/blob/types/payforblob.go)
- [`celestia-app/app/ante/ante.go (ante chain order)`](https://github.com/celestiaorg/celestia-app/blob/main/app/ante/ante.go)

## Verification & Evidence

**Status**: code_verified

celestia-app main branch check_tx.go, blob_tx.go, payforblob.go code confirmed. Absence of blob count cap in ValidateBasic confirmed.

## Mitigations

Recommendations: (1) Add MaxBlobsPerPFB cap to ValidateBasic, (2) Move commitment computation after signature verification, (3) Early rejection in CheckTx based on blob count.
