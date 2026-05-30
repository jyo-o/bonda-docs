# EDA-E02: Single Multisig Controls All Eight Core Contracts Without Timelock

{% hint style="info" %}
**Severity**: Medium (6.3/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

A single Gnosis Safe multisig (`0x002721...`) with a 3-of-4 threshold and no timelock controls the ownership of eight core EigenDA contracts. All four signers are externally owned accounts (EOAs) with no ENS names or metadata URIs, making on-chain identity verification impossible. The root cause is the concentration of all governance authority in a single Safe without privilege separation or execution delay. Compromising any three of the four signer keys would grant total governance control over EigenDA, enabling immediate execution of arbitrary changes with no community response window.

## Description

The multisig (`0x002721...`) owns the following eight core contracts:

1. ServiceManager (`0x870679...`)
2. RegistryCoordinator (`0x0BAAc7...`)
3. EjectionManager (`0x130d8E...`)
4. ThresholdRegistry (`0xdb4c89...`)
5. RelayRegistry (`0xD160e6...`)
6. DisperserRegistry (`0x78cb05...`)
7. PaymentVault (`0xb2e7ef...`)
8. CertVerifierRouter (`0x1be725...`)

Four signers: `0xA3e302...`, `0x1b6cC4...`, `0x403F4d...`, `0x891bbC...` (all EOAs, no ENS).
Threshold: 3-of-4.

**Source**: [`contracts/src/integrations/cert/router/EigenDACertVerifierRouter.sol`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/router/EigenDACertVerifierRouter.sol) -- Router contract with `addCertVerifier()` gated by `onlyOwner`.

Impact scenarios upon 3-of-4 key compromise include:
- Modifying `confirmationThreshold` and `adversaryThreshold` in the ThresholdRegistry
- Using `addCertVerifier()` in the CertVerifierRouter to replace certificate verification logic (though the CertVerifier itself at `0x61692e...` is immutable)
- Calling `withdraw(uint256)` on PaymentVault to drain the vault balance
- Force-ejecting operators via EjectionManager
- Replacing dispersers or relays via their respective registries

This finding is consistent with the Dedaub N1 audit item (Informational classification). Key observations: no timelock (execution is immediate), all eight core contracts under a single Safe (no privilege separation), and signer identities are not verifiable on-chain.

Additionally, 17 contracts total were identified, with 12 being EIP-1967 proxies under a single ProxyAdmin.

## Proof of Concept

### On-Chain Verification

- `getOwners()` returns 4 signers: `[0xA3e3, 0x1b6c, 0x403F, 0x891b]`.
- `getThreshold()` returns 3.
- `owner()` called on all 8 contracts returns `0x002721B4`.
- CertVerifier at `0x61692e...`: `owner()` call reverts (immutable contract).
- CertVerifierRouter at `0x1be725...`: `owner()` returns `0x002721B4`.
- `certVersion()` returns 3 on mainnet (code indicates 4, but mainnet is at version 3).
- Verified at block 25101686.

### Reproduction

- `poc/04-*/evidence.yaml` confirmed multisig configuration and ownership.
- `poc/03-*/evidence.yaml` confirmed CertVerifier immutability and Router-based replacement path.

**PoC References**: #02, #03

## Impact

Compromise of 3-of-4 signer keys grants total governance control over EigenDA with immediate execution and no community response window. The attacker could drain the PaymentVault, replace certificate verification logic via the CertVerifierRouter, eject honest operators, or take over data routing infrastructure by replacing dispersers and relays. The attack requires simultaneous compromise of 3 independent private keys through physical access or social engineering, which is a high barrier. However, the absence of a timelock means there is no recovery window once a malicious transaction is submitted. This is consistent with the Dedaub N1 Informational classification.

### CVSS 3.1

**Score**: 6.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | P (Physical) | Simultaneous compromise of 3 independent keys requires physical access or social engineering |
| AC (Attack Complexity) | H (High) | 3-of-4 multisig is a security hardening measure; compromising 3 independent keys simultaneously is difficult |
| PR (Privileges Required) | L (Low) | Signer credentials are needed |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the EigenDA governance scope |
| C (Confidentiality) | H (High) | Full control over all contract configurations upon compromise |
| I (Integrity) | H (High) | Can modify thresholds, replace verification logic, manipulate quorum composition |
| A (Availability) | H (High) | Can drain PaymentVault, eject operators, replace data routing infrastructure |

## Recommendation

1. Add a timelock to the multisig to provide a community response window before transactions execute.
2. Separate contract ownership across multiple Safes to implement privilege separation (e.g., separate financial operations from protocol parameter changes).
3. Increase the signer set size to raise the threshold for compromise.
4. Publish signer identities or link ENS names to enable on-chain identity verification.
