# AVL-04: Single Relayer Creates Bridge-Wide Single Point of Failure

{% hint style="warning" %}
**Severity**: High · **Category**: Operational Risk · **Status**: verified
{% endhint %}

## Summary

The VectorX bridge contract submits Avail block header commitments to Ethereum through a single relayer. If this relayer goes offline for any reason, the entire bridge halts because no fallback address is authorized and the contract has no mechanism to detect or recover from relayer failure.

## Description

![AVL-04 data flow — Avail Write path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/avail/assets/dfd/avail-write.png)

*Data flow — Avail Write: VectorX Relayer.*

The VectorX contract enforces relayer access control through an `approvedRelayers` mapping with `checkRelayer` enabled. Only the single approved relayer at 0x27BF...787D can call `commitHeaderRange()`, which posts ZK-verified block headers that the bridge depends on.

```solidity
// SP1Vector.sol (VectorX — 0x02993cdC...bf298d)
// @audit commitHeaderRange() is restricted to a single approved relayer.
//        No on-chain heartbeat, timeout, or staleness detection exists
//        anywhere in the inheritance chain. Zero references to block.timestamp.
//        setRelayerApproval() emits no events, unlike removeHeaderHash
//        which emits HeaderHashRemoved — relayer changes are invisible.
mapping(address => bool) public approvedRelayers;
bool public checkRelayer;

function commitHeaderRange(bytes calldata proof, bytes calldata publicValues) external;
function setRelayerApproval(address _relayer, bool _approved) external;
```

The relayer's client-side software operator.rs uses a 60-minute loop interval and processes 360 blocks per update, but these timing parameters are purely off-chain and cannot be enforced or monitored by the contract. The `commitHeaderRange()` function contains zero references to `block.timestamp` and has no cooldown or rate limit logic.

A previous relayer at 0x3243...2D was rotated out, confirming that relayer changes have occurred, but there is no on-chain mechanism to propose or approve a replacement in an emergency.

## Proof of Concept

Anvil mainnet fork PoC and on-chain state verification were conducted. See [Verification Evidence](../evidence.md#vectorx-single-relayer-verification-avl-04) for full commands and results.

- Anvil fork confirmed single relayer access control, absence of staleness detection, and guardian ZK bypass as the intended fallback
- `approvedRelayers(0x27BF...)` returns `true` with `checkRelayer` enabled — sole approved relayer is an EOA (nonce 2632, balance 0.82 ETH)
- Relayer operates approximately every 120 minutes in batches of ~358 blocks at ~458,612 gas per commitment

## Impact

If the single relayer goes offline due to infrastructure failure, key compromise, gas exhaustion, or a targeted DDoS attack, the entire bridge silently goes stale. All `commitHeaderRange()` calls fail because no other address is in the `approvedRelayers` mapping. Avail block headers stop being verified on Ethereum, halting the bridge entirely. Avail chain data remains available on its own network but becomes unverifiable on Ethereum until the relayer is manually restored. No attacker action is required; natural failure alone triggers a full bridge halt.

Affects the Liveness and Verifiability axes. It is tracked as an Operational Indicator shown alongside the risk pentagon, not as a deduction from the structural score.

## Recommendation

1. **Add on-chain staleness detection**: Implement a heartbeat or timeout mechanism in VectorX that tracks the last commitment timestamp and allows anyone to detect when the relayer has been inactive beyond a threshold.
2. **Implement a multi-relayer fallback**: Approve additional relayer addresses in the `approvedRelayers` mapping so that if the primary relayer fails, a backup can continue submitting commitments.
3. **Emit events on relayer changes**: Add event emission to `setRelayerApproval()` to make relayer changes visible to off-chain monitoring systems, matching the pattern used by `removeHeaderHash`.
4. **Implement an on-chain relayer rotation mechanism**: Add a governance-controlled function to propose and approve new relayers in an emergency without requiring a full contract upgrade.
