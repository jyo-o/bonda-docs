# EDA-D03: Disperser V2 KZG Compute Surface Exposed Without Auth/Prepayment

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

The core issue is two specific surfaces that actually burn KZG compute, not V2 gRPC in general. GetBlobCommitment calls committer.GetCommitmentsForPaddedLength directly without auth/payment, and its disable flag defaults to false, making it exposed by default. A mainnet single read probe confirmed an actual BlobCommitmentReply response. DisperseBlob also recomputes KZG commitment in validateDispersalRequest before calling AuthorizePayment, so a well-formed request with valid blob/header/signature consumes CPU before reservation/payment rejection. In contrast, GetBlobStatus bursts are DynamoDB read paths and are not directly relevant to this threat.

## Prerequisites

Access to Disperser gRPC endpoint. The DisperseBlob path requires constructing valid blob/header/signature.

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process |

### BVSS Rationale

B:N -- No financial impact; computing resource exhaustion. AV:N -- Public gRPC. AC:H -- Mainnet WAF/CDN protection layer presumed (unverified); impact confirmed only in local PoC, production-scale exploitability uncertain. A:H -- Unauthenticated KZG compute surface exposure confirmed. AI:M -- Actual service disruption level at production infrastructure scale unproven; auto-scaling/replica possible.

## Code References

### Source Code

- [`disperser/apiserver/server_v2.go:230-233`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/server_v2.go#L230-L233)
- [`disperser/cmd/apiserver/flags/flags.go:251-256`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go#L251-L256) -- DisableGetBlobCommitment 기본 false
- [`encoding/v2/kzg/committer/committer.go:149-176`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/encoding/v2/kzg/committer/committer.go#L149-L176) -- G1+2xG2 MSM sequential all-core
- [`disperser/apiserver/disperse_blob_v2.go:54`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L54)

### PoC Notes

- grpcurl disperser.eigenda.xyz list → V1+V2+Health+Reflection all public
- grpcurl GetBlobCommitment 단건 응답 확인 [VERIFIED live probe]

### Other References

- 286-310 — V2 unary interceptor는 metrics only
- GetBlobCommitment는 auth/payment 없이 GetCommitmentsForPaddedLength 호출
- 257
- 67 — validateDispersalRequest 내 KZG 재계산 후 AuthorizePayment 호출
- [https://github.com/jyo-o/eigenda-kzg-dos-poc — local exact-path load baseline 1.77s → C=8 p50 15.29s](https://github.com/jyo-o/eigenda-kzg-dos-poc — local exact-path load baseline 1.77s → C=8 p50 15.29s)
- throttle 없음

## Verification & Evidence

**Status**: Verified

PoC #02's 100 parallel GetBlobStatus is a cheap read path and inadequate as direct evidence. Instead, mainnet read-only probe confirmed reflection + GetBlobCommitment live response. Local exact-path reproduction showed baseline 1.77s -> C=8 p50 15.29s. Large-scale mainnet exploitability remains unverified due to Cloudflare/WAF.

**PoC References**: #20

## Mitigations

Payment is only enforced after DisperseBlob processing, not on GetBlobCommitment. Cloudflare/WAF may exist upstream but app-layer thresholds are unverified.
