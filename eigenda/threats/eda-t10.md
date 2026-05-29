# EDA-T10: PutAttestation Unconditional Overwrite -- Attestation Integrity Guard Absent (Defense-in-Depth Flaw)

{% hint style="info" %}
**Severity**: Low (1.3/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Partially Verified
{% endhint %}

## Overview

The PutAttestation used by disperser/controller to store attestations in DynamoDB performs an unconditional PutItem without ConditionExpression (attribute_not_exists) -- code comment reads 'Allow overwrite of existing attestation'. This is inconsistent with sibling functions in the same store (PutBlobMetadata, PutBatch) which use attribute_not_exists guards. The controller first writes an empty attestation (line 315), then gathers signatures and writes the final version (line 419); the put failure at line 327 is ignored as 'this error isn't fatal', creating a racing window. Standalone tampering cannot create a valid DACert (onchain checkDACert blocks it; see verification_note). The effective threat is limited to a composite scenario requiring IAM credential theft (or concurrent write contention) combined with the client skipping onchain verification.

## Prerequisites

AWS IAM credential theft (or concurrent write contention) + client skipping onchain verification

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.3/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:M/A:N/CI:N/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | Datastore |

### BVSS Rationale

B:N -- No financial impact. AV:P -- Requires disperser AWS internal write access. AC:H -- Racing window timing + client skipping onchain verification must both be met. I:M/II:M -- Attestation overwrite possible but onchain checkDACert is primary defense.

## Code References

### Source Code

- [`disperser/common/v2/blobstore/dynamo_metadata_store.go:1168-1177`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/common/v2/blobstore/dynamo_metadata_store.go#L1168-L1177) -- PutAttestation 'Allow overwrite' 무조건 PutItem
- [`disperser/controller/controller.go:315-333`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/disperser/controller/controller.go#L315-L333)
- [`contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol:82-122`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L82-L122) -- checkDACert 5단계 검증

### PoC Notes

- #28 attestation-onchain-detect

### Other References

- 410-423 — 빈 attestation→final put
- 327 non-fatal

## Verification & Evidence

**Status**: Partially Verified

Code finding (PutAttestation unconditional overwrite inconsistency) verified from primary source. Security impact is bounded by onchain checkDACert (BLS pairing + Merkle inclusion + stake snapshot 55% + quorum subset, EigenDACertVerificationLib.sol:82-122) -- tampering scenarios a-f,h all revert. signedStake is computed from onchain StakeRegistry, not attestation, so tampering is ineffective. Residual attack surface is limited to (g) IAM theft + client skipping onchain verification composite scenario and the racing window exposure.

**PoC References**: #28

## Mitigations

Add ConditionExpression (attribute_not_exists) or state machine guard to PutAttestation; treat put failure at controller.go:327 as batch fail. Primary defense is onchain checkDACert via mainnet router (0x61692e93b6B045c444e942A91EcD1527F23A3FB7).
