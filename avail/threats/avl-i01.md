# AVL-I01: Incomplete Block Reconstruction Limits DAS Security Guarantees

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: I · **Scope**: chain · **Status**: Unverified
{% endhint %}

## Overview

Avail uses Data Availability Sampling (DAS) to allow light clients to verify that block data has been made available without downloading entire blocks. Observatory measurements show that DAS achieves 99.84% sampling confidence, demonstrating that the sampling mechanism itself is functioning correctly.

However, DAS alone only proves that data was available at the time of sampling. The complementary mechanism, block reconstruction, which allows full blocks to be reassembled from the sampled pieces, is still under development. Without a working reconstruction protocol, there is no guarantee that sampled data can actually be recovered into complete blocks when needed.

Currently, data recovery depends on approximately 40 full node peers that store complete block data. If these full nodes were to go offline or become unavailable, there would be no fallback mechanism to reconstruct blocks from the sampled fragments alone. This means the security guarantee provided by DAS is currently theoretical rather than fully operational. This finding cannot be independently verified through code review because the reconstruction implementation is still in progress.

## Prerequisites

- A scenario where full nodes become unavailable or refuse to serve data
- Absence of a working block reconstruction protocol

## Attack Scenario

1. An attacker or natural event causes a significant number of Avail's approximately 40 full nodes to go offline simultaneously, through a targeted DDoS attack, infrastructure failure, or coordinated shutdown.
2. A light client that previously confirmed data availability through DAS sampling now needs to reconstruct the full block data for verification or dispute resolution purposes.
3. Without the reconstruction protocol in place and with insufficient full nodes available to serve the data, the block cannot be recovered. The data that was confirmed as "available" through sampling becomes practically irretrievable, undermining the core security guarantee of the data availability layer.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N/CI:L/II:N/AI:N` |
| Scope | chain |

### Scoring Rationale

There is no direct financial impact from this issue. The attack vector is network-based since it involves disrupting full node availability. Attack complexity is high because it requires a majority of the approximately 40 full nodes to be simultaneously unavailable, which is difficult to achieve in practice. No special privileges are required to attempt data reconstruction. The scope is limited to the DAS security guarantees. Confidentiality impact is low because some data may become inaccessible if recovery fails, and infrastructure confidentiality impact is similarly low for the same reason.

## Evidence

### On-Chain Verification

- Observatory metric `avail_block_availability_samples` shows DAS confidence of 99.84%, confirming that sampling itself works correctly.
- Approximately 40 full node peers observed in the network.

### Source Code

- Avail documentation confirms that the block reconstruction protocol is under active development and not yet production-ready.

## Mitigations

Multiple full nodes currently exist in the network, with approximately 40 peers observed, providing redundant data storage. DAS itself is fully operational and achieves high confidence levels. The reconstruction protocol is under active development, and once completed, it will close the gap between sampling confidence and data recoverability.
