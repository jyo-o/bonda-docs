# CEL-S01: DAS Selective Disclosure Attack via Sybil Peers

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: S · **Status**: partial
{% endhint %}

## Summary

A selective disclosure attack exploits Celestia's non-anonymous P2P transport to deceive specific light nodes into believing unavailable data is available. The attacker operates Sybil nodes to dominate a target's peer set via DHT poisoning, then responds to all DAS sample requests with data withheld from the broader network. With 16 samples and 25% data withholding, the per-client deception probability is approximately 1%, but across 400 clients the probability of at least one being deceived is approximately 98.2%.

## Description

The attack leverages the non-anonymous nature of Celestia's P2P layer, which allows an attacker to identify which node is making a sample request and provide targeted responses:

```go
// celestia-node/share/availability/light/options.go:10
// @audit DefaultSampleAmount=16 — light nodes request only 16 random samples
```

The attack flow:

1. A malicious block producer creates a block but withholds approximately 25% of EDS shares from the network
2. The withheld shares are distributed exclusively to attacker-controlled Sybil nodes
3. The attacker uses DHT poisoning to replace the target light node's peer set with Sybil nodes
4. The target requests 16 random DAS samples
5. Since Sybil nodes hold all shares (including withheld ones), they respond successfully to every sample
6. The target concludes data is available when the broader network cannot reconstruct the full block

The defense assumption of peer blacklisting is weakened by `EnableBlackListing` defaulting to `false` (see CEL-D06):

```go
// celestia-node/share/shwap/p2p/shrex/peers/options.go:60-62
// @audit EnableBlackListing defaults to false
// @audit Same Sybil peer can reconnect without being blocked
```

According to research by Common Prefix (2022-11-09), with 16 samples and 25% data withholding, the mathematical analysis shows:
- Per-client deception probability: approximately 1%
- Across 400 clients: probability of at least one being deceived is approximately 98.2%

## Proof of Concept

Common Prefix research report "Research analysis of the selective disclosure attack in Celestia" (2022-11-09) provides the mathematical analysis of deception probabilities with 16 samples and 25% withholding. Sybil cluster operating cost via DHT poisoning was not experimentally verified (verification status is partial).

## Impact

Targeted light node deception causing false DA availability attestation. Rollups depending on the deceived node may accept blocks whose data is not actually recoverable by the network. The attack requires block producer collusion, which limits likelihood, but the Sybil infrastructure cost is low. No defense exists in the current codebase; Nym anonymous transport integration is in the R&D stage and has not been deployed.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed over the P2P network via DHT poisoning and Sybil nodes |
| AC (Attack Complexity) | H (High) | Requires block producer collusion, Sybil infrastructure, and successful DHT poisoning of the target |
| PR (Privileges Required) | N (None) | No protocol-level privileges needed, though block producer collusion implies validator access |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the specifically targeted light node(s) |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | The targeted light node produces a false DA attestation, but the broader network is unaffected |
| A (Availability) | N (None) | No direct availability impact; the light node continues operating, just with incorrect state |

## Recommendation

1. Accelerate anonymous transport adoption (e.g., Nym integration) to prevent requestor identification, eliminating the ability to target specific nodes.
2. Enforce peer diversity requirements (e.g., minimum distinct ASN or IP subnet coverage) to make Sybil domination of peer sets harder.
3. Implement cross-verification of sampling results between multiple light nodes to detect inconsistencies in availability attestations.
4. Change `EnableBlackListing` to default to `true` (see CEL-D06) to limit Sybil peer reconnection.
