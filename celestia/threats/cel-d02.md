# CEL-D02: Large PFB Blockspace Monopoly — Low-cost Sustained Congestion Attack

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

Due to Celestia's block structure, a single PFB transaction can occupy up to 8 MiB (MaxTxSize), and only 4 maximum-size PFBs are needed to fill an entire block (BlockMaxBytes=32 MiB). Transaction inclusion order follows fee/gas-based priority, while shares within the square are sorted by namespace (go-square builder.go). An attacker can submit large PFBs repeatedly at minimum gas cost to delay or block normal transactions from being included. While a MaxPFBMessages cap was introduced in v9, it does not resolve the blockspace monopoly issue itself. The fee market increases costs as the attack persists, but initial entry cost is low enough for short-term congestion.

## Core Invariants Affected

Blob inclusion delay means DA commitment cannot be obtained, preventing settlement layer submission and delaying rollup finality. Rollup sequencers using Celestia as DA must submit DA commitments from Celestia blocks to the settlement layer (e.g., Ethereum) for state updates to be finalized. Blockspace monopoly-induced inclusion delays temporarily sever this chain. Since the fee market responds and retries resolve it, this constitutes temporary finality delay rather than complete service disruption.

## Prerequisites

No barrier to entry beyond TIA gas costs. However, the fee market competition increases sustained attack costs.

## Attack Scenario

**Condition**: Attacker can repeatedly submit 8 MiB PFBs by paying only gas costs

**Example**: Mainnet (2026-05-26): GasPerBlobByte=8, minimum_gas_price=0.002 utia/gas, TIA=$0.468. One 8 MiB PFB costs ~0.134 TIA (~$0.063), filling entire block (x4) ~$0.25/block, 1 hour sustained (600 blocks) ~$151. Pre-fee-market short-term congestion cost is very low.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Medium |
| Likelihood | Conditional (initial cost low, sustained cost rises due to fee market response) |
| Scope | protocol |
| Target | Process |

## Code References

- [`celestia-app/pkg/appconsts/app_consts.go (BlockMaxBytes=32 MiB, MaxTxSize=8 MiB, GasPerBlobByte=8)`](https://github.com/celestiaorg/celestia-app/blob/main/pkg/appconsts/app_consts.go)
- [`go-square/builder.go:261 (blob 정렬: namespace 순, tx priority 보존)`](https://github.com/celestiaorg/go-square/blob/main/builder.go#L261)
- [`celestia-app/app/filtered_square_builder.go (Fill: fee/gas 우선순위 기반 포함)`](https://github.com/celestiaorg/celestia-app/blob/main/app/filtered_square_builder.go)
- On-chain: `celestia-rest.publicnode.com/cosmos/base/node/v1beta1/config (minimum_gas_price=0.002utia)`
- [PR #6604: MaxPFBMessages cap 도입](https://github.com/celestiaorg/celestia-app/pull/6604)

## Verification & Evidence

**Status**: code_verified

app_consts.go parameters confirmed. Sort criteria in go-square builder.go directly verified as namespace-ordered -- D02 original claim of byte-budget priority ordering inconsistent with code. Actual mechanism is low-cost blockspace monopoly by large PFBs under fee/gas priority. minimum_gas_price on-chain confirmed. Cost calculations verified.

## Mitigations

Recommendations: (1) Re-weight PFB ordering by fee-per-byte instead of byte-budget, (2) Weighted cost for large PFBs, (3) Per-user PFB ratio cap.
