# CEL-10: Structural Documentation Drift Between Code and Public Surfaces

{% hint style="success" %}
**Category**: Design Note · **Status**: verified
{% endhint %}

## Summary

Multiple user-facing documentation surfaces -- including official specifications, developer docs, blog posts, and CIPs -- have been stale for more than five weeks, continuing to promise security properties and parameters that no longer match the actual codebase. The root cause is the absence of any CI gate or process enforcement linking code changes to documentation updates. L2 builders and academic researchers relying on these public surfaces may design systems or publish analyses based on incorrect assumptions.

## Description

This is a structural pattern rather than an isolated oversight: when parameter changes or safety model modifications are merged via pull requests, accompanying documentation updates are not required.

**Identified Stale Surfaces**

```markdown
// celestia-app/specs/src/fraud_proofs.md:5-13
// @audit Still states "BEFPs enforce DAS" — removed in PR #4934
// https://github.com/celestiaorg/celestia-app/blob/main/specs/src/fraud_proofs.md
```

```markdown
// CIPs/cips/cip-019.md
// @audit Claims "Does not change the security model" — stale after BEFP removal
// https://github.com/celestiaorg/CIPs/blob/main/cips/cip-019.md
```

**Slashing Parameter Drift**

PR `celestia-app#7090` was merged with the description "to match mainnet governance" but no accompanying documentation PR was created. The public documentation at `docs.celestia.org/operate/consensus-validators/slashing` states "25% of 5,000 blocks" while mainnet measurement shows the actual parameter is `min_signed_per_window=0.001` (0.1%) of `signed_blocks_window=10000` blocks. This is a 250x discrepancy in the documented liveness threshold.

The practical consequence is that an L2 builder reading the slashing documentation would design their rollup's liveness assumptions around a 25% missed block tolerance over 5,000 blocks, when the actual threshold is 0.1% of 10,000 blocks -- a fundamentally different liveness guarantee.

## Proof of Concept

Mainnet slashing parameters were confirmed via `celestia-rest.publicnode.com`. See [Verification Evidence](../evidence.md#validator-set-and-slashing-parameters-cel-08-cel-10) for full parameter data. The actual values directly contradict the documented values of "25% of 5,000 blocks" on `docs.celestia.org`.

## Impact

Downstream security design errors in L2 rollups and incorrect academic analyses. The risk is proportional to how widely the stale documentation is referenced. Specific stale surfaces include `fraud_proofs.md` which claims BEFPs enforce DAS, the `docs.celestia.org` slashing page which states 25% of 5,000 blocks while the actual value is 0.1% of 10,000, and CIP-019 which claims the security model is unchanged.

Sets the Verifiability and Liveness Design Baselines through a spec-implementation gap. Documented parameters and the fraud-proof security model do not match the implementation, so the baseline cannot credit the claimed properties.

## Recommendation

1. Make documentation PRs mandatory for code PRs that change safety-relevant parameters or models, enforced via CI gate. For example, require a `docs-updated` label or linked documentation PR before merge.
2. Add deprecation banners to all identified stale documentation surfaces, including `fraud_proofs.md`, CIP-019, and the slashing page on `docs.celestia.org`.
3. Conduct quarterly stale documentation audits to catch drift before it accumulates, comparing on-chain parameters against documented values.
