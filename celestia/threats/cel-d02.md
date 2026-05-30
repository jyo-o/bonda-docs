# CEL-D02: Low-cost Blockspace Monopoly via Large PFB Transactions

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

Celestia's block structure allows a single PayForBlobs (PFB) transaction to occupy up to 8 MiB (MaxTxSize), while the maximum block size is 32 MiB (BlockMaxBytes). This means only four maximum-size PFB transactions are needed to completely fill a block, crowding out all other transactions.

Transaction inclusion follows fee-per-gas priority, and shares within the data square are sorted by namespace. An attacker can repeatedly submit large PFB transactions at the minimum gas price to delay or prevent normal transactions from being included in blocks. While a MaxPFBMessages cap was introduced in v9, it does not resolve the fundamental blockspace monopoly problem.

The fee market provides a natural defense by raising costs as congestion increases, but the initial entry cost is low enough to sustain short-term congestion attacks cheaply. Rollup sequencers using Celestia as their DA layer are directly impacted because blob inclusion delays prevent them from obtaining DA commitments needed for settlement layer submission, causing temporary finality delays.

## Prerequisites

- No barrier beyond TIA gas costs
- Fee market competition increases the cost of sustained attacks over time

## Attack Scenario

1. The attacker crafts maximum-size PFB transactions (8 MiB each) with the minimum gas price.
2. Four such transactions fill an entire block, leaving no room for legitimate transactions.
3. The attacker repeats this across consecutive blocks.
4. Normal transaction inclusion is delayed or blocked until the fee market raises gas prices beyond what the attacker is willing to pay.
5. Rollup sequencers cannot obtain DA commitments, causing temporary finality delays on dependent L2 chains.

## Impact

Temporary blockspace denial for legitimate users and rollup finality delays. At mainnet prices (2026-05-26), a single 8 MiB PFB costs approximately 0.134 TIA (about $0.063), filling an entire block costs about $0.25, and sustaining the attack for one hour (600 blocks) costs roughly $151 before fee market response.

## Evidence

### Source Code

- `celestia-app/pkg/appconsts/app_consts.go` -- BlockMaxBytes=32 MiB, MaxTxSize=8 MiB, GasPerBlobByte=8
- `go-square/builder.go:261` -- blob sorting by namespace order with tx priority preserved
- `celestia-app/app/filtered_square_builder.go` -- Fill function uses fee/gas priority-based inclusion

### On-Chain / Network

- Mainnet minimum_gas_price=0.002 utia/gas confirmed via `celestia-rest.publicnode.com/cosmos/base/node/v1beta1/config`
- PR celestia-app#6604 introduced MaxPFBMessages cap

## Mitigations

The fee market naturally raises costs during sustained attacks, but initial entry cost remains low. Recommended fixes include re-weighting PFB ordering by fee-per-byte instead of flat priority, applying weighted gas costs for large PFBs, and introducing per-user PFB ratio caps.
