# ETH-R01: Blob and Data Column Equivocation Detection Failure

{% hint style="info" %}
**Severity**: Medium (4.2/10) · **STRIDE**: R (Repudiation) · **Status**: code_verified
{% endhint %}

## Summary

When a consensus layer client receives two blobs or data columns with the same slot and index but different content, the second message is silently ignored. No slashing evidence is generated and no equivocation record is preserved. A malicious block proposer can publish conflicting data for the same slot without detection or penalty, violating protocol accountability guarantees.

## Description

The gossip validation logic in consensus layer clients marks duplicate slot-index pairs as IGNORE without comparing content.

```
# @audit — duplicate blob/column silently ignored, no equivocation detection
# Consensus layer gossip validation:
# When blob_sidecar or data_column_sidecar arrives for a
# (slot, index) pair that has already been seen:
#   → message marked as IGNORE
#   → no content comparison performed
#   → no equivocation evidence generated or forwarded for slashing
```

With the Fulu fork making data columns the primary path for data availability, equivocation detection becomes more critical. A proposer who equivocates on data columns could cause different nodes to hold different versions of the data for the same slot, potentially leading to inconsistent state derivation by downstream consumers. This behavior contrasts with existing block equivocation slashing mechanisms.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

A malicious proposer can distribute version A of a blob/column to one part of the network and version B to another. Neither group generates slashing evidence because the second message is discarded. The proposer equivocates without penalty, and different parts of the network hold different data for the same slot. This undermines protocol accountability and can cause some nodes to operate on inconsistent data, potentially affecting downstream state derivation.

### CVSS 3.1
**Score**: 4.2/10 (Medium)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Conflicting messages distributed over the network |
| AC | H (High) | Attacker must be a validator with proposer duties and time the equivocation across network partitions |
| PR | L (Low) | Only block proposers can publish blobs and data columns |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Attack operates within the consensus accountability boundary |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Equivocation does not corrupt committed data but undermines accountability |
| A | L (Low) | Conflicting data versions may cause some nodes to operate on inconsistent data |

## Recommendation

1. **Implement content-hash comparison for duplicate slot-index pairs**: When a blob or data column arrives for an already-seen (slot, index) pair, compare the content hash against the previously seen message instead of silently ignoring.
2. **Generate and broadcast equivocation evidence**: If a content mismatch is detected, preserve both messages as slashing evidence and broadcast an equivocation proof to the network.
3. **Align with existing block equivocation slashing**: Bring blob and data column equivocation detection in line with existing block equivocation slashing mechanisms to maintain consistent protocol accountability.
