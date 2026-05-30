# EDA-T10: Attestation Overwrite Without Integrity Guard in DynamoDB

{% hint style="info" %}
**Severity**: Low (1.3/10) · **STRIDE**: T · **Status**: Partially Verified
{% endhint %}

## Overview

The `PutAttestation` function used by the Disperser controller to store attestations in DynamoDB performs an unconditional `PutItem` without a `ConditionExpression` (such as `attribute_not_exists`). The code explicitly comments "Allow overwrite of existing attestation." This is inconsistent with sibling functions in the same data store: both `PutBlobMetadata` and `PutBatch` use `attribute_not_exists` guards to prevent overwrites.

The controller's workflow creates a timing vulnerability. It first writes an empty attestation at line 315, then gathers signatures from operators and writes the final attestation at line 419. A put failure at line 327 is ignored with the comment "this error isn't fatal," creating a racing window between the initial empty write and the final signed write.

However, standalone attestation tampering cannot produce a valid DACert. The on-chain `checkDACert` function in `EigenDACertVerificationLib.sol` performs five-stage verification including BLS pairing, Merkle inclusion, stake snapshot at 55%, and quorum subset checks. The `signedStake` value is computed from the on-chain `StakeRegistry`, not from the attestation, so attestation tampering cannot forge valid stake data. All tested tampering scenarios (a through f, h) result in revert.

The residual attack surface is limited to a composite scenario: IAM credential theft (or concurrent write contention) combined with the client skipping on-chain verification.

## Prerequisites

- AWS IAM credential theft granting DynamoDB write access to the Disperser's attestation table, or concurrent write contention during the racing window.
- Additionally, the client must skip on-chain `checkDACert` verification for the tampered attestation to have any effect.

## Attack Scenario

1. An attacker obtains AWS IAM credentials with write access to the Disperser's DynamoDB tables.
2. The attacker monitors the controller's attestation lifecycle and identifies the racing window between the initial empty attestation write and the final signed write.
3. The attacker overwrites the attestation with tampered data using the unconditional `PutItem` operation.
4. If a client retrieves the tampered attestation without performing on-chain `checkDACert` verification, it may accept invalid data availability claims.
5. Clients that properly verify certificates on-chain are not affected, as `checkDACert` will reject the tampered attestation.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.3/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:M/A:N/CI:N/II:M/AI:N` |
| Scope | Bridge |

### Scoring Rationale

Blockchain Impact (B) is None because there is no financial impact from this defense-in-depth flaw. Attack Vector (AV) is Physical because the attacker needs internal AWS write access to the Disperser's infrastructure. Attack Complexity (AC) is High because both the racing window timing and client skipping on-chain verification must coincide. Integrity impact (I) is Medium because attestation overwrite is possible, but Integrity Infrastructure impact (II) is also Medium because the on-chain `checkDACert` serves as the primary defense line and catches all known tampering scenarios.

## Evidence

### Source Code

- [`disperser/common/v2/blobstore/dynamo_metadata_store.go:1168-1177`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/common/v2/blobstore/dynamo_metadata_store.go#L1168-L1177) -- `PutAttestation` performs unconditional `PutItem` with "Allow overwrite" comment.
- [`disperser/controller/controller.go:315-333,410-423`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/controller/controller.go#L315-L333) -- Controller writes empty attestation first, ignores put failure as non-fatal, then writes final attestation.
- [`contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol:82-122`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L82-L122) -- `checkDACert` performs 5-stage verification (BLS pairing, Merkle inclusion, stake snapshot, quorum subset).

### PoC Testing

- PoC #28 (attestation-onchain-detect) verified the code inconsistency.
- Security impact is bounded by on-chain `checkDACert` which blocks tampering scenarios a-f and h.
- `signedStake` is computed from on-chain `StakeRegistry`, not from the attestation, rendering attestation tampering ineffective for stake forgery.

**PoC References**: #28

## Mitigations

The primary defense is on-chain `checkDACert` verification via the mainnet router (`0x61692e93b6B045c444e942A91EcD1527F23A3FB7`), which performs BLS pairing, Merkle inclusion, stake snapshot, and quorum subset checks. To close the defense-in-depth gap, `PutAttestation` should add a `ConditionExpression` with `attribute_not_exists` (or a state machine guard), and the put failure at `controller.go:327` should be treated as a batch failure rather than ignored.
