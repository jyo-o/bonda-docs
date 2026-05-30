# CEL-D11: Unbounded pendingSeenTracker Memory Growth via Known Account Addresses

{% hint style="warning" %}
**Severity**: High (7.5/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

The CAT mempool's `pendingSeenTracker` in celestia-core has a per-signer cap of 128 entries but no global cap on the number of distinct signers, allowing the `perSigner` map to grow without bound. An attacker can use real on-chain account addresses with future sequence numbers to create pending entries that persist indefinitely, eventually causing OOM on consensus nodes.

## Description

The `pendingSeenTracker` at `celestia-core/mempool/cat/pending.go` tracks `SeenTx` messages from peers using a `perSigner` map with `defaultPendingSeenPerSigner=128` entries per signer but no global signer count cap and no TTL.

```go
// celestia-core/mempool/cat/reactor.go:397-437
// @audit SeenTx handler accepts msg.Signer without signature verification
// @audit but queries application state via querySequenceFromApplication
// @audit Line 425 TODO: "add per-peer limits or something similar to pendingSeen to prevent overflowing"
```

The validation flow works as follows:

1. `SeenTx` handler receives `msg.Signer` without signature verification
2. `querySequenceFromApplication` (`reactor.go:824-837`) checks the expected sequence for the address
3. If `resp.Sequence==0` or the query fails (non-existent accounts), the entry is rejected (`haveExpected=false`)
4. If the address exists on-chain (sequence > 0) and the message uses a future sequence number, the entry passes validation and creates a pending entry

The attack leverages real on-chain account addresses (obtainable via chain scanning) with future sequence numbers higher than expected. These entries persist indefinitely: there is no TTL, no eviction mechanism, and entries remain until the sequence actually catches up or 128 entries for the same signer push them out. With N known accounts, the map can reach N x 128 entries.

## Proof of Concept

PR `celestia-core#3061` (DRAFT, 2026-05-22) adds per-peer cap of 10,000 and TTL of 2 minutes for eviction, but does not add a global signer count cap. Not yet merged.

## Impact

Consensus node OOM crash leading to consensus participation halt and liveness degradation. The attack requires no fees and can be executed from a single P2P peer. With mainnet's many known accounts with positive sequences, a single peer can recycle these addresses to inflate the `perSigner` map into the gigabyte range.

### CVSS 3.1

**Score**: 7.5/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via P2P SeenTx messages over the network |
| AC (Attack Complexity) | L (Low) | Only requires a list of known on-chain addresses (publicly available via chain scanning) and a P2P connection |
| PR (Privileges Required) | N (None) | No privileges required; any P2P peer can send SeenTx messages |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted consensus node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact; the attack targets availability only |
| A (Availability) | H (High) | OOM crash halts consensus participation entirely |

## Recommendation

1. Add a global cap on the number of distinct signers tracked in the `perSigner` map (not addressed in PR #3061).
2. Merge PR #3061 which adds per-peer caps (10,000) and TTL eviction (2 minutes) for pending entries.
3. Add per-peer rate limits on `SeenTx` message ingestion to bound the injection rate from any single peer.
