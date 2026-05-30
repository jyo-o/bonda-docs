# ETH-T02: KZG Trusted Setup File Replacement

{% hint style="info" %}
**Severity**: Medium (4.8/10) · **STRIDE**: T (Tampering) · **Status**: code_verified
{% endhint %}

## Summary

The KZG trusted setup is a critical cryptographic parameter set used for blob commitment verification. If an attacker could replace it with a malicious version, they could forge valid-looking KZG proofs for arbitrary data, undermining the integrity of blob verification. In go-ethereum, the trusted setup is protected by `go:embed` (compile-time embedding) and `sync.Once` (single initialization), making runtime replacement impossible and elevating this to a supply-chain attack requiring build environment compromise.

## Description

The KZG trusted setup file is embedded using Go's `go:embed` directive, which includes the file contents in the binary at compile time. Initialization is protected by `sync.Once`, preventing any runtime re-initialization.

```go
// @audit — trusted setup embedded at compile time, not replaceable at runtime
// go-ethereum: KZG trusted setup uses go:embed directive
// The setup file is baked into the binary during compilation.
// sync.Once ensures parameters are initialized exactly once.
// Runtime file replacement is impossible.
// Attack requires compromise of build environment or distribution chain.
```

Because of these protections, an attacker would need to compromise the build environment or the binary distribution chain (release pipeline, package repositories) to inject a malicious trusted setup. A successful compromise would affect all nodes running the tampered binary, crossing trust boundaries.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

A successful supply-chain compromise would allow the attacker to forge KZG proofs, enabling invalid blob data to be treated as valid by all nodes running the tampered binary. This undermines the fundamental cryptographic guarantees of the data availability layer and affects any rollup or application relying on the compromised nodes. The scope is changed because a tampered binary affects trust assumptions across the entire network.

### CVSS 3.1
**Score**: 4.8/10 (Medium)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Requires access to the build environment or distribution infrastructure |
| AC | H (High) | Supply-chain compromise is a complex multi-step attack |
| PR | L (Low) | Attacker needs build system access or distribution pipeline credentials |
| UI | N (None) | No user interaction needed; tampered binaries are distributed via normal channels |
| S | C (Changed) | Tampered binary crosses trust boundaries, affecting the entire network |
| C | N (None) | No confidentiality impact |
| I | H (High) | Forged KZG proofs undermine fundamental cryptographic guarantees |
| A | N (None) | No availability impact |

## Recommendation

1. **Maintain `go:embed` and `sync.Once` protections**: Continue using compile-time embedding and single-initialization patterns to prevent runtime trusted setup replacement.
2. **Use reproducible builds and signed releases**: The go-ethereum project should maintain reproducible builds and cryptographically signed releases so node operators can verify binary integrity before deployment.
3. **Verify trusted setup provenance**: The KZG trusted setup was generated through a distributed ceremony with thousands of participants. Node operators should verify that their binaries contain the canonical trusted setup parameters matching the ceremony output.
