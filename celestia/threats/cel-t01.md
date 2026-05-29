# CEL-T01: DAS-only Safety Model — Stale Documentation Misrepresents Security Guarantees

{% hint style="info" %}
**Severity**: High · **STRIDE**: T (Tampering) · **Scope**: protocol · **Status**: verified
{% endhint %}

## Overview

Since the shwap protocol transition, BEFP (Bad Encoding Fraud Proof) never functioned, and it was removed as dead code in PR #4934 on 2026-04-14 (+16/-2398 lines). The current light node security model relies solely on DAS with 16 samples, verifying only availability without any data correctness verification. Technically, if a >=2/3 cartel finalizes a bad-encoded block, light nodes cannot detect it -- but this scenario requires breaking BFT assumptions and is unrealistic. The real threat lies elsewhere: official documentation (fraud_proofs.md, CIP-019) still describes 'BEFP + 1-of-N honest full node' as the security model. Rollup builders trusting this documentation may design systems that depend on Celestia DA without their own correctness verification. The documentation claiming stronger security guarantees than reality constitutes a Spoofing threat that poisons downstream security assumptions.

## Core Invariants Affected

`data_recoverability`

Not a direct DA invariant violation but a Spoofing threat. Documentation claims stronger security guarantees than reality, poisoning rollup builders' security design assumptions. The 2/3 cartel scenario requires breaking BFT assumptions and is unrealistic; the practical harm path is stale docs leading to rollup mis-design leading to runtime vulnerabilities.

## Prerequisites

None. The current state of un-updated documentation is itself the threat. Rollup builders referencing fraud_proofs.md or CIP-019 may design with incorrect security assumptions.

## Attack Scenario

**Condition**: Official documentation states a security model (DAS+BEFP) different from the actual model (DAS-only)

**Example**: PR #4934: 'fraud proofs were never produced or validated post-shwap'. Issue #4930: 'straight-forward removal of dead code'. Reviewer @walldiss: 'Goodbye BEFPs'. go-fraud archive request (go-fraud#143). Meanwhile fraud_proofs.md still states 'BEFPs enforce DAS'.

## Impact

| Metric | Value |
|--------|-------|
| Severity | High |
| Likelihood | Immediate (documentation misrepresentation is currently active and referenceable by rollup builders) |
| Scope | protocol |
| Target | Process, Dataflow |
| Core Invariants | data_recoverability |

## Code References

- [PR #4934: MERGED 2026-04-14, commit 89198d23, +16/-2398](https://github.com/celestiaorg/celestia-node/pull/4934)
- [Issue #4930: 'fraud proofs are not functional post-shwap'](https://github.com/celestiaorg/celestia-node/issues/4930)
- [`celestia-node/share/availability/light/options.go:10 (DefaultSampleAmount=16)`](https://github.com/celestiaorg/celestia-node/blob/main/share/availability/light/options.go#L10)
- [`celestia-core/light/verifier.go:14-16 (DefaultTrustLevel=Fraction{1,3})`](https://github.com/celestiaorg/celestia-core/blob/main/light/verifier.go#L14-L16)
- [`celestia-node/nodebuilder/share/module.go:134-144 (shrexsub no-op stub for light nodes)`](https://github.com/celestiaorg/celestia-node/blob/main/nodebuilder/share/module.go#L134-L144)
- [Doc: `celestia-app/specs/src/fraud_proofs.md:5-13 (stale: 'BEFPs enforce DAS')`](https://github.com/celestiaorg/celestia-app/blob/main/specs/src/fraud_proofs.md#L5-L13)
- [Doc: `CIPs/cips/cip-019.md ('Does not change the security model')`](https://github.com/celestiaorg/CIPs/blob/main/cips/cip-019.md)

## Verification & Evidence

**Status**: verified

PR #4934 body, merge date, and diff confirmed. Issue #4930 confirmed. Documentation (fraud_proofs.md, CIP-019) confirmed as un-updated. BEFP removal itself is not a security change (already non-functional), but documentation not reflecting reality is the core threat.

## Mitigations

Recommendations: (1) Update fraud_proofs.md to document BEFP removal and current DAS-only model, (2) Correct CIP-019's 'security model unchanged' claim, (3) Document in light node docs that DAS guarantees availability only, not correctness, (4) Add self-verification recommendation to rollup integration guide.
