# ETH-07: Self-Reported Custody Count in the ENR Is Not Cryptographically Verifiable

{% hint style="info" %}
**Category**: Governance Observation · **Status**: verified
{% endhint %}

## Summary

Each PeerDAS node advertises its custody group count through the `cgc` field in its ENR. Peers may reject a node that advertises fewer than `CUSTODY_REQUIREMENT` groups, but nothing in the protocol proves that a node actually stores and serves the columns it claims. A node can advertise a high custody count, including the super-full value, while holding far fewer columns. The network's picture of how custody is distributed therefore rests on self-reported values that cannot be checked.

## Description

![ETH-07 data flow — Ethereum PeerDAS Read path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/ethereum/assets/dfd/ethereum-read.png)

*Data flow — Ethereum PeerDAS Read: PeerDAS.*

The custody count is carried in the ENR and consumed as an advertised value.

- The ENR includes `custody_group_count: uint64`, abbreviated `cgc`. Clients may reject peers whose value is below `CUSTODY_REQUIREMENT`. Source: [p2p-interface.md](https://github.com/ethereum/consensus-specs/blob/master/specs/fulu/p2p-interface.md).
- A peer derives the set of custody groups a node should hold by running `get_custody_groups(node_id, cgc)` on the advertised count. This derivation uses the claimed value as input and produces no evidence that the node actually retains the data.

There is no challenge protocol that forces a node to prove possession of the columns implied by its `cgc`. A node that under-provisions can still advertise full custody, and peers selecting it for column requests will only discover the gap when a request fails. Conversely, honest accounting of custody distribution across the network is only as accurate as the advertised counts.

## Proof of Concept

No exploit reproduction was conducted. This finding is based on the ENR `cgc` definition and the peer-acceptance rule in `p2p-interface.md`, together with the `get_custody_groups` derivation in `das-core.md`, which operate on the advertised value with no possession proof.

## Impact

Custody distribution metrics, peer-selection decisions, and any reasoning about how many nodes truly hold a given column depend on values that nodes report about themselves. A node can present itself as a larger custody contributor than it is, which weakens the assurance that the advertised custody map reflects real data retention. No single party is shown to be acting maliciously; the observation is that the trust placed in advertised custody is structural and unverified.

Affects the Decentralization baseline through the integrity of advertised custody distribution. This is recorded as a Governance Observation and carries no score.

## Recommendation

1. Treat advertised `cgc` values as unverified hints rather than guarantees when reasoning about custody coverage.
2. Track request-failure rates per peer so that nodes advertising more custody than they serve can be identified and deprioritized in practice.
3. Consider a possession-sampling mechanism in future protocol work so that advertised custody can be probabilistically checked against real holdings.
