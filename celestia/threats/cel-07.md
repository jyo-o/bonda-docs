# CEL-07: DAS Selective Disclosure Attack via Sybil Peers

{% hint style="info" %}
**Severity**: Low · **Category**: Operational Risk · **Status**: verified
{% endhint %}

## Summary

A selective disclosure attack exploits Celestia's non-anonymous P2P transport to deceive specific light nodes into believing unavailable data is available. The attacker operates Sybil nodes to dominate a target's peer set via DHT poisoning, then responds to all DAS sample requests with data withheld from the broader network. With 16 samples and 25% data withholding, the per-client deception probability is approximately 1%, but across 400 clients the probability of at least one being deceived is approximately 98.2%.

## Description

The attack leverages the non-anonymous nature of Celestia's P2P layer, which allows an attacker to identify which node is making a sample request and provide targeted responses:

```go
// celestia-node/share/availability/light/options.go
// @audit Light nodes sample only 16 random cells before declaring a block available
// https://github.com/celestiaorg/celestia-node/blob/main/share/availability/light/options.go
var (
    DefaultSampleAmount uint = 16
)
```

The attack flow:

1. A malicious block producer creates a block but withholds approximately 25% of EDS shares from the network
2. The withheld shares are distributed exclusively to attacker-controlled Sybil nodes
3. The attacker uses DHT poisoning to replace the target light node's peer set with Sybil nodes
4. The target requests 16 random DAS samples
5. Since Sybil nodes hold all shares (including withheld ones), they respond successfully to every sample
6. The target concludes data is available when the broader network cannot reconstruct the full block

The defense assumption of peer blacklisting is weakened by `EnableBlackListing` defaulting to `false` (see CEL-06):

```go
// celestia-node/share/shwap/p2p/shrex/peers/options.go — DefaultParameters
// @audit EnableBlackListing defaults to false — Sybil peers reconnect without being blocked
// https://github.com/celestiaorg/celestia-node/blob/main/share/shwap/p2p/shrex/peers/options.go
func DefaultParameters() *Parameters {
    return &Parameters{
        // ...
        EnableBlackListing: false,
        // TODO(@walldiss): enable blacklisting once all related issues are resolved
    }
}
```

According to research by Common Prefix (2022-11-09), with 16 samples and 25% data withholding, the mathematical analysis shows:
- Per-client deception probability: approximately 1%
- Across 400 clients: probability of at least one being deceived is approximately 98.2%

## Proof of Concept

Common Prefix research report "Research analysis of the selective disclosure attack in Celestia" (2022-11-09) provides the mathematical analysis of deception probabilities with 16 samples and 25% withholding. Sybil cluster operating cost via DHT poisoning was not experimentally verified.

## Impact

Targeted light node deception causing false DA availability attestation. Rollups depending on the deceived node may accept blocks whose data is not actually recoverable by the network. The attack requires block producer collusion, which limits likelihood, but the Sybil infrastructure cost is low. No defense exists in the current codebase; Nym anonymous transport integration is in the R&D stage and has not been deployed.

Affects the Verifiability axis. It is tracked as an Operational Indicator shown alongside the risk pentagon, not as a deduction from the structural score.

## Recommendation

1. Accelerate anonymous transport adoption (e.g., Nym integration) to prevent requestor identification, eliminating the ability to target specific nodes.
2. Enforce peer diversity requirements (e.g., minimum distinct ASN or IP subnet coverage) to make Sybil domination of peer sets harder.
3. Implement cross-verification of sampling results between multiple light nodes to detect inconsistencies in availability attestations.
4. Change `EnableBlackListing` to default to `true` (see CEL-06) to limit Sybil peer reconnection.
