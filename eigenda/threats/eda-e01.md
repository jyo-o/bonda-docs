# EDA-E01: DisableAnchorSignatureVerification Flag Bypasses All Anchor Verification

{% hint style="info" %}
**Severity**: Low (1.9/10) · **STRIDE**: E · **Scope**: protocol · **Status**: Code Verified
{% endhint %}

## Overview

DisableAnchorSignatureVerification is a cli.BoolFlag (default false). TolerateMissingAnchorSignature is a cli.BoolTFlag (default true). No anchor-related errors/warnings appear in mainnet proxy logs -- it is presumed that anchor verification is currently being skipped or operating in tolerate mode, though the disperser-side configuration cannot be directly verified.

## Prerequisites

Server configuration change permission or ability to inject environment variables

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.9/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:P -- Requires server environment variable access. AC:H -- Default false, intentional activation required. PR:R -- Server administrator privileges. I:H/II:M -- Anchor verification bypass, but other verification layers like BLS verification remain.

## Code References

### Source Code

- [`disperser/server_config.go:50-58`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/server_config.go#L50-L58)
- [`disperser/cmd/apiserver/flags/flags.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go) -- BoolFlag(default false) vs BoolTFlag(default true)

### PoC Notes

- code flags.go DisableAnchorSig=BoolFlag(default false)
- poc/12-*/evidence.yaml [VERIFIED]

### Other References

- Prober: eigenda-proxy 로그 anchor 관련 없음
- TolerateMissing=BoolTFlag(default true) 확인

## Verification & Evidence

**Status**: Code Verified

Code confirms default DisableAnchorSignatureVerification=false. Mainnet disperser settings cannot be directly verified -- code path only.

**PoC References**: #10

## Mitigations

Default is false. TODO: temporary flag, will be removed.
