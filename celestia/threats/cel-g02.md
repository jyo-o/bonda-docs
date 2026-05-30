# CEL-G02: Structural Documentation Drift Between Code and Public Surfaces

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: G · **Status**: verified
{% endhint %}

## Summary

Multiple user-facing documentation surfaces -- including official specifications, developer docs, blog posts, and CIPs -- have been stale for more than five weeks, continuing to promise security properties and parameters that no longer match the actual codebase. The root cause is the absence of any CI gate or process enforcement linking code changes to documentation updates. L2 builders and academic researchers relying on these public surfaces may design systems or publish analyses based on incorrect assumptions.

## Description

This is a structural pattern rather than an isolated oversight: when parameter changes or safety model modifications are merged via pull requests, accompanying documentation updates are not required.

**Identified Stale Surfaces**

```
// celestia-app/specs/src/fraud_proofs.md:5-13
// @audit Still states "BEFPs enforce DAS" — removed in PR #4934
```

```
// CIPs/cips/cip-019.md
// @audit Claims "Does not change the security model" — stale after BEFP removal
```

**Slashing Parameter Drift**

PR `celestia-app#7090` was merged with the description "to match mainnet governance" but no accompanying documentation PR was created. The public documentation at `docs.celestia.org/operate/consensus-validators/slashing` states "25% of 5,000 blocks" while mainnet measurement shows the actual parameter is `min_signed_per_window=0.001` (0.1%) of `signed_blocks_window=10000` blocks. This is a 250x discrepancy in the documented liveness threshold.

The practical consequence is that an L2 builder reading the slashing documentation would design their rollup's liveness assumptions around a 25% missed block tolerance over 5,000 blocks, when the actual threshold is 0.1% of 10,000 blocks -- a fundamentally different liveness guarantee.

## Proof of Concept

Mainnet slashing parameters were confirmed via `celestia-rest.publicnode.com`: `min_signed_per_window=0.001`, `signed_blocks_window=10000`. These directly contradict the documented values of "25% of 5,000 blocks" on `docs.celestia.org`.

## Impact

Downstream security design errors in L2 rollups and incorrect academic analyses. The risk is proportional to how widely the stale documentation is referenced. Specific stale surfaces include `fraud_proofs.md` (claims BEFPs enforce DAS), `docs.celestia.org` slashing page (states 25% of 5,000 blocks when actual is 0.1% of 10,000), and CIP-019 (claims the security model is unchanged).

### CVSS 3.1

**Score**: 5.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Stale documentation is served over the network and consumed remotely |
| AC (Attack Complexity) | L (Low) | No special conditions needed; the stale documentation is publicly accessible and actively referenced |
| PR (Privileges Required) | N (None) | No privileges needed to access the stale documentation |
| UI (User Interaction) | N (None) | No user interaction required; the threat is the passive existence of incorrect documentation |
| S (Scope) | U (Unchanged) | Impact is confined to systems that directly consume Celestia's documented parameters |
| C (Confidentiality) | L (Low) | Information about actual security parameters is obscured by stale documentation, leading to incorrect threat models |
| I (Integrity) | N (None) | No direct integrity impact on Celestia itself; downstream designs may be flawed but Celestia's chain integrity is unaffected |
| A (Availability) | N (None) | No availability impact on Celestia; downstream systems may have flawed liveness assumptions |

## Recommendation

1. Make documentation PRs mandatory for code PRs that change safety-relevant parameters or models, enforced via CI gate (e.g., require a `docs-updated` label or linked documentation PR before merge).
2. Add deprecation banners to all identified stale documentation surfaces, including `fraud_proofs.md`, CIP-019, and the slashing page on `docs.celestia.org`.
3. Conduct quarterly stale documentation audits to catch drift before it accumulates, comparing on-chain parameters against documented values.
