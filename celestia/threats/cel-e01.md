# CEL-E01: SP1Blobstream 4-of-6 Multisig — Instant Upgrade Without Timelock

{% hint style="info" %}
**Severity**: Critical · **STRIDE**: E (Elevation of Privilege) · **Scope**: bridge · **Status**: verified
{% endhint %}

## Overview

SP1Blobstream's guardian, used by L2 rollups as a finality signal, is a 4-of-6 Gnosis Safe (0x8bF34D8df1eF0A8A7f27fC587202848E528018E6) where GUARDIAN, TIMELOCK, and DEFAULT_ADMIN roles are all concentrated on the same multisig (confirmed via 3 on-chain hasRole() calls and RoleGranted events at block 20027685). Root cause: initialize() passes the same address to both _timelock and _guardian via __TimelockedUpgradeable_init(guardian, guardian). Verifier/program vkey replacement functions lack timelock, events, and review windows, allowing instant upgrade with 4 signer consensus in a single transaction. Additionally, ProofOutputs lacks chain-id enabling cross-deployment proof reuse, and updateGenesisState lacks height monotonicity enforcement enabling stale validator set rollback. As of 2026-05-24 on Etherscan, all 12,109 contract transactions are commitHeaderRange (relayer) calls, with 0 internal transactions and 0 verifyAttestation calls -- no L2 uses SP1Blobstream for DA verification on-chain. Molten Network/Rari Chain SequencerInbox's BLOBSTREAM() getter returns 0xa8973B... which has bytecode 0 (dead pointer, confirmed on Arbiscan).

## Core Invariants Affected

L1 bridge trust issue. Outside Celestia DA consensus/signing/recovery invariants. No immediate impact due to zero L2 usage, but critical if adoption increases.

## Prerequisites

Compromise or coercion of 4 of 6 signers. No immediate impact currently, but blast radius increases dramatically if Blobstream adoption expands.

## Attack Scenario

**Condition**: 4-of-6 multisig signer compromise + currently no L2 using Blobstream DA bridge, limiting immediate impact

**Example**: Ethereum mainnet proxy 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe, guardian=0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 (4-of-6 Gnosis Safe v1.3.0, singleton 0xd9db...9552), VERSION 1.1.0, checkRelayer true, nonce 11. 6 signer EOAs: 0x0449...56a9, 0x7939...E899, 0x1358...7caf, 0x4587...1b0, 0x4983...cE4d, 0x91D4...e15.

## Impact

| Metric | Value |
|--------|-------|
| Severity | Critical |
| Likelihood | Conditional (compromise or coercion of 4-of-6 multisig signers) |
| Scope | bridge |
| Target | Process, ExternalEntity |

## Code References

- [`sp1-blobstream/contracts/src/SP1Blobstream.sol:107-120 (updateGenesisState no monotonicity, updateVerifier/updateProgramVkey onlyGuardian no event/timelock)`](https://github.com/succinctlabs/sp1-blobstream/blob/main/contracts/src/SP1Blobstream.sol#L107-L120)
- [`sp1-blobstream/contracts/src/SP1Blobstream.sol:65-72 (ProofOutputs no chain_id)`](https://github.com/succinctlabs/sp1-blobstream/blob/main/contracts/src/SP1Blobstream.sol#L65-L72)
- [`sp1-blobstream/contracts/src/SP1Blobstream.sol:89 (initialize(guardian,guardian) → 3역할 동일)`](https://github.com/succinctlabs/sp1-blobstream/blob/main/contracts/src/SP1Blobstream.sol#L89)
- On-chain: `eth_call hasRole(DEFAULT_ADMIN_ROLE, 0x8bF3...)=true (block latest)`
- On-chain: `eth_call hasRole(TIMELOCK_ROLE, 0x8bF3...)=true`
- On-chain: `eth_call hasRole(GUARDIAN_ROLE, 0x8bF3...)=true`
- On-chain: `RoleGranted events block 20027685 (3역할 동시 부여, RoleRevoked 0건)`
- On-chain: `eth_call getThreshold()=4 getOwners()=6 on 0x8bF3...18E6`
- On-chain: `Etherscan 0x7Cf3... tx history (12,109 tx, 전부 commitHeaderRange, internal tx 0건, verifyAttestation 0건)`
- On-chain: `Arbiscan Molten/Rari SequencerInbox BLOBSTREAM()→0xa8973B... bytecode=0x (dead pointer)`

## Verification & Evidence

**Status**: verified

Phase 2 pen-test (P3) + primary source on-chain verification: (1) eth_call hasRole() 3x confirmed same address holds all 3 roles, (2) getThreshold()=4, getOwners()=6 EOAs confirmed, (3) RoleGranted at block 20027685 with 3 roles granted simultaneously, 0 RoleRevoked events, (4) All 12,109 tx are commitHeaderRange, 0 internal tx confirming 0 L2 DA verification usage, (5) Molten/Rari BLOBSTREAM() dead pointer confirmed. Multisig address corrected from prior report error (0xBaB2c...126, 38 hex chars) to actual 0x8bF34D8...18E6.

## Mitigations

Recommendations: (1) Route updateVerifier/updateProgramVkey through separate TIMELOCK role with MIN_DELAY + add events, (2) Add require(_height>latestBlock) to updateGenesisState, (3) Add chain_id+genesis_hash to ProofOutputs, (4) Separate GUARDIAN (freeze) and TIMELOCK (upgrade) roles.
