# AVL-T04: Guardian updateBlockRangeData() -- Arbitrary Commitment Injection Without ZK Proof (Intended Emergency Mechanism)

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

SP1Vector.sol's updateBlockRangeData() function allows GUARDIAN_ROLE holders to directly inject arbitrary data/state commitments without ZK proof verification. Normal path: relayer -> commitHeaderRange() -> SP1 ZK proof verification -> commitment stored. Guardian path: multisig -> updateBlockRangeData() -> commitment stored directly without proof. This is an intended emergency recovery mechanism. Additional Guardian capabilities: updateVerifier(), updateVectorXProgramVkey(), updateGenesisState(). GUARDIAN_ROLE = Multisig 1 (4/7).

## Prerequisites

GUARDIAN_ROLE holder (Multisig 1, 4/7 key compromise)

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 1.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:N/I:H/A:N/CI:N/II:M/AI:N` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | DataStore, Process |

### BVSS Rationale

B:N -- No direct financial impact. AV:P -- 4/7 multisig key compromise required. AC:H -- 4/7 multisig required. PR:R -- GUARDIAN_ROLE required. S:U -- Within commitment storage scope. I:H/II:M -- ZK bypass possible but intended emergency mechanism with 4/7 multisig protection.

## Code References


### PoC Notes

- 소스코드 분석
- poc/avl_d01_relayer_spof_poc.sh PoC-3(의도된 동작 확인)

### Other References

- github.com/availproject/sp1-vector SP1Vector.sol — updateBlockRangeData()
- GUARDIAN_ROLE로 proof 없이 commitment 직접 주입

## Verification & Evidence

**Status**: Verified

SP1Vector.sol source code: updateBlockRangeData() stores commitments directly without ZK proof verification confirmed. Anvil fork PoC-3 confirmed guardian ZK bypass behavior -- this is an intended emergency recovery mechanism.

**PoC References**: source-SP1Vector, anvil-poc-3

## Mitigations

GUARDIAN_ROLE = Multisig 1 (4/7). Designed for emergency recovery. Intended mechanism.
