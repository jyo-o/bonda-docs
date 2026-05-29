# EDA-S03: Cross-chain Signature Replay (anchor_signature Not Enforced)

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: S · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

TolerateMissingAnchorSignature is a cli.BoolTFlag (default TRUE). The mainnet disperser accepts dispersal without anchor_signature. The anchor_signature mechanism was introduced after Sigma Prime EDA2-02, 11, 18 fixes, but remains non-enforced with default true. DisableAnchorSignatureVerification is a cli.BoolFlag (default false). At the proto level, disperser_v2.proto DisperseBlobRequest.anchor_signature is field 5 (implicit-optional), so the proto definition itself permits omission. No anchor-related errors appear in proxy operation logs. [Consolidated with EDA-T12] The ability to omit anchor_signature is redundantly permitted at two layers: proto design (optional field) and server flag (BoolTFlag=true).

## Prerequisites

Ability to send dispersal requests without anchor_signature

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.7/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:R/UI:N/S:C/C:N/I:M/A:N/CI:N/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | Process |

### BVSS Rationale

B:N -- No direct financial loss path proven. AC:H -- ECDSA signature required + mechanism itself exists (just non-enforced by default). PR:R -- Valid signature required. S:C -- Cross-chain replay possible. I:M/II:M -- Anchor non-enforced but onchain BLS verification remains.

## Code References

### Source Code

- [`disperser/cmd/apiserver/flags/flags.go`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go) -- cli.BoolTFlag = default true
- [`disperser/apiserver/disperse_blob_v2.go:289-291`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L289-L291)
- [`api/proto/disperser/v2/disperser_v2.proto:68-81`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/api/proto/disperser/v2/disperser_v2.proto#L68-L81) -- anchor_signature field 5 optional

### Audit References

- Sigma Prime EDA2-02(Critical Resolved) EDA2-11(Medium Resolved) EDA2-18(Medium Resolved)

### PoC Notes

- poc/12-*/evidence.yaml [VERIFIED]
- github.com/jyo-o/eigenda-anchor-sig-poc (private) [LIVE — ephemeral 지갑 서명 gRPC probe

### Other References

- 응답=Internal(no reservation found)
- anchor 에러 미발생 확인
- 2026-05-24]

## Verification & Evidence

**Status**: Verified

Code confirms default TolerateMissingAnchorSignature=true. Live test (2026-05-24): ephemeral wallet DisperseBlob without anchor_signature -> gRPC Internal(no reservation found) -- not an anchor error -- confirms TolerateMissingAnchorSignature=true in production.

**PoC References**: #10, #anchor-sig

## Mitigations

The anchor_signature mechanism exists but is non-enforced with default true. TODO: set to false and remove.
