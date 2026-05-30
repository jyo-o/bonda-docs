# ETH-S02: Custody Group Node ID Grinding

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: S (Spoofing) · **Status**: code_verified
{% endhint %}

## Overview

PeerDAS assigns each node to custody groups based on its `node_id`. This deterministic assignment means that an attacker who can generate arbitrary node IDs can brute-force search for identities that map to specific data column sets. By concentrating many attacker-controlled nodes in a single custody group, the attacker could degrade data availability for the columns that group is responsible for.

With the Fulu fork activating PeerDAS, custody groups transition from a theoretical construct to an actual security boundary. Nodes within a custody group are responsible for storing and serving specific data columns, making the integrity of group membership directly relevant to network data availability guarantees.

The attack is constrained by the computational cost of node ID grinding relative to the number of custody groups. As the number of groups and honest nodes increases, the resources required to dominate any single group grow substantially, making this a low-severity but protocol-relevant concern.

## Prerequisites

- Significant computing resources capable of brute-force node ID generation
- Ability to deploy multiple nodes with the crafted identities to the network
- PeerDAS must be active (post-Fulu fork)

## Attack Scenario

1. The attacker identifies a target custody group responsible for a specific set of data columns.
2. Using brute-force computation, the attacker generates many node IDs that map to the target custody group under the PeerDAS assignment algorithm.
3. The attacker deploys nodes using these crafted identities, gradually increasing their representation within the target group.
4. Once the attacker controls a sufficient fraction of the custody group, they can selectively withhold data columns, reducing availability for those specific columns.
5. Honest nodes requesting data from the compromised group experience degraded service or reconstruction delays.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:N/II:N/A:M/AI:M` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based but complexity is high due to the computational cost of grinding node IDs. No privileges or user interaction are required. Confidentiality and integrity are unaffected since the attack only targets data availability. Availability impact is medium at both the node and chain levels because a successfully dominated custody group can degrade data column retrieval for affected slots. The scope remains unchanged as the attack does not cross security boundaries.

## Evidence

### Source Code

- **Component**: PeerDAS custody group assignment logic (consensus layer clients)
- **Finding**: Custody group membership is derived deterministically from the node ID, which is publicly controllable by each node operator. The assignment does not incorporate any secret or proof-of-work component that would resist grinding.

## Mitigations

The primary defense is the large number of custody groups combined with the high honest-node-to-attacker ratio on the network. The cost of grinding enough node IDs to dominate a single custody group is prohibitively high under normal network conditions. Additionally, data column redundancy across multiple custody groups ensures that even if one group is partially compromised, data can still be recovered through reconstruction from other groups. Future protocol upgrades could introduce proof-of-work or stake-based identity binding to further increase grinding costs.
