# EDA-D06: Relay Single Point of Failure (1 Relay on Mainnet)

{% hint style="info" %}
**Severity**: Medium (6.6/10) · **STRIDE**: D · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

RelayRegistry (0xD160e6...) onchain query shows nextRelayKey=1. Only key 0 is registered: address=0xe8437B..., url=relay-0-mainnet-ethereum.eigenda.xyz. Keys 1-5 are all 0x0 (unregistered). Only onlyOwner can add relays; no deletion function exists.

## Prerequisites

Relay failure

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 6.6/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:N -- Public endpoint. AC:L -- Only 1 mainnet relay (nextRelayKey=1 confirmed onchain); any failure immediately impacts read path. A:H -- Primary read path SPOF. AI:M -- GetChunks fallback exists so not complete outage but degraded performance; validator direct retrieval possible (auto-switches after relay failure).

## Code References

### Source Code

- [`contracts/src/core/EigenDARelayRegistry.sol:20-23`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/core/EigenDARelayRegistry.sol#L20-L23)

### Onchain Evidence

- `nextRelayKey()=1`
- `relayKeyToAddress(0)=0xe8437B66`
- `block 25097183`
- `0xD160e6C1`
- `0xe8437B66E834B7CdC90cC5D98B8DD6e636b37D7a`

### PoC Notes

- block=25101686
- poc/01-*/evidence.yaml
- poc/02-*/evidence.yaml [VERIFIED]

### Other References

- nextRelayKey()=1
- relayKeyToAddress(0)=0xe8437B66

## Verification & Evidence

**Status**: Verified

Mainnet has 1 relay (nextRelayKey=1).

**PoC References**: #01

## Mitigations

Validator fallback (GetChunks) exists but only activates after relay failure.
