# CEL-D02: Low-cost Blockspace Monopoly via Large PFB Transactions

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

Celestia's block structure allows a single PayForBlobs (PFB) transaction to occupy up to 8 MiB (`MaxTxSize`), while the maximum block size is 32 MiB (`BlockMaxBytes`). Only four maximum-size PFB transactions are needed to completely fill a block, enabling low-cost blockspace monopoly that delays legitimate transaction inclusion and rollup finality. The fee market provides a natural defense over time, but the initial entry cost is low enough for short-term congestion attacks.

## Description

The blockspace monopoly is enabled by the ratio between maximum transaction size and block size:

```go
// celestia-app/pkg/appconsts/app_consts.go
// @audit BlockMaxBytes=32 MiB, MaxTxSize=8 MiB, GasPerBlobByte=8
// @audit Only 4 max-size PFBs needed to fill an entire block
```

Transaction inclusion follows fee-per-gas priority, and shares within the data square are sorted by namespace:

```go
// go-square/builder.go:261
// @audit Blob sorting by namespace order with tx priority preserved
```

```go
// celestia-app/app/filtered_square_builder.go
// @audit Fill function uses fee/gas priority-based inclusion
```

While a `MaxPFBMessages` cap was introduced in v9 (PR `celestia-app#6604`), it does not resolve the fundamental blockspace monopoly problem because a single PFB with maximum-size data is sufficient to consume a large portion of block capacity.

At mainnet prices (2026-05-26), with `minimum_gas_price=0.002 utia/gas` (confirmed via `celestia-rest.publicnode.com/cosmos/base/node/v1beta1/config`):
- A single 8 MiB PFB costs approximately 0.134 TIA (about $0.063)
- Filling an entire block costs about $0.25
- Sustaining the attack for one hour (600 blocks) costs roughly $151 before fee market response

## Proof of Concept

No proof of concept was conducted for this threat. Cost calculations are derived from on-chain gas parameters and current TIA market prices.

## Impact

Temporary blockspace denial for legitimate users and rollup finality delays. Rollup sequencers using Celestia as their DA layer are directly impacted because blob inclusion delays prevent them from obtaining DA commitments needed for settlement layer submission. The fee market naturally raises costs during sustained attacks, but the initial entry cost of approximately $0.25 per block makes short-term attacks very cheap.

### CVSS 3.1

**Score**: 5.9/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via standard transaction submission over the network |
| AC (Attack Complexity) | H (High) | Sustained attacks face exponential fee market response; short-term attacks are cheap but self-limiting |
| PR (Privileges Required) | N (None) | No privileges required beyond TIA for gas fees |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to Celestia blockspace and its direct consumers |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact; transactions are delayed, not corrupted |
| A (Availability) | H (High) | Complete blockspace denial is achievable during the attack window |

## Recommendation

1. Re-weight PFB ordering by fee-per-byte instead of flat priority to make large PFBs proportionally more expensive.
2. Apply weighted gas costs for large PFBs that scale super-linearly with blob size to disincentivize blockspace monopoly.
3. Introduce per-user PFB ratio caps to prevent a single address from dominating blockspace across consecutive blocks.
