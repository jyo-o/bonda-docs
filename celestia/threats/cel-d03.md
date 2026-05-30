# CEL-D03: Unbounded blacklistedHashes Growth Causing Light Node OOM

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D · **Status**: poc_verified
{% endhint %}

## Overview

The SHREX peer manager maintains a map called blacklistedHashes (map[string]bool) that tracks DataHashes identified as invalid. This map has addition paths but no deletion paths anywhere in the codebase. When the cleanUp function runs after the PoolValidationTimeout (2 minutes), it deletes the associated pool but permanently adds the hash to blacklistedHashes.

The shrexsub message validation only checks that the height is non-zero, the EDS is non-empty, and the hash length is 32 bytes. It does not verify whether the DataHash actually exists on-chain. An attacker can inject unique fake 32-byte DataHashes that each create an unvalidated pool. After the validation timeout, the pools are cleaned up but the hashes accumulate permanently in the blacklist map, eventually exhausting the node's memory.

Bridge nodes are not affected because they do not use the WithShrexSubPools path. The attack targets Light nodes exclusively. Since EnableBlackListing defaults to false (see CEL-D06), the attacking peer is never blocked and can inject hashes indefinitely.

## Prerequisites

- One node with P2P network access to the target Light node
- No fees required
- Same peer can inject indefinitely without being blocked under default settings

## Attack Scenario

1. The attacker connects to a target Light node via P2P.
2. The attacker sends shrexsub messages containing unique fake 32-byte DataHashes.
3. Each fake hash creates an unvalidated pool in the peer manager.
4. After the PoolValidationTimeout (2 minutes), cleanUp runs: pools are deleted, but each hash is permanently added to blacklistedHashes.
5. The attacker repeats with new unique hashes. Since EnableBlackListing is false by default, the peer is never disconnected.
6. The blacklistedHashes map grows without bound, eventually causing the Light node to run out of memory.

## Impact

Light node memory exhaustion leading to DAS sampling halt and loss of DA verification capability for that node. Bridge nodes are unaffected. A local PoC confirmed that N unique fake hashes result in N permanent entries in blacklistedHashes after cleanup.

## Evidence

### Source Code

- `celestia-node/share/shwap/p2p/shrex/peers/manager.go:78` -- blacklistedHashes map[string]bool declaration
- `celestia-node/share/shwap/p2p/shrex/peers/manager.go:523` -- cleanUp function: the only write path that sets blacklistedHashes[h]=true
- `celestia-node/share/shwap/p2p/shrex/peers/manager.go:504,511,517` -- delete calls apply only to m.pools, not to blacklistedHashes
- `celestia-node/share/shwap/p2p/shrex/shrexsub/pubsub.go:114` -- message validation checks only height, empty EDS, and hash length
- `celestia-node/share/root.go:28-33` -- DataHash.Validate checks only len==32
- `celestia-node/nodebuilder/share/p2p_constructors.go:58` -- Bridge nodes excluded from ShrexSubPools path

### PoC Testing

- Local unit PoC confirmed: N unique fake hashes injected, after cleanUp blacklistedHashes length increases by N while pools are deleted. Isolated Light node network PoC is feasible but was not executed.

## Mitigations

No current defense exists. Recommended fixes include adding a TTL or maximum size cap to blacklistedHashes, implementing per-peer rate limits on new hash ingestion, changing the EnableBlackListing default to true (see CEL-D06), and adding a header store existence check to shrexsub validation.
