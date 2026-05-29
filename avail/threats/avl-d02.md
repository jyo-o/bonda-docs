# AVL-D02: Validator Set 105/1200 -- Nakamoto Coefficient ~34, 8.75% Utilization

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Scope**: chain · **Status**: Verified
{% endhint %}

## Overview

105 active validators out of max 1200 (8.75% utilization). Nakamoto coefficient ~34 (validators needed to control 33.33% stake). Total staked ~4.794B AVAIL (48% of 10B supply). Top validator: 50.79M AVAIL (1.06%), Bottom: 42.4M (0.88%). Max/min ratio: 1.20x -- NPoS Phragmen achieves very even distribution. Top 10 = 10.54% combined. BFT threshold 2/3 = 70 validators colluding could seize finality.

## Prerequisites

Collusion or compromise of 34+ validators (33.33% stake)

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Likelihood | Unrated |
| Scope | chain |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:N -- Network. AC:H -- 34+ validator collusion required. PR:N -- Validator credentials obtainable. S:U -- Within chain finality scope. A:H -- Finality disruption possible. AI:M -- Phragmen even distribution (1.2x) limits stake concentration; practical collusion difficulty is high.

## Code References


### Onchain Evidence

- `Session.Validators=105`
- `Subscan: Era#688 Nakamoto≈34`
- `Subscan: top validator 1.06%`

### PoC Notes

- poc_onchain_verification.md §10.5

### Other References

- Phragmén 1.2x

## Verification & Evidence

**Status**: Verified

Session.Validators storage=105. Subscan Era #688 stake distribution directly calculated. Nakamoto~34, top 1.06%, max/min 1.20x.

**PoC References**: onchain-§10.5

## Mitigations

NPoS Phragmen even distribution (1.2x variance). Nakamoto 34 = 1/3 of set.
