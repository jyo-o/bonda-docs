# EDA-D10: Unauthenticated POST Requests Can Overload Proxy

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: D · **Status**: Code Verified
{% endhint %}

## Overview

The EigenDA Proxy HTTP POST endpoint has no request count limit. The only protection is a body size limit enforced by `MaxBytesReader` at 16 MB per request. An attacker who can reach the Proxy can send unlimited POST requests to overload it.

However, the Proxy is a rollup operator's self-operated sidecar, not a publicly exposed service. This threat only materializes when an operator fails to configure proper network isolation. This is the same root cause as EDA-D02, and both threats share the same underlying issue of missing rate limiting on the Proxy.

## Prerequisites

- Access to the Proxy HTTP endpoint, which requires the operator to have exposed it without firewall protection.

## Attack Scenario

1. A rollup operator deploys the EigenDA Proxy sidecar without proper firewall or access control configuration.
2. An attacker discovers the exposed Proxy endpoint.
3. The attacker sends a high volume of POST requests, each within the 16 MB body size limit.
4. The Proxy becomes overloaded, degrading the rollup operator's blob dispersal and retrieval capabilities.
5. Impact is confined to that specific rollup operator's infrastructure.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Scope | Rollup |

### Scoring Rationale

Blockchain Impact (B) is None because there is no financial impact. Attack Vector (AV) is Network because the endpoint is reachable over the network when improperly exposed. Attack Complexity (AC) is High because, like EDA-D02, the Proxy is designed as a private sidecar and external exposure requires operator misconfiguration. Availability impact (A) is Low and Availability Infrastructure impact (AI) is Low because damage is limited to the individual rollup operator's sidecar.

## Evidence

### Source Code

- [`api/proxy/servers/rest/handlers_cert.go:198`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/handlers_cert.go#L198) -- Only `MaxBytesReader` is applied; no request count limiter exists.
- [`api/proxy/servers/rest/server.go:57-59`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59) -- Server configuration without rate limiting middleware.

### PoC Testing

- Code review confirmed that `handlers_cert.go:198` has only `MaxBytesReader` with no request count limit.
- Proxy is a rollup sidecar, so mainnet external probing is not possible. Verification is code-path only.
- Same root cause as EDA-D02.
- `poc/08-*/evidence.yaml` verified via PoC #09.

**PoC References**: #07, #25

## Mitigations

Only body size limiting via `MaxBytesReader` (16 MB) exists. There is no request count limit. Operators should configure firewall or reverse-proxy access controls to restrict access to the Proxy endpoint. Adding request rate limiting middleware would provide defense-in-depth.
