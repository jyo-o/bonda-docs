# EDA-E01: Configuration Flag Can Disable All Anchor Signature Verification

{% hint style="info" %}
**Severity**: Medium (4.0/10) · **STRIDE**: E · **Status**: Code Verified
{% endhint %}

## Summary

The EigenDA Disperser has a configuration flag `DisableAnchorSignatureVerification` that, when set to `true`, completely bypasses anchor signature verification. While this flag defaults to `false`, a related flag `TolerateMissingAnchorSignature` defaults to `true`, allowing requests that omit anchor signatures to proceed. The root cause is the existence of a flag that can disable a critical security control introduced following the Sigma Prime audit. Server configuration access would allow an attacker to silently disable anchor verification with no external indication.

## Description

Two configuration flags control anchor signature behavior:

**`DisableAnchorSignatureVerification`** -- `cli.BoolFlag` with default `false`. When set to `true`, completely bypasses all anchor signature verification.

**Source**: [`disperser/server_config.go:50-58`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/server_config.go#L50-L58) -- Server configuration struct with `DisableAnchorSignatureVerification` field.

**`TolerateMissingAnchorSignature`** -- `cli.BoolTFlag` with default `true`. Allows dispersal requests that omit the anchor signature to proceed without error.

**Source**: [`disperser/cmd/apiserver/flags/flags.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go) -- Both flags defined here.

The combination of these two flags weakens the anchor signature protection introduced following the Sigma Prime audit findings (EDA2-02, EDA2-11, EDA2-18). No anchor-related errors or warnings appear in mainnet proxy logs, suggesting that anchor verification is either being skipped or operating in tolerate mode. The disperser-side configuration cannot be directly verified from outside the infrastructure.

## Proof of Concept

### Reproduction

- Code confirms `DisableAnchorSignatureVerification` defaults to `false`.
- Mainnet disperser settings cannot be directly verified; only code path was inspected.
- EigenDA-Proxy logs show no anchor-related errors, consistent with tolerate mode.
- `poc/12-*/evidence.yaml` confirmed the finding.

**PoC References**: #10

## Impact

An attacker with access to the Disperser server's environment variables or configuration can set `DisableAnchorSignatureVerification` to `true`, completely bypassing anchor signature verification. This would enable cross-chain replay attacks (related to EDA-S03) by removing the chain-binding protection. The attack requires server administrator privileges (physical access or environment variable injection), making it a targeted insider or supply-chain attack vector. Other verification layers such as BLS signature verification remain active, limiting the blast radius.

### CVSS 3.1

**Score**: 4.0/10 (Medium)
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | P (Physical) | Server environment variable access is required to change the flag |
| AC (Attack Complexity) | H (High) | The flag defaults to `false` and intentional activation is needed; requires server administrator access |
| PR (Privileges Required) | L (Low) | Server administrator privileges are necessary |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the Disperser's verification scope |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | H (High) | Anchor verification is completely bypassed; other verification layers like BLS remain intact |
| A (Availability) | N (None) | No availability impact |

## Recommendation

1. Deprecate and remove the `DisableAnchorSignatureVerification` flag once the anchor signature mechanism is fully stabilized.
2. Set `TolerateMissingAnchorSignature` to `false` in production to enforce anchor signatures (related to EDA-S03).
3. Implement configuration auditing to detect changes to security-critical flags in production.
4. Mark both flags as temporary with clear removal timelines in the codebase.
