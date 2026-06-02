# EDA-02: Disperser V2 KZG Compute Surface Exposed Without Authentication or Prepayment

{% hint style="warning" %}
**Severity**: High (8.6/10) · **Likelihood**: Very High · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

Two gRPC surfaces on the Disperser V2 server expose computationally expensive KZG operations without requiring authentication or prepayment. `GetBlobCommitment` calls `committer.GetCommitmentsForPaddedLength` with no auth or payment check and is enabled by default. `DisperseBlob` recomputes the KZG commitment inside `validateDispersalRequest` before calling `AuthorizePayment`, consuming CPU before payment rejection. The root cause is missing pre-computation authentication gates. A single 16 MiB blob sent to `GetBlobCommitment` drives roughly 1.15 seconds of wall time and about 14 core-seconds of KZG work, and the endpoint was confirmed live and anonymously callable across every operational environment.

## Description

![EDA-02 data flow — EigenDA Dispersal path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/eigenda/assets/dfd/eigenda-dispersal.png)

*Data flow — EigenDA Dispersal: Disperser.*

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

In both flows the gRPC request context is not propagated into the KZG computation, so a client-side deadline or cancellation does not stop the server-side work once it has begun. The server commits the full G1 + 2xG2 MSM even when the caller disconnects.

Note: `GetBlobStatus` burst requests hit a DynamoDB read path and are not relevant to this compute-exhaustion threat.

## Proof of Concept

The `GetBlobCommitment` endpoint was confirmed live and anonymously callable across every operational environment using `grpcurl` with no credentials:

- Mainnet (`disperser.eigenda.xyz:443`)
- Testnet-Sepolia
- Testnet-Hoodi
- Preprod-Hoodi-v2

A single 16 MiB blob submitted to `GetBlobCommitment` drives roughly 1.15 seconds of wall-clock time and about 14 core-seconds of KZG work on the Disperser, since the G1 commitment, length commitment, and length proof are each computed sequentially and each saturates all available cores.

The gRPC request context is not propagated into `GetCommitmentsForPaddedLength`, so a short client deadline or an early disconnect does not abort the server-side computation. Front-tier protections such as Cloudflare do not mitigate this: the requests are well-formed and individually inexpensive to issue, and the cost asymmetry is algorithmic rather than volumetric, so rate-based or signature-based WAF rules do not block it.

See [Verification Evidence](../evidence.md#getblobcommitment-unauthenticated-compute-eda-02) for the full reproduction environment, commands, and measurements.

## Impact

An attacker can exhaust the Disperser's CPU resources by sending repeated `GetBlobCommitment` or crafted `DisperseBlob` requests, each triggering full KZG commitment computations (G1 + 2xG2 MSM) without authentication. A single 16 MiB `GetBlobCommitment` call costs about 14 core-seconds of work and roughly 1.15 seconds of wall time, so a small number of concurrent callers saturates every core on the Disperser and stalls legitimate dispersals. No authentication is required for `GetBlobCommitment`, and the endpoint is enabled by default. For `DisperseBlob`, the attacker must construct a valid blob, header, and signature, but the KZG work is consumed before payment rejection. Because the cost asymmetry is algorithmic and the request context is not propagated to the computation, neither WAF/CDN filtering nor client-side timeouts curb the load.

Affects the **Liveness** axis, where it produces a Layer 3 deduction while unpatched.

### CVSS 3.1

**Score**: 8.6/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | The gRPC endpoint is publicly accessible and confirmed callable on Mainnet |
| AC (Attack Complexity) | L (Low) | Requests are well-formed and individually cheap to issue; the cost asymmetry is algorithmic, so WAF/CDN layers do not block it and no special conditions are required |
| PR (Privileges Required) | N (None) | No authentication required for `GetBlobCommitment`; `DisperseBlob` requires a valid blob but no payment |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | C (Changed) | CPU exhaustion on the shared Disperser degrades dispersal availability for all other tenants of the service |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | N (None) | No data integrity impact |
| A (Availability) | H (High) | A single 16 MiB request consumes ~14 core-seconds; a few concurrent callers saturate all cores and stall legitimate dispersals |

## Recommendation

1. Add per-endpoint rate limiting on `GetBlobCommitment` to prevent compute exhaustion.
2. Require lightweight authentication (API key or similar) for `GetBlobCommitment` access.
3. Reorder the `DisperseBlob` flow to call `AuthorizePayment` before `validateDispersalRequest` to prevent pre-payment KZG computation.
4. Set `DisableGetBlobCommitment` to `true` by default if the endpoint is not required for normal client operations.
