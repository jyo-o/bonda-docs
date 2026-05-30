# CEL-E01: SP1Blobstream Instant Upgrade via Unprotected 4-of-6 Multisig

{% hint style="danger" %}
**Severity**: Critical · **STRIDE**: E · **Status**: verified
{% endhint %}

## Overview

SP1Blobstream is the on-chain bridge contract that L2 rollups can use as a finality signal for Celestia DA commitments. Its guardian is a 4-of-6 Gnosis Safe multisig at address 0x8bF34D8df1eF0A8A7f27fC587202848E528018E6. Three critical access control roles -- GUARDIAN, TIMELOCK, and DEFAULT_ADMIN -- are all assigned to this same multisig, confirmed via on-chain hasRole() calls and RoleGranted events at block 20027685. The root cause is the initialize function passing the same address for both _timelock and _guardian parameters.

The verifier and program verification key replacement functions (updateVerifier, updateProgramVkey) are gated only by onlyGuardian with no timelock delay, no emitted events, and no review window. If four of the six signers are compromised or coerced, a single transaction can silently replace the proof verification logic. Additionally, ProofOutputs lacks a chain-id field, enabling cross-deployment proof reuse, and updateGenesisState lacks height monotonicity enforcement, enabling validator set rollback.

As of 2026-05-24, the bridge has zero actual users. All 12,109 contract transactions on Etherscan are commitHeaderRange calls from the relayer, with zero internal transactions and zero verifyAttestation calls. Molten Network and Rari Chain's SequencerInbox contracts point to a dead address (bytecode 0x) for their BLOBSTREAM getter. The immediate blast radius is therefore zero, but the risk becomes critical if adoption increases.

## Prerequisites

- Compromise or coercion of 4 out of 6 multisig signers
- No immediate on-chain impact due to zero L2 usage, but blast radius grows with adoption

## Attack Scenario

1. An attacker compromises or coerces 4 of the 6 Gnosis Safe signers through key theft, social engineering, or legal pressure.
2. The attacker submits a multisig transaction calling updateVerifier to replace the ZK proof verifier with a malicious contract that accepts arbitrary proofs.
3. The transaction executes immediately with no timelock delay and emits no event, making detection difficult.
4. Optionally, the attacker calls updateProgramVkey to change the verification key, or updateGenesisState to roll back to a stale validator set.
5. The attacker can now submit fabricated DA commitments that the bridge will accept as valid.
6. Any L2 rollup relying on SP1Blobstream for finality would accept fraudulent state transitions.

## Impact

Complete compromise of the Blobstream DA bridge, enabling arbitrary proof acceptance and fraudulent DA commitments. Currently mitigated by zero L2 adoption, but the impact would be catastrophic if rollups begin using the bridge for finality signals. The lack of timelock means the attack is instantaneous with no window for detection or response.

## Evidence

### Source Code

- `sp1-blobstream/contracts/src/SP1Blobstream.sol:107-120` -- updateGenesisState has no height monotonicity check; updateVerifier and updateProgramVkey are onlyGuardian with no timelock or events
- `sp1-blobstream/contracts/src/SP1Blobstream.sol:65-72` -- ProofOutputs struct lacks chain_id field
- `sp1-blobstream/contracts/src/SP1Blobstream.sol:89` -- initialize(guardian, guardian) assigns all three roles to the same address

### On-Chain / Network

- eth_call hasRole(DEFAULT_ADMIN_ROLE, 0x8bF3...18E6) returns true
- eth_call hasRole(TIMELOCK_ROLE, 0x8bF3...18E6) returns true
- eth_call hasRole(GUARDIAN_ROLE, 0x8bF3...18E6) returns true
- RoleGranted events at block 20027685: all three roles granted simultaneously, zero RoleRevoked events
- eth_call getThreshold()=4, getOwners()=6 on the Gnosis Safe at 0x8bF3...18E6
- Etherscan proxy at 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe: 12,109 transactions, all commitHeaderRange, zero internal transactions, zero verifyAttestation calls
- Arbiscan Molten/Rari SequencerInbox BLOBSTREAM() returns 0xa8973B... with bytecode 0x (dead pointer)
- Six signer EOAs: 0x0449...56a9, 0x7939...E899, 0x1358...7caf, 0x4587...1b0, 0x4983...cE4d, 0x91D4...e15

## Mitigations

Recommended fixes include routing updateVerifier and updateProgramVkey through a separate TIMELOCK role with a minimum delay and adding event emission, adding require(_height > latestBlock) to updateGenesisState for height monotonicity, adding chain_id and genesis_hash fields to ProofOutputs to prevent cross-deployment proof reuse, and separating the GUARDIAN role (for freeze operations) from the TIMELOCK role (for upgrades).
