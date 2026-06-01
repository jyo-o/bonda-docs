# CEL-11: DAS-Only Safety Model After Fraud Proof Removal

{% hint style="success" %}
**Category**: Design Note · **Status**: verified
{% endhint %}

## Summary

Since the transition to the shwap protocol, Bad Encoding Fraud Proofs (BEFPs) never functioned. PR #4934 formally removed BEFP code as dead code on 2026-04-14, deleting 2,398 lines. The remaining DAS-only model has two compounding weaknesses: light nodes cannot verify data correctness without fraud proofs, and the collective availability guarantee is unrealized because light nodes do not share sampling results with each other. Official documentation continues to describe BEFPs as part of the security model, creating a gap between documented and actual security properties.

## Description

The current light node security model relies exclusively on DAS with 16 random samples (`DefaultSampleAmount=16` at `celestia-node/share/availability/light/options.go:10`), which verifies data availability only. There is no mechanism for light nodes to verify data correctness (encoding validity).

**Collective DAS Guarantee is Unrealized**

DAS security depends on collective sampling: if any light node fails to retrieve a sample, the network should reject the block. In practice, Celestia light nodes operate in isolation — each makes a local availability judgment with no mechanism to share results. This reduces security from collective DAS to individual local checks, where each node relies solely on its own 16 samples. As shown in CEL-07, this isolation enables selective disclosure attacks with no network-wide alarm.

BEFPs previously served as an indirect coordination path — fraud proofs propagated to all light nodes, triggering collective rejection. With BEFPs removed, no inter-node observation mechanism remains for either correctness or availability failures.

**Stale Documentation Surfaces**

```markdown
// celestia-app/specs/src/fraud_proofs.md:5-13
// @audit Still states "BEFPs enforce DAS" — this is factually incorrect post-PR #4934
// https://github.com/celestiaorg/celestia-app/blob/main/specs/src/fraud_proofs.md
```

```markdown
// CIPs/cips/cip-019.md
// @audit Claims "Does not change the security model" — stale after BEFP removal
// https://github.com/celestiaorg/CIPs/blob/main/cips/cip-019.md
```

**BEFP Removal Timeline**

- Issue `celestia-node#4930`: identified that fraud proofs are not functional post-shwap
- PR `celestia-node#4934` (merged 2026-04-14, commit `89198d23`): removed BEFP dead code (+16/-2,398 lines)
- `go-fraud#143`: requested archiving the go-fraud repository

**Additional Code References**

- `celestia-core/light/verifier.go:14-16` -- `DefaultTrustLevel=Fraction{1,3}`
- `celestia-node/nodebuilder/share/module.go:134-144` -- shrexsub no-op stub for light nodes

The threat is not the DAS-only model itself — breaking BFT assumptions to exploit it is unrealistic. The threat is that the documentation spoofs a stronger security guarantee than the protocol actually provides, leading to potential downstream security model contamination.

## Proof of Concept

No proof of concept was conducted for this threat. The documentation-reality gap is directly verifiable by comparing the stale specification text against the merged PR #4934 and the current codebase.

## Impact

The DAS-only model has two layers of degradation. First, light nodes cannot verify data correctness because no fraud proof mechanism exists after the BEFP removal. Second, even the availability guarantee is weaker than the theoretical model because light nodes do not share sampling results with each other, reducing collective DAS to isolated local checks. A rollup builder relying on stale documentation would assume both correctness verification via fraud proofs and strong collective availability guarantees, neither of which currently holds. The practical harm path is: stale documentation leads to rollup mis-design leads to undetected encoding errors or selective unavailability at runtime.

Sets the Verifiability Design Baseline. After fraud-proof removal, light-node safety rests on sampling alone, and the documented model overstates the delivered guarantee, so the baseline cannot credit correctness verification.

## Recommendation

1. Update `fraud_proofs.md` to document the BEFP removal and accurately describe the current DAS-only security model.
2. Correct CIP-019's claim that the security model is unchanged, adding a note about the BEFP removal and its implications.
3. Document clearly in light node guides that DAS guarantees availability only, not data correctness (encoding validity).
4. Implement a sampling result gossip protocol so that light nodes can share availability failures, restoring the collective DAS security guarantee.
5. Add a recommendation for independent correctness verification in the rollup integration guide, so downstream builders do not rely solely on Celestia for encoding validation.
