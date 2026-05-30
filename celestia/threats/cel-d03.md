# CEL-D03: Unbounded blacklistedHashes Growth Causing Light Node OOM

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Status**: poc_verified
{% endhint %}

## Summary

The SHREX peer manager maintains a `blacklistedHashes` map (`map[string]bool`) that tracks DataHashes identified as invalid. This map has addition paths but no deletion paths anywhere in the codebase. An attacker can inject unique fake 32-byte DataHashes via shrexsub messages that each create unvalidated pools; after the validation timeout, pools are cleaned up but hashes accumulate permanently in the blacklist map, eventually exhausting light node memory.

## Description

The unbounded growth is caused by a cleanup function that adds to the blacklist but never removes from it:

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go:78
// @audit blacklistedHashes map[string]bool declaration — no deletion path exists
```

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go:523
// @audit cleanUp function: the ONLY write path that sets blacklistedHashes[h]=true
```

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go:504,511,517
// @audit delete calls apply only to m.pools, NOT to blacklistedHashes
```

The shrexsub message validation is insufficient to prevent fake hash injection:

```go
// celestia-node/share/shwap/p2p/shrex/shrexsub/pubsub.go:114
// @audit Message validation checks only: height != 0, EDS non-empty, hash length == 32
// @audit Does NOT verify whether the DataHash exists on-chain
```

```go
// celestia-node/share/root.go:28-33
// @audit DataHash.Validate checks only len==32
```

Bridge nodes are not affected because they do not use the `WithShrexSubPools` path (`celestia-node/nodebuilder/share/p2p_constructors.go:58`). The attack targets Light nodes exclusively. Since `EnableBlackListing` defaults to `false` (see CEL-D06), the attacking peer is never blocked and can inject hashes indefinitely.

## Proof of Concept

Local unit PoC confirmed: N unique fake hashes injected, after `cleanUp` the `blacklistedHashes` length increases by N while pools are deleted. Isolated Light node network PoC is feasible but was not executed.

## Impact

Light node memory exhaustion leading to DAS sampling halt and loss of DA verification capability for that node. Bridge nodes are unaffected. The attack requires no fees and can be sustained indefinitely from a single peer due to disabled blacklisting (CEL-D06).

### CVSS 3.1

**Score**: 5.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via P2P shrexsub messages over the network |
| AC (Attack Complexity) | L (Low) | Generating unique fake 32-byte hashes and sending shrexsub messages is straightforward |
| PR (Privileges Required) | N (None) | No privileges required; any P2P peer can send shrexsub messages |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted light node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | L (Low) | Light node memory exhaustion is gradual; the 2-minute cleanup cycle and per-hash overhead mean OOM takes sustained effort |

## Recommendation

1. Add a TTL or maximum size cap to `blacklistedHashes` to prevent unbounded growth.
2. Implement per-peer rate limits on new hash ingestion to bound the injection rate from any single peer.
3. Change the `EnableBlackListing` default to `true` to disconnect peers that send invalid data (see CEL-D06).
4. Add a header store existence check to shrexsub validation to reject hashes for non-existent blocks before pool creation.
