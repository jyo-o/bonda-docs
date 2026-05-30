# ETH-R01: Blob and Data Column Equivocation Detection Failure

{% hint style="info" %}
**Severity**: Low (1.1/10) · **STRIDE**: R (Repudiation) · **Status**: code_verified
{% endhint %}

## Overview

When a consensus layer client receives two blobs or data columns with the same slot and index but different content, the second message is silently ignored. No slashing evidence is generated and no equivocation record is preserved. This means a malicious block proposer can publish conflicting data for the same slot without being detected or penalized through the normal slashing mechanism.

Equivocation detection is important for maintaining protocol accountability. In a well-functioning protocol, any validator that publishes conflicting messages should be identifiable and subject to slashing penalties. The current behavior of simply ignoring the second message means that evidence of misbehavior is discarded rather than preserved for potential slashing proceedings.

With the Fulu fork making data columns the primary path for data availability, equivocation detection becomes more critical. A proposer who equivocates on data columns could cause different nodes to hold different versions of the data for the same slot, potentially leading to inconsistent state derivation by downstream consumers.

## Prerequisites

- The attacker must be a block proposer with the ability to publish blobs or data columns for a given slot
- The attacker must be able to distribute conflicting versions to different parts of the network before the first version propagates fully

## Attack Scenario

1. A malicious block proposer creates two different versions of a blob or data column for the same slot and index.
2. The proposer distributes version A to one subset of the network and version B to another subset.
3. Nodes that receive version A first will silently ignore version B when it arrives, and vice versa.
4. Neither group of nodes generates slashing evidence because the second message is treated as a duplicate and discarded.
5. The proposer successfully equivocates without penalty, and different parts of the network hold different data for the same slot.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.1/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:R/UI:N/S:U/C:N/CI:N/I:L/II:L/A:L/AI:L` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based but complexity is high because the attacker must be a validator with proposer duties and must time the equivocation to reach different network partitions. Privileges are required since only block proposers can publish blobs and data columns. Integrity impact is low at both node and chain levels because the equivocation does not corrupt committed data but does undermine accountability. Availability impact is low because conflicting data versions may cause some nodes to operate on stale or inconsistent data. The scope remains unchanged.

## Evidence

### Source Code

- **Component**: Consensus layer client gossip validation logic
- **Finding**: When a blob sidecar or data column sidecar arrives for a slot and index pair that has already been seen, the message is marked as IGNORE. No comparison of the content is performed, and no equivocation evidence is generated or forwarded for slashing.

## Mitigations

Currently, the only handling is IGNORE processing for duplicate slot-index pairs. A slashing evidence generation mechanism for blob and data column equivocation has not been implemented. To address this gap, clients could compare the content hash of incoming messages against previously seen messages for the same slot-index pair. If a mismatch is detected, the node should preserve both messages as slashing evidence and broadcast an equivocation proof to the network. This would bring blob and data column equivocation detection in line with existing block equivocation slashing mechanisms.
