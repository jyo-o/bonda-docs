# EDA-D02: Proxy HTTP Server Missing Rate Limiting

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: Code Verified
{% endhint %}

## Summary

The EigenDA Proxy REST server lacks rate limiter middleware, accepting an unlimited number of incoming requests. While body size is capped at 16 MB via `MaxServerPOSTRequestBodySize`, no request count limit exists. The root cause is the absence of rate limiting middleware in the server configuration. However, the Proxy is designed as a private sidecar for rollup operators and is explicitly documented as not intended for public exposure. External exposure only occurs through operator misconfiguration, and any impact is confined to the specific rollup operator's sidecar instance.

## Description

The Proxy server configuration lacks rate limiting middleware:

**Source**: [`api/proxy/servers/rest/server.go:57-59`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59) -- Server configuration with no rate limiter middleware.

The default bind address is `0.0.0.0`:

**Source**: [`api/proxy/servers/rest/cli.go:47`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/cli.go#L47) -- Default bind address is `0.0.0.0`.

Code comments and documentation explicitly state the Proxy is not meant for public exposure:

**Source**: [`api/proxy/servers/rest/routing.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/routing.go) -- Comment states the proxy is not meant to be exposed publicly.

The README at line 139 states the proxy should "NEVER be publicly accessible".

Server timeouts are set to `ReadHeaderTimeout: 10s` and `WriteTimeout: 40min`, which are generous but not exploitable in the absence of external exposure.

## Proof of Concept

### Reproduction

- PoC #08 confirmed only a global throttle exists; the Proxy (EigenDA client-side) is a separate component.
- PoC #09 cross-check confirmed the finding.
- External exposure is unintended by design.

**PoC References**: #07, #23

## Impact

If a rollup operator deploys the Proxy sidecar without configuring firewall rules or reverse-proxy access controls, an attacker who discovers the exposed endpoint can send a high volume of requests to overload it. The impact is confined to that specific rollup operator's blob dispersal and retrieval capabilities. There is no protocol-level impact. The Proxy is designed as a private sidecar, and the documentation explicitly warns against public exposure, making this a conditional finding dependent on operator misconfiguration.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | The endpoint is reachable over the network when improperly exposed |
| AC (Attack Complexity) | H (High) | The Proxy is designed as a private sidecar; external exposure only occurs through operator misconfiguration, which is explicitly warned against in both code and documentation |
| PR (Privileges Required) | N (None) | No authentication required when the Proxy is exposed |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is limited to the specific rollup operator's sidecar |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | N (None) | No data integrity impact |
| A (Availability) | L (Low) | Damage is limited to the individual rollup sidecar with no protocol-level effect |

## Recommendation

1. Add request rate limiting middleware to the Proxy REST server for defense-in-depth, even though it is designed as a private sidecar.
2. Change the default bind address from `0.0.0.0` to `127.0.0.1` (localhost) to prevent accidental public exposure.
3. Operators must configure firewall or reverse-proxy access controls to restrict access to the Proxy endpoint.
