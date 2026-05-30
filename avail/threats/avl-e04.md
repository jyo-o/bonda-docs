# AVL-E04: Technical Committee Can Upgrade Runtime with Supermajority Consensus

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: E · **Scope**: chain · **Status**: Verified
{% endhint %}

## Overview

Avail's Technical Committee has the authority to upgrade the mainnet runtime, which controls all on-chain logic including consensus rules, staking parameters, transaction processing, and governance mechanisms. A runtime upgrade can change any aspect of how the chain operates, making it one of the most powerful governance actions available.

The Technical Committee consists of 7 members and can execute a runtime upgrade with either unanimous consent (5/5 of present members) or a supermajority (5/7 of all members). This mechanism has already been used in production: at block #1,095,300, a 5/5 consensus TC runtime upgrade was applied to fix a bug in the `send_message` logic. This event is documented in Avail's Transparency Report 16, published on the Avail Forum.

While the high threshold provides meaningful protection, a compromised Technical Committee could alter consensus rules, modify staking parameters, change finality conditions, or introduce arbitrary logic changes that affect the entire chain. The publication of Transparency Reports provides some after-the-fact accountability, but does not prevent a malicious upgrade from executing.

## Prerequisites

- Compromise 5 of the 7 Technical Committee member keys
- This requires physical access or social engineering against multiple independent committee members
- Alternatively, collude with 5 committee members directly

## Attack Scenario

1. An attacker compromises 5 of the 7 Technical Committee member keys through targeted phishing, social engineering, physical device access, or direct collusion with committee members.
2. The attacker submits a malicious runtime upgrade proposal through the Technical Committee governance mechanism. With 5 of 7 keys controlled, the proposal meets the supermajority threshold and is approved.
3. The malicious runtime is applied to the chain, giving the attacker the ability to change consensus rules, redirect staking rewards, censor transactions, alter finality conditions, or introduce backdoors into any on-chain logic. While Transparency Reports would eventually document the upgrade, the damage occurs before public disclosure.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.7/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:C/C:N/I:H/A:H/CI:N/II:M/AI:M` |
| Scope | chain |

### Scoring Rationale

There is no direct financial impact from the governance mechanism itself (B:N). Compromising 5 of 7 TC member keys requires physical or social engineering access (AV:P). Complexity is high because 5-of-7 consensus is a strict threshold (AC:H). The attacker needs TC member credentials specifically (PR:R). The scope is changed because runtime upgrades affect chain-wide consensus rules and all dependent systems (S:C). Integrity impact is high because arbitrary staking and finality rule changes are possible, though they are detectable via the Transparency Reports that Avail publishes (I:H, II:M). Availability impact is high because a chain halt is possible, but the strict TC consensus requirement provides meaningful protection (A:H, AI:M).

## Evidence

### On-Chain Verification

- Block #1,095,300 contains a verified TC runtime upgrade executed with 5/5 unanimous consensus, confirming this governance mechanism is actively used in production

### Source Code

- Avail Forum Transparency Report 16 documents the runtime upgrade at block #1,095,300, including the 5/5 consensus vote and the fix applied to `send_message` logic

## Mitigations

The 5-of-5 or 5-of-7 consensus requirement provides strong protection, requiring compromise of a supermajority of independent committee members. Avail publishes Transparency Reports on the Avail Forum documenting all TC runtime upgrades, providing after-the-fact accountability and public visibility into governance actions. However, these reports do not prevent a malicious upgrade from executing, and there is no timelock or community veto period before upgrades take effect.
