# EDA-D03: Disperser V2 KZG Compute Surface Exposed Without Authentication or Prepayment

{% hint style="warning" %}
**Severity**: Medium (5.3/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Overview

Two specific gRPC surfaces on the Disperser V2 server expose computationally expensive KZG operations without requiring authentication or prepayment. The first is `GetBlobCommitment`, which directly calls `committer.GetCommitmentsForPaddedLength` without any auth or payment check. Its disable flag (`DisableGetBlobCommitment`) defaults to `false`, meaning the endpoint is exposed by default. A mainnet single-read probe confirmed that it returns an actual `BlobCommitmentReply` response.

The second surface is `DisperseBlob`, which recomputes the KZG commitment inside `validateDispersalRequest` before calling `AuthorizePayment`. This means a well-formed request with valid blob, header, and signature will consume CPU on KZG computation before payment is checked and potentially rejected. In contrast, `GetBlobStatus` burst requests hit a DynamoDB read path and are not relevant to this compute-exhaustion threat.

A local exact-path reproduction demonstrated that baseline KZG computation takes 1.77 seconds, and at concurrency 8, the p50 latency rises to 15.29 seconds with no throttling. Large-scale mainnet exploitability remains uncertain due to potential Cloudflare/WAF protections that have not been verified.

## Prerequisites

- Access to the Disperser gRPC endpoint (publicly reachable).
- For the `DisperseBlob` path, the attacker must construct a valid blob, header, and signature.

## Attack Scenario

1. The attacker identifies the publicly available Disperser V2 gRPC endpoint (confirmed via `grpcurl` listing V1, V2, Health, and Reflection services).
2. The attacker sends repeated `GetBlobCommitment` requests, each triggering a full KZG commitment computation (G1 + 2xG2 MSM, sequential all-core) without authentication.
3. Alternatively, the attacker constructs valid `DisperseBlob` requests that pass header validation and trigger KZG recomputation before being rejected at the payment stage.
4. The Disperser's CPU resources are exhausted, degrading service for legitimate users.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because this is a computing resource exhaustion issue with no financial impact. Attack Vector (AV) is Network since the gRPC endpoint is publicly accessible. Attack Complexity (AC) is High because mainnet WAF/CDN protection layers are presumed to exist but have not been verified, and the impact was only confirmed in a local PoC, making production-scale exploitability uncertain. Availability impact (A) is High because the unauthenticated KZG compute surface exposure is confirmed. Availability Infrastructure impact (AI) is Medium because actual service disruption at production infrastructure scale is unproven, and auto-scaling or replica capacity may absorb the load.

## Evidence

### Source Code

- [`disperser/apiserver/server_v2.go:230-233,286-310`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/server_v2.go#L230-L233) -- V2 unary interceptor only collects metrics; `GetBlobCommitment` calls `GetCommitmentsForPaddedLength` without auth or payment.
- [`disperser/cmd/apiserver/flags/flags.go:251-256`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go#L251-L256) -- `DisableGetBlobCommitment` defaults to `false`.
- [`encoding/v2/kzg/committer/committer.go:149-176`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/encoding/v2/kzg/committer/committer.go#L149-L176) -- G1 + 2xG2 MSM sequential all-core computation.
- [`disperser/apiserver/disperse_blob_v2.go:54,257,67`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L54) -- `validateDispersalRequest` performs KZG recomputation before `AuthorizePayment`.

### PoC Testing

- `grpcurl disperser.eigenda.xyz list` confirmed V1, V2, Health, and Reflection services are all publicly accessible.
- Single-request `GetBlobCommitment` probe returned a valid `BlobCommitmentReply` on mainnet.
- Local exact-path load test: baseline 1.77s, concurrency 8 p50 15.29s, no throttling observed. See [eigenda-kzg-dos-poc](https://github.com/jyo-o/eigenda-kzg-dos-poc).
- PoC #02's 100 parallel `GetBlobStatus` hits a cheap DynamoDB read path and is not relevant evidence for this threat.

**PoC References**: #20

## Mitigations

Payment is only enforced after `DisperseBlob` processing completes, and `GetBlobCommitment` has no payment check at all. Cloudflare or WAF may exist upstream of the Disperser, but application-layer rate thresholds have not been verified. Adding per-endpoint rate limiting or requiring authentication for `GetBlobCommitment` would close this surface.
