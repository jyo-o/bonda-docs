# ETH-D01: Per-Account Blobpool Exhaustion via Minimum Fee

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: D (Denial of Service) · **Status**: verified
{% endhint %}

## Overview

The go-ethereum execution client maintains a dedicated transaction pool for blob-carrying transactions called the blobpool. An attacker could attempt to exhaust blobpool capacity by submitting large numbers of blob transactions with the minimum possible fee, aiming to fill the pool with low-priority transactions and displace legitimate ones.

The go-ethereum implementation at `blobpool.go` line 86 sets `maxTxsPerAccount` to 16, which limits how many blob transactions a single account can hold in the pool simultaneously. This per-account cap prevents a single attacker from monopolizing the pool with one identity, but a well-funded attacker with many accounts could still attempt pool-wide exhaustion.

This threat has been effectively mitigated by EIP-7918, which establishes a fee floor for blob transactions, and by the fee-based eviction mechanism that removes the lowest-fee transactions when the pool reaches capacity. Together, these measures ensure that spam transactions are economically costly to maintain and are the first to be evicted when pool pressure increases.

## Prerequisites

- One or more valid Ethereum accounts
- Enough ETH to cover minimum gas fees for blob transactions
- Willingness to spend ETH on transaction fees that will be consumed even if the attack fails

## Attack Scenario

1. The attacker creates multiple Ethereum accounts and funds them with minimal ETH.
2. The attacker submits blob transactions from each account with the lowest possible fee, filling up to 16 slots per account.
3. As the blobpool fills with low-fee transactions, legitimate blob transactions with higher fees arrive.
4. The fee-based eviction mechanism removes the attacker's low-fee transactions to make room for higher-fee ones.
5. The attacker's transactions are evicted, and the fees spent on submission are lost. The attack fails to meaningfully degrade blobpool availability.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:N/II:N/A:L/AI:L` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based but complexity is high because multiple mitigations must be overcome simultaneously. No privileges or user interaction are required. Confidentiality and integrity are unaffected since the attack only targets pool availability. Availability impact is low at both node and chain levels because the per-account limit, fee floor, and eviction mechanism effectively neutralize the attack. The scope remains unchanged.

## Evidence

### Source Code

- **Repository**: go-ethereum (Geth execution client)
- **File**: [`blobpool.go`, line 86](https://github.com/ethereum/go-ethereum/blob/master/blobpool.go#L86)
- **Finding**: `maxTxsPerAccount` is set to 16, limiting per-account blob transaction pool occupancy.

### Verification

A proof-of-concept (`poc-eth-da-013-blobpool-dos.py`) was executed to confirm the attack vector and validate that existing mitigations are effective. The PoC confirmed that the per-account limit, EIP-7918 fee floor, and fee-based eviction together prevent meaningful pool exhaustion.

## Mitigations

Three complementary mechanisms effectively mitigate this threat. First, the `maxTxsPerAccount` limit of 16 prevents any single account from monopolizing the pool. Second, EIP-7918 establishes a fee floor for blob transactions, ensuring that even minimum-fee spam has a non-trivial economic cost. Third, the fee-based eviction mechanism automatically removes the lowest-fee transactions when pool capacity is reached, guaranteeing that legitimate higher-fee transactions can always enter the pool. Together, these make sustained blobpool exhaustion economically infeasible.
