# AVL-T03: Unlimited Token Minting via Malicious Bridge or VectorX Upgrade

{% hint style="info" %}
**Severity**: Medium (4.0/10) · **STRIDE**: T · **Status**: Verified
{% endhint %}

## Summary

The AVAIL token contract (0xeeb4d8400aeefafc1b2953e0094134a887c76bd8) holds ~791 million tokens and is itself immutable with no admin. However, minting authority resides in the Bridge proxy contract, which can be upgraded. Two upgrade paths exist: the Bridge contract is protected by a 24-hour timelock, but VectorX can be upgraded immediately with a 4-of-7 multisig approval. A malicious upgrade through either path could enable unlimited token minting.

## Description

The AVAIL token contract is immutable -- `owner()` reverts, and there is no admin function. Minting and burning authority resides solely in the Bridge proxy contract (0x054f...).

```
// @audit — Token minting risk via upgrade paths:
//          Token contract: immutable, owner() reverts, no admin
//          Mint/burn authority: Bridge proxy (0x054f...) only
//          Bridge upgrade path: 24-hour TimelockController delay + 4/7 multisig
//          VectorX upgrade path: immediate upgrade with 4/7 multisig (no timelock)
//          VectorX is the weaker link — no detection window for community.
```

The Bridge contract is protected by a TimelockController that enforces a 24-hour delay, giving users time to detect a malicious proposal and exit. VectorX has no timelock and can be upgraded immediately, making it the weaker link in the upgrade chain. A successful attack through either path would allow arbitrary inflation of the token supply.

## Proof of Concept

On-chain verification confirmed the token contract's immutability and minting authority:

- `cast call 0xeeb4...c6bd8 "totalSupply()(uint256)"` returns approximately 791 million AVAIL tokens
- `cast call 0xeeb4...c6bd8 "owner()(address)"` reverts, confirming the token contract has no admin
- Mint and burn functions are restricted to the Bridge proxy contract only

Reference: poc_onchain_verification.md, section 6.

## Impact

A successful malicious upgrade through either the Bridge or VectorX path would allow the attacker to mint an unlimited number of AVAIL tokens, flooding the market and destroying the token's economic value. Bridge users who rely on accurate token accounting face direct financial losses. The VectorX path offers no detection window, while the Bridge path gives users 24 hours to react.

### CVSS 3.1
**Score**: 4.0/10 (Medium)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Requires physical or social engineering access to key holders; 4 of 7 keys must be compromised |
| AC | H (High) | 24-hour timelock on Bridge path and 4-of-7 multisig requirement on VectorX path raise complexity |
| PR | L (Low) | Attacker needs multisig signer or timelock proposer credentials |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact within the token minting function scope |
| C | N (None) | No confidentiality impact |
| I | H (High) | Unlimited minting is possible upon successful exploitation through either upgrade path |
| A | N (None) | No direct availability impact from token minting |

## Recommendation

1. **Add a timelock to VectorX upgrades**: Implement a TimelockController for VectorX matching the 24-hour delay used by the Bridge contract, closing the instant-upgrade gap.
2. **Implement mint rate limiting**: Add on-chain constraints to the minting function that limit the maximum number of tokens that can be minted per time period, even by authorized contracts.
3. **Deploy upgrade monitoring**: Set up automated monitoring to detect and alert on any upgrade proposals to Bridge or VectorX contracts, providing early warning for the community.
