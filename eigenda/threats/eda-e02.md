# EDA-E02: Single 3-of-4 Multisig Controls 8 Core Contracts Simultaneously

{% hint style="info" %}
**Severity**: Low (2.7/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

Gnosis Safe 0x002721... (3-of-4 multisig, no timelock) is the owner of 8 core contracts: ServiceManager (0x870679...), RegistryCoordinator (0x0BAAc7...), EjectionManager (0x130d8E...), ThresholdRegistry (0xdb4c89...), RelayRegistry (0xD160e6...), DisperserRegistry (0x78cb05...), PaymentVault (0xb2e7ef...), CertVerifierRouter (0x1be725...). All 4 signers are EOAs (0xA3e302..., 0x1b6cC4..., 0x403F4d..., 0x891bbC...) with no ENS or metadataURI set, making onchain identity verification impossible. Compromising 3 keys enables total governance takeover. Impact scenarios: (1) ThresholdRegistry -- modify confirmationThreshold/adversaryThreshold to manipulate security inequality. (2) CertVerifierRouter -- addCertVerifier() to replace cert verification logic. CertVerifier itself (0x61692e...) is immutable (owner() reverts) but can be bypassed via Router. (3) PaymentVault -- withdraw(uint256) onlyOwner to drain vault balance. (4) EjectionManager -- force eject operators to manipulate quorum. (5) DisperserRegistry/RelayRegistry -- replace disperser/relay to control data paths.

## Prerequisites

Compromise 3 of 4 signer private keys. Signers: 0xA3e302..., 0x1b6cC4..., 0x403F4d..., 0x891bbC...

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.7/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:H/I:H/A:H/CI:M/II:M/AI:M` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | Process |

### BVSS Rationale

B:N -- Multisig key compromise leading to fund theft is a common premise for all Safe-based protocols, not an EigenDA-specific vulnerability. Consistent with Dedaub N1 Informational classification. AV:P -- Simultaneous compromise of 3 independent keys requires physical access or social engineering. AC:H -- 3-of-4 multisig is a security hardening measure; binary BVSS choice (H/L) overrepresents actual difficulty. PR:R -- Signer credentials required. EigenDA-specific findings: (1) No timelock -- execution is immediate with no community response time. (2) Single Safe for 8 core contracts -- no privilege separation. (3) Signer identities not onchain-verified. CIA reflects full control on successful compromise, but Impact downgraded to M -- the compromise scenario itself is governance observation, not an exploit path.

## Code References

### Source Code

- [`contracts/src/integrations/cert/router/EigenDACertVerifierRouter.sol`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/router/EigenDACertVerifierRouter.sol)

### Audit References

- Dedaub N1(Informational)

### Onchain Evidence

- `getOwners()=[4 signers]`
- `getThreshold()=3`
- `block 25097183`
- `owner() 호출로 8개 컨트랙트 확인`
- `CertVerifierRouter owner()=0x002721B4`
- `CertVerifier owner()=reverted(immutable)`

### PoC Notes

- block=25101686
- poc/04-*/evidence.yaml [VERIFIED]
- CertVerifier.owner()=reverted
- poc/03-*/evidence.yaml [VERIFIED]

### Other References

- getThreshold()=3
- getOwners()=[0xA3e3
- 0x1b6c
- 0x403F
- 0x891b]
- owner()×8=0x002721B4 (all confirmed)
- CertVerifierRouter.owner()=0x002721B4
- certVersion()=3(NOT 4 — code says 4 but mainnet is 3)

## Verification & Evidence

**Status**: Verified

DA Ops Safe 3-of-4, all EOAs, no timelock. 17 contracts of which 12 are EIP-1967 proxies under a single ProxyAdmin. CertVerifier confirmed immutable; Router-based replacement confirmed possible.

**PoC References**: #02, #03

## Mitigations

3-of-4 multisig structure. Also noted by Dedaub N1. However, signer identities are not onchain-verified.
