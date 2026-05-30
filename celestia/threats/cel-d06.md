# CEL-D06: Peer Blacklisting Disabled by Default Allowing Sybil Reconnection

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

The SHREX peer manager's EnableBlackListing flag defaults to false, as set in options.go line 62 with a TODO comment stating "enable blacklisting once all related issues are resolved." When this flag is false, the blacklistPeers function in manager.go skips calls to connGater.BlockPeer() and host.Network().ClosePeer(), meaning peers that send invalid data are logged but never actually disconnected or blocked.

This default undermines the defense assumptions of several other threats. CEL-D03 (blacklistedHashes unbounded growth) relies on eventual peer blocking to limit injection rate. CEL-D05 (ShrEx unbounded response) and CEL-S01 (DAS Selective Disclosure) both cite "peer blacklisting after one failure" as an existing defense, but this defense does not function under default settings.

The result is that a malicious peer can send invalid data, get logged, and immediately continue its attack or reconnect without any penalty. This acts as a force multiplier for multiple other vulnerabilities.

## Prerequisites

- None required beyond the default configuration itself
- Any malicious peer with P2P access can retry indefinitely without being blocked

## Attack Scenario

1. A Light node runs with default celestia-node settings where EnableBlackListing is false.
2. A malicious peer connects via P2P and sends fake DataHashes or invalid ShrEx responses.
3. The peer manager detects the invalid data and marks the hash in its blacklist map.
4. However, because EnableBlackListing is false, BlockPeer() and ClosePeer() are never called.
5. The malicious peer remains connected and continues sending new fake hashes or invalid data.
6. This amplifies the blast radius of CEL-D03, CEL-D05, and CEL-S01.

## Impact

Defense mechanism bypass that enables unlimited retries from malicious peers. The default configuration itself is the threat condition, requiring no separate exploit. This is not a direct DA invariant violation but an enabler that increases the severity of multiple related threats.

## Evidence

### Source Code

- `celestia-node/share/shwap/p2p/shrex/peers/options.go:60-62` -- EnableBlackListing defaults to false with TODO comment
- `celestia-node/share/shwap/p2p/shrex/peers/manager.go:416-438` -- blacklistPeers function: when EnableBlackListing is false, BlockPeer and ClosePeer are skipped
- `celestia-node/share/shwap/p2p/shrex/peers/manager.go:423-425` -- the gating condition: if !m.params.EnableBlackListing { continue }
- Verified at commit celestia-node f8cefbe3e5bd3e144a414cb2140dd223ec6191c6

## Mitigations

Recommended fixes include changing the EnableBlackListing default to true, publishing a roadmap for resolving the TODO-referenced "related issues," adding a recommendation for EnableBlackListing=true in operator documentation, and implementing per-peer rate limits that function independently of the blacklisting mechanism.
