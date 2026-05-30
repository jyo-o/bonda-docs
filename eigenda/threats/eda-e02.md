# EDA-E02: Single Multisig Controls All Eight Core Contracts Without Timelock

{% hint style="info" %}
**Severity**: Low (2.7/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Overview

A single Gnosis Safe multisig (`0x002721...`) with a 3-of-4 threshold and no timelock controls the ownership of eight core EigenDA contracts: ServiceManager (`0x870679...`), RegistryCoordinator (`0x0BAAc7...`), EjectionManager (`0x130d8E...`), ThresholdRegistry (`0xdb4c89...`), RelayRegistry (`0xD160e6...`), DisperserRegistry (`0x78cb05...`), PaymentVault (`0xb2e7ef...`), and CertVerifierRouter (`0x1be725...`). All four signers are externally owned accounts (EOAs) with no ENS names or metadata URIs set, making on-chain identity verification impossible.

Compromising any three of the four signer keys would grant total governance control over EigenDA. The impact scenarios include: modifying `confirmationThreshold` and `adversaryThreshold` in the ThresholdRegistry to manipulate security parameters; using `addCertVerifier()` in the CertVerifierRouter to replace certificate verification logic (though the CertVerifier itself at `0x61692e...` is immutable); calling `withdraw(uint256)` on PaymentVault to drain the vault balance; force-ejecting operators via EjectionManager to manipulate quorum composition; and replacing dispersers or relays via their respective registries to control data paths.

This finding is consistent with the Dedaub N1 audit item, which classified it as Informational. Key EigenDA-specific observations include the absence of a timelock (execution is immediate with no community response window), the concentration of all eight core contracts under a single Safe (no privilege separation), and the inability to verify signer identities on-chain.

## Prerequisites

- Compromise of 3 out of 4 signer private keys. Signers: `0xA3e302...`, `0x1b6cC4...`, `0x403F4d...`, `0x891bbC...`.

## Attack Scenario

1. An attacker compromises three of the four signer EOA private keys through phishing, social engineering, or key theft.
2. The attacker constructs a multisig transaction targeting one of the eight controlled contracts.
3. The transaction executes immediately with no timelock delay, giving the community no time to respond.
4. Depending on the target contract, the attacker can drain the PaymentVault, replace certificate verification logic, eject honest operators, or take over data routing infrastructure.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.7/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:H/I:H/A:H/CI:M/II:M/AI:M` |
| Scope | Bridge |

### Scoring Rationale

Blockchain Impact (B) is None because multisig key compromise leading to fund theft is a common premise for all Safe-based protocols and is not an EigenDA-specific vulnerability, consistent with the Dedaub N1 Informational classification. Attack Vector (AV) is Physical because simultaneous compromise of 3 independent keys requires physical access or social engineering. Attack Complexity (AC) is High because 3-of-4 multisig is a security hardening measure, though the binary BVSS choice between High and Low overrepresents the actual difficulty. Privileges Required (PR) is Reserved because signer credentials are needed. The CIA scores reflect full control upon successful compromise, but the Impact is downgraded to Medium because the compromise scenario is a governance observation rather than an exploit path.

## Evidence

### On-Chain Verification

- `getOwners()` returns 4 signers: `[0xA3e3, 0x1b6c, 0x403F, 0x891b]`.
- `getThreshold()` returns 3.
- `owner()` called on all 8 contracts returns `0x002721B4`.
- CertVerifier at `0x61692e...`: `owner()` call reverts (immutable contract).
- CertVerifierRouter at `0x1be725...`: `owner()` returns `0x002721B4`.
- `certVersion()` returns 3 on mainnet (code indicates 4, but mainnet is at version 3).
- Verified at block 25101686.

### Source Code

- [`contracts/src/integrations/cert/router/EigenDACertVerifierRouter.sol`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/router/EigenDACertVerifierRouter.sol) -- Router contract with `addCertVerifier()` gated by `onlyOwner`.

### PoC Testing

- `poc/04-*/evidence.yaml` confirmed multisig configuration and ownership.
- `poc/03-*/evidence.yaml` confirmed CertVerifier immutability and Router-based replacement path.
- 17 contracts total, 12 are EIP-1967 proxies under a single ProxyAdmin.

**PoC References**: #02, #03

## Mitigations

The 3-of-4 multisig structure provides baseline security against single-key compromise. This was also noted by the Dedaub N1 audit. However, the absence of a timelock means that any multisig transaction executes immediately, and signer identities are not verifiable on-chain. Adding a timelock and separating contract ownership across multiple Safes would improve the governance posture.
