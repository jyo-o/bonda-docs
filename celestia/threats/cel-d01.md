# CEL-D01: Zero-cost Prevote-nil Censorship by 1/3 Cartel

{% hint style="info" %}
**Severity**: Informational · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: verified
{% endhint %}

## Overview

A cartel controlling 1/3 of voting power can permanently censor targeted block proposals by sending nil votes at the prevote stage indefinitely. When the 2/3 threshold is not met, nil precommit followed by round timeout and proposer rotation repeats, leaving the targeted block permanently unfinalized. The slashing penalty is 0 TIA, and cartel members can avoid jail by signing just 10/10,000 blocks (min_signed_per_window=0.001, downtime_jail_duration=60s). The absence of a nil-vote evidence type makes it impossible to distinguish honest from malicious nil votes.

## Core Invariants Affected

`consensus_liveness`

1/3 withholding signatures (prevote-nil) blocks targeted block finalization = targeted denial of consensus liveness.

## Prerequisites

Control of at least 1/3 of active bonded validators. Technical cost is 0 TIA (no slashing); the only opportunity cost is block rewards lost during the 60-second jail period.

## Attack Scenario

**Condition**: 1/3 voting power collusion + slash_fraction_downtime=0 (active on mainnet)

**Example**: Mainnet (2026-05-20, height 11,172,730): slash_fraction_downtime=0, min_signed_per_window=0.001, signed_blocks_window=10000, downtime_jail_duration=60s.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Informational |
| Likelihood | Unrealistic (requires collusion of top 8 institutional validators with no economic incentive) |
| Scope | protocol |
| Target | Process |
| Core Invariants | consensus_liveness |

## Code References

- [`celestia-core/types/evidence.go:22-219 (Evidence 구현체 2종만, nil-vote evidence 부재)`](https://github.com/celestiaorg/celestia-core/blob/main/types/evidence.go#L22-L219)
- [`celestia-core/consensus/state.go:1553-1577 (정직/악의 prevote-nil 동일 호출)`](https://github.com/celestiaorg/celestia-core/blob/main/consensus/state.go#L1553-L1577)
- [`celestia-core/consensus/state.go:1711-1722 (round timeout)`](https://github.com/celestiaorg/celestia-core/blob/main/consensus/state.go#L1711-L1722)
- [`celestia-app/app/default_overrides.go:113-122 (슬래싱 기본값)`](https://github.com/celestiaorg/celestia-app/blob/main/app/default_overrides.go#L113-L122)
- On-chain: `cosmos/slashing/v1beta1/params (slash_fraction_downtime=0, min_signed_per_window=0.001)`
- [PR #7090: 2026-04-17 MERGED, 'to match mainnet governance'](https://github.com/celestiaorg/celestia-app/pull/7090)

## Verification & Evidence

**Status**: verified

Phase 1 gap analysis. Slashing parameters cross-source verified against mainnet REST (celestia-rest.publicnode.com). Code file:line independently re-verified.

## Mitigations

Currently only slash_fraction_double_sign=0.02 is active; prevote-nil is not a double sign and therefore not penalized. Recommendations: (1) Introduce nil-vote evidence type (consensus-breaking), (2) Set slash_fraction_downtime>0 via governance, (3) Explore correlation penalty, (4) Surface censorship pattern monitoring.
