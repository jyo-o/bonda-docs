# CEL-D11: Unbounded pendingSeenTracker Memory Growth via Known Account Addresses

{% hint style="warning" %}
**Severity**: High · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

The CAT mempool in celestia-core uses a pendingSeenTracker to track SeenTx messages from peers. While this tracker has a per-signer cap of 128 entries, there is no global cap on the number of distinct signers. This allows the perSigner map to grow without bound.

The SeenTx handler in reactor.go accepts msg.Signer without signature verification, but internally queries the application state via querySequenceFromApplication to retrieve the expected sequence for the address. If the response sequence is zero or the query fails (which happens for new or non-existent accounts), the entry is rejected. This blocks mass injection of fake signer addresses.

However, an attacker can use real on-chain account addresses (which have sequence greater than zero) combined with future sequence numbers higher than expected. These combinations pass the validation check and create pending entries that persist indefinitely: there is no TTL, no eviction mechanism, and entries remain until the sequence actually catches up or 128 entries for the same signer push them out. Since mainnet has many known accounts with positive sequences, a single peer can recycle these addresses to inflate the perSigner map into the gigabyte range. The TODO comment at reactor.go line 425 explicitly acknowledges this problem.

## Prerequisites

- One P2P-connected node
- A list of on-chain account addresses obtainable via chain scanning
- No fees required

## Attack Scenario

1. The attacker collects a list of known on-chain account addresses with sequence greater than zero by scanning the chain.
2. The attacker connects to a target consensus node via P2P.
3. For each known signer address, the attacker sends a SeenTx message with a future sequence number.
4. The target node queries the application state, confirms the address has a positive sequence, and creates a pending entry.
5. The attacker repeats with many known addresses, each creating up to 128 slots in the perSigner map.
6. With N known accounts, the map can reach N x 128 entries, inflating to gigabytes and eventually causing OOM.

## Impact

Consensus node OOM crash leading to consensus participation halt and liveness degradation. The attack requires no fees and can be executed from a single P2P peer.

## Evidence

### Source Code

- `celestia-core/mempool/cat/pending.go` -- perSigner map with defaultPendingSeenPerSigner=128, no global signer cap, no TTL
- `celestia-core/mempool/cat/reactor.go:397-437` -- SeenTx handler: applies querySequenceFromApplication filter then calls pendingSeen.add. Line 425 TODO: "add per-peer limits or something similar to pendingSeen to prevent overflowing"
- `celestia-core/mempool/cat/reactor.go:824-837` -- querySequenceFromApplication: returns haveExpected=false when resp.Sequence==0 or on error

### PoC Testing

- PR celestia-core#3061 (DRAFT, 2026-05-22): adds per-peer cap of 10,000 and TTL of 2 minutes for eviction, but does not add a global signer count cap. Not yet merged.

## Mitigations

PR #3061 (DRAFT, 2026-05-22) adds per-peer caps and TTL eviction but omits a global signer count cap. Until this PR is merged, there is no defense against this attack. Recommended additional fixes include adding a global cap on the number of distinct signers tracked.
