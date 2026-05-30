# EDA-S03: Cross-Chain Signature Replay Due to Non-Enforced Anchor Signature

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: S · **Status**: Verified
{% endhint %}

## Summary

The EigenDA Disperser accepts dispersal requests without anchor signatures on mainnet. The `TolerateMissingAnchorSignature` flag defaults to `true`, meaning the server tolerates missing anchor signatures by default.

The root cause is that the anchor signature mechanism, introduced following the Sigma Prime audit (EDA2-02 Critical, EDA2-11 Medium, EDA2-18 Medium, all resolved), remains non-enforced in production. An attacker could replay a valid dispersal request from one chain on a different chain or EigenDA deployment, bypassing the chain-binding protection that anchor signatures are designed to provide.

## Description

The anchor signature non-enforcement exists at two independent layers.

**Server configuration** -- The Disperser has two relevant flags. `TolerateMissingAnchorSignature` defaults to `true`, allowing requests that omit the anchor signature to proceed without error. `DisableAnchorSignatureVerification` defaults to `false`.

```go
// disperser/server_config.go
// @audit TolerateMissingAnchorSignature defaults to true
// TODO (litt3): this field should eventually be set to false, and then removed,
// once all clients have updated to a version that includes anchor signatures.
TolerateMissingAnchorSignature bool

// @audit DisableAnchorSignatureVerification defaults to false
DisableAnchorSignatureVerification bool
```

The anchor validation function reflects this layered bypass. When `DisableAnchorSignatureVerification` is true, all verification is skipped entirely. When the anchor signature is missing but `TolerateMissingAnchorSignature` is true, the request proceeds silently.

```go
// disperser/apiserver/disperse_blob_v2.go:280-300
// @audit Anchor validation can be entirely skipped or tolerate missing signatures
func (s *DispersalServerV2) validateAnchorSignature(
    req *pb.DisperseBlobRequest,
    blobHeader *corev2.BlobHeader,
) error {
    if s.serverConfig.DisableAnchorSignatureVerification {
        return nil
    }
    anchorSignature := req.GetAnchorSignature()
    if len(anchorSignature) == 0 {
        if s.serverConfig.TolerateMissingAnchorSignature {
            return nil
        }
        return errors.New("anchor signature is required but not provided")
    }
}
```

**Protocol buffer definition** -- The proto definition itself permits omission of the anchor signature field because proto3 makes all fields implicit-optional.

```protobuf
// api/proto/disperser/v2/disperser_v2.proto:68-81
// @audit anchor_signature (field 5) is implicit-optional — proto3 allows omission
bytes anchor_signature = 5;
uint32 disperser_id = 6;
bytes chain_id = 7;
```

No anchor-related errors appear in proxy operation logs, consistent with the tolerate mode being active in production.

### Audit References

- Sigma Prime EDA2-02 (Critical, Resolved), EDA2-11 (Medium, Resolved), EDA2-18 (Medium, Resolved).

## Proof of Concept

A live test was conducted on 2026-05-24 against the mainnet Disperser.

An ephemeral wallet sent a `DisperseBlob` request without an anchor signature. The server responded with `gRPC Internal (no reservation found)`, which is a payment-related rejection, not an anchor verification error. This confirms that `TolerateMissingAnchorSignature=true` is active in the production Disperser.

## Impact

Cross-chain replay is possible because the chain-binding protection that anchor signatures provide is not enforced. An attacker can capture a valid dispersal request from one chain and replay it on a different chain or EigenDA deployment. The request will not be rejected for missing anchor data, as confirmed by live testing.

However, on-chain BLS verification still applies as a secondary defense layer, and the attacker needs a valid ECDSA signature for the dispersal request. Payment validation may also block the replayed request if no reservation exists on the target chain.

### CVSS 3.1

**Score**: 3.5/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Dispersal requests are submitted over the network |
| AC (Attack Complexity) | H (High) | An ECDSA signature is required and the anchor signature mechanism itself exists, just not enforced by default |
| PR (Privileges Required) | L (Low) | A valid signature is needed for dispersal requests |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | C (Changed) | Cross-chain replay is possible, affecting systems beyond the original chain |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | L (Low) | Anchor signature is not enforced, but on-chain BLS verification remains active as a secondary defense |
| A (Availability) | N (None) | No availability impact from replay |

## Recommendation

1. Set `TolerateMissingAnchorSignature` to `false` in the production Disperser configuration to enforce anchor signatures.
2. Remove both `TolerateMissingAnchorSignature` and `DisableAnchorSignatureVerification` flags once the anchor signature mechanism is fully stabilized, as indicated by the TODO comment in the codebase.
3. Change the proto definition to make `anchor_signature` a required field in future protocol versions.
