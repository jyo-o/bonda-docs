# ETH-R01: c-kzg-4844 load\_trusted\_setup Missing Subgroup Check

{% hint style="info" %}
**Severity**: Defense-in-Depth (no CVSS) · **STRIDE**: T (Tampering) · **Status**: code\_review
{% endhint %}

## Summary

`load_trusted_setup` deserializes G1/G2 points from the trusted setup without performing **subgroup membership checks** (`blst_p1_in_g1` / `blst_p2_in_g2`). In contrast, the runtime input path (`validate_kzg_g1`) in the same codebase does perform this check, creating a **validation asymmetry**. If an attacker compromises the build pipeline or supply chain and injects a tampered setup, the pairing equation's soundness breaks, allowing **forged proofs to be accepted as valid (theoretical)**. However, since the setup is embedded at build time, this is not a remotely triggerable vulnerability but a **defense-in-depth deficiency**.

## Description

`blst_p1_uncompress` / `blst_p2_uncompress` only verify that a point lies **on the curve** (curve membership) but do not verify **subgroup membership**. The runtime input path calls `blst_p1_in_g1()` after uncompression, but the setup loading path omits this follow-up call. A gap exists between the intended behavior (all points verified for subgroup membership) and the actual behavior (only curve membership verified).

### Vulnerable Code -- Setup Loading Path (no subgroup check)

```c
// src/setup/setup.c -- G1 monomial loading
// https://github.com/ethereum/c-kzg-4844
BLST_ERROR err = blst_p1_uncompress(&p1_affine, &g1_monomial_bytes[i * BYTES_PER_G1]);
if (err != BLST_SUCCESS) goto out_error;
blst_p1_from_affine(&s->g1_values_monomial[i], &p1_affine);
// @audit missing subgroup check -- no blst_p1_in_g1() call
// @audit G1 lagrange and G2 monomial loops have the same omission
```

### Correct Pattern -- Runtime Input Path (for comparison)

```c
// src/common/bytes.c -- validate_kzg_g1
// https://github.com/ethereum/c-kzg-4844
if (blst_p1_uncompress(&p1_affine, b->bytes) != BLST_SUCCESS) return C_KZG_BADARGS;
blst_p1_from_affine(out, &p1_affine);
if (blst_p1_is_inf(out)) return C_KZG_OK;
if (!blst_p1_in_g1(out)) return C_KZG_BADARGS;   // @audit subgroup check -- present at runtime
```

### Prerequisites

The client embeds the setup at build time (Go `go:embed`, Rust `include_bytes!`). Injecting a malicious setup requires **build/deployment pipeline compromise** (supply chain attack). Therefore, this cannot be triggered remotely.

### STRIDE Detail

| Category | Relevance | Analysis |
|----------|-----------|----------|
| **T -- Tampering** | **Primary** | Supply chain compromise to inject points outside the subgroup breaks pairing soundness, allowing forged proof acceptance |
| R -- Repudiation | Partial | No subgroup verification means no failure log on tampered setup load, preventing post-incident tracing |
| D -- DoS | Indirect | Corrupted setup could reject valid blobs or accept invalid ones, disabling DA verification (secondary effect of tampering) |

## Proof of Concept

No exploit reproduction was conducted. The trusted setup is fixed at build time, so no runtime reproduction path exists. This finding is established through **code comparison** (setup loading path vs. runtime input path), not through exploitation.

**Precedent (attributed):** CVE-2023-2003 -- blst's infinity point group-check skip allowed invalid signatures to pass. This demonstrates that subgroup verification omissions in the same library family have been real defects historically, though the reachability conditions differ from this finding.

## Impact

1. **Supply chain compromise** injects tampered trusted setup bytes into the build
2. **Points outside the subgroup are loaded** -- `load_trusted_setup` accepts them without verification
3. **Pairing equation soundness breaks** -- forged proofs pass `verify_kzg_proof`
4. **DA layer disabled** -- invalid blobs accepted as valid, or valid blobs rejected
5. **Cascade (theoretical):** All L2 rollups depending on EIP-4844 blob verification have their data integrity compromised

Standard CVSS (network/remote model) **does not apply**. The attack prerequisite is "build/deployment pipeline control," which cannot be expressed through the CVSS AV axis. **No score is assigned**; this is classified as a **defense-in-depth / input validation consistency** defect.

## Recommendation

Add subgroup checks to all three loading loops in `src/setup/setup.c`:

```c
// [Before] G1 monomial loading -- no check
blst_p1_from_affine(&s->g1_values_monomial[i], &p1_affine);

// [After] Add after G1 monomial / G1 lagrange loading
blst_p1_from_affine(&s->g1_values_monomial[i], &p1_affine);
if (!blst_p1_in_g1(&s->g1_values_monomial[i])) { ret = C_KZG_BADARGS; goto out_error; }

// [After] Add after G2 monomial loading
blst_p2_from_affine(&s->g2_values_monomial[i], &p2_affine);
if (!blst_p2_in_g2(&s->g2_values_monomial[i])) { ret = C_KZG_BADARGS; goto out_error; }
```

**Performance note:** This adds approximately 8,000 subgroup checks (G1 4096+4096 + G2 65) at setup loading time only (one-time cost). Actual performance delta should be measured before submission.
