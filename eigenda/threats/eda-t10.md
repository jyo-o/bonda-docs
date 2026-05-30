# EDA-T10: Attestation Overwrite Without Integrity Guard in DynamoDB

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: T · **Status**: Partially Verified
{% endhint %}

## Summary

The `PutAttestation` function in the Disperser controller performs an unconditional `PutItem` to DynamoDB without a `ConditionExpression`, explicitly allowing attestation overwrites. This is inconsistent with sibling functions `PutBlobMetadata` and `PutBatch` which use `attribute_not_exists` guards. The root cause is a missing conditional write guard on the attestation store. However, standalone attestation tampering cannot produce a valid DACert because on-chain `checkDACert` performs five-stage verification including BLS pairing, Merkle inclusion, and stake snapshot checks.

## Description

The inconsistency exists at the data store layer:

**Source**: [`disperser/common/v2/blobstore/dynamo_metadata_store.go:1168-1177`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/common/v2/blobstore/dynamo_metadata_store.go#L1168-L1177) -- `PutAttestation` performs unconditional `PutItem` with comment "Allow overwrite of existing attestation."

The controller's workflow creates a timing vulnerability:

**Source**: [`disperser/controller/controller.go:315-333,410-423`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/controller/controller.go#L315-L333) -- Controller writes empty attestation first (line 315), ignores put failure as non-fatal (line 327 with comment "this error isn't fatal"), then writes final signed attestation (line 419).

This creates a racing window between the initial empty write and the final signed write.

However, on-chain verification blocks all known tampering scenarios:

**Source**: [`contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol:82-122`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L82-L122) -- `checkDACert` performs 5-stage verification: BLS pairing, Merkle inclusion, stake snapshot at 55%, and quorum subset checks.

The `signedStake` value is computed from the on-chain `StakeRegistry`, not from the attestation, so attestation tampering cannot forge valid stake data. All tested tampering scenarios (a through f, h) result in revert.

The residual attack surface is limited to a composite scenario: IAM credential theft (or concurrent write contention) combined with the client skipping on-chain verification.

## Proof of Concept

### Reproduction

- PoC #28 (attestation-onchain-detect) verified the code inconsistency.
- Security impact is bounded by on-chain `checkDACert` which blocks tampering scenarios a-f and h.
- `signedStake` is computed from on-chain `StakeRegistry`, not from the attestation.

**PoC References**: #28

## Impact

An attacker with AWS IAM credentials granting DynamoDB write access could overwrite attestations during the racing window between the initial empty write and the final signed write. However, the impact is severely bounded: on-chain `checkDACert` verification via the mainnet router (`0x61692e93b6B045c444e942A91EcD1527F23A3FB7`) catches all known tampering scenarios through BLS pairing, Merkle inclusion, stake snapshot, and quorum subset checks. Only clients that skip on-chain verification would be affected. The attack requires both internal AWS access and client misconfiguration, making it a low-probability composite scenario.

### CVSS 3.1

**Score**: 1.8/10 (Low)
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | P (Physical) | Requires internal AWS write access to the Disperser's DynamoDB infrastructure |
| AC (Attack Complexity) | H (High) | Both the racing window timing and client skipping on-chain verification must coincide |
| PR (Privileges Required) | L (Low) | AWS IAM credentials with DynamoDB write access are needed |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the attestation storage layer |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | L (Low) | Attestation overwrite is possible, but on-chain `checkDACert` serves as the primary defense and catches all known tampering scenarios |
| A (Availability) | N (None) | No availability impact |

## Recommendation

1. Add a `ConditionExpression` with `attribute_not_exists` to `PutAttestation` to match the behavior of `PutBlobMetadata` and `PutBatch`.
2. Treat the put failure at `controller.go:327` as a batch failure rather than ignoring it, to close the racing window.
3. Implement a state machine guard on attestation writes to enforce the expected lifecycle transitions.
