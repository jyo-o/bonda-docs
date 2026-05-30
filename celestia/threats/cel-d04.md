# CEL-D04: Three Code Defects in the Evidence Subsystem

{% hint style="info" %}
**Severity**: Low · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

Three independent code defects exist in celestia-core's evidence processing, though all have limited practical impact.

The first defect is a hash truncation bug: LightClientAttackEvidence.Hash() copies only 31 of 32 bytes due to an off-by-one error at evidence.go line 325. However, the probability of a collision on a 248-bit hash is effectively zero, so this has no security consequence.

The second defect is an unbounded consensus buffer: the consensusBuffer has no cap on entries. In theory a byzantine validator could flood it with conflicting votes. In practice, the buffer drains every block (approximately 6 seconds), and ed25519 signature verification is the CPU bottleneck at roughly 500-1000 verifications per second. This limits the buffer to about 3,000-6,000 entries (approximately 3 MB) within a drain cycle, making OOM impossible. The practical impact is minor CPU load.

The third defect is an evidence expiry gap: the evidence validity period (approximately 17 days based on max_age_num_blocks=242,640) exceeds the unbonding period (14 days) by about 3 days. This creates a window where evidence might be submitted after unbonding completes. However, double signs are almost always detected well within 14 days, and tombstoning is the primary penalty, making the 2% slashing avoidance during the gap practically meaningless.

## Prerequisites

- Buffer attack requires one validator but cannot cause OOM due to drain cycle and CPU bottleneck
- Expiry gap exploitation requires the unrealistic premise of no evidence submission for 14 days

## Attack Scenario

1. A byzantine validator sends a large volume of conflicting votes to inflate the consensusBuffer.
2. The buffer accepts entries without a cap, but drains every approximately 6 seconds.
3. CPU-bound ed25519 signature verification limits throughput to roughly 3,000-6,000 entries per drain cycle.
4. The buffer reaches approximately 3 MB before draining, far below OOM thresholds.
5. Separately, a validator could attempt to exploit the 3-day expiry gap by double signing and unbonding before evidence is submitted, but detection within 14 days is virtually certain.

## Impact

All three defects have negligible practical impact. The hash truncation is a one-character fix with no exploitability. The buffer cannot be inflated beyond approximately 3 MB. The expiry gap is theoretically exploitable but practically irrelevant due to near-certain detection within the unbonding period.

## Evidence

### Source Code

- `celestia-core/types/evidence.go:321-328` -- Hash() off-by-one: line 325 uses copy(bz[:tmhash.Size-1]) instead of tmhash.Size
- `celestia-core/evidence/pool.go:47,179-186,459-537` -- consensusBuffer with unbounded append and per-block drain
- `celestia-core/evidence/verify.go:308-316` -- IsEvidenceExpired uses AND logic for the two expiry conditions
- `celestia-core/consensus/state.go:2395` -- ErrVoteConflictingVotes handler

### On-Chain / Network

- Mainnet consensus parameters: max_age_num_blocks=242,640, max_age_duration=1,213,200s (337 hours), unbonding_time=1,213,200s
- 242,640 blocks at 6 seconds each equals approximately 404 hours (17 days), exceeding the 14-day unbonding period by about 3 days

## Mitigations

Recommended fixes include a one-character fix changing tmhash.Size-1 to tmhash.Size in evidence.go line 325, adding per-validator deduplication and a global cap (e.g., 1,000 pairs per height) to consensusBuffer, changing evidence expiry from AND to OR logic or setting MaxAgeNumBlocks shorter than unbonding, and adding a global evidence pool size cap.
