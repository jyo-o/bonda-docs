# ETH-T05: Gloas Column Proof Verification Gap

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: T (Tampering) · **Status**: partial
{% endhint %}

## Summary

The Gloas fork proposal contains gaps in its data column proof verification mechanism that could allow improperly proven columns to be accepted as valid. If exploited after Gloas activation, this would undermine the integrity of data availability sampling. Gloas is currently unscheduled with no confirmed timeline, making this a design-phase threat distinct from ETH-T03's inclusion proof omission — this concerns the proof verification logic itself.

## Description

Column proof verification logic in the current Gloas design has been identified as incomplete. Code paths have been traced and confirmed to be in an unfinished state, consistent with the fork's unscheduled status.

```
# @audit — column proof verification logic incomplete in Gloas
# Gloas fork: proof verification mechanism has identified gaps
# Even if inclusion proofs are added (ETH-T03), the verification
# mechanism itself must be cryptographically sound.
# Current design allows improperly proven columns to pass validation.
```

This threat is distinct from ETH-T03 in that it concerns the proof verification logic itself rather than the omission of inclusion proofs. Even if inclusion proofs are added, the verification mechanism must be cryptographically sound and correctly implemented to provide meaningful security guarantees.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Flawed proof verification could allow tampered data columns to pass validation. Nodes relying on the verified columns for data availability sampling or reconstruction would make decisions based on corrupted data. Rollups or other consumers that depend on data availability guarantees may derive incorrect state. The threat is contingent on Gloas activation — there is no impact on the current live network.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Tampered columns distributed through PeerDAS network |
| AC | H (High) | Exploitation depends on a future fork activation with an unresolved spec gap |
| PR | N (None) | No privileges required |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Attack does not cross trust boundaries |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Flawed verification could allow tampered data columns to pass |
| A | N (None) | No availability impact |

## Recommendation

1. **Fully specify and formally analyze the proof verification mechanism**: The column proof verification must be completely specified and subjected to formal cryptographic analysis before Gloas progresses toward activation.
2. **Implement across all major clients with multi-client testing**: The verification mechanism must be implemented and validated across all major clients with consensus-spec-tests coverage.
3. **Commission independent security audits**: Independent security audits of the proof verification scheme are recommended before the fork is finalized.
