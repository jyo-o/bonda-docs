# EDA-D03: Disperser V2 KZG Compute Surface Exposed Without Authentication or Prepayment

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

Two gRPC surfaces on the Disperser V2 server expose computationally expensive KZG operations without requiring authentication or prepayment. `GetBlobCommitment` calls `committer.GetCommitmentsForPaddedLength` with no auth or payment check and is enabled by default. `DisperseBlob` recomputes the KZG commitment inside `validateDispersalRequest` before calling `AuthorizePayment`, consuming CPU before payment rejection. The root cause is missing pre-computation authentication gates. A local reproduction demonstrated baseline KZG computation at 1.77 seconds, rising to 15.29 seconds p50 at concurrency 8 with no throttling.

## Description

### Case #1: `GetBlobCommitment` Unauthenticated Compute

The V2 unary interceptor only collects metrics. `GetBlobCommitment` directly calls `GetCommitmentsForPaddedLength` without any auth or payment check.

**Source**: [`disperser/apiserver/server_v2.go:230-233,286-310`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/server_v2.go#L230-L233) -- V2 unary interceptor only collects metrics; `GetBlobCommitment` calls `GetCommitmentsForPaddedLength` without auth or payment.

The disable flag `DisableGetBlobCommitment` defaults to `false`, meaning the endpoint is exposed by default.

**Source**: [`disperser/cmd/apiserver/flags/flags.go:251-256`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go#L251-L256) -- `DisableGetBlobCommitment` defaults to `false`.

The underlying KZG computation performs G1 + 2xG2 MSM sequential all-core operations.

**Source**: [`encoding/v2/kzg/committer/committer.go:149-176`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/encoding/v2/kzg/committer/committer.go#L149-L176) -- G1 + 2xG2 MSM sequential all-core computation.

### Case #2: `DisperseBlob` Pre-Payment KZG Recomputation

`validateDispersalRequest` performs KZG recomputation before `AuthorizePayment` is called. A well-formed request with valid blob, header, and signature consumes CPU on KZG computation before payment is checked and potentially rejected.

**Source**: [`disperser/apiserver/disperse_blob_v2.go:54,257,67`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L54) -- `validateDispersalRequest` performs KZG recomputation before `AuthorizePayment`.

Note: `GetBlobStatus` burst requests hit a DynamoDB read path and are not relevant to this compute-exhaustion threat.

## Proof of Concept

### Reproduction

- `grpcurl disperser.eigenda.xyz list` confirmed V1, V2, Health, and Reflection services are all publicly accessible.
- Single-request `GetBlobCommitment` probe returned a valid `BlobCommitmentReply` on mainnet.

### Results

- Local exact-path load test: baseline 1.77s, concurrency 8 p50 15.29s, no throttling observed.
- PoC repository: [eigenda-kzg-dos-poc](https://github.com/jyo-o/eigenda-kzg-dos-poc).
- PoC #02's 100 parallel `GetBlobStatus` hits a cheap DynamoDB read path and is not relevant evidence for this threat.

**PoC References**: #20

## Impact

An attacker can exhaust the Disperser's CPU resources by sending repeated `GetBlobCommitment` or crafted `DisperseBlob` requests, each triggering full KZG commitment computations (G1 + 2xG2 MSM) without authentication. The local PoC demonstrated an 8.6x latency increase at concurrency 8 with no throttling. No authentication is required for `GetBlobCommitment`. For `DisperseBlob`, the attacker must construct a valid blob, header, and signature, but CPU is consumed before payment rejection. Large-scale mainnet exploitability remains uncertain due to potential Cloudflare/WAF protections that have not been verified.

### CVSS 3.1

**Score**: 5.9/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | The gRPC endpoint is publicly accessible |
| AC (Attack Complexity) | H (High) | Mainnet WAF/CDN protection layers are presumed to exist but have not been verified; impact was only confirmed in a local PoC, making production-scale exploitability uncertain |
| PR (Privileges Required) | N (None) | No authentication required for `GetBlobCommitment`; `DisperseBlob` requires a valid blob but no payment |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the Disperser service |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | N (None) | No data integrity impact |
| A (Availability) | H (High) | Unauthenticated KZG compute surface exposure confirmed; 8.6x latency increase demonstrated at concurrency 8 |

## Recommendation

1. Add per-endpoint rate limiting on `GetBlobCommitment` to prevent compute exhaustion.
2. Require lightweight authentication (API key or similar) for `GetBlobCommitment` access.
3. Reorder the `DisperseBlob` flow to call `AuthorizePayment` before `validateDispersalRequest` to prevent pre-payment KZG computation.
4. Set `DisableGetBlobCommitment` to `true` by default if the endpoint is not required for normal client operations.
