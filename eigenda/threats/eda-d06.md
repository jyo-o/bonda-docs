# EDA-D06: Relay Single Point of Failure on Mainnet

{% hint style="warning" %}
**Severity**: High (7.5/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

The EigenDA mainnet operates with only a single Relay registered in the `RelayRegistry` contract (`0xD160e6...`), creating a single point of failure for the primary blob read path. The root cause is that `nextRelayKey` equals 1, meaning only relay key 0 is registered, and new relays can only be added by the contract owner via `onlyOwner`. If this single relay goes down, the primary data retrieval path for all clients is immediately disrupted, forcing a fallback to the degraded `GetChunks` validator direct retrieval path.

## Description

On-chain queries to the `RelayRegistry` contract confirm the single-relay configuration:

- `nextRelayKey()` returns `1` at block 25101686, confirming only one relay is registered.
- `relayKeyToAddress(0)` returns `0xe8437B66E834B7CdC90cC5D98B8DD6e636b37D7a`.
- Keys 1 through 5 all return `0x0` (unregistered).

The relay registry contract restricts relay addition to the contract owner. Once a relay is added, there is no function to remove or replace it:

```solidity
// contracts/src/core/EigenDARelayRegistry.sol:20-23
// @audit onlyOwner addition with no deletion function — registered relays are permanent
function addRelayInfo(EigenDATypesV2.RelayInfo memory relayInfo) external onlyOwner returns (uint32) {
    relayKeyToInfo[nextRelayKey] = relayInfo;
    emit RelayAdded(relayInfo.relayAddress, nextRelayKey, relayInfo.relayURL);
    return nextRelayKey++;
}
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/core/EigenDARelayRegistry.sol#L20-L23
```

A fallback mechanism exists through validator direct retrieval via `GetChunks`, which automatically activates after relay failure. However, this fallback offers degraded performance compared to the relay path and is reactive rather than preventive.

## Proof of Concept

On-chain state was queried at block 25101686. See [Verification Evidence](../evidence.md#5-relay-registry-single-point-of-failure-eda-d06) for full commands and results.

No exploit reproduction was conducted beyond on-chain state verification.

- `nextRelayKey()` returns `1`, confirming only one relay is registered
- `relayKeyToAddress(0)` returns `0xe8437B...`, keys 1 through 5 all return `0x0`

## Impact

A denial-of-service attack or outage targeting the single relay at `relay-0-mainnet-ethereum.eigenda.xyz` would immediately disrupt the primary blob read path for all EigenDA clients. While the `GetChunks` fallback exists, it provides degraded performance as all read traffic shifts to a path not designed for primary use. No authentication is required to target the relay, and any network-level disruption suffices. The impact extends to all rollups depending on EigenDA for data retrieval.

### CVSS 3.1

**Score**: 7.5/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | The relay endpoint is publicly reachable over the network |
| AC (Attack Complexity) | L (Low) | Only one relay exists on mainnet (confirmed on-chain with `nextRelayKey=1`), so any failure immediately impacts the read path |
| PR (Privileges Required) | N (None) | No privileges needed to target the relay with a denial-of-service attack |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the EigenDA read path |
| C (Confidentiality) | N (None) | No data exposure from relay outage |
| I (Integrity) | N (None) | No data integrity impact; data is not corrupted |
| A (Availability) | H (High) | Single point of failure for the primary read path; fallback exists but with degraded performance |

## Recommendation

1. Register additional relays in the `RelayRegistry` to eliminate the single point of failure.
2. Deploy relays across geographically distributed infrastructure to ensure resilience against regional outages.
3. Consider implementing proactive health monitoring and automatic failover mechanisms rather than relying solely on the reactive `GetChunks` fallback.
