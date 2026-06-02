# ETH-08: Blob and Column Publication Concentrated in the Builder and Relay Market

{% hint style="info" %}
**Category**: Governance Observation · **Status**: verified
{% endhint %}

## Summary

Under proposer-builder separation, a small set of external builders and relays produces the large majority of Ethereum blocks. For a block carrying many blobs, the timely publication of every column sidecar is part of the path that the builder and relay control. The data availability of externally built blocks therefore leans on a concentrated set of well-resourced market participants, which is a structural property of how blocks are produced rather than a defect in the PeerDAS logic.

## Description

![ETH-08 data flow — Ethereum PeerDAS Write path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/ethereum/assets/dfd/ethereum-write.png)

*Data flow — Ethereum PeerDAS Write: CL Builder.*

PeerDAS requires that a block's data be split into 128 columns and published as column sidecars across the gossip subnets. When a block is built externally and delivered through a relay, the construction of the block and its associated blobs sits with the builder, and the proposer commits to the builder's payload without locally holding all of the underlying data.

- Column sidecars are published per column across `DATA_COLUMN_SIDECAR_SUBNET_COUNT` subnets. Source: [p2p-interface.md](https://github.com/ethereum/consensus-specs/blob/master/specs/fulu/p2p-interface.md).
- The proposer of an externally built block does not necessarily custody the full set of columns and relies on the building path to make the data available.

Because the builder and relay market is concentrated, the operational responsibility for promptly publishing all columns of high-blob blocks rests with few parties. A proposer that has outsourced block construction has limited ability to independently republish columns it never held. The concern is the concentration of this operational role, not an allegation that any specific builder or relay misbehaves.

## Proof of Concept

No exploit reproduction was conducted. This finding is an observation about the interaction between the proposer-builder separation market and PeerDAS column publication, based on the per-column sidecar publication model in `p2p-interface.md` and the well-documented concentration of the builder and relay market.

## Impact

The data availability of the majority of blocks depends, in practice, on a small number of builders and relays publishing all column sidecars on time. A degradation or withdrawal among these parties would disproportionately affect blob availability for externally built blocks. This concentrates a liveness-relevant role in few hands and is relevant to how decentralized the effective data availability path is, independent of the protocol's own guarantees.

Affects the Decentralization baseline through concentration of the block-building and column-publication path. This is recorded as a Governance Observation and carries no score.

## Recommendation

1. Track the share of blocks and blobs flowing through each builder and relay so that concentration in the column-publication path is visible.
2. Support proposer-side fallbacks, such as local block building, that do not depend on a single builder publishing all columns.
3. Encourage relay and builder diversity so that the availability of externally built blocks does not rest on a small set of operators.
