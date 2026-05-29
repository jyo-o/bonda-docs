# CEL-D11: pendingSeenTracker Unbounded Memory Growth — Node OOM via Known On-chain Accounts + Future Sequence SeenTx

{% hint style="info" %}
**Severity**: High · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

The CAT mempool's pendingSeenTracker in celestia-core has a per-signer cap of 128 entries but no global cap on the number of signers. The reactor.go SeenTx handler accepts msg.Signer without signature verification but internally queries querySequenceFromApplication(msg.Signer) to look up the address's expected sequence. If the response sequence is 0 or the query fails (including new/non-existent accounts), haveExpected=false is returned and pendingSeen.add is not entered, blocking mass fake signer injection. However, combining actual on-chain account addresses (sequence>0) with future sequences higher than the current expected sequence creates pending entries. These entries have no TTL or eviction and persist in the map until the sequence catches up or the 128th entry for the same signer pushes it out. Since mainnet has many known accounts (sequence>0), a single peer can recycle known signer lists to inflate the perSigner map without bound. The TODO comment at reactor.go line 425 directly acknowledges this issue.

## Core Invariants Affected

`consensus_liveness`

Consensus node OOM -> consensus participation halt -> liveness degradation.

## Prerequisites

One P2P-connected node. On-chain account address collection (obtainable via chain scanning). No fees required.

## Attack Scenario

**Condition**: CAT mempool-enabled node with P2P connection + possession of known on-chain account address list

**Example**: Known signer A -> seq 999 SeenTx sent -> perSigner[A] entry created. Known signer B -> seq 999 sent -> perSigner[B] created. N known accounts x 128 slots x entry size -> GB-scale memory inflation.

## Impact

| Metric | Value |
|--------|-------|
| Severity | High |
| Likelihood | Conditional (1 P2P peer + known on-chain signer list required) |
| Scope | implementation |
| Target | Process |
| Core Invariants | consensus_liveness |

## Code References

- [`celestia-core/mempool/cat/pending.go (perSigner map, defaultPendingSeenPerSigner=128, no global signer cap, no TTL)`](https://github.com/celestiaorg/celestia-core/blob/main/mempool/cat/pending.go)
- [`celestia-core/mempool/cat/reactor.go:397-437 (SeenTx handler: querySequenceFromApplication 필터 후 pendingSeen.add, 425번줄 TODO: 'add per-peer limits or something similar to pendingSeen to prevent overflowing')`](https://github.com/celestiaorg/celestia-core/blob/main/mempool/cat/reactor.go#L397-L437)
- [`celestia-core/mempool/cat/reactor.go:824-837 (querySequenceFromApplication: resp.Sequence==0이면 haveExpected=false)`](https://github.com/celestiaorg/celestia-core/blob/main/mempool/cat/reactor.go#L824-L837)
- [PR #3061: 2026-05-22 DRAFT, 'fix(mempool/cat): bound pendingSeen against resource exhaustion'](https://github.com/celestiaorg/celestia-core/pull/3061)

## Verification & Evidence

**Status**: code_verified

pending.go directly confirmed: defaultPendingSeenPerSigner=128 (line 11), perSigner map has no TTL or global signer cap. reactor.go directly confirmed: querySequenceFromApplication (line 824-837) returns haveExpected=false when resp.Sequence==0 or on error; TODO comment at line 425 original text confirmed. PR celestia-core#3061 DRAFT status and diff confirmed: seenTxPerPeerLimit=10,000 (cache.go), pendingSeenTTL=2*time.Minute (pending.go) added; global signer count cap not added.

## Mitigations

PR #3061 (DRAFT, 2026-05-22): adds per-peer cap (10,000) + TTL (2 min) eviction. Global signer cap not added. No defense before merge.
