# CEL-D17: TxCache Key Mismatch — Blob Tx Cache Entry Permanent Leak Causing Validator OOM

{% hint style="info" %}
**Severity**: High · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: poc_verified
{% endhint %}

## Overview

celestia-app's TxCache stores entries keyed by sha256(inner SDK tx) during CheckTx, but deletes using sha256(full BlobTx wire bytes) during FinalizeBlock. Since PrepareProposal re-serializes blob tx via MarshalBlobTx(innerTx, blobs...), FinalizeBlock's req.Txs contain full BlobTx bytes that differ from inner SDK tx bytes. Therefore sha256(full) != sha256(inner), and cache deletion always fails. TxCache is based on sync.Map with no cap, TTL, or separate cleanup path, so entries accumulate indefinitely. Additionally, txCache.Set() executes before BaseApp.CheckTx() in CheckTx, so rejected transactions with valid blob structure but invalid nonce/fee/gas also persist in cache. In this case, attack cost is 0 TIA -- leakage occurs at CheckTx ingress rate without requiring block inclusion.

## Core Invariants Affected

`consensus_liveness`

Validator/consensus node memory exhaustion -> OOM crash -> consensus participation halt. Irreversible accumulation (no recovery except restart). Simultaneous attack on multiple validators can cause 1/3 departure -> chain liveness threat.

## Prerequisites

RPC or P2P access. The rejected tx path requires no fees. The valid tx path requires only minimum gas fees.

## Attack Scenario

**Condition**: Any path that can submit blob txs to a celestia-app node (RPC or P2P)

**Example**: Directly verified: future sequence blob tx -> checktx_code=32, cache entry persists. Zero-fee blob tx -> checktx_code=11, cache entry persists. Production path test: CheckTx then FinalizeBlock(wrappedTx) -> fromCache=true (cache not deleted confirmed). Per-entry measured memory: ~204 bytes. At 100 Mbps rejected tx rate: ~160 seconds per 1 GB leak.

## Impact

| Metric | Value |
|--------|-------|
| Severity | High |
| Likelihood | Immediate (rejected blob tx path: zero cost, requires only RPC/P2P access) |
| Scope | implementation |
| Target | Process |
| Core Invariants | consensus_liveness |

## Code References

- [`celestia-app/app/check_tx.go:63 (txCache.Set(btx.Tx) — inner SDK tx 키)`](https://github.com/celestiaorg/celestia-app/blob/main/app/check_tx.go#L63)
- [`celestia-app/app/app.go:589 (txCache.RemoveTransaction(tx) — full BlobTx 키)`](https://github.com/celestiaorg/celestia-app/blob/main/app/app.go#L589)
- [`celestia-app/app/tx_cache.go:23-27 (sha256 기반 키 생성)`](https://github.com/celestiaorg/celestia-app/blob/main/app/tx_cache.go#L23-L27)
- [`celestia-app/app/filtered_square_builder.go:193-197 (encodeBlobTxs: MarshalBlobTx 재직렬화)`](https://github.com/celestiaorg/celestia-app/blob/main/app/filtered_square_builder.go#L193-L197)
- [`celestia-app/app/process_proposal.go:251 (Exists는 inner tx 키로 정상 조회)`](https://github.com/celestiaorg/celestia-app/blob/main/app/process_proposal.go#L251)
- [Test: `celestia-app/x/blob/types/blob_tx_test.go:437-438 (기존 테스트가 blobTx.Tx를 FinalizeBlock에 전달 — 프로덕션 경로 미재현)`](https://github.com/celestiaorg/celestia-app/blob/main/x/blob/types/blob_tx_test.go#L437-L438)
- [Test: `celestia-app/app/test/integration_test.go:205 (통합 테스트에서 블록 tx가 wrapped BlobTx임을 확인)`](https://github.com/celestiaorg/celestia-app/blob/main/app/test/integration_test.go#L205)
- Commit: `celestia-app 849429e879b18f489b3a939ebe301409e0f35e09 (검증 시점 HEAD)`

## Verification & Evidence

**Status**: poc_verified

Full code path trace + sha256 hash direct computation + production path reproduction test written and executed (PASS). Rejected tx cache persistence also execution-verified. Per-entry memory measured (~204 bytes/entry). Root cause of existing tests not reproducing production path also identified.

**PoC References**:

- TestTxCacheLeakProductionPath: CheckTx → FinalizeBlock(wrappedTx) → fromCache still true (PASS)

## Mitigations

No current defense. Recommendations: (1) Re-parse blob tx via UnmarshalBlobTx in FinalizeBlock and delete using inner tx key, (2) Call txCache.Set only after BaseApp.CheckTx succeeds in CheckTx, (3) Add max size cap or TTL to TxCache.
