# EDA-E01: Configuration Flag Can Disable All Anchor Signature Verification

{% hint style="info" %}
**Severity**: Medium (4.0/10) · **STRIDE**: E · **Status**: Code Verified
{% endhint %}

## Summary

The EigenDA Disperser has a configuration flag `DisableAnchorSignatureVerification` that, when set to `true`, completely bypasses anchor signature verification. While this flag defaults to `false`, a related flag `TolerateMissingAnchorSignature` defaults to `true`, allowing requests that omit anchor signatures to proceed.

The root cause is the existence of a flag that can disable a critical security control introduced following the Sigma Prime audit. Server configuration access would allow an attacker to silently disable anchor verification with no external indication.

## Description

Two configuration flags control anchor signature behavior in the Disperser's `ServerConfig` struct:

```go
// disperser/server_config.go
// @audit DisableAnchorSignatureVerification can bypass all anchor verification
type ServerConfig struct {
    // ...
    // Whether to tolerate requests without an anchor signature.
    // Default: true (for backwards compatibility with old client code during migration)
    // TODO (litt3): this field should eventually be set to false, and then removed
    TolerateMissingAnchorSignature bool

    // Whether to disable anchor signature verification entirely.
    // If true, anchor signatures will not be verified even if present.
    // Default: false
    // TODO (litt3): This is a temporary flag to allow a second LayrLabs disperser
    DisableAnchorSignatureVerification bool
}
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/server_config.go
```

`DisableAnchorSignatureVerification` is registered as a `cli.BoolFlag`, which means it defaults to `false`. When set to `true`, it completely bypasses all anchor signature verification.

`TolerateMissingAnchorSignature` is registered as a `cli.BoolTFlag`, which means it defaults to `true`. This allows dispersal requests that omit the anchor signature to proceed without error.

The combination of these two flags weakens the anchor signature protection introduced following the Sigma Prime audit findings (EDA2-02, EDA2-11, EDA2-18). No anchor-related errors or warnings appear in mainnet proxy logs, suggesting that anchor verification is either being skipped or operating in tolerate mode. The disperser-side configuration cannot be directly verified from outside the infrastructure.

## Proof of Concept

No exploit reproduction was conducted. This finding is based on source code analysis of the EigenDA codebase at commit `ec2ce8ab`.

`DisableAnchorSignatureVerification` is registered as `cli.BoolFlag` (defaults to `false`). `TolerateMissingAnchorSignature` is registered as `cli.BoolTFlag` (defaults to `true`). Mainnet disperser settings cannot be directly verified from outside the infrastructure, but proxy logs show no anchor-related errors, consistent with tolerate mode being active.

## Impact

An attacker with access to the Disperser server's environment variables or configuration can set `DisableAnchorSignatureVerification` to `true`, completely bypassing anchor signature verification. This would enable cross-chain replay attacks (related to EDA-S03) by removing the chain-binding protection.

The attack requires server administrator privileges, either through physical access or environment variable injection. This makes it a targeted insider or supply-chain attack vector. Other verification layers such as BLS signature verification remain active, limiting the blast radius.

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
