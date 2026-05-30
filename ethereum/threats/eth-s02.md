# ETH-S02: Custody Group Node ID Grinding

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: S (Spoofing) · **Status**: code_verified
{% endhint %}

## Summary

PeerDAS assigns each node to custody groups deterministically based on its `node_id`. Because node IDs are publicly controllable, an attacker can brute-force search for identities that map to a specific custody group. By concentrating many attacker-controlled nodes in a single group, the attacker could degrade data availability for the columns that group is responsible for.

## Description

Custody group membership is derived deterministically from the node ID without incorporating any secret or proof-of-work component that would resist grinding.

```
# @audit — custody group assignment uses node_id directly
# Consensus layer: custody group = f(node_id)
# No proof-of-work, stake binding, or secret component in assignment.
# Attacker can generate arbitrary node_ids and select those mapping
# to a target custody group.
```

With the Fulu fork activating PeerDAS, custody groups transition from a theoretical construct to an actual security boundary. Nodes within a custody group store and serve specific data columns, making group membership integrity directly relevant to network data availability guarantees. The attack is constrained by the computational cost of node ID grinding relative to the number of custody groups and honest nodes.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

A successfully dominated custody group can degrade data column retrieval for affected slots. However, data column redundancy across multiple custody groups ensures that even partial group compromise allows data recovery through reconstruction from other groups. The cost of grinding enough node IDs to dominate a single group is prohibitively high under normal network conditions due to the large number of custody groups and the high honest-node-to-attacker ratio.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Attacker deploys crafted nodes over the network |
| AC | H (High) | Requires significant computational resources for brute-force node ID generation |
| PR | N (None) | No privileges required to generate and deploy node identities |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Attack operates within the PeerDAS trust boundary |
| C | N (None) | No confidentiality impact; attack targets availability only |
| I | N (None) | No integrity impact; data columns are not tampered with |
| A | L (Low) | Partial degradation of data column retrieval for affected custody group |

## Recommendation

1. **Rely on custody group redundancy**: The large number of custody groups combined with high honest-node ratio makes single-group domination prohibitively expensive. Maintain sufficient network participation to preserve this property.
2. **Introduce proof-of-work or stake-based identity binding**: Future protocol upgrades should incorporate proof-of-work or stake-based identity binding to the node ID assignment, increasing the cost of grinding attacks.
3. **Monitor custody group composition**: Implement monitoring for anomalous concentration of new node IDs within any single custody group to detect grinding attempts early.
