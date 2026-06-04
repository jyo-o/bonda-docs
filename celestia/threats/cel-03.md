# CEL-03: Unbounded blacklistedHashes Growth Causing Light Node OOM

{% hint style="warning" %}
**Severity**: High (7.5/10) · **Likelihood**: Moderate · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

The SHREX peer manager creates an unvalidated `syncPool` for every DataHash in an inbound shrexsub message before checking whether the hash exists on-chain, and the `blacklistedHashes` map that absorbs timed-out pools has no deletion path. An attacker broadcasting unique fake 32-byte DataHashes exhausts a light node's memory along two paths: `m.pools` grows immediately during the flood, and `blacklistedHashes` accumulates permanently afterward. A live reproduction drove a memory-capped light node to a kernel OOM kill in 79 seconds via the pool path.

## Description

![CEL-03 data flow — Celestia Read path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/celestia/assets/dfd/celestia-read.png)

*Data flow — Celestia Read: Light Node.*

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

Because validation never checks chain existence, `Manager.Validate()` calls `getOrCreatePool()` for every fake hash before the data is known to exist, allocating a roughly 1.5 KB `syncPool` per unique hash. This is the faster of the two memory-exhaustion paths: `m.pools` grows immediately during the flood, while `blacklistedHashes` accumulates permanently after each pool's 2-minute validation timeout.

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go — getOrCreatePool
// @audit a new ~1.5 KB syncPool is allocated per unique DataHash before any chain-existence check; m.pools has no cap
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go
p, ok := m.pools[datahash]
if !ok {
    p = &syncPool{height: height, pool: newPool(m.params.PeerCooldown), createdAt: time.Now()}
    m.pools[datahash] = p // no global or per-height cap
}
```

Bridge nodes are not affected because they do not use the `WithShrexSubPools` path at `celestia-node/nodebuilder/share/p2p_constructors.go:58`. The attack targets Light nodes exclusively. Since `EnableBlackListing` defaults to `false` (see CEL-06), the attacking peer is never blocked and can inject hashes indefinitely.

## Proof of Concept

A live isolated-network reproduction drove a memory-capped light node to a kernel OOM kill from a single unauthenticated attacker peer. See [Verification Evidence](../evidence.md#cel-03-shrex-unvalidated-pool-and-blacklist-exhaustion-poc_verified) for the full setup and measurements.

- **Pool path (fast)**: at 5,000 fake hashes/s against a 600 MB-capped light node, `m.pools` peaked at 388,116 entries and the kernel OOM-killer terminated the node at t ≈ 79 s.
- **Blacklist path (permanent)**: at 4,000/s against a 1.4 GB cap, `blacklistedHashes` reached 2,594,020 entries and OOM-killed the node at t ≈ 865 s; uncapped, roughly 1.18 GB stays resident after the attack stops and is never reclaimed.
- **Asymmetry**: the attacker only generates and broadcasts random 32-byte hashes; one peer is sufficient because peer blacklisting is disabled by default (CEL-06).

## Impact

A single unauthenticated peer exhausts a light node's memory and triggers a kernel OOM kill, halting that node's DAS sampling and DA verification. A live reproduction reached OOM in 79 seconds via the pool path and in roughly 14 minutes via the blacklist path; the blacklist memory is never reclaimed without a restart. Bridge nodes are unaffected. shrexsub uses FloodSub, so an attacker connected to many light nodes can drive the same flood into all of them at once, degrading network-wide DAS coverage, though the impact does not self-propagate because victims return ValidationIgnore.

Affects the **Verifiability** axis — memory exhaustion halts the light node's data availability sampling — where it produces a Layer 3 deduction while unpatched.

### CVSS 3.1

**Score**: 7.5/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via P2P shrexsub messages over the network |
| AC (Attack Complexity) | L (Low) | Generating unique fake 32-byte hashes and sending shrexsub messages is straightforward |
| PR (Privileges Required) | N (None) | No privileges required; any P2P peer can send shrexsub messages |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted light node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | H (High) | A single peer drives a memory-capped light node to a kernel OOM kill in 79 seconds via the pool path; the node crashes and the blacklist memory is not reclaimed without a restart |

## Recommendation

1. Add a TTL or maximum size cap to `blacklistedHashes` to prevent unbounded growth.
2. Implement per-peer rate limits on new hash ingestion to bound the injection rate from any single peer.
3. Change the `EnableBlackListing` default to `true` to disconnect peers that send invalid data (see CEL-06).
4. Add a header store existence check to shrexsub validation to reject hashes for non-existent blocks before pool creation.
