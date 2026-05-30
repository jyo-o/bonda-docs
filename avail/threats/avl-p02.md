# AVL-P02: Incomplete Block Reconstruction Limits DAS Security Guarantees

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: P · **Status**: Unverified
{% endhint %}

## Summary

Avail's Data Availability Sampling (DAS) achieves 99.84% sampling confidence, but the complementary block reconstruction protocol is still under development. Without a working reconstruction mechanism, sampled data cannot be reassembled into complete blocks when needed. Data recovery currently depends on approximately 40 full node peers, and if these go offline, blocks confirmed as "available" through DAS become practically irretrievable.

## Description

DAS allows light clients to verify data availability without downloading entire blocks. Observatory measurements confirm the sampling mechanism itself functions correctly with 99.84% confidence. However, DAS alone only proves data was available at the time of sampling.

```
// @audit — DAS security gap:
//          DAS confidence: 99.84% (Observatory measurement)
//          Block reconstruction protocol: under development, not production-ready
//          Full node peers: ~40 (sole data recovery fallback)
//          Gap: sampling proves availability but cannot guarantee recoverability
//          without reconstruction or full node availability.
```

The block reconstruction protocol, which would allow full blocks to be reassembled from sampled fragments alone, is not yet production-ready. This means the complete DAS security guarantee (availability implies recoverability) is currently theoretical rather than fully operational.

## Proof of Concept

No proof of concept was conducted for this threat. The finding is based on Observatory metrics showing DAS confidence of 99.84% and Avail documentation confirming the block reconstruction protocol is under active development and not yet production-ready. Independent verification through code review is not possible because the implementation is still in progress.

## Impact

If a significant number of the approximately 40 full nodes go offline simultaneously (through DDoS, infrastructure failure, or coordinated shutdown), light clients that confirmed data availability through DAS would be unable to reconstruct full block data for verification or dispute resolution. Data confirmed as "available" through sampling becomes practically irretrievable, undermining the core security guarantee of the data availability layer.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Involves disrupting full node availability at the network level |
| AC | H (High) | Requires a majority of ~40 full nodes to be simultaneously unavailable |
| PR | N (None) | No special privileges required to attempt data reconstruction |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact limited to the DAS security guarantees |
| C | L (Low) | Some data may become inaccessible if recovery fails |
| I | N (None) | No integrity impact |
| A | N (None) | No direct availability impact on chain operations |

## Recommendation

1. **Prioritize block reconstruction protocol completion**: Accelerate development of the reconstruction protocol to close the gap between sampling confidence and data recoverability.
2. **Increase full node redundancy**: Incentivize more full node operators to join the network, reducing the risk that a simultaneous outage makes data unrecoverable.
3. **Implement full node health monitoring**: Deploy monitoring for the full node peer set to detect significant drops in available nodes before they impact data recoverability.
