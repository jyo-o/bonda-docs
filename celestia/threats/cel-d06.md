# CEL-D06: Peer Blacklisting Disabled by Default Allowing Sybil Reconnection

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

The SHREX peer manager's `EnableBlackListing` flag defaults to `false`, meaning peers that send invalid data are logged but never actually disconnected or blocked. This default undermines the defense assumptions of multiple other threats (CEL-D03, CEL-S01) that cite peer blacklisting as an existing defense mechanism, acting as a force multiplier for these vulnerabilities.

## Description

The blacklisting mechanism exists in code but is disabled by default:

```go
// celestia-node/share/shwap/p2p/shrex/peers/options.go:60-62
// @audit EnableBlackListing defaults to false
// @audit TODO comment: "enable blacklisting once all related issues are resolved"
```

When `EnableBlackListing` is `false`, the `blacklistPeers` function skips the actual blocking:

```go
// celestia-node/share/shwap/p2p/shrex/peers/manager.go:416-438
// @audit blacklistPeers function: when EnableBlackListing is false,
// @audit BlockPeer() and ClosePeer() are skipped

// celestia-node/share/shwap/p2p/shrex/peers/manager.go:423-425
// @audit Gating condition: if !m.params.EnableBlackListing { continue }
```

Verified at commit `celestia-node f8cefbe3e5bd3e144a414cb2140dd223ec6191c6`.

The result is that a malicious peer can send invalid data, get logged, and immediately continue its attack or reconnect without any penalty. This undermines defenses for:
- **CEL-D03**: `blacklistedHashes` unbounded growth relies on eventual peer blocking to limit injection rate
- **CEL-S01**: DAS Selective Disclosure cites peer blacklisting as a defense, but it does not function under default settings

## Proof of Concept

No proof of concept was conducted for this threat. The default configuration is directly verifiable in the source code at the referenced file and line numbers.

## Impact

Defense mechanism bypass that enables unlimited retries from malicious peers. The default configuration itself is the threat condition, requiring no separate exploit. This is not a direct DA invariant violation but an enabler that increases the severity of CEL-D03 and CEL-S01.

### CVSS 3.1

**Score**: 5.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Malicious peers connect and attack over the P2P network |
| AC (Attack Complexity) | L (Low) | No special conditions needed; the vulnerable default is always active |
| PR (Privileges Required) | N (None) | No privileges required; any P2P peer can exploit the disabled blacklisting |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the node running with default configuration |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No direct integrity impact |
| A (Availability) | L (Low) | Indirect availability impact as a force multiplier for other attacks; not a direct DoS by itself |

## Recommendation

1. Change the `EnableBlackListing` default to `true` to activate peer disconnection for invalid data senders.
2. Publish a roadmap for resolving the TODO-referenced "related issues" that are blocking the default change.
3. Add a recommendation for `EnableBlackListing=true` in operator documentation until the default is changed.
4. Implement per-peer rate limits that function independently of the blacklisting mechanism as a defense-in-depth measure.
