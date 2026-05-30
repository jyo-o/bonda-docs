# AVL-D01: Single Relayer Creates Bridge-Wide Single Point of Failure

{% hint style="warning" %}
**Severity**: High (7.5/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

VectorX relies on a single relayer EOA (0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D) to submit Avail block header commitments to Ethereum. This relayer is the only address authorized to call `commitHeaderRange()`, and if it goes offline, the entire bridge halts with no fallback. The contract has no on-chain heartbeat, timeout, or staleness detection mechanism, and `setRelayerApproval()` emits no events, making relayer changes invisible to off-chain monitoring.

## Description

The VectorX contract enforces relayer access control through an `approvedRelayers` mapping with `checkRelayer` enabled. Only the single approved relayer can call `commitHeaderRange()`, which posts ZK-verified block headers that the bridge depends on.

```solidity
// @audit — SP1Vector.sol: commitHeaderRange() is restricted to approvedRelayers.
//          Only one relayer (0x27BF...) is approved. No on-chain heartbeat,
//          timeout, or staleness detection exists anywhere in the inheritance chain.
//          setRelayerApproval() emits no events, unlike removeHeaderHash which
//          emits HeaderHashRemoved.
```

The relayer's client-side software (operator.rs) uses a 60-minute loop interval (`LOOP_INTERVAL_MINS=60`) and `BLOCK_UPDATE_INTERVAL=360`, but these are purely off-chain and cannot be enforced or monitored by the contract. The `commitHeaderRange()` function contains zero references to `block.timestamp` and has no cooldown or rate limit logic in the full inheritance chain.

A previous relayer (0x3243...2D) was rotated out, confirming that relayer changes have occurred, but there is no on-chain mechanism to propose or approve a replacement in an emergency.

## Proof of Concept

Anvil mainnet fork PoC executed three tests:

1. Confirmed single relayer access control -- only the approved relayer can call `commitHeaderRange()`
2. Confirmed absence of staleness detection -- no on-chain mechanism detects relayer failure
3. Confirmed guardian ZK bypass as the intended fallback mechanism

On-chain state at time of verification:
- `eth_getCode(0x27BF...)` returns `0x` -- confirms EOA, not a contract
- Nonce = 2632, balance = 0.82 ETH -- active account
- `approvedRelayers(0x27BF...)` returns `true` -- sole approved relayer
- `checkRelayer` returns `true` -- relayer access control is enforced
- `latestBlock` = 2975481, `headerRangeCommitmentTreeSize` = 2048

The relayer operates approximately every 120 minutes in batches of 358 blocks, consuming about 458,612 gas per commitment.

References: poc_onchain_verification.md sections 2 and 14; avl_d01_relayer_spof_poc.sh (Anvil fork, 3 tests).

## Impact

If the single relayer goes offline due to infrastructure failure, key compromise, gas exhaustion, or a targeted DDoS attack, the entire bridge silently goes stale. All `commitHeaderRange()` calls fail because no other address is in the `approvedRelayers` mapping. Avail block headers stop being verified on Ethereum, halting the bridge entirely. Avail chain data remains available on its own network but becomes unverifiable on Ethereum until the relayer is manually restored. No attacker action is required; natural failure alone triggers a full bridge halt.

### CVSS 3.1
**Score**: 7.5/10 (High)  
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Attack surface is at the network level, including DDoS or key compromise |
| AC | L (Low) | Single point of failure; even natural failure triggers a full bridge halt |
| PR | N (None) | No special privileges needed for an external attacker to cause the failure |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact stays within the bridge scope |
| C | N (None) | No confidentiality impact |
| I | N (None) | No integrity impact from relayer outage |
| A | H (High) | DA attestation bridge completely halts when commitHeaderRange() calls become impossible |

## Recommendation

1. **Add on-chain staleness detection**: Implement a heartbeat or timeout mechanism in VectorX that tracks the last commitment timestamp and allows anyone to detect when the relayer has been inactive beyond a threshold.
2. **Implement a multi-relayer fallback**: Approve additional relayer addresses in the `approvedRelayers` mapping so that if the primary relayer fails, a backup can continue submitting commitments.
3. **Emit events on relayer changes**: Add event emission to `setRelayerApproval()` to make relayer changes visible to off-chain monitoring systems, matching the pattern used by `removeHeaderHash`.
4. **Implement an on-chain relayer rotation mechanism**: Add a governance-controlled function to propose and approve new relayers in an emergency without requiring a full contract upgrade.
