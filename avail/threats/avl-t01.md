# AVL-T01: VectorX Can Be Upgraded Instantly Without Timelock

{% hint style="info" %}
**Severity**: Low (2.5/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX is the ZK light-client bridge contract that verifies Avail block headers on Ethereum. It uses the UUPS proxy pattern, where upgrade logic lives inside the implementation contract rather than the proxy. The EIP-1967 admin slot is set to 0x0, confirming this UUPS design.

The Governance Multisig (Multisig 1, a 4-of-7 Safe at 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666) holds the TIMELOCK_ROLE and can upgrade VectorX instantly. Unlike the Avail Bridge contract, which enforces a 24-hour timelock delay on upgrades, VectorX has no such delay. This means a malicious or compromised multisig could replace the VectorX implementation with arbitrary code in a single transaction, with no time window for the community to detect and respond.

The contract inherits from a class called `TimelockedUpgradeable`, but this class only provides an AccessControl role wrapper. It does not implement any actual timelock delay logic. The name is misleading because it suggests time-based protection that does not exist.

## Prerequisites

- Compromise 4 of the 7 signer keys on Avail Governance Multisig 1
- This requires physical access or social engineering against multiple independent signers

## Attack Scenario

1. An attacker compromises 4 of the 7 keys on the Governance Multisig through targeted phishing, social engineering, or physical access to signer devices.
2. The attacker submits and confirms a multisig transaction calling `upgradeTo(malicious_implementation)` on VectorX. Because there is no timelock, the upgrade executes immediately in a single transaction.
3. The malicious implementation can forge data roots to produce false block header attestations, redirect bridge operations, or halt the bridge entirely. The community has no time window to detect the upgrade and respond before damage is done, unlike the Avail Bridge which has a 24-hour delay for the same operation.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.5/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:H/CI:N/II:M/AI:M` |
| Scope | bridge |

### Scoring Rationale

Direct financial impact is uncertain since exploitation requires a malicious upgrade first (B:N). The attack vector requires physical or social engineering access to obtain 4 of 7 multisig signer keys (AV:P). Complexity is high because simultaneously compromising 4 of 7 independent signers is difficult (AC:H). The attacker needs multisig signer credentials specifically (PR:R). The impact stays within the VectorX upgrade scope (S:U). Integrity impact is high because a malicious upgrade can forge data roots, though community detection is possible after the fact (I:H, II:M). Availability impact is high because a bridge halt is possible, but the 4-of-7 multisig threshold provides meaningful protection (A:H, AI:M).

## Evidence

### On-Chain Verification

- EIP-1967 admin slot reads `0x0`, confirming the UUPS proxy pattern where upgrade authority resides in the implementation contract, not in a separate proxy admin

### Source Code

- [TimelockedUpgradeable.sol](https://github.com/availproject/sp1-vector) -- source code confirms this class provides only an AccessControl role wrapper with no actual delay logic implemented, despite its name suggesting timelock functionality
- Avail Bridge contract has a 24-hour timelock for upgrades, but VectorX does not, creating an inconsistency in governance protections

### PoC Testing

On-chain verification confirmed the UUPS pattern via the admin slot value of 0x0. Source code review confirmed the absence of timelock delay logic in TimelockedUpgradeable.

References: poc_onchain_verification.md sections 2 and 4.

## Mitigations

The 4-of-7 multisig threshold provides the primary protection, requiring compromise of a majority of independent signers. However, there is no timelock delay on VectorX upgrades, unlike the Avail Bridge which enforces a 24-hour delay. This means the community has no detection window between when an upgrade is submitted and when it takes effect.
