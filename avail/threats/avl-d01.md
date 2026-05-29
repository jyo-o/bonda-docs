# AVL-D01: VectorX Single Relayer SPOF -- No Code-Level Rate Limit/Heartbeat

{% hint style="info" %}
**Severity**: Medium (6.6/10) · **STRIDE**: D · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX relayer operates as a single EOA (0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D). nonce=2632, balance=0.82 ETH, code=0x (EOA). checkRelayer=true, approvedRelayers has only this EOA set to true. Code-level verification: SP1Vector.sol commitHeaderRange() has zero block.timestamp references, no cooldown/rate limit/heartbeat/timeout logic (full inheritance chain checked). operator.rs uses LOOP_INTERVAL_MINS=60, BLOCK_UPDATE_INTERVAL=360, PROOF_TIMEOUT_SECS=1800 for client-side interval control only -- no onchain enforcement. setRelayerApproval() emits no events (asymmetric with removeHeaderHash which has HeaderHashRemoved event). Previous relayer 0x3243...2D has approvedRelayers=false (rotation history confirmed). Avg relay interval: 120min, batch size: 358 blocks, gas per commit: 458,612. latestBlock=2975481, headerRangeCommitmentTreeSize=2048, latestAuthoritySetId=753.

## Prerequisites

Relayer EOA failure or key compromise -- natural failure alone can trigger this. No onchain staleness detection mechanism.

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 6.6/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | Process, ExternalEntity |

### BVSS Rationale

B:N -- No direct financial impact. AV:N -- Network level (DDoS, key compromise). AC:L -- Single point of failure; natural failure alone triggers this; zero onchain rate limit/heartbeat (code confirmed). PR:N -- External attacker capable. S:U -- Impact within bridge scope. A:H -- DA attestation bridge completely halted (commitHeaderRange calls impossible). AI:M -- Avail chain data itself remains accessible but unverifiable on Ethereum (verifiable availability lost). No relayer replacement/fallback mechanism.

## Code References


### Onchain Evidence

- `code 0x27BF...=0x(EOA)`
- `nonce=2632`
- `balance=0.82ETH`
- `approvedRelayers(0x27BF...)=true`
- `checkRelayer=true`
- `latestBlock=2975481`

### PoC Notes

- poc_onchain_verification.md §2 §14
- poc/avl_d01_relayer_spof_poc.sh(Anvil fork PoC 3 tests)

### Other References

- github.com/availproject/sp1-vector SP1Vector.sol — commitHeaderRange()에 block.timestamp/cooldown/rate limit 0건
- github.com/availproject/sp1-vector operator.rs — LOOP_INTERVAL_MINS=60 BLOCK_UPDATE_INTERVAL=360(클라이언트 제어)
- L2BEAT: avail — No mechanism to propose new relayers

## Verification & Evidence

**Status**: Verified

cast confirmed EOA/nonce/balance/approvedRelayers. SP1Vector.sol source code: commitHeaderRange() has zero rate limit/heartbeat/timeout (full inheritance chain). operator.rs LOOP_INTERVAL_MINS=60 confirmed (no onchain enforcement). setRelayerApproval event absence confirmed. Anvil mainnet fork PoC: (1) single relayer access control (2) staleness detection absence (3) guardian ZK bypass (intended mechanism). Previous relayer 0x3243...2D rotation history confirmed.

**PoC References**: onchain-§2, onchain-§14, anvil-poc-3tests

## Mitigations

None -- no relayer replacement mechanism (confirmed by L2BEAT). No onchain heartbeat/timeout. Observability is also limited (setRelayerApproval emits no events).
