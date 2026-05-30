# CEL-E01: SP1Blobstream Instant Upgrade via Unprotected 4-of-6 Multisig

{% hint style="warning" %}
**Severity**: High (7.7/10) · **STRIDE**: E · **Status**: verified
{% endhint %}

## Summary

SP1Blobstream's on-chain bridge contract assigns all three critical access control roles (GUARDIAN, TIMELOCK, DEFAULT_ADMIN) to a single 4-of-6 Gnosis Safe multisig, enabling instant replacement of proof verification logic without any timelock delay or event emission. The root cause is the `initialize` function passing the same address for both `_timelock` and `_guardian` parameters. If four signers are compromised, the bridge's ZK proof verification can be silently replaced, enabling acceptance of arbitrary fraudulent DA commitments by any dependent L2 rollup.

## Description

The SP1Blobstream contract at `sp1-blobstream/contracts/src/SP1Blobstream.sol` contains multiple access control and structural defects:

**Case #1: Role Concentration**

```solidity
// sp1-blobstream/contracts/src/SP1Blobstream.sol:89
// @audit initialize(guardian, guardian) assigns all three roles to the same address
initialize(_guardian, _guardian);
```

On-chain `hasRole()` calls confirm that `DEFAULT_ADMIN_ROLE`, `TIMELOCK_ROLE`, and `GUARDIAN_ROLE` are all held by the Gnosis Safe at `0x8bF34D8df1eF0A8A7f27fC587202848E528018E6` (threshold=4, owners=6). All three `RoleGranted` events were emitted simultaneously at block 20027685 with zero subsequent `RoleRevoked` events.

**Case #2: Missing Timelock on Critical Functions**

```solidity
// sp1-blobstream/contracts/src/SP1Blobstream.sol:107-120
// @audit updateVerifier and updateProgramVkey are gated only by onlyGuardian
// @audit No timelock delay, no emitted events, no review window
function updateVerifier(address _verifier) external onlyGuardian { ... }
function updateProgramVkey(bytes32 _vkey) external onlyGuardian { ... }
```

**Case #3: Missing Height Monotonicity**

`updateGenesisState` at line 107 has no `require(_height > latestBlock)` check, enabling validator set rollback to stale states.

**Case #4: Missing Cross-Deployment Isolation**

```solidity
// sp1-blobstream/contracts/src/SP1Blobstream.sol:65-72
// @audit ProofOutputs struct lacks chain_id field, enabling cross-deployment proof reuse
struct ProofOutputs { ... }
```

As of 2026-05-24, the bridge has zero actual users. All 12,109 contract transactions on Etherscan are `commitHeaderRange` calls from the relayer, with zero internal transactions and zero `verifyAttestation` calls. Molten Network and Rari Chain's `SequencerInbox` contracts point to a dead address (bytecode `0x`) for their `BLOBSTREAM` getter.

## Proof of Concept

On-chain verification was conducted:

- `eth_call hasRole(DEFAULT_ADMIN_ROLE, 0x8bF3...18E6)` returns `true`
- `eth_call hasRole(TIMELOCK_ROLE, 0x8bF3...18E6)` returns `true`
- `eth_call hasRole(GUARDIAN_ROLE, 0x8bF3...18E6)` returns `true`
- `RoleGranted` events at block 20027685: all three roles granted simultaneously, zero `RoleRevoked` events
- `eth_call getThreshold()=4`, `getOwners()=6` on the Gnosis Safe at `0x8bF3...18E6`
- Etherscan proxy at `0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe`: 12,109 transactions, all `commitHeaderRange`, zero internal transactions, zero `verifyAttestation` calls
- Arbiscan Molten/Rari `SequencerInbox BLOBSTREAM()` returns `0xa8973B...` with bytecode `0x` (dead pointer)
- Six signer EOAs: `0x0449...56a9`, `0x7939...E899`, `0x1358...7caf`, `0x4587...1b0`, `0x4983...cE4d`, `0x91D4...e15`

## Impact

Complete compromise of the Blobstream DA bridge, enabling arbitrary proof acceptance and fraudulent DA commitments. The attack is instantaneous with no window for detection or response due to the lack of timelock. Currently mitigated by zero L2 adoption, but the impact becomes catastrophic if rollups begin using the bridge for finality signals. The blast radius scales linearly with adoption.

### CVSS 3.1

**Score**: 7.7/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack is executed via on-chain multisig transactions over the network |
| AC (Attack Complexity) | H (High) | Requires compromising or coercing 4 of 6 independent multisig signers |
| PR (Privileges Required) | H (High) | Attacker must control 4 multisig signer keys (privileged role) |
| UI (User Interaction) | N (None) | No user interaction required once signer keys are obtained |
| S (Scope) | C (Changed) | Compromise of the bridge affects all dependent L2 rollups (different trust boundary) |
| C (Confidentiality) | N (None) | No confidentiality impact; attack targets integrity and availability of DA commitments |
| I (Integrity) | H (High) | Arbitrary proof acceptance enables fraudulent DA commitments |
| A (Availability) | H (High) | Validator set rollback and verifier replacement can halt bridge functionality |

## Recommendation

1. Route `updateVerifier` and `updateProgramVkey` through a separate `TIMELOCK` role with a minimum delay (e.g., 48 hours) and add event emission for all state-changing operations.
2. Add `require(_height > latestBlock)` to `updateGenesisState` to enforce height monotonicity and prevent validator set rollback.
3. Add `chain_id` and `genesis_hash` fields to the `ProofOutputs` struct to prevent cross-deployment proof reuse.
4. Separate the `GUARDIAN` role (for freeze/emergency operations) from the `TIMELOCK` role (for upgrades and parameter changes).
