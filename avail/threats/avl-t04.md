# AVL-T04: Guardian Can Inject Commitments Without ZK Proof Verification

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX normally verifies Avail block headers through a secure pipeline: the relayer calls `commitHeaderRange()`, which verifies an SP1 zero-knowledge proof before storing the commitment on-chain. This ensures that only cryptographically proven block headers are accepted by the bridge.

However, the `updateBlockRangeData()` function in SP1Vector.sol allows the GUARDIAN_ROLE holder to bypass this entire ZK verification pipeline and directly inject arbitrary data and state commitments into the contract. This is an intentional emergency recovery mechanism, designed to allow the system to recover from situations where the ZK proving pipeline fails or the relayer is unable to produce valid proofs.

The GUARDIAN_ROLE is held by Governance Multisig 1, a 4-of-7 Safe. In addition to `updateBlockRangeData()`, the Guardian can also call `updateVerifier()`, `updateVectorXProgramVkey()`, and `updateGenesisState()`, giving it broad control over the verification infrastructure. While this is a deliberate design choice for operational resilience, it means that a compromised multisig could inject false commitments that would be accepted by the bridge without any cryptographic verification.

## Prerequisites

- Compromise 4 of the 7 keys on Governance Multisig 1, which holds GUARDIAN_ROLE
- This requires physical access or social engineering against multiple independent signers

## Attack Scenario

1. An attacker compromises 4 of the 7 keys on the Governance Multisig through targeted phishing, social engineering, or physical access to signer devices.
2. The attacker calls `updateBlockRangeData()` with fabricated block header commitments. Unlike the normal `commitHeaderRange()` path, this function stores the commitments directly without requiring an SP1 ZK proof.
3. The bridge accepts the false commitments as valid Avail block headers. This could enable fraudulent bridge withdrawals, incorrect state attestations, or other manipulations that depend on the integrity of block header data. However, the false data would be detectable by anyone comparing the on-chain commitments against actual Avail block headers.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Scope | bridge |

### Scoring Rationale

There is no direct financial impact from this function alone (B:N). Exploiting it requires physical or social engineering access to obtain 4 of 7 multisig keys (AV:P). Complexity is high because 4-of-7 multisig compromise is required (AC:H). The attacker needs GUARDIAN_ROLE credentials specifically (PR:R). The impact stays within the commitment storage scope (S:U). Integrity impact is high because ZK proof verification can be completely bypassed, but this is an intended emergency mechanism protected by the 4-of-7 multisig (I:H, II:M). There is no availability impact because this function adds data rather than disrupting service (A:N, AI:N).

## Evidence

### Source Code

- [SP1Vector.sol](https://github.com/availproject/sp1-vector) `updateBlockRangeData()` -- source code confirms this function stores commitments directly without any ZK proof verification step, unlike `commitHeaderRange()` which requires SP1 proof verification
- The function is restricted to GUARDIAN_ROLE, which maps to Governance Multisig 1 (4/7)

### PoC Testing

Anvil mainnet fork PoC (test 3) confirmed the guardian ZK bypass behavior, verifying that `updateBlockRangeData()` successfully stores commitments without proof verification. This confirmed the function works as designed for its intended emergency recovery purpose.

References: SP1Vector.sol source analysis; avl_d01_relayer_spof_poc.sh PoC test 3.

## Mitigations

The GUARDIAN_ROLE is held by Governance Multisig 1 with a 4-of-7 threshold, requiring compromise of a majority of independent signers to exploit. This function is designed as an intentional emergency recovery mechanism for situations where the ZK proving pipeline is unavailable. The tradeoff between operational resilience and proof verification bypass is a deliberate architectural decision.
