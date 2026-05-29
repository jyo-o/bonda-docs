# ETH-S01: Testing API JWT Authentication Missing

{% hint style="info" %}
**Severity**: Low (2.8/10) · **STRIDE**: S (Spoofing) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

In go-ethereum/eth/catalyst/api_testing.go L37-44, the `testing_` namespace is configured with Authenticated:false. If the Engine API port (8551) is exposed to the internet due to firewall misconfiguration, the testing API becomes accessible without authentication. This remains active in the Osaka/BPO fork beyond the Fulu fork.

## Prerequisites

Engine API port exposed to the internet due to firewall misconfiguration

## Attack Scenario

**Condition**: Engine port 8551 exposed (firewall misconfigured)

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:L/CI:M/I:L/II:L/A:N/AI:N` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

- [`go-ethereum/eth/catalyst/api_testing.go:37-44 (testing_ namespace Authenticated:false)`](https://github.com/ethereum/go-ethereum/blob/master/eth/catalyst/api_testing.go#L37-L44)

## Verification & Evidence

**Status**: code_verified

Confirmed testing_ namespace Authenticated:false in api_testing.go. Only accessible externally when firewall is misconfigured.

## Mitigations

Attack surface eliminated when port 8551 is restricted by firewall. Under normal operation, it binds to localhost.
