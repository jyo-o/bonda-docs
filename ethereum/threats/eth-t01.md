# ETH-T01: Blob Fee Denominator Fork-Dependent Formula

{% hint style="info" %}
**Severity**: Low (0.8/10) · **STRIDE**: T (Tampering) · **Status**: code_verified
{% endhint %}

## Overview

The blob fee calculation in Ethereum uses a fork-dependent denominator (`updateFraction`) that changes across protocol upgrades. In the BPO2 fork, this value is set to 11,684,671. If a client implementation applies the wrong denominator for a given fork, blob fee calculations will diverge from consensus, potentially causing the node to reject valid blocks or accept invalid ones.

This is primarily a correctness concern rather than an active exploit vector. The risk lies in implementation errors during fork transitions where developers might use the wrong constant for the active fork. Such a mismatch would cause the affected node to fall out of consensus with the rest of the network.

The threat is well-covered by the existing consensus-spec-tests suite, which validates fee calculations across all fork boundaries. This test coverage significantly reduces the likelihood of a denominator mismatch reaching production.

## Prerequisites

- A client implementation bug that applies the wrong `updateFraction` for the active fork
- The bug must survive the consensus-spec-tests validation pipeline

## Attack Scenario

1. A client developer introduces or modifies blob fee calculation code during a fork upgrade.
2. The implementation incorrectly references the `updateFraction` from a previous or future fork instead of the currently active one.
3. Nodes running the buggy client compute different blob base fees than the rest of the network.
4. Affected nodes reject valid blocks or accept invalid ones, causing a consensus split among clients running the faulty version.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.8/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:L/II:L/A:N/AI:N` |
| Scope | protocol |

### Scoring Rationale

The attack complexity is high because exploiting this requires an implementation bug that would need to bypass comprehensive test suites. No privileges or user interaction are required for the mismatch to occur, but the scenario is a passive implementation defect rather than an actively exploitable vulnerability. Integrity impact is low at both node and chain levels since fee miscalculations would be detected quickly by consensus divergence. Availability and confidentiality are unaffected.

## Evidence

### Source Code

- **Component**: Blob fee calculation logic across execution layer clients
- **Finding**: The `updateFraction` constant is set to 11,684,671 in BPO2. Different forks use different values, and the code path must correctly select the denominator based on the active fork.

## Mitigations

The consensus-spec-tests suite provides comprehensive coverage for fork-specific fee calculation formulas. Each client implementation is validated against these reference tests before release. The deterministic nature of the fee calculation means any mismatch is immediately detectable through consensus divergence monitoring. Client teams maintain fork-aware test cases that explicitly verify denominator values at fork boundaries.
