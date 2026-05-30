# AVL-E01: ZK Verifier Route Manipulation via SP1VerifierGateway Multisig

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

The SP1VerifierGateway contract (0xCafEf00d348Adbd57c37d1B77e0619C6244C6878) controls which ZK verifier contracts are used to validate proofs on Avail's bridge. It determines whether a given zero-knowledge proof is accepted as valid. This contract is owned by a Gnosis Safe multisig with a 2-of-3 signing threshold.

The vulnerability lies in the low threshold combined with key holder overlap. Owner #2 (0x72Ff...4f54) of the SP1VerifierGateway is the same person as owner #4 of the Governance Multisig. This means that one individual already holds signing power across multiple critical contracts. Only two signers need to be compromised to change the verifier route.

If an attacker compromises 2 of the 3 signing keys, they could replace the legitimate ZK verifier contract with a malicious one. This would allow fabricated zero-knowledge proofs to be accepted as valid, potentially enabling fraudulent bridge operations. The overlap between the SP1 and Governance multisig weakens the effective independence of the signing set.

## Prerequisites

- Compromise 2 of the 3 SP1VerifierGateway signer keys
- Ability to deploy a malicious verifier contract on Ethereum

## Attack Scenario

1. The attacker compromises 2 of the 3 SP1VerifierGateway signing keys, either through phishing, key theft, or social engineering. The overlapping key holder (0x72Ff...4f54) is a high-value target since they appear in multiple multisigs.
2. Using the compromised keys, the attacker submits a transaction to the SP1VerifierGateway that replaces the legitimate ZK verifier contract address with a malicious verifier that accepts any proof as valid.
3. With the malicious verifier in place, the attacker can submit fabricated proofs to the bridge. These false proofs pass verification, enabling unauthorized bridge operations such as withdrawing funds that were never deposited on the source chain.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Scope | bridge |

### Scoring Rationale

There is no direct financial impact under normal conditions because the attack requires compromising multisig keys first. The attack vector is physical or social engineering-based, since 2 of the 3 keys must be compromised through direct targeting of the key holders. Attack complexity is high because it requires simultaneous compromise of two separate signer keys. The attacker needs multisig signer credentials to execute, and the scope is limited to the verifier route change function. Integrity impact is high because a successful verifier replacement would allow false proofs to be accepted. The infrastructure integrity impact is medium because the one overlapping member between the SP1 and Governance multisigs weakens the effective independence of the signing set.

## Evidence

### On-Chain Verification

- `cast call 0xCafE...6878 "getThreshold()(uint256)"` returns `2`, confirming the 2-of-3 threshold.
- `cast call 0xCafE...6878 "getOwners()(address[])"` returns 3 owner addresses.
- Owner #2 (0x72Ff26D9517324eEFA89A48B75c5df41132c4f54) was cross-verified as identical to Governance Multisig owner #4.

### PoC Testing

- Documented in poc_onchain_verification.md, section 4.

## Mitigations

Verifier replacement is restricted exclusively to the SP1VerifierGateway multisig owners. The 2-of-3 threshold prevents any single compromised key from making changes unilaterally. However, the key holder overlap between the SP1 and Governance multisigs reduces the effective number of independent signers that an attacker would need to target.
