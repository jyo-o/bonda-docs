# ETH-E01: Reconstruction Failure Mode Inconsistency Across Clients

{% hint style="info" %}
**Severity**: High (8.2/10) · **STRIDE**: E (Elevation of Privilege) · **Status**: code_verified
{% endhint %}

## Overview

Lighthouse and Prysm, two major Ethereum consensus clients, handle data column reconstruction failures in fundamentally different ways. When reconstruction fails, Lighthouse deletes all columns associated with the affected slot, while Prysm marks the reconstructed columns as verified without performing re-verification. This behavioral divergence means that after the same failure event, Lighthouse nodes have no data for the slot while Prysm nodes treat potentially corrupted data as verified.

This cross-client inconsistency can lead to network-level consensus issues. Nodes running Lighthouse would report the data as unavailable and require re-download, while nodes running Prysm would report it as available and verified. If the reconstructed columns are actually invalid, Prysm nodes are operating on corrupted data that has been marked as trustworthy. This inconsistency violates a core invariant of the consensus protocol: all honest nodes should reach the same conclusion about data availability for any given slot.

With the Fulu fork, data column reconstruction becomes the primary mechanism for data availability. This elevates reconstruction from an edge-case recovery path to a core protocol function, making behavioral inconsistency between clients a direct threat to consensus safety and data recoverability.

## Prerequisites

- At least one corrupted or invalid data column must be received by both Lighthouse and Prysm nodes
- The corrupted column must trigger a reconstruction failure
- PeerDAS must be active (post-Fulu fork)

## Attack Scenario

1. An attacker who is a block proposer or a malicious peer injects a corrupted data column into the network.
2. Both Lighthouse and Prysm nodes receive the corrupted column and attempt data column reconstruction for the affected slot.
3. Reconstruction fails on both clients because the corrupted column produces an invalid result.
4. Lighthouse responds by deleting all columns for the slot, including previously verified ones. The node reports the data as unavailable and initiates re-download.
5. Prysm responds by marking the reconstructed columns as verified without re-checking their validity. The node reports the data as available.
6. The network now has a split view: Lighthouse nodes see the data as unavailable while Prysm nodes treat potentially corrupted data as verified and available.
7. This inconsistency can propagate to attestation behavior, where Lighthouse validators may vote against data availability while Prysm validators vote in favor, creating conflicting consensus signals.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 8.2/10 (High) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:C/C:N/CI:N/I:M/II:M/A:M/AI:M` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based with high complexity because triggering reconstruction failure requires injecting a corrupted column that passes initial validation. No privileges or user interaction are required. The scope is changed because the inconsistency crosses trust boundaries between client implementations, affecting the entire network's consensus layer rather than just individual nodes. Integrity impact is medium at both node and chain levels because Prysm's behavior of marking unverified reconstructions as verified compromises data integrity guarantees. Availability impact is medium at both levels because Lighthouse's aggressive deletion forces unnecessary re-downloads while the network-wide inconsistency can delay finality. This threat affects two core invariants: consensus safety and data recoverability.

## Evidence

### Source Code

- **Repository**: Lighthouse (Sigma Prime consensus client)
- **Finding**: On reconstruction failure, Lighthouse deletes all columns for the affected slot from its cache. This is the conservative approach but causes unnecessary data loss for verified columns.

- **Repository**: Prysm (Prysmatic Labs consensus client)
- **Finding**: On reconstruction failure, Prysm marks reconstructed columns as verified without performing re-verification. This is the permissive approach but risks treating corrupted data as valid.

- **Critical difference**: The reconstruction path is a primary mechanism in Fulu. The opposing failure modes mean the same network event produces contradictory outcomes across client implementations.

## Mitigations

Each client currently handles reconstruction failure independently with no cross-client coordination on failure semantics. Lighthouse's conservative approach of deleting everything is safe but wasteful, while Prysm's permissive approach of trusting reconstructions is efficient but potentially unsafe. A unified specification for reconstruction failure handling is needed, ideally one that preserves individually verified columns while requiring re-verification of any columns produced during a failed reconstruction. The consensus specification should explicitly define the expected behavior on reconstruction failure to prevent implementation-level divergence. Cross-client integration tests should be added to verify consistent behavior under reconstruction failure scenarios.
