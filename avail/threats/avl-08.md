# AVL-08: Key Holder Overlap Across Three Governance Multisigs

{% hint style="info" %}
**Category**: Governance Observation · **Status**: verified
{% endhint %}

## Summary

Avail uses three separate governance multisigs for different functions, but extensive key holder overlap undermines their independence. Four of five Pauser Multisig owners are also Governance Multisig members, and one address appears in all three multisigs. Compromising the Governance Multisig effectively compromises the Pauser as well, since overlapping members exceed the Pauser threshold.

## Description

The bridge infrastructure relies on three separate multisig wallets for different governance functions. In principle, this provides defense in depth. In practice, the overlapping membership undermines true independence.

![Key holder overlap across three governance multisigs](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/avail/assets/avl-08-key-overlap.png)

The practical consequence is that the three multisigs do not provide truly independent layers of security. A governance compromise cascades into pauser control, and a single key holder participating in all three creates a concentrated point of risk.

## Proof of Concept

On-chain state was queried on Ethereum mainnet. See [Verification Evidence](../evidence.md#governance-multisig-cross-analysis-avl-08) for full commands and results.

- Pauser Multisig `getOwners()` returns 5 owners, 4 of which are identical to Governance Multisig members
- Address 0x72Ff...4f54 confirmed present in all three multisigs through cross-referencing owner lists
- Pauser Multisig was initially discovered by tracing `RoleGranted` events on the bridge contracts

## Impact

Compromising 4 of the 7 Governance Multisig keys automatically grants control over the Pauser Multisig because at least 3 of those keys also meet the Pauser's 3-of-5 threshold. The attacker can pause the bridge at will or prevent emergency pauses during an active attack. If the compromised set includes the shared key holder 0x72Ff...4f54, the attacker also gains a signing position in the SP1VerifierGateway's 2-of-3 multisig, needing only one more key to manipulate ZK verifier routing.

Affects the Decentralization baseline; signer overlap reduces the effective independence of the governing multisigs. This is recorded as a Governance Observation and carries no score.

## Recommendation

1. **Diversify Pauser Multisig membership**: Replace overlapping members with independent key holders so that the Pauser function is genuinely separate from governance.
2. **Remove the shared key holder from one or more multisigs**: Ensure no single address appears in all three multisigs to eliminate the concentrated point of risk at 0x72Ff...4f54.
3. **Document multisig independence requirements**: Establish a policy requiring minimum independence between governance multisigs and audit compliance regularly.
