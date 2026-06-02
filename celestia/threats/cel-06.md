# CEL-06: Peer Blacklisting Disabled by Default Allowing Sybil Reconnection

{% hint style="info" %}
**Severity**: Medium · **Category**: Operational Risk · **Status**: verified
{% endhint %}

## Summary

The SHREX peer manager's `EnableBlackListing` flag defaults to `false`, meaning peers that send invalid data are logged but never actually disconnected or blocked. This default undermines the defense assumptions of multiple other threats (CEL-03, CEL-07) that cite peer blacklisting as an existing defense mechanism, acting as a force multiplier for these vulnerabilities.

## Description

![CEL-06 data flow — Celestia Read path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/celestia/assets/dfd/celestia-read.png)

*Data flow — Celestia Read: Light Node.*

The blacklisting mechanism exists in code but is disabled by default:

```go
// celestia-node/share/shwap/p2p/shrex/peers/options.go — DefaultParameters
// @audit EnableBlackListing defaults to false with explicit TODO
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/options.go
func DefaultParameters() *Parameters {
    return &Parameters{
        PoolValidationTimeout: 2 * time.Minute,
        PeerCooldown:          3 * time.Second,
        GcInterval:            time.Second * 30,
        // blacklisting is off by default
        // TODO(@walldiss): enable blacklisting once all related issues are resolved
        EnableBlackListing: false,
    }
}
```

When `EnableBlackListing` is `false`, the `blacklistPeers` function logs but skips actual blocking:

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go — blacklistPeers
// @audit When EnableBlackListing is false, BlockPeer() and ClosePeer() are skipped
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go
func (m *Manager) blacklistPeers(reason blacklistPeerReason, peerIDs ...peer.ID) {
    for _, peerID := range peerIDs {
        log.Debugw("blacklisting peer", "peer", peerID.String(), "reason", reason)
        if !m.params.EnableBlackListing {
            continue // @audit logs the event but does NOT block or disconnect
        }
        m.nodes.remove(peerID)
        m.connGater.BlockPeer(peerID)
        m.host.Network().ClosePeer(peerID)
    }
}
```

Verified at commit `celestia-node f8cefbe3e5bd3e144a414cb2140dd223ec6191c6`.

The result is that a malicious peer can send invalid data, get logged, and immediately continue its attack or reconnect without any penalty. This undermines defenses for:
- **CEL-03**: `blacklistedHashes` unbounded growth relies on eventual peer blocking to limit injection rate
- **CEL-07**: DAS Selective Disclosure cites peer blacklisting as a defense, but it does not function under default settings

## Proof of Concept

No proof of concept was conducted for this threat. The default configuration is directly verifiable in the source code at the referenced file and line numbers.

## Impact

Defense mechanism bypass that enables unlimited retries from malicious peers. The default configuration itself is the threat condition, requiring no separate exploit. This is not a direct DA invariant violation but an enabler that increases the severity of CEL-03 and CEL-07.

Affects the Liveness axis. It is tracked as an Operational Indicator shown alongside the risk pentagon, not as a deduction from the structural score.

## Recommendation

1. Change the `EnableBlackListing` default to `true` to activate peer disconnection for invalid data senders.
2. Publish a roadmap for resolving the TODO-referenced "related issues" that are blocking the default change.
3. Add a recommendation for `EnableBlackListing=true` in operator documentation until the default is changed.
4. Implement per-peer rate limits that function independently of the blacklisting mechanism as a defense-in-depth measure.
