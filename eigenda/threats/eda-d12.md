# EDA-D12: Dead Operators Serving Zero Chunks Despite Active BLS Signing

{% hint style="info" %}
**Severity**: Low (2.2/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Overview

A 24-hour prober measurement of 79 EigenDA operators revealed that 11 operators are completely dead, returning a 0% success rate on chunk retrieval via `GetChunks`. Additionally, 2 operators are degraded with less than 90% success, while 66 operators are healthy. The dead operators include recognizable entities such as chorus.one, swell-eigenda, and attestant.io.

These operators appear to continue signing BLS attestations while not storing or serving chunks, making them free-riding candidates. They collect rewards from participation but do not fulfill their data availability obligations. This is directly connected to the slashing absence documented in EDA-P01: without economic penalties, there is no disincentive for this behavior.

Currently, 11 out of 79 operators (13.9%) are non-responsive, which remains below the Reed-Solomon erasure coding reconstruction threshold of 22%. The system is therefore operating within its fault tolerance range, but further degradation would erode this safety margin.

## Prerequisites

- Operators sign BLS attestations but do not store or serve data chunks.
- No slashing mechanism exists to penalize non-serving behavior.

## Attack Scenario

1. An operator registers with the EigenDA network and begins signing BLS attestations.
2. The operator does not store or serve data chunks, effectively free-riding on the network.
3. The operator continues to receive rewards without fulfilling data availability obligations.
4. As more operators adopt this strategy (enabled by the absence of slashing), the number of dead operators grows.
5. If dead operators exceed the 22% reconstruction threshold, data recovery becomes unreliable.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.2/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:M/CI:N/II:N/AI:L` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because there is no direct financial impact. Attack Complexity (AC) is Low because this behavior is currently being observed in production (11/79 dead operators). Availability impact (A) is Medium because chunk serving quality is impacted. Availability Infrastructure impact (AI) is Low because 11/79 equals 13.9%, which is below the Reed-Solomon erasure coding threshold of 22%, meaning the system currently operates within its fault tolerance bounds. If slashing remains unimplemented (EDA-P01), the dead operator count may increase, but the assessment is based on the current state.

## Evidence

### On-Chain Verification

- Prober DB 24-hour measurement: 79 operators probed, 11 dead (0.0% success), 1 at 46.2%, 34 at 100%.
- Signing-info 1h/24h shows 3 dead operators, indicating an 8-operator gap between signing activity and chunk serving, consistent with the free-rider hypothesis.

### PoC Testing

- `poc/14-*/evidence.yaml` confirmed the dead operator counts and behavior.

**PoC References**: #12

## Mitigations

Reed-Solomon erasure coding enables data recovery even when some operators do not respond, with a reconstruction threshold of 22%. The current 13.9% non-response rate falls within this tolerance. However, without slashing (EDA-P01), there is no economic deterrent against free-riding, and the dead operator count could grow over time to exceed the threshold.
