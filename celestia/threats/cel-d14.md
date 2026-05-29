# CEL-D14: ProcessProposal TxCache Bypass — Malicious Proposer Forces Full Commitment Recomputation

{% hint style="info" %}
**Severity**: Low · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

In ProcessProposal, ValidateBlobTxWithCache skips commitment recomputation for blob txs present in TxCache. A malicious proposer can include blob txs that did not pass other validators' CheckTx, forcing non-proposer validators to perform full commitment computation. However, total block data is limited by square size (current ODS 128 -> max ~8 MiB), and even with MaxPFBMessages=200, total data cannot exceed the square. The original claim of '200 x 8 MiB = 1.6 GiB' is impossible. Commitment computation is parallelized with runtime.NumCPU()*2 workers, taking only hundreds of milliseconds for 8 MiB of data.

## Core Invariants Affected

`consensus_liveness`

Asymmetry between proposer and validator exists, but square size limits make actual CPU load minor. No meaningful impact on consensus liveness.

## Prerequisites

One active validator with minimum stake.

## Attack Scenario

**Condition**: Malicious validator selected as proposer includes uncached blob tx in block proposal. Total data limited by square size.

**Example**: MaxPFBMessages=200 but total block data is limited to ~8 MiB at ODS 128. CreateParallelCommitments runs with NumCPU()*2 workers in parallel. 8 MiB commitment computation takes ~hundreds of milliseconds.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Low |
| Likelihood | Low (requires being selected as proposer + actual computation load limited by square size) |
| Scope | implementation |
| Target | Process |
| Core Invariants | consensus_liveness |

## Code References

- [`celestia-app/app/process_proposal.go (ValidateBlobTxWithCache: cache miss → full ValidateBlobTx)`](https://github.com/celestiaorg/celestia-app/blob/main/app/process_proposal.go)
- [`celestia-app/app/check_tx.go (handleBlobCheckTx: txCache.Set on CheckTx)`](https://github.com/celestiaorg/celestia-app/blob/main/app/check_tx.go)
- [`celestia-app/pkg/appconsts/app_consts.go (MaxPFBMessages=200)`](https://github.com/celestiaorg/celestia-app/blob/main/pkg/appconsts/app_consts.go)

## Verification & Evidence

**Status**: code_verified

process_proposal.go ValidateBlobTxWithCache code confirmed. Full validation path on cache miss confirmed.

## Mitigations

Recommendations: (1) Limit uncached tx ratio in ProcessProposal, (2) Enforce commitment computation timeout, (3) Lightweight pre-verification on TxCache miss.
