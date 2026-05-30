# AVL-T05: KZG Trusted Setup Relies on Unauditable Ceremony

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: T · **Status**: Unverified
{% endhint %}

## Summary

Avail uses KZG polynomial commitments for data availability proofs, relying on the Filecoin Powers of Tau ceremony (challenge_19) on BLS12-381. The security rests on the 1-of-N honest participant assumption. If every ceremony participant colluded or was compromised, an attacker could forge valid KZG proofs for invalid data, breaking DA integrity guarantees. The ceremony data is not independently auditable, making this threat inherently unverifiable.

## Description

Avail's KZG commitment scheme depends on a structured reference string (SRS) generated through the Filecoin Powers of Tau trusted setup ceremony (challenge_19). The ceremony operates on the BLS12-381 elliptic curve.

```
// @audit — KZG trusted setup dependency:
//          Ceremony: Filecoin Powers of Tau (challenge_19)
//          Curve: BLS12-381
//          Security assumption: 1-of-N honest participant
//          Verification status: Unauditable — no independent verification
//          of SRS integrity is possible outside the ceremony process.
```

The 1-of-N assumption means that as long as at least one participant honestly destroyed their toxic waste, the parameters are secure. If all participants were compromised, the secret trapdoor could be reconstructed, enabling forgery of valid KZG proofs for arbitrary invalid data.

## Proof of Concept

No proof of concept was conducted for this threat. Confirming or ruling out the integrity of the trusted setup would require independent verification of the structured reference string parameters, which is not possible from outside the ceremony process. The threat remains theoretical.

## Impact

A compromised trusted setup would allow an attacker to generate valid-looking KZG proofs for fabricated data. These proofs would pass on-chain verification because the SRS itself is compromised. The Avail network would accept forged proofs as valid data availability attestations, breaking the fundamental guarantee that data was actually made available. Any system relying on Avail's DA guarantees would be affected. The practical probability is considered extremely low given the large number of independent participants in the ceremony.

### CVSS 3.1
**Score**: 5.9/10 (Medium)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Attack operates through the cryptographic infrastructure at the network level |
| AC | H (High) | Requires all ceremony participants to have been dishonest (1-of-N assumption) |
| PR | N (None) | Vulnerability is in the ceremony itself, not in access control |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact stays within the KZG verification scope |
| C | N (None) | No confidentiality impact |
| I | H (High) | Validity proof forgery is theoretically possible, enabling fake DA attestations |
| A | N (None) | Forged proofs do not disrupt service availability |

## Recommendation

1. **Document the trusted setup dependency explicitly**: Ensure all security documentation clearly states the reliance on the Filecoin Powers of Tau ceremony and the 1-of-N honest participant assumption.
2. **Monitor cryptographic research on transparent setup alternatives**: Track progress on transparent polynomial commitment schemes (e.g., FRI-based) that do not require a trusted setup and could serve as a future migration path.
3. **Publish ceremony participation details**: Provide public documentation of the ceremony's participant count and diversity to support confidence in the 1-of-N assumption.
