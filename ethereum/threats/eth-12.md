# ETH-12: EIP-7918 Sets a Blob Base Fee Reserve Relative to Execution Cost

{% hint style="success" %}
**Category**: Design Note · **Status**: verified
{% endhint %}

## Summary

EIP-7918 introduces a reserve price that couples the blob base fee to execution gas cost. When the cost of an equivalent amount of execution gas exceeds the blob fee for the same data, the excess blob gas is updated without subtracting the target, which keeps the blob base fee from staying arbitrarily low relative to execution. This repricing shapes the long-run cost dynamics of posting data to Ethereum and sets the Cost Efficiency design baseline for the Ethereum data availability path.

## Description

![ETH-12 data flow — Ethereum PeerDAS Write path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/ethereum/assets/dfd/ethereum-write.png)

*Data flow — Ethereum PeerDAS Write: Blobpool.*

The reserve rule changes how `excess_blob_gas` evolves when blob demand is low.

- EIP-7918 adds a floor so that the blob base fee cannot remain negligible while execution gas is expensive. When `BLOB_BASE_COST * base_fee_per_gas > GAS_PER_BLOB * get_base_fee_per_blob_gas(parent)`, the excess blob gas for the child is computed without subtracting the target blob gas. Source: [EIP-7918](https://eips.ethereum.org/EIPS/eip-7918).
- `BLOB_BASE_COST` is `2**13`.

Before this change, sustained low blob demand could drive the blob base fee toward its minimum and hold it there regardless of how expensive execution became. The reserve links the two markets so that the blob fee retains a floor proportional to execution cost, smoothing the fee path that data availability users pay during periods of low blob demand.

## Proof of Concept

No exploit reproduction was conducted. This is a design note recording the reserve-price rule and the `BLOB_BASE_COST` constant as specified in EIP-7918.

## Impact

The reserve rule sets the cost floor that data availability users face when blob demand is low, so cost-efficiency assessments must account for the coupling between blob fees and execution gas rather than assuming the blob fee can fall to its minimum. This is a deliberate fee-market design property that defines the baseline cost behavior of the Ethereum data availability path.

Sets the Cost Efficiency Design Baseline through the fee-floor sub-property. As an acknowledged fee-market design choice, it carries no score.

## Recommendation

1. Model data availability cost on Ethereum with the EIP-7918 reserve in place rather than assuming an unbounded floor on the blob base fee.
2. Re-evaluate the cost baseline if future fee-market changes alter the coupling between blob and execution fees.
