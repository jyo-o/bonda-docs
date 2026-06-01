# ETH-09: Rising Blob Counts Raise the Resource Floor for Running a Node

{% hint style="info" %}
**Category**: Governance Observation · **Status**: verified
{% endhint %}

## Summary

Fusaka introduces Blob Parameter Only forks, configuration-only forks that raise the maximum number of blobs per block without a code fork. The mainnet schedule raises the maximum to 15 blobs at the first step and 21 at the second. As the blob count grows, the bandwidth and compute required to custody columns, gossip sidecars, and reconstruct data rises with it, lifting the practical floor for participating as a validator or full node. This gradual increase in the cost of participation is a decentralization-relevant trend rather than an exploitable defect.

## Description

Blob capacity is scaled through the Blob Parameter Only mechanism rather than through changes to the data availability code.

- Blob Parameter Only forks are defined in [EIP-7892](https://eips.ethereum.org/EIPS/eip-7892) as config-only forks that change the blob target, maximum, and base-fee update fraction.
- The mainnet blob schedule sets `MAX_BLOBS_PER_BLOCK` to 15 at the first parameter step and 21 at the second. Source: [configs/mainnet.yaml](https://github.com/ethereum/consensus-specs/blob/master/configs/mainnet.yaml).

PeerDAS lowers the per-node storage burden relative to downloading all blobs, but the absolute amount of column gossip, proof verification, and potential reconstruction work still scales with the number of blobs in a block. Each increase in the blob maximum raises the steady-state bandwidth and compute a node must sustain to keep up with custody and sampling duties. Over successive parameter steps, this raises the minimum viable hardware and network provisioning for an independent operator.

## Proof of Concept

No exploit reproduction was conducted. This finding is based on the Blob Parameter Only mechanism in EIP-7892 and the mainnet blob schedule maxima of 15 and 21 blobs per block.

## Impact

As the blob maximum rises, operators with constrained bandwidth or hardware face a higher barrier to running a node that keeps pace with custody and sampling. This pressure tends to concentrate node operation among better-resourced participants over time. The effect is gradual and tied to governance decisions about parameter scaling rather than to any single defect, and it is relevant to how broadly the network can be independently validated.

Affects the Decentralization baseline through the rising resource floor for independent participation as blob capacity scales. This is recorded as a Governance Observation and carries no score.

## Recommendation

1. Pair each blob parameter increase with published guidance on the bandwidth and hardware required to keep up, so operators can plan provisioning.
2. Monitor the distribution of node operators and home stakers across parameter steps to detect centralizing pressure early.
3. Weigh decentralization impact alongside throughput when scheduling future Blob Parameter Only steps.
