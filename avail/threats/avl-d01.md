# AVL-D01: Single Relayer Creates Bridge-Wide Single Point of Failure

{% hint style="info" %}
**Severity**: Medium (6.6/10) · **STRIDE**: D · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX relies on a single relayer EOA (0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D) to submit Avail block header commitments to Ethereum. This relayer is the only address authorized to call `commitHeaderRange()`, which posts ZK-verified block headers that the bridge depends on. If this relayer goes offline for any reason, the entire bridge halts with no fallback.

The contract enforces relayer access control through an `approvedRelayers` mapping with `checkRelayer` enabled, but provides no on-chain mechanisms to detect or respond to relayer failure. The `commitHeaderRange()` function contains zero references to `block.timestamp` and has no cooldown, rate limit, heartbeat, or timeout logic anywhere in the inheritance chain. The relayer's client-side software uses a 60-minute loop interval (LOOP_INTERVAL_MINS=60), but this is purely off-chain and cannot be enforced or monitored by the contract. Additionally, `setRelayerApproval()` emits no events, making relayer changes invisible to off-chain monitoring tools.

The relayer currently operates with nonce 2632 and a balance of 0.82 ETH. It relays approximately every 120 minutes in batches of 358 blocks, consuming about 458,612 gas per commitment. A previous relayer (0x3243...2D) was rotated out, confirming that relayer changes have occurred, but there is no on-chain mechanism to propose or approve a replacement in an emergency.

## Prerequisites

- Relayer EOA goes offline, runs out of gas, or has its key compromised
- No attacker action is required; natural failure alone triggers a full bridge halt
- No on-chain staleness detection mechanism exists to alert anyone

## Attack Scenario

1. The single relayer EOA stops submitting commitments, either due to infrastructure failure, key compromise, gas exhaustion, or a targeted DDoS attack against the relayer operator.
2. Because VectorX has no on-chain heartbeat, timeout, or staleness detection, the contract cannot detect that the relayer has stopped. No events are emitted, and no automatic fallback activates. The bridge silently goes stale.
3. All `commitHeaderRange()` calls fail because no other address is in the `approvedRelayers` mapping. Avail block headers stop being verified on Ethereum, halting the bridge entirely. Avail chain data remains available on its own network but becomes unverifiable on Ethereum until the relayer is manually restored.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 6.6/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Scope | bridge |

### Scoring Rationale

There is no direct financial impact from a relayer outage (B:N). The attack surface is at the network level, including DDoS or key compromise (AV:N). Complexity is low because this is a single point of failure where even natural failure triggers the issue, and code review confirmed zero on-chain rate limiting or heartbeat mechanisms (AC:L). No special privileges are needed for an external attacker to cause the failure (PR:N). The impact stays within the bridge scope (S:U). Availability impact is high because the DA attestation bridge completely halts when `commitHeaderRange()` calls become impossible (A:H). Infrastructure availability impact is medium because Avail chain data itself remains accessible on its own network, but it becomes unverifiable on Ethereum (AI:M).

## Evidence

### On-Chain Verification

The following on-chain queries confirmed the single relayer configuration:

- `eth_getCode(0x27BF...)` returns `0x` -- confirms EOA, not a contract
- `nonce` = 2632, `balance` = 0.82 ETH -- active account
- `approvedRelayers(0x27BF...)` returns `true` -- sole approved relayer
- `checkRelayer` returns `true` -- relayer access control is enforced
- `latestBlock` = 2975481, `headerRangeCommitmentTreeSize` = 2048

### Source Code

- [SP1Vector.sol](https://github.com/availproject/sp1-vector) `commitHeaderRange()` -- contains zero `block.timestamp` references; no cooldown, rate limit, heartbeat, or timeout logic exists in the full inheritance chain
- [operator.rs](https://github.com/availproject/sp1-vector) -- uses `LOOP_INTERVAL_MINS=60` and `BLOCK_UPDATE_INTERVAL=360` for client-side interval control only; no on-chain enforcement
- `setRelayerApproval()` emits no events, unlike `removeHeaderHash` which emits `HeaderHashRemoved`
- Source code review confirms no on-chain mechanism exists to propose or approve new relayers

### PoC Testing

Anvil mainnet fork PoC executed three tests: (1) confirmed single relayer access control, (2) confirmed absence of staleness detection, (3) confirmed guardian ZK bypass as the intended fallback mechanism. Previous relayer (0x3243...2D) rotation history was also confirmed.

References: poc_onchain_verification.md sections 2 and 14; avl_d01_relayer_spof_poc.sh (Anvil fork, 3 tests).

## Mitigations

No mitigations exist. There is no on-chain relayer replacement mechanism, no heartbeat or timeout enforcement, and no staleness detection. Observability is also limited because `setRelayerApproval()` emits no events, making relayer changes invisible to off-chain monitoring systems.
