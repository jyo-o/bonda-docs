# CEL-D14: TxCache Bypass Forcing Full Commitment Recomputation in ProcessProposal

{% hint style="info" %}
**Severity**: Low · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

During ProcessProposal, ValidateBlobTxWithCache checks the TxCache to skip commitment recomputation for blob transactions that already passed CheckTx. If a transaction is found in the cache, the expensive CreateParallelCommitments step is skipped. A malicious proposer can include blob transactions that did not pass through other validators' CheckTx, forcing non-proposer validators to perform full commitment computation.

However, the practical impact is limited by the data square size constraint. Total block data is bounded by the square size (currently ODS 128, meaning a maximum of approximately 8 MiB per block). The original concern that 200 maximum-size PFBs could force 1.6 GiB of computation is impossible because the total data cannot exceed the square capacity. Furthermore, commitment computation is parallelized across runtime.NumCPU()*2 workers, completing the 8 MiB computation in approximately hundreds of milliseconds.

The threat represents a real asymmetry between proposer and validator workloads, but the square size constraint and parallel computation make the actual CPU overhead minor.

## Prerequisites

- One active validator with minimum stake who is selected as block proposer

## Attack Scenario

1. A malicious validator is selected as the block proposer.
2. The proposer includes blob transactions that were not broadcast to the mempool and therefore are not in other validators' TxCache.
3. Non-proposer validators receive the block proposal during ProcessProposal.
4. ValidateBlobTxWithCache finds no cache entries for these transactions and falls through to full ValidateBlobTx, computing commitments for all blobs.
5. Total block data is limited to approximately 8 MiB by the square size, and computation completes in hundreds of milliseconds with parallel workers.

## Impact

Minor additional CPU load on non-proposer validators during ProcessProposal. The square size constraint prevents the computation from becoming a meaningful burden, and the parallelized commitment computation handles 8 MiB in sub-second time.

## Evidence

### Source Code

- `celestia-app/app/process_proposal.go` -- ValidateBlobTxWithCache: cache miss triggers full ValidateBlobTx
- `celestia-app/app/check_tx.go` -- handleBlobCheckTx calls txCache.Set on successful CheckTx
- `celestia-app/pkg/appconsts/app_consts.go` -- MaxPFBMessages=200, but total data bounded by square size

## Mitigations

Recommended fixes include limiting the ratio of uncached transactions allowed in ProcessProposal, enforcing a timeout on commitment computation, and adding lightweight pre-verification for TxCache misses.
