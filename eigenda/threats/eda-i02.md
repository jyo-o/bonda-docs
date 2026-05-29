# EDA-I02: BLS Private Key Exposure on Node Process Compromise

{% hint style="info" %}
**Severity**: Low (2.8/10) · **STRIDE**: I · **Scope**: protocol · **Status**: Code Verified
{% endhint %}

## Overview

The Node process holds BLS private keys in memory. If the process is compromised, the corresponding operator's signatures can be forged. Probe measurements detected evidence of some IPs having downed Node processes (GetChunks connection refused).

## Prerequisites

Node process compromise

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:H/I:H/A:N/CI:H/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process |

### BVSS Rationale

B:N -- Protocol-level fund theft path unproven (single operator signature forgery). AV:P -- Requires Node process compromise (OS level). AC:H -- Requires OS security breach. C:H/CI:H -- BLS private key exposure. I:H/II:M -- Can forge signatures for the compromised operator but limited to single operator.

## Code References

### Source Code

- [`node/node.go:73`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/node/node.go#L73)

### PoC Notes

- code node.go:73 KeyPair 메모리 보유 확인 + prober connection refused 에러(Node 다운 증거) [CODE_VERIFIED via PoC #09]

### Other References

- Prober: operator_probes — connection refused 에러 다수 IP (138.68.36.39
- 209.38.186.212
- 146.190.207.21 등)

## Verification & Evidence

**Status**: Code Verified

BLS keypair storage method is an operational domain concern; external verification not possible. PoC #09: cross-check OK.

**PoC References**: #23

## Mitigations

Process security (OS-level).
