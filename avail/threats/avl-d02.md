# AVL-D02: Low Validator Utilization Concentrates Consensus Power

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Scope**: chain · **Status**: Verified
{% endhint %}

## Overview

Avail's mainnet supports up to 1,200 validator slots, but only 105 are currently active, representing just 8.75% utilization. This means the network's consensus security depends on a relatively small validator set compared to its designed capacity. The total staked amount is approximately 4.794 billion AVAIL, which is about 48% of the 10 billion total supply.

The Nakamoto coefficient for this validator set is approximately 34, meaning an attacker would need to compromise or collude with at least 34 validators to control 33.33% of the total stake and disrupt consensus. For a full Byzantine fault tolerance attack, 70 validators colluding would be needed to control the two-thirds majority required to seize finality.

On the positive side, Avail uses Nominated Proof-of-Stake with Phragmen election, which achieves a very even stake distribution across validators. The top validator holds only 50.79 million AVAIL (1.06% of total stake), and the bottom validator holds 42.4 million (0.88%). The ratio between the highest and lowest stake is just 1.20x, and the top 10 validators combined hold only 10.54% of total stake. This even distribution makes it significantly harder for any small group of validators to accumulate disproportionate influence.

## Prerequisites

- Collusion or compromise of at least 34 validators to reach the 33.33% stake threshold
- Alternatively, compromise of 70 validators to control two-thirds of stake for finality attacks

## Attack Scenario

1. An attacker identifies and begins compromising validator keys or recruiting colluding validators. Due to the even Phragmen distribution, the attacker cannot focus on a few high-stake validators and must target many validators with similar stake levels.
2. Once the attacker controls 34 or more validators (representing 33.33% of stake), they can begin blocking finality by refusing to vote on blocks. This prevents the network from reaching the two-thirds consensus needed for finalization.
3. With 70 or more compromised validators (two-thirds of stake), the attacker could seize full control of finality, potentially censoring transactions, reorganizing blocks, or halting the chain entirely. However, the even stake distribution means this requires compromising a large number of independent operators.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Scope | chain |

### Scoring Rationale

There is no direct financial impact from validator collusion alone (B:N). The attack operates at the network level (AV:N). Complexity is high because it requires coordinated collusion of 34 or more validators (AC:H). No special privileges are needed since validator credentials can be obtained by anyone who stakes (PR:N). The impact stays within the chain's finality scope (S:U). Availability impact is high because finality disruption is possible if the threshold is reached (A:H). Infrastructure availability impact is medium because the Phragmen election's even distribution (1.2x variance) limits stake concentration and makes practical collusion very difficult (AI:M).

## Evidence

### On-Chain Verification

- `Session.Validators` storage query returns 105 active validators
- Subscan Era #688 stake distribution data was used to calculate the Nakamoto coefficient of approximately 34
- Top validator holds 1.06% of total stake, confirming no single validator has outsized influence

### Source Code

- Avail uses NPoS with Phragmen election algorithm, which produces stake distributions with a maximum variance of 1.2x between the highest and lowest validator stakes

### PoC Testing

Direct calculation from Subscan Era #688 data confirmed all distribution metrics: 105 active validators, Nakamoto coefficient of 34, top validator at 1.06%, and max/min ratio of 1.20x.

Reference: poc_onchain_verification.md section 10.5.

## Mitigations

Avail's NPoS Phragmen election algorithm enforces a very even stake distribution, with only 1.2x variance between the highest and lowest validator stakes. This makes stake concentration attacks impractical. The Nakamoto coefficient of 34 means an attacker would need to compromise roughly one-third of the entire active validator set, which represents a high practical barrier to collusion.
