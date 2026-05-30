# CEL-D04: Three Code Defects in the Evidence Subsystem

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

Three independent code defects exist in celestia-core's evidence processing: a hash truncation off-by-one error, an unbounded consensus buffer, and an evidence expiry gap exceeding the unbonding period. All three have negligible practical impact due to collision probability, CPU bottlenecks, and near-certain detection timelines respectively.

## Description

**Case #1: Hash Truncation Off-by-One**

```go
// celestia-core/types/evidence.go:321-328
// @audit Hash() off-by-one: line 325 uses copy(bz[:tmhash.Size-1]) instead of tmhash.Size
// @audit Copies only 31 of 32 bytes from LightClientAttackEvidence
// @audit Collision probability on 248-bit hash is effectively zero — no security consequence
```

**Case #2: Unbounded Consensus Buffer**

```go
// celestia-core/evidence/pool.go:47,179-186,459-537
// @audit consensusBuffer has no cap on entries — unbounded append
// @audit However, buffer drains every block (~6 seconds)
// @audit ed25519 signature verification is CPU bottleneck: ~500-1000 verifications/sec
// @audit This limits buffer to ~3,000-6,000 entries (~3 MB) per drain cycle — OOM impossible
```

```go
// celestia-core/consensus/state.go:2395
// @audit ErrVoteConflictingVotes handler feeds the consensusBuffer
```

**Case #3: Evidence Expiry Gap**

```go
// celestia-core/evidence/verify.go:308-316
// @audit IsEvidenceExpired uses AND logic for two expiry conditions
// @audit max_age_num_blocks=242,640 → ~17 days (at 6s/block)
// @audit unbonding_time=1,213,200s → 14 days
// @audit Gap of ~3 days where evidence might be submitted after unbonding completes
```

Mainnet consensus parameters confirm: `max_age_num_blocks=242,640`, `max_age_duration=1,213,200s` (337 hours), `unbonding_time=1,213,200s`. The 242,640 blocks at 6 seconds each equals approximately 404 hours (17 days), exceeding the 14-day unbonding period by about 3 days. However, double signs are almost always detected well within 14 days, and tombstoning is the primary penalty, making the 2% slashing avoidance during the gap practically meaningless.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

All three defects have negligible practical impact. The hash truncation is a one-character fix with no exploitability. The buffer cannot be inflated beyond approximately 3 MB due to the drain cycle and CPU bottleneck. The expiry gap is theoretically exploitable but practically irrelevant due to near-certain detection within the unbonding period.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Evidence and votes are submitted over the network |
| AC (Attack Complexity) | H (High) | Buffer attack is bounded by CPU; expiry gap requires 14-day undetected double sign (extremely unlikely) |
| PR (Privileges Required) | N (None) | Buffer flooding requires a byzantine validator, but the hash/expiry defects need no privileges |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the evidence processing subsystem |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | The expiry gap theoretically allows a validator to avoid 2% slashing, a minor integrity impact |
| A (Availability) | N (None) | Buffer cannot cause OOM; no availability impact |

## Recommendation

1. Apply the one-character fix changing `tmhash.Size-1` to `tmhash.Size` in `evidence.go` line 325 to correct the hash truncation.
2. Add per-validator deduplication and a global cap (e.g., 1,000 pairs per height) to `consensusBuffer` as a defense-in-depth measure.
3. Change evidence expiry from AND to OR logic, or set `MaxAgeNumBlocks` shorter than the unbonding period, to close the 3-day expiry gap.
4. Add a global evidence pool size cap to prevent future unbounded growth scenarios.
