# EDA-D10: Unauthenticated POST Requests Can Overload Proxy

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: Code Verified
{% endhint %}

## Summary

The EigenDA Proxy HTTP POST endpoint has no request count limit. The only protection is a body size limit enforced by `MaxBytesReader` at 16 MB per request. The root cause is identical to EDA-D02: missing rate limiting middleware on the Proxy REST server. An attacker who can reach the Proxy can send unlimited POST requests to overload it. However, the Proxy is a rollup operator's self-operated sidecar, not a publicly exposed service, and this threat only materializes through operator misconfiguration.

## Description

The POST endpoint lacks request count limiting:

**Source**: [`api/proxy/servers/rest/handlers_cert.go:198`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/handlers_cert.go#L198) -- Only `MaxBytesReader` is applied; no request count limiter exists.

The server configuration confirms the absence of rate limiting middleware:

**Source**: [`api/proxy/servers/rest/server.go:57-59`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59) -- Server configuration without rate limiting middleware.

This is the same root cause as EDA-D02, and both threats share the same underlying issue: the Proxy is a private sidecar that lacks rate limiting and is only vulnerable when improperly exposed to the internet.

## Proof of Concept

### Reproduction

- Code review confirmed that `handlers_cert.go:198` has only `MaxBytesReader` with no request count limit.
- Proxy is a rollup sidecar, so mainnet external probing is not possible. Verification is code-path only.
- Same root cause as EDA-D02.
- `poc/08-*/evidence.yaml` verified via PoC #09.

**PoC References**: #07, #25

## Impact

If a rollup operator exposes the Proxy without proper network isolation, an attacker can send a high volume of POST requests (each within the 16 MB body size limit) to overload the Proxy. The impact is confined to that specific rollup operator's infrastructure, with no protocol-level effect. The Proxy is designed as a private sidecar, and external exposure requires operator misconfiguration. This shares the same root cause and impact profile as EDA-D02.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | The endpoint is reachable over the network when improperly exposed |
| AC (Attack Complexity) | H (High) | The Proxy is designed as a private sidecar; external exposure requires operator misconfiguration |
| PR (Privileges Required) | N (None) | No authentication required when the Proxy is exposed |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is limited to the individual rollup operator's sidecar |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | N (None) | No data integrity impact |
| A (Availability) | L (Low) | Damage is limited to the individual rollup sidecar with no protocol-level effect |

## Recommendation

1. Add request rate limiting middleware to the POST handler for defense-in-depth.
2. Operators must configure firewall or reverse-proxy access controls to restrict access to the Proxy endpoint.
3. Consider consolidating this finding with EDA-D02, as both share the same root cause of missing rate limiting on the Proxy.
