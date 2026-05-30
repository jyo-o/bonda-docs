# EDA-D02: Proxy HTTP Server Missing Rate Limiting

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: Code Verified
{% endhint %}

## Summary

The EigenDA Proxy REST server lacks rate limiter middleware, accepting an unlimited number of incoming requests. While body size is capped at 16 MB via `MaxServerPOSTRequestBodySize`, no request count limit exists. The root cause is the absence of rate limiting middleware in the server configuration. However, the Proxy is designed as a private sidecar for rollup operators and is explicitly documented as not intended for public exposure. External exposure only occurs through operator misconfiguration, and any impact is confined to the specific rollup operator's sidecar instance.

## Description

The Proxy server initializes a plain `http.Server` with no rate limiting or authentication middleware. The only configured parameters are timeouts:

```go
// api/proxy/servers/rest/server.go:50-62
// @audit No rate limiter or auth middleware configured in server init
httpServer: &http.Server{
    Addr:              endpoint,
    ReadHeaderTimeout: 10 * time.Second,
    WriteTimeout:      40 * time.Minute,
},
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/server.go#L57-L59
```

The default bind address is `0.0.0.0`, which listens on all interfaces. This means a freshly deployed Proxy is network-reachable by default unless the operator adds firewall rules:

```go
// api/proxy/servers/rest/cli.go:42-50
// @audit Default bind address is 0.0.0.0 — listens on all interfaces
&cli.StringFlag{
    Name:     ListenAddrFlagName,
    Usage:    "Server listening address",
    Value:    "0.0.0.0",
    EnvVars:  withEnvPrefix(envPrefix, "ADDR"),
    Category: category,
},
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proxy/servers/rest/cli.go#L47
```

The Proxy is designed as a private sidecar, and the documentation explicitly warns against public exposure. The README states the proxy should "NEVER be publicly accessible."

Server timeouts are set to `ReadHeaderTimeout: 10s` and `WriteTimeout: 40min`. These are generous but not exploitable in the absence of external exposure.

## Proof of Concept

No exploit reproduction was conducted. This finding is based on source code analysis of the EigenDA codebase at commit `ec2ce8ab`.

The Proxy REST server source code was reviewed and confirmed to have no rate limiting or authentication middleware in its server initialization. External exposure is unintended by design, and the documentation explicitly warns against public access.

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
