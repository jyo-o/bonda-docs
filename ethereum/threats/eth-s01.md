# ETH-S01: Testing API JWT Authentication Bypass

{% hint style="info" %}
**Severity**: Low (2.8/10) · **STRIDE**: S (Spoofing) · **Status**: code_verified
{% endhint %}

## Overview

The go-ethereum execution client exposes a `testing_` namespace in its Engine API that is configured with `Authenticated: false`. This setting is found in `go-ethereum/eth/catalyst/api_testing.go` at lines 37-44. Unlike production Engine API namespaces that require JWT authentication, the testing namespace can be accessed without any credentials.

Under normal operation, the Engine API port (8551) binds to localhost only, making this a non-issue. However, if a node operator misconfigures their firewall and exposes port 8551 to the public internet, an unauthenticated attacker can invoke testing API methods remotely. This misconfiguration scenario is the sole prerequisite for exploitation.

The vulnerability persists across fork boundaries. Even after the Fulu fork, the Osaka and BPO forks continue to register this namespace with authentication disabled, meaning the exposure window extends into future protocol upgrades.

## Prerequisites

- Engine API port 8551 must be exposed to the internet due to firewall misconfiguration
- No JWT token or other authentication is needed once the port is reachable

## Attack Scenario

1. The attacker scans the internet for Ethereum nodes with port 8551 open to external connections.
2. Upon finding an exposed node, the attacker sends RPC requests to the `testing_` namespace without providing a JWT bearer token.
3. The go-ethereum client accepts these requests because the `testing_` namespace has `Authenticated: false`.
4. The attacker can invoke testing API methods, potentially disrupting the node's consensus participation or extracting internal state information.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:L/CI:M/I:L/II:L/A:N/AI:N` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based with low complexity, requiring no privileges or user interaction. Confidentiality impact is low since limited internal state may be exposed. Integrity impact is low at the node level but medium at the chain level because testing API calls could interfere with consensus duties. Availability is unaffected as the testing namespace does not provide shutdown or resource exhaustion capabilities. The scope is unchanged because exploitation does not cross trust boundaries beyond the already-exposed node.

## Evidence

### Source Code

- **Repository**: go-ethereum (Geth execution client)
- **File**: [`eth/catalyst/api_testing.go`, lines 37-44](https://github.com/ethereum/go-ethereum/blob/master/eth/catalyst/api_testing.go#L37-L44)
- **Finding**: The `testing_` namespace is registered with `Authenticated: false`, exempting it from JWT authentication required by other Engine API namespaces.

## Mitigations

The primary mitigation is proper firewall configuration. When port 8551 is restricted to localhost or trusted peers only, the attack surface is completely eliminated. In standard deployment configurations, the Engine API binds to `127.0.0.1` by default, which prevents external access. Node operators should verify that their firewall rules explicitly block external access to port 8551. Additionally, infrastructure monitoring should alert on any unexpected exposure of Engine API ports.
