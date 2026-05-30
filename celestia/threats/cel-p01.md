# CEL-P01: DAS-Only Safety Model After Fraud Proof Removal

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: P · **Status**: verified
{% endhint %}

## Summary

Since the transition to the shwap protocol, Bad Encoding Fraud Proofs (BEFPs) never functioned. PR #4934 formally removed BEFP code as dead code on 2026-04-14, deleting 2,398 lines. However, official documentation (`fraud_proofs.md` and CIP-019) continues to describe BEFPs as part of the security model, creating a documentation-reality gap that can lead rollup builders to design systems with incorrect security assumptions about Celestia's data correctness guarantees.

## Description

The current light node security model relies exclusively on DAS with 16 random samples (`DefaultSampleAmount=16` at `celestia-node/share/availability/light/options.go:10`), which verifies data availability only. There is no mechanism for light nodes to verify data correctness (encoding validity).

**Stale Documentation Surfaces**

```
// celestia-app/specs/src/fraud_proofs.md:5-13
// @audit Still states "BEFPs enforce DAS" — this is factually incorrect post-PR #4934
```

```
// CIPs/cips/cip-019.md
// @audit Claims "Does not change the security model" — stale after BEFP removal
```

**BEFP Removal Timeline**

- Issue `celestia-node#4930`: identified that fraud proofs are not functional post-shwap
- PR `celestia-node#4934` (merged 2026-04-14, commit `89198d23`): removed BEFP dead code (+16/-2,398 lines)
- `go-fraud#143`: requested archiving the go-fraud repository

**Additional Code References**

- `celestia-core/light/verifier.go:14-16` -- `DefaultTrustLevel=Fraction{1,3}`
- `celestia-node/nodebuilder/share/module.go:134-144` -- shrexsub no-op stub for light nodes

The threat is not the DAS-only model itself (breaking BFT assumptions to exploit it is unrealistic), but the fact that the documentation spoofs a stronger security guarantee than the protocol actually provides, leading to potential downstream security model contamination.

## Proof of Concept

No proof of concept was conducted for this threat. The documentation-reality gap is directly verifiable by comparing the stale specification text against the merged PR #4934 and the current codebase.

## Impact

Downstream security model contamination affecting any rollup builder or researcher who relies on stale documentation. A rollup designed with the assumption that BEFPs provide encoding correctness verification would have a blind spot in its security model. The documentation-reality gap is currently active and referenceable. While the underlying BFT-break scenario is unrealistic, the practical harm path is: stale documentation leads to rollup mis-design leads to undetected encoding errors at runtime.

### CVSS 3.1

**Score**: 6.5/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Stale documentation is accessible over the network and consumed by remote builders |
| AC (Attack Complexity) | H (High) | Exploitation requires a rollup builder to rely on stale docs and deploy a system without independent verification |
| PR (Privileges Required) | N (None) | No privileges needed; the stale documentation is publicly accessible |
| UI (User Interaction) | N (None) | No user interaction required; the threat is the passive existence of incorrect documentation |
| S (Scope) | U (Unchanged) | Impact is confined to systems that directly consume Celestia's documented security model |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | H (High) | Rollups may accept blocks with invalid encodings, believing fraud proofs would catch them |
| A (Availability) | L (Low) | Encoding errors could cause partial data recovery failures in affected rollups |

## Recommendation

1. Update `fraud_proofs.md` to document the BEFP removal and accurately describe the current DAS-only security model.
2. Correct CIP-019's claim that the security model is unchanged, adding a note about the BEFP removal and its implications.
3. Document clearly in light node guides that DAS guarantees availability only, not data correctness (encoding validity).
4. Add a recommendation for independent correctness verification in the rollup integration guide, so downstream builders do not rely solely on Celestia for encoding validation.
