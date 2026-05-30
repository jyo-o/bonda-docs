# EDA-D02: Proxy HTTP Server Missing Rate Limiting

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: D · **Status**: Code Verified
{% endhint %}

## Overview

The EigenDA Proxy REST server lacks rate limiter middleware, meaning there is no limit on the number of incoming requests. While body size is capped at 16 MB via `MaxServerPOSTRequestBodySize`, the server will accept an unlimited number of requests. The server binds to `0.0.0.0` by default, but code comments in `routing.go` and the README explicitly state that the Proxy is not intended for public exposure and should never be publicly accessible.

The Proxy is designed as a private sidecar for rollup operators. External exposure only occurs when an operator fails to configure proper firewall rules or reverse-proxy access controls. Even in that scenario, the impact is confined to the specific rollup operator's sidecar instance. There is no protocol-level impact.

Server timeouts are set to `ReadHeaderTimeout: 10s` and `WriteTimeout: 40min`, which are generous but not exploitable in the absence of external exposure.

## Prerequisites

- Proxy exposed to the internet without firewall protection due to operator misconfiguration.

## Attack Scenario

1. An operator deploys the Proxy sidecar without configuring firewall rules or reverse-proxy access controls.
2. An attacker discovers the publicly exposed Proxy REST endpoint.
3. The attacker sends a high volume of HTTP requests to the Proxy, exploiting the absence of request count limits.
4. The Proxy becomes overloaded, degrading or disrupting blob dispersal and retrieval for that specific rollup operator.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Scope | Rollup |

### Scoring Rationale

The Blockchain Impact (B) is None because there is no direct financial impact from this threat. The Attack Vector (AV) is Network since the endpoint is reachable over the network when improperly exposed. Attack Complexity (AC) is High because the Proxy is designed as a private sidecar and external exposure only occurs through operator misconfiguration, which is explicitly warned against in both code and documentation. Availability impact (A) is Low and Availability Infrastructure impact (AI) is also Low because any damage is limited to the specific rollup sidecar with no protocol-level effect.

## Evidence

### Source Code

- [`api/proxy/servers/rest/server.go:57-59`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59) -- Server configuration with no rate limiter middleware.
- [`api/proxy/servers/rest/cli.go:47`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/cli.go#L47) -- Default bind address is `0.0.0.0`.
- [`api/proxy/servers/rest/routing.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/routing.go) -- Comment states the proxy is not meant to be exposed publicly.
- `README.md:139` -- States the proxy should "NEVER be publicly accessible".

### PoC Testing

- PoC #08 confirmed only a global throttle exists; the Proxy (EigenDA client-side) is a separate component.
- PoC #09 cross-check confirmed the finding.
- External exposure is unintended by design, leading to AC:H downgrade.

**PoC References**: #07, #23

## Mitigations

The `http.MaxBytesReader` enforces a 16 MB body size limit, which prevents individual oversized payloads. However, no request count limit exists. When operators properly configure firewall or reverse-proxy access controls, the entire attack surface is eliminated. The audit consolidated assessment classified this as a conditional finding.
