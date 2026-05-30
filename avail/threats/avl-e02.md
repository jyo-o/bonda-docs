# AVL-E02: Key Holder Overlap Across Three Governance Multisigs

{% hint style="info" %}
**Severity**: Low (2.9/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

Avail's three governance multisigs (Governance 4-of-7, Pauser 3-of-5, SP1VerifierGateway 2-of-3) have extensive key holder overlap. Four of five Pauser Multisig owners are also Governance Multisig members, and one address (0x72Ff...4f54) appears in all three multisigs. This overlap means that compromising the Governance Multisig effectively compromises the Pauser Multisig, undermining the intended separation of governance functions.

## Description

The bridge infrastructure relies on three separate multisig wallets for different governance functions. In principle, this provides defense in depth. In practice, the overlapping membership undermines true independence.

```
// @audit — Multisig key holder overlap:
//          Governance Multisig: 4-of-7 threshold
//          Pauser Multisig (0x1a5b...8930): 3-of-5 threshold, 4/5 owners overlap with Governance
//          SP1VerifierGateway (0xCafE...6878): 2-of-3 threshold
//          Address 0x72Ff...4f54: present in ALL THREE multisigs
//          (Governance #4, Pauser #4, SP1VerifierGateway #2)
//          Compromising 3 Governance keys also meets Pauser's 3-of-5 threshold.
```

The practical consequence is that the three multisigs do not provide truly independent layers of security. A governance compromise cascades into pauser control, and a single key holder participating in all three creates a concentrated point of risk.

## Proof of Concept

On-chain verification confirmed the overlap:

- `cast call 0x1a5b...8930 "getOwners()(address[])"` returns 5 owners, of which 4 are identical to Governance Multisig members
- `cast call 0x1a5b...8930 "getThreshold()(uint256)"` returns `3`, confirming the 3-of-5 threshold
- Address 0x72Ff26D9517324eEFA89A48B75c5df41132c4f54 confirmed present in all three multisigs through cross-referencing owner lists
- Pauser Multisig was initially discovered by tracing `RoleGranted` events on the bridge contracts

Reference: poc_onchain_verification.md, section 11.

## Impact

Compromising 4 of the 7 Governance Multisig keys automatically grants control over the Pauser Multisig (since at least 3 of those keys also meet the Pauser's 3-of-5 threshold). The attacker can pause the bridge at will or prevent emergency pauses during an active attack. If the compromised set includes the shared key holder 0x72Ff...4f54, the attacker also gains a signing position in the SP1VerifierGateway's 2-of-3 multisig, needing only one more key to manipulate ZK verifier routing.

### CVSS 3.1
**Score**: 2.9/10 (Low)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Requires physical or social engineering access to compromise multiple key holders |
| AC | H (High) | Multiple simultaneous key compromises needed |
| PR | L (Low) | Attacker needs signer credentials for the multisigs |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact limited to internal governance structure |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Pauser independence from governance is lost but does not create a direct exploitation path |
| A | L (Low) | Emergency response capabilities may be delayed or compromised if same entity controls both functions |

## Recommendation

1. **Diversify Pauser Multisig membership**: Replace overlapping members with independent key holders so that the Pauser function is genuinely separate from governance.
2. **Remove the shared key holder from one or more multisigs**: Ensure no single address appears in all three multisigs to eliminate the concentrated point of risk at 0x72Ff...4f54.
3. **Document multisig independence requirements**: Establish a policy requiring minimum independence between governance multisigs and audit compliance regularly.
