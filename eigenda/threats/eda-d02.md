# EDA-D02: Proxy HTTP Server Rate Limit Absence

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: D · **Scope**: rollup · **Status**: Code Verified
{% endhint %}

## Overview

The Proxy REST server lacks rate limiter middleware. ReadHeaderTimeout is 10s, WriteTimeout is 40min. Body size is limited to MaxServerPOSTRequestBodySize=16MB, but there is no request count limit. Default bind is 0.0.0.0, however code comments (routing.go) and README explicitly state 'not intended for external exposure / NEVER publicly accessible' -- it is designed as a private sidecar. External exposure only occurs when operators fail to configure firewalls, and impact is limited to that specific rollup operator. No protocol-level impact.

## Prerequisites

Proxy exposed to the internet without firewall (operator misconfiguration)

## Attack Scenario

**Trigger condition**: `target.controls.handlesResourceConsumption is False and target.port != 0`



## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Likelihood | Unrated |
| Scope | rollup |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:N -- Network exposure when firewall is not applied. AC:H -- Designed as a private sidecar; external exposure only occurs with operator misconfiguration (explicitly stated in code and documentation). A:L/AI:L -- Impact limited to the specific rollup sidecar; no protocol-level effect.

## Code References

### Source Code

- [`api/proxy/servers/rest/server.go:57-59`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59)
- [`api/proxy/servers/rest/cli.go:47`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/cli.go#L47) -- 기본 0.0.0.0
- [`api/proxy/servers/rest/routing.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/routing.go) -- proxy isn't meant to be exposed publicly

### Audit References

- 조건부 판정

### PoC Notes

- code server.go rate limiter middleware 없음 확인
- poc/08-*/evidence.yaml [PARTIAL]

### Other References

- README.md:139(NEVER be publicly accessible)

## Verification & Evidence

**Status**: Code Verified

PoC #08 confirmed only global throttle; Proxy (EigenDA client-side) is separate. PoC #09: cross-check OK. External exposure is unintended by design (downgraded to AC:H).

**PoC References**: #07, #23

## Mitigations

http.MaxBytesReader limits body size, but no request count limit exists. If the operator configures firewall/reverse-proxy access controls, the attack surface is eliminated.
