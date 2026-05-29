# EDA-D10: Unauthenticated POST Bulk Requests Overload Proxy

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: D · **Scope**: rollup · **Status**: Code Verified
{% endhint %}

## Overview

Proxy HTTP POST has no request count limit. Body size is limited by MaxBytesReader at 16MB. Since the Proxy is a rollup operator's self-operated sidecar, this is only a threat when externally exposed. Same root cause as EDA-D02.

## Prerequisites

Access to Proxy endpoint

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Likelihood | Unrated |
| Scope | rollup |
| Target | Dataflow |

### BVSS Rationale

B:N -- No financial impact. AV:N. AC:H -- Same root cause as EDA-D02; Proxy is designed as a private sidecar. A:L/AI:L -- Limited to individual rollup operator.

## Code References

### Source Code

- [`api/proxy/servers/rest/handlers_cert.go:198`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/handlers_cert.go#L198)
- [`api/proxy/servers/rest/server.go:57-59`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59)

### PoC Notes

- code handlers_cert.go:198 MaxBytesReader만 존재 확인. EDA-D02와 동일 근본 원인
- poc/08-*/evidence.yaml [VERIFIED via PoC #09]

## Verification & Evidence

**Status**: Code Verified

Code confirms handlers_cert.go:198 has only MaxBytesReader. Proxy is a rollup sidecar so mainnet external probing is not possible -- code path only. Same root cause as EDA-D02.

**PoC References**: #07, #25

## Mitigations

Only body size limit exists.
