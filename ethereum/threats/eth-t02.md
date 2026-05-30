# ETH-T02: KZG Trusted Setup File Replacement

{% hint style="info" %}
**Severity**: Medium (4.2/10) · **STRIDE**: T (Tampering) · **Status**: code_verified
{% endhint %}

## Overview

The KZG trusted setup is a critical cryptographic parameter set used for blob commitment verification in Ethereum's data availability layer. If an attacker could replace the trusted setup file with a malicious version, they could forge valid-looking KZG proofs for arbitrary data, completely undermining the integrity of blob verification across the network.

In the go-ethereum client, the trusted setup file is protected by two mechanisms: `go:embed` and `sync.Once`. The `go:embed` directive embeds the trusted setup data directly into the compiled binary at build time, meaning there is no separate file to replace at runtime. The `sync.Once` primitive ensures the setup parameters are initialized exactly once and cannot be re-initialized during the process lifetime.

Because of these protections, an attacker would need to compromise the build environment or the binary distribution chain to inject a malicious trusted setup. This elevates the attack to a supply-chain compromise, which is significantly harder than runtime file replacement. The scope is changed because a successful compromise would affect all nodes running the tampered binary, crossing trust boundaries.

## Prerequisites

- Access to the build environment where go-ethereum binaries are compiled, or
- Ability to compromise the binary distribution chain (e.g., release pipeline, package repositories)
- The attack cannot be executed at runtime against a deployed node

## Attack Scenario

1. The attacker gains access to the go-ethereum build infrastructure or release pipeline.
2. The attacker replaces the embedded KZG trusted setup file with a malicious version containing parameters they control.
3. Binaries compiled with the tampered setup are distributed to node operators through normal update channels.
4. Nodes running the compromised binary accept forged KZG proofs, allowing invalid blob data to be treated as valid.
5. The attacker publishes blobs with forged commitments, undermining data availability guarantees for any rollup or application relying on the compromised nodes.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 4.2/10 (Medium) |
| BVSS Vector | `B:N/AV:P/AC:H/PR:R/UI:N/S:C/C:N/CI:N/I:H/II:H/A:N/AI:N` |
| Scope | protocol |

### Scoring Rationale

The attack vector is physical/local since it requires access to the build environment, making the access vector restricted. Attack complexity is high due to the need for supply-chain compromise. Privileges are required as the attacker needs build system access. The scope is changed because a tampered binary affects trust assumptions across the entire network, not just the compromised build system. Integrity impact is high at both node and chain levels because forged KZG proofs would undermine the fundamental cryptographic guarantees of the data availability layer. Confidentiality and availability are unaffected.

## Evidence

### Source Code

- **Repository**: go-ethereum (Geth execution client)
- **Finding**: The KZG trusted setup file is embedded using Go's `go:embed` directive, which includes the file contents in the binary at compile time. Initialization is protected by `sync.Once`, preventing any runtime re-initialization. These two mechanisms together make runtime replacement of the trusted setup impossible.

## Mitigations

The `go:embed` mechanism ensures the trusted setup is immutable after compilation, eliminating runtime file replacement as an attack vector. The `sync.Once` guard prevents re-initialization even if an attacker gains code execution within the process. Beyond these code-level protections, the go-ethereum project uses reproducible builds and signed releases, allowing node operators to verify binary integrity. The KZG trusted setup itself was generated through a distributed ceremony with thousands of participants, ensuring that no single party can reconstruct the secret parameters.
