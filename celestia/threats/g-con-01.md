# G-CON-01: KYC Validator Concentration Enabling Legal Censorship

{% hint style="danger" %}
**Severity**: Critical · **STRIDE**: D · **Status**: verified
{% endhint %}

## Overview

Celestia's validator set is highly concentrated: only 8 validators are needed to exceed the one-third voting power threshold, and 6 of these 8 are KYC-regulated financial institutions operating under US, EU, Swiss, and Hong Kong jurisdictions. This concentration means a single coordinated judicial action or sanctions designation could compel enough validators to perform censorship without any malicious intent on their part.

Anchorage Digital alone controls 11.08% of voting power and, as a US-regulated entity, could be compelled to comply with a single court order. A judicial order targeting just 6-7 KYC entities would be sufficient to align one-third of voting power, enabling the same prevote-nil censorship mechanism described in CEL-D01 but executed as regulatory compliance rather than an attack.

The situation is compounded by validator set saturation: max_validators is set to 100 with 94 currently bonded, effectively blocking new entrants. Out of 301 total registered validators, only 94 are bonded, 192 are unbonding, and 15 are in other states. Delegator diversification does not help because redistributing stake among the same validators does not reduce the number of entities needed to reach the one-third threshold.

## Prerequisites

- Court order or OFAC sanctions designation targeting 6-7 KYC-regulated validator entities
- Validators comply out of legal obligation, not malice
- No technical exploit required

## Attack Scenario

1. A government agency identifies specific transactions or namespaces on Celestia for censorship (e.g., OFAC-sanctioned addresses).
2. The agency issues court orders or sanctions designations to 6-7 KYC-regulated validator operators across US, EU, Swiss, and Hong Kong jurisdictions.
3. The targeted validators, comprising more than one-third of voting power, are legally compelled to comply.
4. When blocks containing the targeted transactions are proposed, the compelled validators cast prevote-nil, preventing the block from reaching the two-thirds threshold.
5. The censorship continues indefinitely at zero technical cost, exactly as described in CEL-D01.
6. Because the validators are acting under legal obligation, there is no economic deterrent or community remedy.

## Impact

Legally enforced, indefinite transaction censorship with no technical cost and no available on-chain countermeasure. The attack leverages existing regulatory compliance obligations and cannot be addressed through slashing or social consensus mechanisms.

## Evidence

### On-Chain / Network

- Mainnet staking (2026-05-24): top 8 validators hold 35.77% (exceeding one-third), top 28 hold 67.02% (exceeding two-thirds)
- Anchorage Digital holds 11.08% of voting power
- 94 out of 100 maximum validator slots are filled (validator set saturation)
- Total registered validators: 301 (94 bonded, 192 unbonding, 15 other)
- Cross-verified across three endpoints: publicnode, polkachu, pops.one (data consistent as of 2026-05-24)
- Staking parameters: max_validators=100 confirmed on-chain

## Mitigations

Recommended fixes include creating incentive programs for non-KYC validator participation, increasing MaxValidators beyond 100 to reduce set saturation, actively working to resolve validator set saturation so new independent validators can join, and providing L2 and user-side censorship resistance SLA evaluation tools.
