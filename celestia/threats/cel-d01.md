# CEL-D01: Zero-cost Prevote-nil Censorship by One-third Cartel

{% hint style="success" %}
**Severity**: Informational · **STRIDE**: D · **Status**: verified
{% endhint %}

## Overview

Celestia uses Tendermint-based BFT consensus where a block is finalized only when it receives prevotes from more than two-thirds of voting power. If a cartel controls at least one-third of voting power, it can permanently censor targeted block proposals by casting nil votes at the prevote stage indefinitely.

When the two-thirds threshold is not met, the round produces nil precommits, triggers a timeout, and rotates to the next proposer. This cycle repeats endlessly, leaving the targeted block permanently unfinalized. The slashing penalty for this behavior is zero TIA because prevote-nil is not classified as a double sign. Cartel members can avoid jail by signing as few as 10 out of 10,000 blocks, since min_signed_per_window is set to 0.001 and downtime_jail_duration is only 60 seconds.

The root cause is the absence of a nil-vote evidence type in the evidence subsystem. The protocol cannot distinguish between honest nil votes (e.g., a validator that genuinely did not receive the proposal) and malicious nil votes cast for censorship purposes.

## Prerequisites

- Control of at least one-third of active bonded validators' voting power
- Technical cost is zero TIA due to no slashing for downtime
- Opportunity cost is limited to block rewards lost during the 60-second jail period

## Attack Scenario

1. A cartel of validators controlling at least one-third of voting power identifies a target block proposal to censor.
2. When the target block is proposed, all cartel members send prevote-nil instead of prevoting for the block.
3. The block fails to reach the two-thirds prevote threshold, resulting in nil precommits.
4. A round timeout occurs and the proposer rotates to the next validator.
5. If the new proposer re-proposes the same transactions, the cartel repeats nil voting.
6. The targeted block remains permanently unfinalized while the cartel members avoid jail by occasionally signing other blocks (10 out of 10,000 is sufficient).

## Impact

Targeted block censorship with zero on-chain cost. The attack is considered unrealistic because it requires collusion among the top 8 institutional validators with no economic incentive to do so. However, the protocol lacks any mechanism to detect or penalize this behavior if it were to occur.

## Evidence

### Source Code

- `celestia-core/types/evidence.go:22-219` -- only two evidence types are implemented; no nil-vote evidence type exists
- `celestia-core/consensus/state.go:1553-1577` -- honest and malicious prevote-nil follow the same code path
- `celestia-core/consensus/state.go:1711-1722` -- round timeout logic
- `celestia-app/app/default_overrides.go:113-122` -- slashing default values

### On-Chain / Network

- Mainnet slashing parameters (2026-05-20, height 11,172,730): slash_fraction_downtime=0, min_signed_per_window=0.001, signed_blocks_window=10000, downtime_jail_duration=60s
- Source: `celestia-rest.publicnode.com/cosmos/slashing/v1beta1/params`
- PR celestia-app#7090 (merged 2026-04-17): changed defaults "to match mainnet governance"

## Mitigations

Currently only slash_fraction_double_sign=0.02 is active. Prevote-nil is not classified as a double sign and therefore carries no penalty.

Recommended fixes include introducing a nil-vote evidence type (consensus-breaking change), setting slash_fraction_downtime above zero via governance, exploring a correlation penalty mechanism, and building monitoring tools to surface censorship patterns on-chain.
