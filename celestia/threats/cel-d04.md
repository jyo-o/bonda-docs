# CEL-D04: Evidence Subsystem Three Code Defects (Hash Truncation / Buffer Unbounded / Expiry Gap)

{% hint style="info" %}
**Severity**: Low · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

Three independent defects exist in celestia-core evidence processing, though practical impact is limited. First, LightClientAttackEvidence.Hash() copies only 31 of 32 bytes, but the probability of a 248-bit hash collision is effectively 0. Second, consensusBuffer has no cap, but it drains every block (~6 seconds) and ed25519 signature verification is the CPU bottleneck (~500-1000/sec), limiting entries to ~3,000-6,000 (~3 MB) within 6 seconds -- OOM is impossible. Practical impact is minor CPU load. Third, the evidence validity period (~17 days) exceeds unbonding (14 days) by ~3 days, but double signs are almost certainly detected within 14 days and tombstoning is the primary penalty, making the 2% slashing avoidance practically meaningless.

## Core Invariants Affected

`consensus_liveness`, `signing_liveness`

Claims that consensusBuffer OOM could crash consensus nodes exist, but this is impossible due to 6-second drain + CPU bottleneck.

## Prerequisites

Buffer attack can be attempted with 1 validator but cannot cause OOM. Expiry gap exploitation requires the unrealistic premise of no evidence submission for 14 days.

## Attack Scenario

**Condition**: Byzantine validator mass-sending conflicting votes still drains at ~3 MB/block level

**Example**: Mainnet: evidence.max_age_num_blocks=242,640, max_age_duration=1213200s (337h), unbonding_time=1213200s. 242640x6s ~ 404h > 337h, so ~17 days vs 14 days.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Low |
| Likelihood | Unrealistic (OOM impossible: 6-second drain + CPU bottleneck. Probability of non-detection within 14 days ~0) |
| Scope | protocol |
| Target | Process |
| Core Invariants | consensus_liveness, signing_liveness |

## Code References

- [`celestia-core/types/evidence.go:321-328 (Hash() off-by-one, line 325 copy(bz[:tmhash.Size-1]))`](https://github.com/celestiaorg/celestia-core/blob/main/types/evidence.go#L321-L328)
- [`celestia-core/evidence/pool.go:47,179-186,459-537 (consensusBuffer unbounded append + drain)`](https://github.com/celestiaorg/celestia-core/blob/main/evidence/pool.go:47,179-186,459-537)
- [`celestia-core/evidence/verify.go:308-316 (IsEvidenceExpired AND logic)`](https://github.com/celestiaorg/celestia-core/blob/main/evidence/verify.go#L308-L316)
- [`celestia-core/consensus/state.go:2395 (ErrVoteConflictingVotes 핸들러)`](https://github.com/celestiaorg/celestia-core/blob/main/consensus/state.go#L2395)
- On-chain: `cosmos/consensus/v1beta1/params (max_age_num_blocks=242640, max_age_duration=1213200s)`

## Verification & Evidence

**Status**: code_verified

Full code audit completed. Evidence/consensus parameters confirmed via mainnet RPC. All three defects have limited practical impact.

## Mitigations

Recommendations: 1-char fix for evidence.go:325 (tmhash.Size-1 to tmhash.Size), add per-validator dedup + global cap (e.g., 1000 pairs/height) to consensusBuffer, change evidence expiry from AND to OR logic or set MaxAgeNumBlocks shorter than unbonding, add global evidence pool size cap.
