# CEL-T01: Stale Documentation Misrepresents the DAS-only Security Model

{% hint style="warning" %}
**Severity**: High · **STRIDE**: T · **Status**: verified
{% endhint %}

## Overview

Since the transition to the shwap protocol, Bad Encoding Fraud Proofs (BEFPs) never functioned. On 2026-04-14, PR #4934 formally removed BEFP code as dead code, deleting 2,398 lines and adding only 16. The current light node security model relies exclusively on DAS with 16 random samples, which verifies data availability only. There is no mechanism for light nodes to verify data correctness (encoding validity).

Technically, if a cartel controlling two-thirds or more of voting power finalizes a block with invalid encoding, light nodes cannot detect it. However, this scenario requires breaking BFT assumptions and is considered unrealistic. The real threat is not the DAS-only model itself but the fact that official documentation still describes a stronger model.

The fraud_proofs.md specification and CIP-019 continue to state that BEFPs are part of the security model, claiming "BEFPs enforce DAS" and that the security model remains unchanged. Rollup builders who consult this documentation may design systems that rely on Celestia for data correctness verification, assuming fraud proofs will catch invalid encodings. Since those proofs no longer exist, such designs would have a blind spot in their security model. The documentation effectively spoofs a stronger security guarantee than what the protocol actually provides.

## Prerequisites

- None required. The un-updated documentation is itself the ongoing threat.
- Any rollup builder referencing fraud_proofs.md or CIP-019 may adopt incorrect security assumptions.

## Attack Scenario

1. A rollup builder reads Celestia's fraud_proofs.md specification, which states that BEFPs enforce DAS and that one honest full node is sufficient to detect bad encodings.
2. Based on this documentation, the builder designs the rollup's DA verification to rely on Celestia light nodes without implementing independent correctness checks.
3. The rollup launches, trusting that BEFP protection exists.
4. In reality, BEFPs were removed in PR #4934 and never functioned after the shwap transition.
5. The rollup has no mechanism to detect invalid encodings, creating a gap in its security model.

## Impact

Downstream security model contamination affecting any rollup builder who relies on stale documentation. The documentation-reality gap is currently active and referenceable. While the BFT-break scenario is unrealistic, the practical harm path is stale documentation leading to rollup mis-design leading to undetected encoding errors at runtime.

## Evidence

### Source Code

- PR celestia-node#4934 (merged 2026-04-14, commit 89198d23, +16/-2398 lines): removed BEFP dead code
- Issue celestia-node#4930: "fraud proofs are not functional post-shwap"
- `celestia-node/share/availability/light/options.go:10` -- DefaultSampleAmount=16
- `celestia-core/light/verifier.go:14-16` -- DefaultTrustLevel=Fraction{1,3}
- `celestia-node/nodebuilder/share/module.go:134-144` -- shrexsub no-op stub for light nodes
- `celestia-app/specs/src/fraud_proofs.md:5-13` -- still states "BEFPs enforce DAS" (stale)
- `CIPs/cips/cip-019.md` -- claims "Does not change the security model" (stale)
- go-fraud#143 requested archiving the go-fraud repository

## Mitigations

Recommended fixes include updating fraud_proofs.md to document the BEFP removal and describe the current DAS-only model, correcting CIP-019's claim that the security model is unchanged, documenting clearly in light node guides that DAS guarantees availability only and not correctness, and adding a recommendation for independent correctness verification in the rollup integration guide.
