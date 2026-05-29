# CEL-S01: DAS Selective Disclosure — Deceiving Light Nodes via Sybil Peers

{% hint style="info" %}
**Severity**: Low · **STRIDE**: S (Spoofing) · **Scope**: protocol · **Status**: partial
{% endhint %}

## Overview

An attacker operating numerous sybil nodes to dominate a specific light node's peer set can deceive it into believing unavailable data is available. Procedure: (1) Malicious block producer withholds ~25% of EDS shares from the network, (2) Distributes withheld shares only to sybil nodes, (3) Replaces target light node's peers with sybils via DHT poisoning, (4) When the target requests DAS samples, sybils respond to all -- target falsely concludes data is available. P2P transport is non-anonymous, allowing attackers to identify requesters and provide selective responses per target. With DefaultSampleAmount=16, even without sybils the per-client deception probability is ~1%, and with 400 clients the probability of at least one being deceived is ~98.2% (Common Prefix 2022).

## Core Invariants Affected

`data_recoverability`

Target light node falsely judges unavailable data as available, neutralizing DA verification for rollups depending on that node.

## Prerequisites

Sybil node operating costs (N servers), DHT poisoning to dominate target's peer set. EnableBlackListing defaults to false, so the same sybil can reconnect without being blocked.

## Attack Scenario

**Condition**: Non-anonymous P2P transport + sybil nodes dominate target light node's peer set

**Example**: Common Prefix (2022-11-09): 16 samples, 25% withheld results in ~1% per-client deception probability. With 400 clients, probability of at least one being deceived is ~98.2%.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Low |
| Likelihood | Low (sybil infrastructure cost is low but block producer collusion is required) |
| Scope | protocol |
| Target | Process, Dataflow, Actor |
| Core Invariants | data_recoverability |

## Code References

- Research: Common Prefix 'Research analysis of the selective disclosure attack in Celestia' (2022-11-09, commonprefix.com/static/clients/celestia/celestia_report_selective_disclosure_attack.pdf)
- [`celestia-node/share/availability/light/options.go:10 (DefaultSampleAmount=16)`](https://github.com/celestiaorg/celestia-node/blob/main/share/availability/light/options.go#L10)
- [`celestia-node/share/shwap/p2p/shrex/peers/options.go:60-62 (EnableBlackListing: false)`](https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/options.go#L60-L62)

## Verification & Evidence

**Status**: partial

Phase 3 external input cross-check. Common Prefix research paper body confirmed. k=15 to 16 recalculation correction applied. Actual sybil cluster operating cost (DHT poisoning) not verified (PARTIAL).

## Mitigations

No defense in current code. Nym anonymous transport integration is in R&D (not deployed). Recommendations: (1) Accelerate anonymous transport adoption, (2) Enforce peer diversity, (3) Cross-verify sampling results between light nodes, (4) Change EnableBlackListing default to true.
