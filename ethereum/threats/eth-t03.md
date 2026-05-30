# ETH-T03: Gloas Data Column Inclusion Proof Omission

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: T (Tampering) · **Status**: partial
{% endhint %}

## Overview

Gloas is a proposed future Ethereum fork that introduces changes to the data availability architecture. In its current design, Gloas omits data column inclusion proofs, meaning that nodes would accept data columns without cryptographic proof that those columns are correctly included in a committed dataset. Without inclusion proofs, an attacker could potentially supply fabricated or corrupted data columns that pass validation.

Gloas is currently unscheduled with no confirmed timeline for activation. This makes the threat theoretical at present, with no immediate impact on the live network. However, if Gloas is activated without addressing this design gap, it would create a tampering vector in the data availability layer.

The partial verification status reflects that while the Gloas-related code paths have been identified and reviewed, the feature is not yet finalized. Re-evaluation will be necessary once Gloas moves to a scheduled status and its specification stabilizes.

## Prerequisites

- The Gloas fork must be scheduled and activated on the Ethereum mainnet
- The inclusion proof omission must persist in the final Gloas specification

## Attack Scenario

1. The Gloas fork activates on the Ethereum network without implementing data column inclusion proofs.
2. An attacker crafts data columns with valid-looking formats but without verifiable inclusion in any committed blob.
3. The attacker distributes these fabricated columns to nodes through the PeerDAS gossip network.
4. Receiving nodes accept the columns because no inclusion proof verification step exists in the Gloas protocol.
5. Downstream consumers relying on data availability guarantees receive incorrect or fabricated data, potentially affecting rollup state derivation.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:M/II:M/A:N/AI:N` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based but complexity is high because Gloas must first be activated, making exploitation depend on a future protocol change. No privileges or user interaction are required. Integrity impact is medium at both node and chain levels because accepting unproven data columns could corrupt data availability guarantees. Confidentiality and availability are unaffected. The scope remains unchanged as the attack operates within the existing data availability trust boundary.

## Evidence

### Source Code

- **Component**: Gloas fork specification and related client code paths
- **Finding**: Data column inclusion proof verification is absent from the current Gloas design. Code paths related to Gloas have been identified but remain in an unfinished state consistent with the fork's unscheduled status.

## Mitigations

The most important mitigation is that Gloas is currently unscheduled, providing ample time to address the design gap before any network impact. The Ethereum protocol development process requires extensive specification review, test coverage, and multi-client testing before any fork is activated. A data column inclusion proof mechanism must be implemented and validated as part of the Gloas specification before it can progress to a scheduled fork. Community review and formal analysis of the proof scheme should precede any activation decision.
