# AVL-T05: KZG Trusted Setup Relies on Unauditable Ceremony

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: T · **Scope**: chain · **Status**: Unverified
{% endhint %}

## Overview

Avail uses KZG polynomial commitments for data availability proofs, and these commitments depend on a structured reference string generated through a trusted setup ceremony. Avail specifically uses the Filecoin Powers of Tau ceremony (challenge_19) on the BLS12-381 elliptic curve.

The security of this trusted setup rests on the 1-of-N honest participant assumption: as long as at least one participant in the ceremony was honest and properly destroyed their toxic waste, the resulting parameters are secure. If every single participant colluded or was compromised, an attacker could reconstruct the secret trapdoor and forge valid KZG proofs for invalid data. This would allow fabricated data availability proofs to pass verification, fundamentally breaking the integrity guarantees that Avail's DA layer provides.

The practical probability of all ceremony participants being dishonest is considered extremely low, given the large number of independent participants in the Filecoin Powers of Tau ceremony. However, this threat is classified as Unverified because the ceremony data is not independently auditable. There is no way to independently verify the integrity of the ceremony parameters without trusting the ceremony process and its participants.

## Prerequisites

- All participants in the Filecoin Powers of Tau ceremony must have been dishonest or compromised
- The attacker must reconstruct the secret trapdoor from the compromised ceremony parameters
- This is a theoretical threat with extremely low practical probability

## Attack Scenario

1. An attacker who participated in or compromised all participants of the Filecoin Powers of Tau ceremony reconstructs the secret trapdoor value from the ceremony's toxic waste.
2. Using the trapdoor, the attacker generates valid-looking KZG proofs for fabricated data. These proofs pass on-chain verification because the structured reference string itself is compromised.
3. The Avail network accepts the forged proofs as valid data availability attestations. This breaks the fundamental guarantee that data was actually made available, potentially allowing validators to attest to data that was never published. Any system relying on Avail's DA guarantees would be affected.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Scope | chain |

### Scoring Rationale

There is no direct financial impact from forged DA proofs alone (B:N). The attack operates at the network level through the cryptographic infrastructure (AV:N). Complexity is high because it requires all ceremony participants to have been dishonest, which is the 1-of-N assumption (AC:H). No special privileges are needed since the vulnerability is in the ceremony itself, not in access control (PR:N). The impact stays within the KZG verification scope (S:U). Integrity impact is high because validity proof forgery is theoretically possible, but the practical probability is extremely low given the number of ceremony participants (I:H, II:M). There is no availability impact because forged proofs do not disrupt service (A:N, AI:N).

## Evidence

### Source Code

- Avail uses the Filecoin Powers of Tau ceremony (challenge_19) for its KZG trusted setup
- The commitment scheme operates on the BLS12-381 elliptic curve

### Verification Status

This threat is classified as Unverified. Confirming or ruling out the integrity of the trusted setup would require independent verification of the structured reference string parameters, which is not possible from outside the ceremony process. The threat remains theoretical.

## Mitigations

The primary mitigation is the 1-of-N honest participant assumption itself. The Filecoin Powers of Tau ceremony included a large number of independent participants from diverse backgrounds and organizations. As long as at least one participant honestly destroyed their toxic waste, the setup parameters are secure. However, the ceremony data cannot be independently audited, so this assurance relies on trust in the ceremony process rather than cryptographic verification.
