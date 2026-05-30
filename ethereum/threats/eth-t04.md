# ETH-T04: Cell Index Bounds Check Asymmetry

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: T (Tampering) · **Status**: code_verified
{% endhint %}

## Summary

The KZG cryptographic library contains an asymmetry in cell index bounds checking: `recover_cells_and_kzg_proofs` validates that the number of cells does not exceed `CELLS_PER_EXT_BLOB`, but `verify_cell_kzg_proof_batch` does not perform the equivalent check. Out-of-bounds cell indices could reach the batch verification function, potentially causing undefined behavior. This is a defense-in-depth gap rather than a directly exploitable vulnerability.

## Description

The bounds check asymmetry exists between two related KZG library functions that both process cell indices.

```
# @audit — bounds check present in recovery but missing in batch verification
# recover_cells_and_kzg_proofs:
#   validates num_cells <= CELLS_PER_EXT_BLOB  ← check present
#
# verify_cell_kzg_proof_batch:
#   no equivalent bounds check on cell indices  ← check missing
#
# Asymmetry allows out-of-bounds indices if batch verification
# is reached through a code path that skips recovery.
```

In practice, the risk is low because `recover_cells_and_kzg_proofs` is typically called before batch verification, and upper-layer validation in client implementations filters out malformed inputs before they reach the KZG library. With the Fulu fork, cell operations become the primary path for data availability verification, elevating the importance of consistent bounds checking.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

If out-of-bounds cell indices reach `verify_cell_kzg_proof_batch` through a code path that bypasses recovery, the result could be undefined behavior or incorrect verification results in the KZG library — potentially accepting invalid proofs or triggering a client crash. The practical exploitability is low because upper-layer client validation and typical call ordering (recovery before verification) provide defense.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Malformed data column sidecars can be sent over the network |
| AC | H (High) | Must bypass both upper-layer validation and typical call ordering |
| PR | N (None) | No privileges needed to submit crafted inputs |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Scope limited to the processing node |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Missing redundant check; primary validation exists in the recovery path |
| A | N (None) | Crash possibility is speculative given existing upstream checks |

## Recommendation

1. **Add bounds check to `verify_cell_kzg_proof_batch`**: Add a consistent `num_cells <= CELLS_PER_EXT_BLOB` validation to the batch verification function. This closes the defense-in-depth gap with no performance cost.
2. **Enforce independent input validation**: Every function that processes cell indices should independently validate its inputs rather than relying on upstream callers to enforce bounds.
3. **Maintain upper-layer client validation**: Client implementations should continue filtering malformed inputs before they reach the KZG library as an additional defense layer.
