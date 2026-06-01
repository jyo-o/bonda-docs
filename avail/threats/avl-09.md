# AVL-09: Unlimited Token Minting via Malicious Bridge or VectorX Upgrade

{% hint style="info" %}
**Category**: Governance Observation · **Status**: verified
{% endhint %}

## Summary

The AVAIL token contract is immutable with no admin, but its minting authority resides in the Bridge proxy contract which can be upgraded. Two upgrade paths exist with different protection levels: the Bridge enforces a 24-hour timelock, while VectorX can be upgraded immediately. A malicious upgrade through either path could enable unlimited token minting.

## Description

The AVAIL token contract at 0xeeb4...c6bd8 is immutable since calling `owner()` reverts, confirming there is no admin function. Minting and burning authority resides solely in the Bridge proxy contract at 0x054f...

![Two upgrade paths to AVAIL token minting](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/avail/assets/avl-09-upgrade-paths.png)

The Bridge contract is protected by a TimelockController that enforces a 24-hour delay, giving users time to detect a malicious proposal and exit. VectorX has no timelock and can be upgraded immediately, making it the weaker link in the upgrade chain. A successful attack through either path would allow arbitrary inflation of the token supply.

## Proof of Concept

On-chain state was queried on Ethereum mainnet. See [Verification Evidence](../evidence.md#bridge-and-token-verification) for full commands and results.

- Token `owner()` reverts — confirms the AVAIL token contract is immutable with no admin
- `totalSupply()` returns ~791 million AVAIL; mint/burn authority is restricted to the Bridge proxy contract only

## Impact

A successful malicious upgrade through either the Bridge or VectorX path would allow the attacker to mint an unlimited number of AVAIL tokens, flooding the market and destroying the token's economic value. Bridge users who rely on accurate token accounting face direct financial losses. The VectorX path offers no detection window, while the Bridge path gives users 24 hours to react.

Affects the Decentralization baseline; an upgrade path permits unbounded token minting by the governing authority. This is recorded as a Governance Observation and carries no score.

## Recommendation

1. **Add a timelock to VectorX upgrades**: Implement a TimelockController for VectorX matching the 24-hour delay used by the Bridge contract, closing the instant-upgrade gap.
2. **Implement mint rate limiting**: Add on-chain constraints to the minting function that limit the maximum number of tokens that can be minted per time period, even by authorized contracts.
3. **Deploy upgrade monitoring**: Set up automated monitoring to detect and alert on any upgrade proposals to Bridge or VectorX contracts, providing early warning for the community.
