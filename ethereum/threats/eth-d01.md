# ETH-D01: Per-Account Blobpool Exhaustion via Minimum Fee

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D (Denial of Service) · **Status**: verified
{% endhint %}

## Summary

An attacker could attempt to exhaust the go-ethereum blobpool by submitting large numbers of blob transactions with the minimum possible fee. The go-ethereum implementation limits per-account blob transactions to 16 (`maxTxsPerAccount`), but a well-funded attacker with many accounts could attempt pool-wide exhaustion. This threat is effectively mitigated by EIP-7918's fee floor and the fee-based eviction mechanism.

## Description

The blobpool in go-ethereum includes a per-account cap that limits pool occupancy.

```go
// @audit — per-account cap limits single-identity monopolization
// go-ethereum/blobpool.go, line 86
// maxTxsPerAccount = 16
// Limits how many blob transactions a single account can hold
// in the pool simultaneously.
```

The per-account cap prevents a single attacker from monopolizing the pool with one identity. However, the primary defense comes from two additional mechanisms: EIP-7918 establishes a fee floor for blob transactions, ensuring that even minimum-fee spam has a non-trivial economic cost; and the fee-based eviction mechanism removes the lowest-fee transactions when pool capacity is reached, guaranteeing that legitimate higher-fee transactions can always enter.

## Proof of Concept

A proof-of-concept (`poc-eth-da-013-blobpool-dos.py`) was executed to confirm the attack vector and validate that existing mitigations are effective. The PoC confirmed that the per-account limit, EIP-7918 fee floor, and fee-based eviction together prevent meaningful pool exhaustion.

## Impact

The attack fails to meaningfully degrade blobpool availability because low-fee attacker transactions are evicted when legitimate higher-fee transactions arrive. The attacker's submitted fees are consumed even if the attack fails, making sustained attempts economically costly. Both node-level and chain-level availability impact is minimal due to the combined defensive mechanisms.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Blob transactions submitted over the network |
| AC | H (High) | Multiple mitigations (per-account limit, fee floor, eviction) must be overcome simultaneously |
| PR | N (None) | Any account with ETH can submit blob transactions |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Attack limited to the blobpool of targeted nodes |
| C | N (None) | No confidentiality impact |
| I | N (None) | No integrity impact; attack targets pool availability only |
| A | L (Low) | Per-account limit, fee floor, and eviction effectively neutralize the attack |

## Recommendation

1. **Maintain the `maxTxsPerAccount` limit**: Keep the per-account cap at 16 to prevent single-identity pool monopolization.
2. **Enforce EIP-7918 fee floor**: Continue enforcing the blob transaction fee floor to ensure minimum-fee spam carries a non-trivial economic cost.
3. **Preserve fee-based eviction**: The fee-based eviction mechanism that removes lowest-fee transactions at pool capacity is critical and must remain in place to guarantee legitimate transaction throughput.
