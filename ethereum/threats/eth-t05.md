# ETH-T05: Gloas Column Proof Verification Gap

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: T (Tampering) · **Status**: partial
{% endhint %}

## Overview

The Gloas fork proposal introduces changes to how data column proofs are verified in Ethereum's data availability layer. Analysis of the Gloas specification reveals gaps in the column proof verification mechanism that could allow improperly proven columns to be accepted as valid. If exploited after Gloas activation, this could undermine the integrity of data availability sampling.

Like ETH-T03, this threat is contingent on the Gloas fork being scheduled and activated. Gloas is currently unscheduled with no confirmed timeline, meaning there is no immediate risk to the live network. The verification status is partial because the Gloas specification is still in development, and the final verification logic may differ from what has been reviewed.

This threat is distinct from ETH-T03 in that it concerns the proof verification logic itself rather than the omission of inclusion proofs. Even if inclusion proofs are added, the verification mechanism must be cryptographically sound and correctly implemented to provide meaningful security guarantees.

## Prerequisites

- The Gloas fork must be scheduled and activated on the Ethereum mainnet
- The column proof verification gap must persist in the final Gloas specification and client implementations

## Attack Scenario

1. The Gloas fork activates with incomplete or flawed column proof verification logic.
2. An attacker constructs data columns with proofs that exploit the verification gap, creating columns that pass the flawed verification but contain incorrect data.
3. The attacker distributes these columns through the PeerDAS network, where receiving nodes accept them as valid.
4. Nodes relying on the verified columns for data availability sampling or reconstruction make decisions based on corrupted data.
5. Rollups or other consumers that depend on data availability guarantees may derive incorrect state from the tampered columns.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:M/II:M/A:N/AI:N` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based but complexity is high because exploitation depends on a future fork activation with an unresolved specification gap. No privileges or user interaction are required. Integrity impact is medium at both node and chain levels because flawed proof verification could allow tampered data columns to pass validation. Confidentiality and availability are unaffected. The scope remains unchanged as the attack does not cross trust boundaries.

## Evidence

### Source Code

- **Component**: Gloas fork specification and related client code paths
- **Finding**: Column proof verification logic in the current Gloas design has been identified as incomplete. Code paths have been traced and confirmed to be in an unfinished state, consistent with the fork's unscheduled status.

## Mitigations

The Gloas fork is currently unscheduled, providing time to address the verification gap before any network impact. The column proof verification mechanism must be fully specified, formally analyzed, and implemented across all major clients before Gloas can progress to activation. The Ethereum specification review process, combined with multi-client testing and consensus-spec-tests coverage, should catch verification logic flaws before mainnet deployment. Independent security audits of the proof verification scheme are recommended before the fork is finalized.
