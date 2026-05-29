# G-OPS-01: Multi-surface Information Asymmetry — Structural Pattern (docs/spec/blog vs. code)

{% hint style="info" %}
**Severity**: High · **STRIDE**: T (Tampering) · **Scope**: protocol · **Status**: verified
{% endhint %}

## Overview

Multiple user-facing surfaces including official specs, docs, blog, and CIPs have been stale for 5+ weeks, promising BEFP, 1-of-N honest full node, and 25% slashing threshold. The discrepancy is not accidental but a structural pattern: parameter/safety-model change PRs are not accompanied by docs PRs. This can cause L2 builder finality mis-design and academic citation errors.

## Core Invariants Affected

Documentation/process transparency gap. Can cause L2 builder mis-design.

## Prerequisites

Not a code exploit. L2 builders/researchers trust stale surfaces and design incorrectly.

## Attack Scenario

**Condition**: Safety model/parameter change PRs merge without accompanying docs + users trust stale surfaces

**Example**: Stale surfaces: fraud_proofs.md ('BEFPs enforce DAS'), docs slashing ('25% of 5,000 blocks', actual is 0.1%/10,000), CIP-019 ('Does not change the security model').

## Impact

| Metric | Value |
|--------|-------|
| Severity | High |
| Likelihood | Structural/non-exploit (social engineering surface) |
| Scope | protocol |
| Target | ExternalEntity |

## Code References

- [Doc: `celestia-app/specs/src/fraud_proofs.md:5-13 (stale)`](https://github.com/celestiaorg/celestia-app/blob/main/specs/src/fraud_proofs.md#L5-L13)
- Doc: `docs.celestia.org/operate/consensus-validators/slashing (25% of 5000 blocks, stale)`
- [Doc: `CIPs/cips/cip-019.md ('Does not change the security model')`](https://github.com/celestiaorg/CIPs/blob/main/cips/cip-019.md)
- [PR #7090: 'to match mainnet governance', docs PR 미동반](https://github.com/celestiaorg/celestia-app/pull/7090)

## Verification & Evidence

**Status**: verified

docs.celestia.org slashing page confirmed stale. Contradiction with mainnet measurement (0.1%/10,000) confirmed.

## Mitigations

Recommendations: (1) Make docs PR mandatory for code PRs (block CI without docs PR), (2) Add deprecation banner to all stale surfaces, (3) Quarterly stale audit.
