# EDA-S03: Cross-Chain Signature Replay Due to Non-Enforced Anchor Signature

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: S · **Status**: Verified
{% endhint %}

## Overview

The EigenDA Disperser accepts dispersal requests without anchor signatures on mainnet. The `TolerateMissingAnchorSignature` flag is a `cli.BoolTFlag` with a default value of `true`, meaning the server tolerates missing anchor signatures by default. The anchor signature mechanism was introduced following the Sigma Prime audit (findings EDA2-02 Critical, EDA2-11 Medium, EDA2-18 Medium, all resolved), but it remains non-enforced in production.

At the protocol buffer level, `disperser_v2.proto` defines `DisperseBlobRequest.anchor_signature` as field 5, which is implicit-optional. This means the proto definition itself permits omission of the field. Combined with the server flag defaulting to true, the ability to omit anchor signatures is redundantly permitted at two independent layers: the proto design and the server configuration.

A separate flag, `DisableAnchorSignatureVerification`, is a `cli.BoolFlag` with default `false`. No anchor-related errors appear in proxy operation logs, consistent with the tolerate mode being active in production.

Live testing on 2026-05-24 confirmed the behavior: an ephemeral wallet sent a `DisperseBlob` request without an anchor signature. The response was `gRPC Internal (no reservation found)`, which is a payment-related rejection, not an anchor verification error. This proves that `TolerateMissingAnchorSignature=true` is active in the production Disperser.

## Prerequisites

- Ability to send dispersal requests without anchor signatures, which is permitted by default.

## Attack Scenario

1. An attacker captures a valid dispersal request from one chain or deployment.
2. The attacker replays the request on a different chain or EigenDA deployment, omitting the anchor signature.
3. Because `TolerateMissingAnchorSignature` defaults to `true`, the Disperser does not reject the request for missing anchor data.
4. The replayed request is processed (assuming it passes payment validation), potentially causing data to be attested on an unintended chain.
5. On-chain BLS verification still applies, but the chain-binding protection that anchor signatures are designed to provide is absent.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.7/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:R/UI:N/S:C/C:N/I:M/A:N/CI:N/II:M/AI:N` |
| Scope | Bridge |

### Scoring Rationale

Blockchain Impact (B) is None because no direct financial loss path has been proven. Attack Complexity (AC) is High because an ECDSA signature is required and the anchor signature mechanism itself exists, just not enforced by default. Privileges Required (PR) is Reserved because a valid signature is needed for dispersal requests. Scope (S) is Changed because cross-chain replay is possible, affecting systems beyond the original chain. Integrity impact (I) is Medium because the anchor signature is not enforced, but on-chain BLS verification remains active. Integrity Infrastructure impact (II) is Medium for the same reason.

## Evidence

### Source Code

- [`disperser/cmd/apiserver/flags/flags.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go) -- `TolerateMissingAnchorSignature` is `cli.BoolTFlag` (default `true`).
- [`disperser/apiserver/disperse_blob_v2.go:289-291`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L289-L291) -- Anchor signature check logic.
- [`api/proto/disperser/v2/disperser_v2.proto:68-81`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proto/disperser/v2/disperser_v2.proto#L68-L81) -- `anchor_signature` is field 5, implicit-optional.

### PoC Testing

- Live test (2026-05-24): Ephemeral wallet `DisperseBlob` without anchor signature returned `gRPC Internal (no reservation found)`, confirming no anchor error was raised. See [eigenda-anchor-sig-poc](https://github.com/jyo-o/eigenda-anchor-sig-poc) (private).
- `poc/12-*/evidence.yaml` confirmed code-level findings.

**PoC References**: #10, #anchor-sig

### Audit References

- Sigma Prime EDA2-02 (Critical, Resolved), EDA2-11 (Medium, Resolved), EDA2-18 (Medium, Resolved).

## Mitigations

The anchor signature mechanism exists but is not enforced with the default configuration. The `TolerateMissingAnchorSignature` flag should be set to `false` and subsequently removed, as indicated by the TODO comment in the codebase. On-chain BLS verification remains active as a secondary defense layer.
