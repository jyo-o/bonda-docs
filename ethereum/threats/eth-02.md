# ETH-02: c-kzg-4844 load\_trusted\_setup Missing Subgroup Check

{% hint style="info" %}
**Severity**: Low (3.8/10) · **Likelihood**: Very Low · **Category**: Vulnerability · **Status**: verified
{% endhint %}

## Summary

`load_trusted_setup` deserializes G1/G2 points from the trusted setup without performing subgroup membership checks (`blst_p1_in_g1` / `blst_p2_in_g2`). The runtime input path (`validate_kzg_g1`) in the same codebase does perform this check, creating a validation asymmetry. If an attacker compromises the build pipeline or supply chain and injects a tampered setup, the pairing equation's soundness breaks, allowing forged proofs to be accepted as valid. Since the setup is embedded at build time, this is not remotely triggerable but a defense-in-depth deficiency.

## Description

![ETH-02 data flow — Ethereum PeerDAS Write path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/ethereum/assets/dfd/ethereum-write.png)

*Data flow — Ethereum PeerDAS Write: KZG.*

`blst_p1_uncompress` / `blst_p2_uncompress` only verify that a point lies on the curve but do not verify subgroup membership. The runtime input path calls `blst_p1_in_g1()` after uncompression, but the setup loading path omits this call. The client embeds the setup at build time (Go `go:embed`, Rust `include_bytes!`), so injecting a malicious setup requires build/deployment pipeline compromise.

```c
// src/setup/setup.c -- G1 monomial loading
// https://github.com/ethereum/c-kzg-4844
BLST_ERROR err = blst_p1_uncompress(&p1_affine, &g1_monomial_bytes[i * BYTES_PER_G1]);
if (err != BLST_SUCCESS) goto out_error;
blst_p1_from_affine(&s->g1_values_monomial[i], &p1_affine);
// @audit missing subgroup check -- no blst_p1_in_g1() call
// @audit G1 lagrange and G2 monomial loops have the same omission
```

For comparison, the runtime input path includes the check:

```c
// src/common/bytes.c -- validate_kzg_g1
// https://github.com/ethereum/c-kzg-4844
if (blst_p1_uncompress(&p1_affine, b->bytes) != BLST_SUCCESS) return C_KZG_BADARGS;
blst_p1_from_affine(out, &p1_affine);
if (blst_p1_is_inf(out)) return C_KZG_OK;
if (!blst_p1_in_g1(out)) return C_KZG_BADARGS;   // @audit subgroup check -- present at runtime
```

## Proof of Concept

No exploit reproduction was conducted. The trusted setup is fixed at build time, so no runtime reproduction path exists. This finding is established through code comparison of the setup loading path vs. the runtime input path.

## Impact

A supply chain compromise injecting tampered trusted setup bytes would cause `load_trusted_setup` to accept points outside the subgroup without verification. This breaks pairing equation soundness, allowing forged proofs to pass `verify_kzg_proof`. All L2 rollups depending on EIP-4844 blob verification would have their data integrity compromised.

Affects the **Verifiability** axis — a tampered trusted setup would let forged proofs pass verification — where it produces a Layer 3 deduction while unpatched.

### CVSS 3.1

**Score**: 3.8/10 (Low)
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | P (Physical) | The setup is embedded at build time (`go:embed` / `include_bytes!`); injecting a tampered setup requires compromising the build or release pipeline rather than any network-reachable interface |
| AC (Attack Complexity) | H (High) | Requires crafting setup points that lie outside the prime-order subgroup yet still pass the on-curve uncompress check, then getting them into the embedded setup |
| PR (Privileges Required) | H (High) | Requires control over the build/deployment pipeline that produces the embedded trusted setup |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the client instance that loads the tampered setup |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | H (High) | A tampered setup that skips the subgroup check breaks pairing-equation soundness, letting forged KZG proofs pass `verify_kzg_proof` |
| A (Availability) | N (None) | No availability impact |

## Recommendation

1. Add `blst_p1_in_g1()` checks after G1 monomial and G1 lagrange loading loops in `src/setup/setup.c`.
2. Add `blst_p2_in_g2()` check after the G2 monomial loading loop.
3. Measure the one-time startup performance delta before submission (approximately 8,000 subgroup checks at load time).
