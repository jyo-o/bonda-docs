# AVL-E02: Key Holder Overlap Across Three Governance Multisigs

{% hint style="info" %}
**Severity**: Low (0.5/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

Avail's bridge infrastructure relies on three separate multisig wallets for different governance functions: the Governance Multisig (4-of-7 threshold), the Pauser Multisig (0x1a5b...8930, 3-of-5 threshold), and the SP1VerifierGateway (0xCafE...6878, 2-of-3 threshold). In principle, separating these functions across different multisigs provides defense in depth. In practice, the key holders overlap extensively, undermining this separation.

Four of the five Pauser Multisig owners are the same individuals who sit on the Governance Multisig. This means that compromising 3 Governance keys is enough to also control the Pauser function, since those same keys meet the Pauser's 3-of-5 threshold. Additionally, one address (0x72Ff26D9517324eEFA89A48B75c5df41132c4f54) appears in all three multisigs: as owner #4 in Governance, owner #4 in Pauser, and owner #2 in SP1VerifierGateway.

The practical consequence is that the three multisigs do not provide truly independent layers of security. Compromising the Governance Multisig effectively compromises the Pauser Multisig as well, and a single key holder participating in all three multisigs creates a concentrated point of risk. While this is not a direct attack vector on its own, it weakens the overall governance security model.

## Prerequisites

- Compromise of the Governance Multisig keys automatically grants control over the Pauser Multisig due to member overlap
- The shared key holder (0x72Ff...4f54) is a single point of overlap across all three multisigs

## Attack Scenario

1. An attacker targets and compromises 4 of the 7 Governance Multisig signing keys through phishing, social engineering, or key theft. Among these compromised keys, at least 3 belong to individuals who are also Pauser Multisig members.
2. With 3 compromised keys that overlap with the Pauser Multisig, the attacker now meets the Pauser's 3-of-5 threshold. The attacker can pause the bridge at will, disrupting operations, or conversely prevent emergency pauses during an active attack.
3. If the compromised set includes the shared key holder 0x72Ff...4f54, the attacker also gains a signing position in the SP1VerifierGateway's 2-of-3 multisig, needing only one more SP1 key to manipulate ZK verifier routing. A single governance compromise cascades across all three security functions.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.5/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:L/A:L/CI:N/II:L/AI:L` |
| Scope | bridge |

### Scoring Rationale

There is no direct financial impact because the overlap itself does not enable fund theft. The attack vector requires physical or social engineering access to compromise multiple key holders. Attack complexity is high because multiple simultaneous key compromises are needed. The attacker needs signer credentials for the multisigs. The scope is limited to internal governance structure. Integrity impact is low because the Pauser's independence from governance is lost but this does not create a direct exploitation path. Availability impact is low because emergency response capabilities may be delayed or compromised if the Pauser function is controlled by the same entity as governance.

## Evidence

### On-Chain Verification

- `cast call 0x1a5b...8930 "getOwners()(address[])"` returns 5 owners, of which 4 are identical to Governance Multisig members.
- `cast call 0x1a5b...8930 "getThreshold()(uint256)"` returns `3`, confirming the 3-of-5 threshold.
- Address 0x72Ff26D9517324eEFA89A48B75c5df41132c4f54 was confirmed present in all three multisigs through cross-referencing owner lists.
- Pauser Multisig was initially discovered by tracing `RoleGranted` events on the bridge contracts.

### PoC Testing

- Documented in poc_onchain_verification.md, section 11.

## Mitigations

Each multisig maintains its own threshold: the Governance Multisig requires 4 of 7 signatures, the Pauser requires 3 of 5, and the SP1VerifierGateway requires 2 of 3. These separate thresholds provide some defense, but the overlapping membership means the practical security of the Pauser and SP1 multisigs is bounded by the security of the Governance Multisig rather than being truly independent.
