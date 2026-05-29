# CEL-D03: blacklistedHashes Unbounded Growth — Light Node OOM via Fake DataHash Injection

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: poc_verified
{% endhint %}

## Overview

The SHREX peer manager's blacklistedHashes (map[string]bool) has only addition paths and no deletion paths. shrexsub message validation checks only height!=0, non-empty EDS, and 32-byte hash length without verifying whether the DataHash actually exists on-chain. An attacker injecting unique fake 32-byte DataHashes causes each to create an unvalidated pool. After PoolValidationTimeout (2 minutes), cleanUp() deletes the pool but permanently adds the hash to blacklistedHashes[h]=true. In manager.go, delete() applies only to m.pools; no delete() for m.blacklistedHashes exists anywhere in the codebase. Bridge nodes do not use the WithShrexSubPools path (p2p_constructors.go:58), so direct targets are limited to Light nodes.

## Core Invariants Affected

`data_recoverability`

Light node memory exhaustion -> DAS sampling halt -> DA verification disabled for that node. Bridge nodes are unaffected.

## Prerequisites

One node with P2P network access. No fees required. Same peer can inject indefinitely without blocking (see CEL-D06).

## Attack Scenario

**Condition**: P2P connection to Light node + repeated unique fake DataHash injection. Peer blocking disabled by default.

**Example**: Local PoC verified: N unique fake hashes injected -> N unvalidated pools created -> timeout then cleanUp() -> blacklistedHashes length increases by N, pools deleted but hashes persist. Defaults: PoolValidationTimeout=2min, GcInterval=30s.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Medium |
| Likelihood | Conditional (P2P peer access + repeated unique hash injection; no fee needed; peer blocking disabled by default) |
| Scope | implementation |
| Target | Process |
| Core Invariants | data_recoverability |

## Code References

- [`celestia-node/share/shwap/p2p/shrex/peers/manager.go:78 (blacklistedHashes map[string]bool)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go#L78)
- [`celestia-node/share/shwap/p2p/shrex/peers/manager.go:523 (cleanUp: m.blacklistedHashes[h]=true, 유일한 write 경로)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go#L523)
- [`celestia-node/share/shwap/p2p/shrex/peers/manager.go:504,511,517 (delete는 m.pools에만 적용)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go:504,511,517)
- [`celestia-node/share/shwap/p2p/shrex/shrexsub/pubsub.go:114 (height/emptyEDS/length만 검증)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/shrexsub/pubsub.go#L114)
- [`celestia-node/share/root.go:28-33 (DataHash.Validate: len==32만 확인)`](https://github.com/celestiaorg/celestia-node/blob/main/share/root.go#L28-L33)
- [`celestia-node/nodebuilder/share/p2p_constructors.go:58 (Bridge 제외)`](https://github.com/celestiaorg/celestia-node/blob/main/nodebuilder/share/p2p_constructors.go#L58)
- Commit: `celestia-node f8cefbe3e5bd3e144a414cb2140dd223ec6191c6`

## Verification & Evidence

**Status**: poc_verified

Full code audit completed (commit f8cefbe). Absence of delete() for blacklistedHashes confirmed. Local unit reproduction completed. Isolated Light node network PoC is feasible but not executed. Real-world exploitability on public network requires further testing.

**PoC References**:

- 로컬 단위 PoC: unique fake hash 주입 → cleanUp 후 blacklistedHashes 영구 증가 확인

## Mitigations

No current defense. Recommendations: (1) Add TTL or max size cap to blacklistedHashes, (2) Per-peer rate limit on new hash ingestion, (3) Change EnableBlackListing default to true (CEL-D06), (4) Add header store existence check to shrexsub validation.
