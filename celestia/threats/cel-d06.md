# CEL-D06: EnableBlackListing Disabled by Default — Sybil Peer Reconnection Allowed

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D (Denial of Service) · **Scope**: implementation · **Status**: code_verified
{% endhint %}

## Overview

The SHREX peer manager's EnableBlackListing defaults to false (options.go:62, TODO comment: 'enable blacklisting once all related issues are resolved'). In blacklistPeers() (manager.go:416-438), when EnableBlackListing=false, calls to connGater.BlockPeer() and host.Network().ClosePeer() are skipped. As a result, peers that sent invalid data are only logged but not actually blocked, allowing them to reconnect immediately or continue attacks on the existing connection. This default weakens the defense premises of CEL-D03 (blacklistedHashes unbounded growth), CEL-D05 (ShrEx unbounded response), and CEL-S01 (DAS Selective Disclosure). CEL-D05 and CEL-S01 cite 'peer blacklisting after one failure' as an existing defense, but this defense is inoperative under default settings.

## Core Invariants Affected

`data_recoverability`

Not a direct DA invariant violation but defense mechanism disabled. Acts as an enabler that amplifies the blast radius of CEL-D03/D05/S01.

## Prerequisites

None. The default configuration itself is the threat condition. Malicious peers need only P2P access to retry indefinitely without being blocked.

## Attack Scenario

**Condition**: Light node running with celestia-node default settings. EnableBlackListing=false is the default.

**Example**: Default settings: EnableBlackListing=false, PoolValidationTimeout=2min, GcInterval=30s. Malicious peer sends fake DataHash -> hash added to blacklistedHashes but peer itself is not blocked (BlockPeer()/ClosePeer() not called) -> peer retries with new hash.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Medium |
| Likelihood | Immediate (default configuration is itself the threat; no separate attack action needed) |
| Scope | implementation |
| Target | Process, Actor |
| Core Invariants | data_recoverability |

## Code References

- [`celestia-node/share/shwap/p2p/shrex/peers/options.go:60-62 (EnableBlackListing: false, TODO comment)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/options.go#L60-L62)
- [`celestia-node/share/shwap/p2p/shrex/peers/manager.go:416-438 (blacklistPeers: EnableBlackListing=false → skip BlockPeer/ClosePeer)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go#L416-L438)
- [`celestia-node/share/shwap/p2p/shrex/peers/manager.go:423-425 (if !m.params.EnableBlackListing { continue })`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/manager.go#L423-L425)
- Commit: `celestia-node f8cefbe3e5bd3e144a414cb2140dd223ec6191c6`

## Verification & Evidence

**Status**: code_verified

Code directly confirmed (commit f8cefbe). EnableBlackListing=false default, TODO comment original text, and blacklistPeers() gating logic all confirmed. Cross-verified that CEL-D05/S01's 'blacklist defense' claim is inoperative under default settings.

## Mitigations

Recommendations: (1) Change EnableBlackListing default to true, (2) Publish roadmap for resolving TODO ('all related issues'), (3) Add EnableBlackListing=true recommendation to operator documentation, (4) Implement per-peer rate limit that works without blacklisting.
