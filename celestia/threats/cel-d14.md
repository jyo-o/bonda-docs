# CEL-D14: TxCache Bypass Forcing Full Commitment Recomputation in ProcessProposal

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

During `ProcessProposal`, a malicious proposer can include blob transactions that did not pass through other validators' `CheckTx`, forcing non-proposer validators to perform full NMT commitment computation. However, the practical impact is limited by the data square size constraint (maximum approximately 8 MiB per block) and parallelized computation, making the actual CPU overhead minor.

## Description

The `TxCache` optimization in `ProcessProposal` allows skipping commitment recomputation for blob transactions that already passed `CheckTx`:

```go
// celestia-app/app/process_proposal.go
// @audit ValidateBlobTxWithCache: cache miss triggers full ValidateBlobTx
// @audit A malicious proposer includes txs not in other validators' TxCache
```

```go
// celestia-app/app/check_tx.go
// @audit handleBlobCheckTx calls txCache.Set on successful CheckTx
// @audit Only transactions that pass CheckTx are cached
```

The original concern was that `MaxPFBMessages=200` maximum-size PFBs could force 1.6 GiB of computation. However, this is impossible because total block data is bounded by the square size:

```go
// celestia-app/pkg/appconsts/app_consts.go
// @audit MaxPFBMessages=200, but total data bounded by square size
// @audit ODS 128 → maximum ~8 MiB per block, not 200 * 8 MiB
```

Commitment computation is parallelized across `runtime.NumCPU()*2` workers, completing the 8 MiB computation in approximately hundreds of milliseconds. The threat represents a real asymmetry between proposer and validator workloads, but the square size constraint and parallel computation make the actual CPU overhead negligible.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Minor additional CPU load on non-proposer validators during `ProcessProposal`. The square size constraint prevents the computation from becoming a meaningful burden, and the parallelized commitment computation handles 8 MiB in sub-second time.

### CVSS 3.1

**Score**: 3.7/10 (Low)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Malicious proposals are broadcast over the consensus network |
| AC (Attack Complexity) | H (High) | Requires the attacker to be selected as block proposer (probabilistic, proportional to stake) |
| PR (Privileges Required) | N (None) | Minimum stake is required to be a validator, but the threshold is low |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to non-proposer validators' CPU during ProcessProposal |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | The proposer can introduce transactions that bypass the normal mempool validation path |
| A (Availability) | N (None) | Sub-second computation overhead does not meaningfully affect availability |

## Recommendation

1. Limit the ratio of uncached transactions allowed in `ProcessProposal` to bound the worst-case recomputation burden.
2. Enforce a timeout on commitment computation within `ProcessProposal` to prevent any single block from consuming excessive CPU.
3. Add lightweight pre-verification for `TxCache` misses to detect and reject obviously invalid transactions before full commitment computation.
