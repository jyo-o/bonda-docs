# CEL-03: Unbounded blacklistedHashes Growth Causing Light Node OOM

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **Likelihood**: Low · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

The SHREX peer manager maintains a `blacklistedHashes` map (`map[string]bool`) that tracks DataHashes identified as invalid. This map has addition paths but no deletion paths anywhere in the codebase. An attacker can inject unique fake 32-byte DataHashes via shrexsub messages that each create unvalidated pools; after the validation timeout, pools are cleaned up but hashes accumulate permanently in the blacklist map, eventually exhausting light node memory.

## Description

The unbounded growth is caused by a cleanup function that adds to the blacklist but never removes from it:

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go — Manager struct
// @audit blacklistedHashes has no deletion path anywhere in the codebase
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go
type Manager struct {
    // ...
    blacklistedHashes map[string]bool // @audit grows without bound
    // ...
}
```

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go — cleanUp
// @audit The ONLY write path: sets blacklistedHashes[h]=true, never deletes
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go
func (m *Manager) cleanUp() []peer.ID {
    // ...
    for h, p := range m.pools {
        if p.isValidatedDataHash.Load() {
            if p.height < m.storeFrom.Load() {
                delete(m.pools, h)   // @audit deletes pool, NOT blacklistedHashes
            }
            continue
        }
        if time.Since(p.createdAt) > m.params.PoolValidationTimeout {
            delete(m.pools, h)       // @audit deletes pool
            m.blacklistedHashes[h] = true  // @audit adds to blacklist — never removed
            for _, peer := range p.peersList {
                addToBlackList[peer] = struct{}{}
            }
        }
    }
    // ...
}
```

The shrexsub message validation is insufficient to prevent fake hash injection:

```go
// celestia-node/share/shwap/p2p/shrex/shrexsub/pubsub.go — validate
// @audit Only checks height != 0, non-empty EDS, and hash length == 32
// @audit Does NOT verify whether the DataHash exists on-chain
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/shrexsub/pubsub.go
func (v ValidatorFn) validate(ctx context.Context, p peer.ID, msg *pubsub.Message) pubsub.ValidationResult {
    var pbmsg pb.RecentEDSNotification
    if err := pbmsg.Unmarshal(msg.Data); err != nil {
        return pubsub.ValidationReject
    }
    n := Notification{DataHash: pbmsg.DataHash, Height: pbmsg.Height}
    if n.Height == 0 || n.DataHash.IsEmptyEDS() || n.DataHash.Validate() != nil {
        return pubsub.ValidationReject
        // @audit Validate() checks only len==32 — any 32-byte value passes
    }
    return v(ctx, p, n)
}
```

Bridge nodes are not affected because they do not use the `WithShrexSubPools` path at `celestia-node/nodebuilder/share/p2p_constructors.go:58`. The attack targets Light nodes exclusively. Since `EnableBlackListing` defaults to `false` (see CEL-06), the attacking peer is never blocked and can inject hashes indefinitely.

## Proof of Concept

Local unit PoC confirmed. See [Verification Evidence](../evidence.md#cel-03-blacklistedhashes-growth-poc_verified) for details. N unique fake hashes were injected; after `cleanUp`, the `blacklistedHashes` map length increased by N while pools were correctly deleted. Isolated Light node network PoC is feasible but was not executed.

## Impact

Light node memory exhaustion leading to DAS sampling halt and loss of DA verification capability for that node. Bridge nodes are unaffected. The attack requires no fees and can be sustained indefinitely from a single peer due to disabled blacklisting (CEL-06).

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
3. Change the `EnableBlackListing` default to `true` to disconnect peers that send invalid data (see CEL-06).
4. Add a header store existence check to shrexsub validation to reject hashes for non-existent blocks before pool creation.
