# AVL-T03: Unlimited Token Minting via Malicious Bridge or VectorX Upgrade

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

The AVAIL token contract (0xeeb4d8400aeefafc1b2953e0094134a887c76bd8) holds approximately 791 million tokens in total supply. The contract itself is immutable: calling `owner()` reverts, and there is no admin function to change its behavior. Minting and burning authority resides solely in the Bridge proxy contract (0x054f...).

The risk arises from the upgrade paths of the contracts that hold minting power. If an attacker could push a malicious upgrade to either the Bridge contract or the VectorX contract, they could potentially mint an unlimited number of AVAIL tokens. The Bridge contract is protected by a 24-hour timelock through a TimelockController, meaning any upgrade must wait a full day before taking effect. VectorX, however, has no timelock protection and can be upgraded immediately with a 4-of-7 multisig approval.

This makes VectorX the weaker link in the upgrade chain. While the Bridge path gives users 24 hours to detect a malicious proposal and exit, the VectorX path offers no such window. A successful attack through either path would allow the attacker to inflate the token supply arbitrarily, destroying the token's economic value.

## Prerequisites

- Bridge upgrade path: compromise the TimelockController proposer role and 4 of 7 Governance Multisig keys, then wait 24 hours
- VectorX upgrade path: compromise 4 of 7 Governance Multisig keys for immediate upgrade

## Attack Scenario

1. The attacker compromises 4 of the 7 Governance Multisig signing keys through targeted phishing, key theft, or insider collusion. With these keys, the attacker can propose and execute contract upgrades.
2. Using the VectorX path to avoid the 24-hour timelock, the attacker immediately deploys a malicious upgrade that modifies the minting logic. Alternatively, via the Bridge path, the attacker proposes a malicious upgrade and waits 24 hours for the timelock to expire.
3. Once the malicious upgrade is active, the attacker calls the modified mint function to create an unlimited number of AVAIL tokens, flooding the market and destroying the token's value. Bridge users who rely on accurate token accounting face direct financial losses.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Scope | bridge |

### Scoring Rationale

There is no direct financial impact under normal conditions because the attack requires compromising a multisig first. The attack vector requires physical or social engineering access to key holders since 4 of 7 keys must be compromised. Attack complexity is high due to the 24-hour timelock on the Bridge path and the 4-of-7 multisig requirement on the VectorX path. The attacker needs multisig signer or timelock proposer credentials. The scope remains within the token minting function. Integrity impact is high because unlimited minting is possible upon successful exploitation, but the infrastructure integrity impact is medium because both the timelock and multisig protections significantly raise the bar for execution.

## Evidence

### On-Chain Verification

- `cast call 0xeeb4...c6bd8 "totalSupply()(uint256)"` returns approximately 791 million AVAIL tokens.
- `cast call 0xeeb4...c6bd8 "owner()(address)"` reverts, confirming the token contract is immutable with no admin.
- Mint and burn functions are restricted to the Bridge proxy contract only.

### PoC Testing

- Documented in poc_onchain_verification.md, section 6.

## Mitigations

The Bridge contract is protected by a 24-hour timelock, giving users and monitoring systems a full day to detect a malicious upgrade proposal and withdraw funds before it takes effect. VectorX lacks a timelock but still requires a 4-of-7 multisig approval, which provides meaningful protection against unilateral action. The token contract itself is immutable, so the minting logic cannot be changed directly.
