# EDA-E01: Configuration Flag Can Disable All Anchor Signature Verification

{% hint style="info" %}
**Severity**: Low (1.9/10) · **STRIDE**: E · **Status**: Code Verified
{% endhint %}

## Overview

The EigenDA Disperser has a configuration flag called `DisableAnchorSignatureVerification` that, when set to `true`, completely bypasses anchor signature verification. This flag is a `cli.BoolFlag` with a default value of `false`, meaning anchor verification is enabled by default. However, a related flag, `TolerateMissingAnchorSignature`, is a `cli.BoolTFlag` with a default value of `true`, which allows dispersal requests that omit the anchor signature to proceed without error.

No anchor-related errors or warnings appear in mainnet proxy logs, suggesting that anchor verification is either being skipped or operating in tolerate mode. The disperser-side configuration cannot be directly verified from outside the infrastructure.

The anchor signature mechanism was introduced following the Sigma Prime audit findings (EDA2-02, EDA2-11, EDA2-18), but the combination of `DisableAnchorSignatureVerification` (available as a flag) and `TolerateMissingAnchorSignature` (defaulting to true) weakens the intended protection.

## Prerequisites

- Server configuration change permission or the ability to inject environment variables to enable the `DisableAnchorSignatureVerification` flag.

## Attack Scenario

1. An attacker with access to the Disperser server's environment variables or configuration sets `DisableAnchorSignatureVerification` to `true`.
2. All anchor signature verification is bypassed for incoming dispersal requests.
3. The attacker can submit dispersal requests without anchor signatures, potentially enabling cross-chain replay attacks (related to EDA-S03).
4. Other verification layers such as BLS signature verification remain active, limiting the blast radius.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.9/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because there is no direct financial impact. Attack Vector (AV) is Physical because server environment variable access is required. Attack Complexity (AC) is High because the flag defaults to `false` and intentional activation is needed. Privileges Required (PR) is Reserved because server administrator privileges are necessary. Integrity impact (I) is High because anchor verification is completely bypassed, but Integrity Infrastructure impact (II) is Medium because other verification layers like BLS verification remain intact.

## Evidence

### Source Code

- [`disperser/server_config.go:50-58`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/server_config.go#L50-L58) -- Server configuration struct with `DisableAnchorSignatureVerification` field.
- [`disperser/cmd/apiserver/flags/flags.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go) -- `DisableAnchorSignatureVerification` is `BoolFlag` (default false); `TolerateMissingAnchorSignature` is `BoolTFlag` (default true).

### PoC Testing

- Code confirms `DisableAnchorSignatureVerification` defaults to `false`.
- Mainnet disperser settings cannot be directly verified; only code path was inspected.
- EigenDA-Proxy logs show no anchor-related errors, consistent with tolerate mode.
- `poc/12-*/evidence.yaml` confirmed the finding.

**PoC References**: #10

## Mitigations

The default value is `false`, providing protection in standard deployments. The flag is marked as temporary and intended for removal. Both flags (`DisableAnchorSignatureVerification` and `TolerateMissingAnchorSignature`) should be deprecated once the anchor signature mechanism is fully stabilized.
