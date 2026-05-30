# AVL-E04: Technical Committee Can Upgrade Runtime with Supermajority Consensus

{% hint style="info" %}
**Severity**: Medium (6.7/10) · **STRIDE**: E · **Status**: Verified
{% endhint %}

## Summary

Avail's Technical Committee (7 members) can execute a runtime upgrade with 5/7 supermajority or 5/5 unanimous consent. A runtime upgrade can change any on-chain logic including consensus rules, staking parameters, and finality conditions. This mechanism has been used in production (block #1,095,300). While the high threshold provides meaningful protection, a compromised committee could alter arbitrary chain logic without a timelock or community veto period.

## Description

The Technical Committee governance mechanism allows runtime upgrades that control all on-chain logic. The upgrade threshold requires either unanimous consent of present members (5/5) or a supermajority of all members (5/7).

```
// @audit — Technical Committee runtime upgrade path:
//          5/7 supermajority threshold with no timelock delay.
//          Block #1,095,300: 5/5 consensus TC upgrade applied to fix
//          send_message logic (documented in Transparency Report 16).
//          No community veto period exists before upgrades take effect.
```

Avail publishes Transparency Reports on the Avail Forum documenting TC runtime upgrades, providing after-the-fact accountability. However, these reports do not prevent a malicious upgrade from executing.

## Proof of Concept

On-chain verification confirmed a TC runtime upgrade at block #1,095,300, executed with 5/5 unanimous consensus to fix a bug in the `send_message` logic. This event is documented in Avail's Transparency Report 16, published on the Avail Forum, confirming this governance mechanism is actively used in production.

## Impact

A compromised Technical Committee could alter consensus rules, modify staking parameters, change finality conditions, or introduce arbitrary logic changes that affect the entire chain and all dependent systems. The publication of Transparency Reports provides some after-the-fact accountability but does not prevent a malicious upgrade from executing. There is no timelock or community veto period before upgrades take effect.

### CVSS 3.1
**Score**: 6.7/10 (Medium)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Compromising 5 of 7 TC member keys requires physical or social engineering access |
| AC | H (High) | 5-of-7 consensus is a strict threshold requiring multiple independent compromises |
| PR | L (Low) | Attacker needs TC member credentials specifically |
| UI | N (None) | No user interaction required |
| S | C (Changed) | Runtime upgrades affect chain-wide consensus rules and all dependent systems |
| C | N (None) | No confidentiality impact |
| I | H (High) | Arbitrary staking and finality rule changes are possible, detectable via Transparency Reports |
| A | H (High) | Chain halt is possible, though the strict TC consensus requirement provides meaningful protection |

## Recommendation

1. **Introduce a timelock delay for TC runtime upgrades**: Implement a mandatory waiting period between proposal and execution to give the community a detection window, similar to the 24-hour timelock on bridge upgrades.
2. **Implement a community veto mechanism**: Allow token holders or the broader community to reject a proposed runtime upgrade during the timelock period.
3. **Continue and expand Transparency Report publication**: Maintain Transparency Reports for all TC actions and consider publishing upgrade proposals before execution rather than after.
