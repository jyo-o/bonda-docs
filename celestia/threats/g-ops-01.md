# G-OPS-01: Structural Documentation Drift Between Code and Public Surfaces

{% hint style="warning" %}
**Severity**: High · **STRIDE**: T · **Status**: verified
{% endhint %}

## Overview

Multiple user-facing documentation surfaces including official specifications, developer docs, blog posts, and CIPs have been stale for more than five weeks. These surfaces continue to promise security properties and parameters that no longer match the actual codebase, including BEFP-based fraud proofs, a 1-of-N honest full node assumption, and a 25% slashing threshold.

This is not an isolated oversight but a structural pattern: when parameter changes or safety model modifications are merged via pull requests, accompanying documentation updates are not required. There is no CI gate or process enforcement that links code changes to documentation changes. As a result, the gap between documented guarantees and actual behavior grows silently with every safety-relevant code change.

The practical consequence is that L2 builders and academic researchers who rely on these public surfaces may design systems or publish analyses based on incorrect assumptions. For example, a rollup builder reading the slashing documentation would believe that 25% of 5,000 blocks must be missed before penalties apply, when the actual mainnet parameter is 0.1% of 10,000 blocks. Such discrepancies can lead to fundamentally flawed security designs in downstream systems.

## Prerequisites

- No code exploit is involved
- The threat materializes when L2 builders, researchers, or auditors trust stale documentation and design or evaluate systems based on incorrect assumptions

## Attack Scenario

1. A safety-relevant PR is merged in celestia-app (e.g., PR #7090 changing slashing parameters "to match mainnet governance").
2. No accompanying documentation PR is required or created.
3. Public documentation surfaces (docs.celestia.org, specs, CIPs) continue to state the old parameters.
4. An L2 builder reads the slashing page on docs.celestia.org, which states "25% of 5,000 blocks."
5. The builder designs their rollup's liveness assumptions around this incorrect threshold.
6. The actual mainnet parameter is 0.1% of 10,000 blocks, meaning the real liveness guarantee is vastly different from what was assumed.
7. The rollup launches with flawed security assumptions derived from stale documentation.

## Impact

Downstream security design errors in L2 rollups and incorrect academic analyses. The risk is proportional to how widely the stale documentation is referenced. Specific stale surfaces include fraud_proofs.md (claims BEFPs enforce DAS), docs.celestia.org slashing page (states 25% of 5,000 blocks when actual is 0.1% of 10,000), and CIP-019 (claims the security model is unchanged).

## Evidence

### Source Code

- `celestia-app/specs/src/fraud_proofs.md:5-13` -- stale: still states "BEFPs enforce DAS"
- `CIPs/cips/cip-019.md` -- stale: claims "Does not change the security model"
- PR celestia-app#7090 -- merged with description "to match mainnet governance" but no accompanying documentation PR

### On-Chain / Network

- docs.celestia.org/operate/consensus-validators/slashing -- states "25% of 5,000 blocks" while mainnet measurement shows 0.1% of 10,000 blocks
- Mainnet slashing parameters confirmed via celestia-rest.publicnode.com: min_signed_per_window=0.001, signed_blocks_window=10000

## Mitigations

Recommended fixes include making documentation PRs mandatory for code PRs that change safety-relevant parameters or models (enforced via CI), adding deprecation banners to all identified stale documentation surfaces, and conducting quarterly stale documentation audits to catch drift before it accumulates.
