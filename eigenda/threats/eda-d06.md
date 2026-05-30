# EDA-D06: Relay Single Point of Failure on Mainnet

{% hint style="warning" %}
**Severity**: Medium (6.6/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Overview

The EigenDA mainnet currently operates with only a single Relay, creating a single point of failure for the primary blob read path. On-chain queries to the RelayRegistry contract (`0xD160e6...`) show that `nextRelayKey` equals 1, meaning only key 0 is registered. This relay is mapped to address `0xe8437B...` with URL `relay-0-mainnet-ethereum.eigenda.xyz`. Keys 1 through 5 all resolve to `0x0` (unregistered).

New relays can only be added by the contract owner via the `onlyOwner` modifier, and no deletion function exists in the contract. If this single relay goes down, the primary data retrieval path for all clients is immediately disrupted.

A fallback mechanism exists through validator direct retrieval via `GetChunks`, which automatically activates after relay failure. However, this fallback offers degraded performance compared to the relay path and is reactive rather than preventive.

## Prerequisites

- Relay failure due to outage, network disruption, or targeted attack.

## Attack Scenario

1. An attacker targets the single mainnet Relay at `relay-0-mainnet-ethereum.eigenda.xyz` with a denial-of-service attack or exploits a vulnerability in the Relay software.
2. The Relay becomes unavailable, disrupting the primary blob read path for all EigenDA clients.
3. Clients automatically fall back to the `GetChunks` validator direct retrieval path.
4. Performance degrades significantly as all read traffic shifts to the fallback path, which is not designed for primary use.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 6.6/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because there is no direct financial impact from a relay outage. Attack Vector (AV) is Network because the relay endpoint is publicly reachable. Attack Complexity (AC) is Low because only one relay exists on mainnet (confirmed on-chain with `nextRelayKey=1`), so any failure immediately impacts the read path. Availability impact (A) is High because this is a single point of failure for the primary read path. Availability Infrastructure impact (AI) is Medium because the `GetChunks` fallback exists, preventing a complete outage but resulting in degraded performance, and validators can retrieve data directly after relay failure through automatic switching.

## Evidence

### On-Chain Verification

- `nextRelayKey()` returns `1` at block 25101686, confirming only one relay is registered.
- `relayKeyToAddress(0)` returns `0xe8437B66E834B7CdC90cC5D98B8DD6e636b37D7a`.
- Keys 1 through 5 all return `0x0` (unregistered).
- Contracts queried: RelayRegistry at `0xD160e6C1`.

### Source Code

- [`contracts/src/core/EigenDARelayRegistry.sol:20-23`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/core/EigenDARelayRegistry.sol#L20-L23) -- Registry contract with `onlyOwner` addition and no deletion function.

### PoC Testing

- `poc/01-*/evidence.yaml` and `poc/02-*/evidence.yaml` confirmed the single-relay configuration.

**PoC References**: #01

## Mitigations

A validator fallback via `GetChunks` exists but only activates after relay failure. Adding additional relays to the RelayRegistry would eliminate the single point of failure. The contract owner can register new relays through the `onlyOwner`-gated function.
