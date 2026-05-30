# ETH-T03: Gloas Data Column Inclusion Proof Omission

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: T (Tampering) · **Status**: partial
{% endhint %}

## Summary

The Gloas fork proposal omits data column inclusion proofs from its design, meaning nodes would accept data columns without cryptographic proof that those columns are correctly included in a committed dataset. Without inclusion proofs, an attacker could supply fabricated or corrupted data columns that pass validation. Gloas is currently unscheduled with no confirmed timeline, making this a design-phase threat.

## Description

Data column inclusion proof verification is absent from the current Gloas design. Code paths related to Gloas have been identified but remain in an unfinished state consistent with the fork's unscheduled status.

```
# @audit — no inclusion proof verification in Gloas design
# Gloas fork: data columns accepted without cryptographic inclusion proof
# Nodes cannot verify that a received column is correctly included
# in any committed blob dataset.
# Fabricated columns with valid-looking formats would pass validation.
```

This is a design gap rather than an implementation bug. If Gloas is activated without addressing it, an attacker could craft data columns with valid-looking formats but without verifiable inclusion in any committed blob, and distribute them through the PeerDAS gossip network. Receiving nodes would accept these fabricated columns, potentially affecting rollup state derivation.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Downstream consumers relying on data availability guarantees could receive incorrect or fabricated data, potentially affecting rollup state derivation. Integrity impact is medium because accepting unproven data columns corrupts data availability guarantees. The threat is contingent on Gloas activation — there is no impact on the current live network.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Fabricated columns distributed through PeerDAS gossip network |
| AC | H (High) | Gloas must first be activated; exploitation depends on a future protocol change |
| PR | N (None) | No privileges required to submit data columns |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Attack operates within the data availability trust boundary |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Unproven data columns could corrupt data availability guarantees |
| A | N (None) | No availability impact |

## Recommendation

1. **Implement data column inclusion proof mechanism**: A cryptographic inclusion proof scheme must be designed and implemented as part of the Gloas specification before the fork progresses to a scheduled status.
2. **Require formal analysis before activation**: Community review and formal analysis of the inclusion proof scheme should precede any activation decision.
3. **Ensure multi-client test coverage**: Extensive specification review, consensus-spec-tests coverage, and multi-client testing must validate the inclusion proof mechanism before mainnet deployment.
