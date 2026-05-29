# EDA-D12: 11 Dead Operators -- 0% Chunk Serving Response

{% hint style="info" %}
**Severity**: Low (2.2/10) · **STRIDE**: D · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

Prober DB 24-hour measurement: 79 operators probed, 11 dead (0% success), 2 degraded (<90%), 66 healthy. Dead operators include chorus.one, swell-eigenda, attestant.io, among others. They may be signing BLS attestations but not serving chunks (free-riding candidates).

## Prerequisites

Operator signs BLS attestations but does not store/serve chunks

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.2/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:M/CI:N/II:N/AI:L` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AC:L -- Currently observed (11/79 dead). A:M -- Impacts chunk serving quality. AI:L -- 11/79=13.9%, below Reed-Solomon erasure coding threshold 22%; currently operating within fault tolerance. Conservative note: if slashing remains unimplemented (EDA-P01), dead operator count may increase, but assessed based on current state.

## Code References


### PoC Notes

- prober 24h — 11 operators at 0.0% success
- poc/14-*/evidence.yaml [VERIFIED]

### Other References

- Prober: operator_probes 79명/24시간 — 11명 0% 성공
- eigenda_dfd_v2.yaml:P5 description
- 1 at 46.2%
- 34 at 100%

## Verification & Evidence

**Status**: Verified

signing-info 1h/24h shows 3 dead. The threat's 11 are based on prober DB (GetChunks) -- 8 gap represents free-rider candidates who sign BLS but don't serve chunks.

**PoC References**: #12

## Mitigations

Reed-Solomon erasure coding enables recovery despite some operator non-responses. ReconstructionThreshold=22%.
