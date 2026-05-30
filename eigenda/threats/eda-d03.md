# EDA-D03: Disperser V2 KZG Compute Surface Exposed Without Authentication or Prepayment

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

Two gRPC surfaces on the Disperser V2 server expose computationally expensive KZG operations without requiring authentication or prepayment. `GetBlobCommitment` calls `committer.GetCommitmentsForPaddedLength` with no auth or payment check and is enabled by default. `DisperseBlob` recomputes the KZG commitment inside `validateDispersalRequest` before calling `AuthorizePayment`, consuming CPU before payment rejection. The root cause is missing pre-computation authentication gates. A local reproduction demonstrated baseline KZG computation at 1.77 seconds, rising to 15.29 seconds p50 at concurrency 8 with no throttling.

## Description

### Case #1: `GetBlobCommitment` Unauthenticated Compute

The V2 gRPC server registers only a metrics interceptor in its unary chain. There is no authentication or authorization middleware:

```go
// disperser/apiserver/server_v2.go:230-233
// @audit V2 unary interceptor only collects metrics — no auth check
s.grpcServer = grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        s.metrics.grpcMetrics.UnaryServerInterceptor(),
    ), opt, keepAliveConfig)
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/server_v2.go#L230-L233
```

`GetBlobCommitment` directly calls `GetCommitmentsForPaddedLength` without any auth or payment check. The `disableGetBlobCommitment` flag can gate the endpoint, but it defaults to `false`:

```go
// disperser/apiserver/server_v2.go:286-310
// @audit GetBlobCommitment calls committer without auth or payment check
func (s *DispersalServerV2) getBlobCommitment(
    req *pb.BlobCommitmentRequest,
) (*pb.BlobCommitmentReply, *status.Status) {
    // ...
    if s.disableGetBlobCommitment {
        return nil, status.New(codes.Unimplemented, "GetBlobCommitment is deprecated...")
    }
    // No auth check before calling committer
    c, err := s.committer.GetCommitmentsForPaddedLength(req.GetBlob())
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/server_v2.go#L286-L310
```

The disable flag definition confirms its default value is `false`, meaning the endpoint is exposed by default:

```go
// disperser/cmd/apiserver/flags/flags.go:251-256
// @audit DisableGetBlobCommitment defaults to false — endpoint enabled by default
DisableGetBlobCommitment = cli.BoolFlag{
    Name:     common.PrefixFlag(FlagPrefix, "disable-get-blob-commitment"),
    Usage:    "If true, the GetBlobCommitment gRPC endpoint will return a deprecation error.",
    Required: false,
    EnvVar:   common.PrefixEnvVar(envVarPrefix, "DISABLE_GET_BLOB_COMMITMENT"),
}
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/cmd/apiserver/flags/flags.go#L251-L256
```

The underlying KZG computation performs G1 + 2xG2 MSM sequential all-core operations. All three commitments are computed sequentially, and each individual computation already saturates all CPU cores:

```go
// encoding/v2/kzg/committer/committer.go:149-176
// @audit G1 + 2xG2 MSM — each computation saturates all cores
// We compute all 3 commitments sequentially, since each individual computation
// already saturates all cores by default.
commit, err := c.computeCommitmentV2(inputFr)
lengthCommitment, err := c.computeLengthCommitmentV2(inputFr)
lenProof, err := c.computeLengthProofV2(inputFr)
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/encoding/v2/kzg/committer/committer.go#L149-L176
```

### Case #2: `DisperseBlob` Pre-Payment KZG Recomputation

In the `DisperseBlob` flow, `validateDispersalRequest` is called before `AuthorizePayment`. The validation function internally calls `GetCommitmentsForPaddedLength`, meaning the full KZG computation runs before the server ever checks whether the caller has paid:

```go
// disperser/apiserver/disperse_blob_v2.go:54-67
// @audit KZG commitment computed in validateDispersalRequest BEFORE AuthorizePayment
blobHeader, err := s.validateDispersalRequest(req, onchainState)
// ...
_, err = s.controllerClient.AuthorizePayment(ctx, authorizePaymentRequest)
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L54
```

Inside `validateDispersalRequest`, the KZG recomputation is triggered:

```go
// disperser/apiserver/disperse_blob_v2.go:257
// @audit Full KZG recomputation inside validation — runs before payment check
commitments, err := s.committer.GetCommitmentsForPaddedLength(blob)
// https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/apiserver/disperse_blob_v2.go#L257
```

A well-formed request with valid blob, header, and signature consumes CPU on KZG computation before payment is checked and potentially rejected.

Note: `GetBlobStatus` burst requests hit a DynamoDB read path and are not relevant to this compute-exhaustion threat.

## Proof of Concept

Exploitation testing was conducted against the `GetBlobCommitment` and `DisperseBlob` endpoints. Detailed reproduction steps and measurements will be added upon completion of the vulnerability report.

- Mainnet V2 Disperser endpoints confirmed publicly accessible via `grpcurl`
- Local load test demonstrated KZG computation latency degradation under concurrent requests
- inabox environment test confirmed CPU exhaustion from a single attacker

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
