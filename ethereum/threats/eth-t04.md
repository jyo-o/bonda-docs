# ETH-T04: Cell Index Bounds Check Asymmetry

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: T (Tampering) · **Status**: code_verified
{% endhint %}

## Overview

The KZG cryptographic library used in Ethereum's data availability layer contains an asymmetry in cell index bounds checking between two related functions. The `recover_cells_and_kzg_proofs` function validates that the number of cells does not exceed `CELLS_PER_EXT_BLOB`, but `verify_cell_kzg_proof_batch` does not perform the equivalent check. This means that out-of-bounds cell indices could potentially be passed to the batch verification function without being rejected.

With the Fulu fork, cell operations become the primary path for data availability verification, elevating the importance of consistent bounds checking across all cell-related functions. From a defense-in-depth perspective, every function that processes cell indices should independently validate its inputs rather than relying on upstream callers to enforce bounds.

In practice, the risk is low because `recover_cells_and_kzg_proofs` is typically called before batch verification, and upper-layer validation in client implementations filters out malformed inputs before they reach the KZG library. The asymmetry is a defense-in-depth gap rather than a directly exploitable vulnerability.

## Prerequisites

- Ability to craft inputs with out-of-bounds cell indices that bypass upper-layer validation
- The crafted input must reach `verify_cell_kzg_proof_batch` without first passing through `recover_cells_and_kzg_proofs`

## Attack Scenario

1. The attacker constructs a data column sidecar containing cell indices that exceed `CELLS_PER_EXT_BLOB`.
2. If the input reaches `verify_cell_kzg_proof_batch` through a code path that does not first call `recover_cells_and_kzg_proofs`, the bounds check is skipped.
3. The batch verification function processes the out-of-bounds cell indices, potentially causing undefined behavior or incorrect verification results in the KZG library.
4. Depending on the library implementation, this could result in accepting invalid proofs or triggering a crash in the client node.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:L/II:L/A:N/AI:N` |
| Scope | protocol |

### Scoring Rationale

The attack complexity is high because exploiting this asymmetry requires bypassing both upper-layer client validation and the typical call ordering where recovery precedes verification. No privileges or user interaction are needed. Integrity impact is low at both node and chain levels because the asymmetry is a missing redundant check rather than a primary validation gap. Confidentiality and availability are unaffected. The scope remains unchanged.

## Evidence

### Source Code

- **Component**: KZG cryptographic library (consensus layer specification)
- **Finding**: `recover_cells_and_kzg_proofs` includes a check for `num_cells > CELLS_PER_EXT_BLOB`, while `verify_cell_kzg_proof_batch` does not perform this same bounds validation. The asymmetry has been confirmed through code review.

## Mitigations

The `recover_cells_and_kzg_proofs` function performs the bounds check as a preceding step in the typical processing pipeline, catching out-of-bounds indices before they reach batch verification. Client implementations add additional upper-layer validation that filters malformed inputs before they reach the KZG library. As a defense-in-depth improvement, adding a consistent bounds check to `verify_cell_kzg_proof_batch` would close this gap without any performance cost.
