# AVL-E01: ZK Verifier Route Manipulation via SP1VerifierGateway Multisig

{% hint style="info" %}
**Severity**: Medium (4.0/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

The SP1VerifierGateway contract (0xCafEf00d348Adbd57c37d1B77e0619C6244C6878) controls which ZK verifier contracts validate proofs on Avail's bridge. It is owned by a 2-of-3 Gnosis Safe multisig with key holder overlap: Owner #2 (0x72Ff...4f54) is the same individual as Owner #4 of the Governance Multisig. This overlap weakens the effective independence of the signing set, and only two compromised keys are needed to replace the verifier with a malicious contract.

## Description

The SP1VerifierGateway determines whether zero-knowledge proofs submitted to the bridge are accepted as valid. Its ownership is controlled by a Gnosis Safe with a 2-of-3 signing threshold.

```
// @audit — SP1VerifierGateway (0xCafE...6878):
//          Threshold: 2-of-3 Gnosis Safe
//          Owner #2 (0x72Ff...4f54) == Governance Multisig Owner #4
//          Key holder overlap weakens effective signing independence.
//          Only 2 keys needed to replace the ZK verifier contract.
```

The vulnerability lies in the low threshold combined with key holder overlap. One individual already holds signing power across multiple critical contracts, meaning an attacker who compromises that key is already 1/2 of the way to controlling the verifier route and 1/4 of the way to controlling governance.

## Proof of Concept

On-chain state was queried on Ethereum mainnet. See [Verification Evidence](../evidence.md#2-sp1verifiergateway-multisig-analysis-avl-e01) for full commands and results.

- `getThreshold()` returns `2`, confirming the 2-of-3 threshold
- `getOwners()` returns 3 addresses; Owner #2 (0x72Ff...4f54) cross-verified as identical to Governance Multisig Owner #4

## Impact

If 2 of the 3 signing keys are compromised, the attacker could replace the legitimate ZK verifier contract with a malicious one that accepts any proof as valid. This would enable fabricated zero-knowledge proofs to be accepted by the bridge, potentially allowing unauthorized bridge operations such as withdrawing funds that were never deposited on the source chain. The overlapping key holder (0x72Ff...4f54) between the SP1 and Governance multisigs is a high-value target whose compromise cascades across both security domains.

### CVSS 3.1
**Score**: 4.0/10 (Medium)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | 2 of 3 keys must be compromised through physical or social engineering targeting of key holders |
| AC | H (High) | Requires simultaneous compromise of two separate signer keys |
| PR | L (Low) | Attacker needs multisig signer credentials to execute |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact limited to the verifier route change function |
| C | N (None) | No confidentiality impact |
| I | H (High) | Successful verifier replacement would allow false proofs to be accepted |
| A | N (None) | No direct availability impact from verifier replacement |

## Recommendation

1. **Increase the SP1VerifierGateway multisig threshold**: Raise the threshold from 2-of-3 to at least 3-of-5 to require more key compromises for a successful attack.
2. **Eliminate key holder overlap**: Ensure that SP1VerifierGateway signers are independent from Governance Multisig members to provide true separation of concerns.
3. **Add a timelock to verifier changes**: Implement a delay between proposing and executing a verifier replacement, giving the community a window to detect suspicious changes.
