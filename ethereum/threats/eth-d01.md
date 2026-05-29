# ETH-D01: Per-Account Blobpool Exhaustion (1-Wei Fee)

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: verified
{% endhint %}

## Overview

In go-ethereum blobpool.go L86, maxTxsPerAccount=16 limits per-account submissions. Analysis of blobpool exhaustion attacks using minimum 1-Wei fee. Already mitigated by EIP-7918 fee floor and fee-based eviction.

## Prerequisites

Valid Ethereum account with minimum gas fee

## Attack Scenario

**Condition**: Mass submission of low-cost blob txs to blobpool

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:N/II:N/A:L/AI:L` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

- [`go-ethereum/blobpool.go:86 (maxTxsPerAccount=16)`](https://github.com/ethereum/go-ethereum/blob/master/blobpool.go#L86)

## Verification & Evidence

**Status**: verified

Confirmed blobpool.go maxTxsPerAccount=16. Mitigated by EIP-7918 fee floor + fee-based eviction. PoC execution confirmed.

## Mitigations

maxTxsPerAccount=16 limit, EIP-7918 fee floor, and fee-based eviction.
