# EDA-D07: GetBlob Unauthenticated -- Relies Solely on Rate Limiting

{% hint style="info" %}
**Severity**: Low (2.0/10) · **STRIDE**: D · **Scope**: rollup · **Status**: Verified
{% endhint %}

## Overview

Relay's GetBlob has no authentication, and the rate limiter has no per-client field -- only global limits. Mainnet testing showed GetBlob accepts unauthenticated access (NotFound response), and 31 instances of 429 Too Many Requests were observed over 7 days, demonstrating global rate limit exhaustion. In contrast, GetChunks requires operator authentication (returns InvalidArgument), showing asymmetric auth policies between GetBlob and GetChunks.

## Prerequisites

Access to Relay endpoint

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.0/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:M` |
| Likelihood | Unrated |
| Scope | rollup |
| Target | Process |

### BVSS Rationale

B:N -- No financial impact. AV:N -- Unauthenticated access. AC:L -- Confirmed on mainnet. A:L/AI:M -- Read-only path, but legitimate users also receive 429 when global rate limit is reached (31 instances observed over 7 days).

## Code References

### Source Code

- [`relay/limiter/blob_rate_limiter.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/relay/limiter/blob_rate_limiter.go) -- per-client 필드 없음

### PoC Notes

- grpcurl GetBlob → NotFound(not Unauthorized)
- poc/08-*/evidence.yaml [VERIFIED]
- grpcurl GetChunks→InvalidArgument(auth required

### Other References

- gRPC probe: relay-0-mainnet-ethereum.eigenda.xyz:443 GetBlob → NotFound
- Prober: retrieval_probes 429 에러 31건/7일
- DFD: DFD YAML f21 note
- prober 24h — 0 rate_limit_429 (reduced from 31/7d)
- 8/122745 failures
- wrong status code)

## Verification & Evidence

**Status**: Verified

grpcurl without auth headers achieved 50/50 retrieval success.

**PoC References**: #07

## Mitigations

Rate limit exists.
