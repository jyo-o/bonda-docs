# CEL-D01: Zero-cost Prevote-nil Censorship by One-third Cartel

{% hint style="info" %}
**Severity**: Medium (4.2/10) · **STRIDE**: D · **Status**: verified
{% endhint %}

## Summary

Celestia uses Tendermint-based BFT consensus where a cartel controlling at least one-third of voting power can permanently censor targeted block proposals by casting prevote-nil at zero on-chain cost. The root cause is the absence of a nil-vote evidence type in the evidence subsystem, making it impossible to distinguish honest nil votes from malicious censorship. While considered unrealistic due to the coordination required among top institutional validators, the protocol lacks any mechanism to detect or penalize this behavior.

## Description

The censorship mechanism exploits the two-thirds prevote threshold required for block finalization:

```go
// celestia-core/types/evidence.go:22-219
// @audit Only two evidence types are implemented
// @audit No nil-vote evidence type exists — protocol cannot distinguish honest vs malicious nil votes
```

```go
// celestia-core/consensus/state.go:1553-1577
// @audit Honest and malicious prevote-nil follow the same code path
// @audit No differentiation between "didn't receive proposal" and "intentionally nil-voting"
```

```go
// celestia-core/consensus/state.go:1711-1722
// @audit Round timeout logic: when two-thirds is not met, nil precommits are produced
// @audit Proposer rotates, but cartel can repeat nil-voting on any proposer's block
```

The slashing penalty for this behavior is zero TIA:

```go
// celestia-app/app/default_overrides.go:113-122
// @audit Slashing default values — prevote-nil is not classified as a double sign
```

Mainnet slashing parameters (2026-05-20, height 11,172,730) confirmed via `celestia-rest.publicnode.com/cosmos/slashing/v1beta1/params`:
- `slash_fraction_downtime=0`
- `min_signed_per_window=0.001`
- `signed_blocks_window=10000`
- `downtime_jail_duration=60s`

Cartel members can avoid jail by signing as few as 10 out of 10,000 blocks (0.1%). PR `celestia-app#7090` (merged 2026-04-17) changed these defaults "to match mainnet governance."

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Targeted block censorship with zero on-chain cost. The attack is considered unrealistic because it requires collusion among the top 8 institutional validators (35.77% of voting power) with no economic incentive to do so. However, the protocol lacks any mechanism to detect or penalize this behavior if it were to occur. Currently only `slash_fraction_double_sign=0.02` is active; prevote-nil is not classified as a double sign and therefore carries no penalty.

### CVSS 3.1

**Score**: 4.2/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Censorship is executed via network-level prevote-nil messages |
| AC (Attack Complexity) | H (High) | Requires coordinating a cartel of top validators controlling one-third of voting power |
| PR (Privileges Required) | L (Low) | Requires being an active bonded validator (staked position) |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to Celestia's consensus layer |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | Targeted transactions are excluded from blocks, but no data is corrupted |
| A (Availability) | L (Low) | Targeted blocks are delayed but the chain continues producing other blocks |

## Recommendation

1. Introduce a nil-vote evidence type in the evidence subsystem to enable detection of systematic nil-voting patterns (consensus-breaking change).
2. Set `slash_fraction_downtime` above zero via governance to create at least minimal cost for nil-voting behavior.
3. Explore a correlation penalty mechanism that increases slashing for coordinated nil-voting by multiple validators.
4. Build monitoring tools to surface censorship patterns (e.g., repeated nil-vote concentrations on specific proposers or transactions) for on-chain visibility.
