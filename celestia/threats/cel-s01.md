# CEL-S01: DAS Selective Disclosure Attack via Sybil Peers

{% hint style="info" %}
**Severity**: Low · **STRIDE**: S · **Status**: partial
{% endhint %}

## Overview

A selective disclosure attack exploits Celestia's non-anonymous P2P transport to deceive specific light nodes into believing unavailable data is available. The attacker operates numerous sybil nodes to dominate a target light node's peer set, then responds to all DAS sample requests with data that was withheld from the broader network.

The attack works because Celestia's P2P layer is not anonymous: an attacker can identify which node is making a sample request and provide targeted responses. A malicious block producer withholds approximately 25% of EDS shares from the network and distributes them only to sybil nodes. Through DHT poisoning, the attacker replaces the target's peers with sybils. When the target requests DAS samples, the sybils respond to all 16 samples, causing the target to falsely conclude the data is available.

According to research by Common Prefix (2022-11-09), with 16 samples and 25% data withholding, the per-client deception probability is approximately 1%. Across 400 clients, the probability of at least one being deceived is approximately 98.2%. The defense assumption of peer blacklisting is weakened by EnableBlackListing defaulting to false (see CEL-D06).

## Prerequisites

- Sybil node infrastructure (multiple servers)
- DHT poisoning capability to dominate the target's peer set
- Block producer collusion to withhold shares from the network
- EnableBlackListing defaults to false, allowing the same sybil to reconnect without being blocked

## Attack Scenario

1. A malicious block producer creates a block but withholds approximately 25% of EDS shares from the network.
2. The withheld shares are distributed exclusively to attacker-controlled sybil nodes.
3. The attacker uses DHT poisoning to replace the target light node's peer set with sybil nodes.
4. The target light node initiates DAS by requesting 16 random samples.
5. Since the sybil nodes hold all shares (including the withheld ones), they respond successfully to every sample request.
6. The target light node concludes the data is available, when in reality the broader network cannot reconstruct the full block.
7. Any rollup relying on this light node's DA attestation is operating on a false assumption.

## Impact

Targeted light node deception causing false DA availability attestation. Rollups depending on the deceived node may accept blocks whose data is not actually recoverable by the network. The attack requires block producer collusion, which limits likelihood, but the sybil infrastructure cost is low.

## Evidence

### Source Code

- `celestia-node/share/availability/light/options.go:10` -- DefaultSampleAmount=16
- `celestia-node/share/shwap/p2p/shrex/peers/options.go:60-62` -- EnableBlackListing defaults to false

### PoC Testing

- Common Prefix research report "Research analysis of the selective disclosure attack in Celestia" (2022-11-09): mathematical analysis of deception probabilities with 16 samples and 25% withholding
- Sybil cluster operating cost via DHT poisoning was not experimentally verified (verification status is partial)

## Mitigations

No defense exists in the current codebase. Nym anonymous transport integration is in the R&D stage and has not been deployed. Recommended fixes include accelerating anonymous transport adoption to prevent requestor identification, enforcing peer diversity requirements to make sybil domination harder, implementing cross-verification of sampling results between multiple light nodes, and changing EnableBlackListing to default to true.
