# ETH-S01: Testing API JWT Authentication Bypass

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: S (Spoofing) · **Status**: code_verified
{% endhint %}

## Summary

The go-ethereum execution client exposes a `testing_` namespace in its Engine API configured with `Authenticated: false`, exempting it from the JWT authentication required by all other Engine API namespaces. If a node operator misconfigures their firewall and exposes port 8551 to the public internet, an unauthenticated attacker can invoke testing API methods remotely. This vulnerability persists across fork boundaries: Osaka and BPO forks continue to register this namespace with authentication disabled.

## Description

The root cause is in the `testing_` namespace registration within the Engine API.

```go
// @audit — testing_ namespace registered without authentication
// go-ethereum/eth/catalyst/api_testing.go, lines 37-44
// The testing_ namespace is configured with Authenticated: false,
// while all production Engine API namespaces require JWT bearer tokens.
```

Under normal operation, the Engine API port (8551) binds to localhost only. However, the authentication bypass becomes exploitable when port 8551 is exposed to external networks due to firewall misconfiguration. The vulnerability is not time-bounded — it persists into future protocol upgrades (Osaka, BPO) because the namespace continues to be registered with authentication disabled.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

An attacker who discovers an exposed Engine API port can invoke testing namespace methods without any credentials. This could allow disruption of the node's consensus participation or extraction of internal state information. The attack requires only network reachability to port 8551 — no JWT token or other credential is needed.

### CVSS 3.1
**Score**: 6.5/10 (Medium)  
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Exploitable remotely over the network once port 8551 is exposed |
| AC | L (Low) | No special conditions beyond network reachability to the exposed port |
| PR | N (None) | No authentication or privileges required; JWT is bypassed |
| UI | N (None) | No user interaction needed |
| S | U (Unchanged) | Exploitation does not cross trust boundaries beyond the exposed node |
| C | L (Low) | Limited internal state information may be exposed via testing API |
| I | L (Low) | Testing API calls could interfere with consensus duties at the node level |
| A | N (None) | Testing namespace does not provide shutdown or resource exhaustion capabilities |

## Recommendation

1. **Enforce firewall rules on Engine API port**: Ensure port 8551 is restricted to localhost or trusted peers only. The Engine API binds to `127.0.0.1` by default — node operators must verify that firewall rules explicitly block external access.
2. **Monitor for unexpected port exposure**: Deploy infrastructure monitoring that alerts on any unexpected exposure of Engine API ports to external networks.
3. **Consider adding authentication to the testing namespace**: As a defense-in-depth measure, the `testing_` namespace should require JWT authentication consistent with other Engine API namespaces, even though it is intended for testing purposes.
