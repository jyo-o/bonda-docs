# ETH-T01: Blob Fee Denominator Fork-Dependent Formula

{% hint style="info" %}
**Severity**: Low (3.7/10) · **STRIDE**: T (Tampering) · **Status**: code_verified
{% endhint %}

## Summary

The blob fee calculation in Ethereum uses a fork-dependent denominator (`updateFraction`) that changes across protocol upgrades. If a client implementation applies the wrong denominator for a given fork, blob fee calculations diverge from consensus, causing the node to reject valid blocks or accept invalid ones. This is a correctness concern mitigated by comprehensive consensus-spec-tests coverage.

## Description

The `updateFraction` constant is set to 11,684,671 in BPO2. Different forks use different values, and the code path must correctly select the denominator based on the active fork.

```
# @audit — fork-dependent denominator must match active fork
# Blob fee = f(excess_blob_gas, updateFraction)
# BPO2: updateFraction = 11,684,671
# Each fork defines its own updateFraction value.
# Using the wrong fork's constant causes consensus divergence.
```

The risk lies in implementation errors during fork transitions where developers might reference the `updateFraction` from a previous or future fork instead of the currently active one. Such a mismatch would cause the affected node to fall out of consensus with the rest of the network. The threat is a passive implementation defect rather than an actively exploitable vulnerability.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Nodes running a buggy client would compute different blob base fees than the rest of the network, resulting in a consensus split among clients running the faulty version. Fee miscalculations would be detected quickly by consensus divergence monitoring. The deterministic nature of the fee calculation means any mismatch is immediately detectable.

### CVSS 3.1
**Score**: 3.7/10 (Low)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Miscalculation affects network consensus participation |
| AC | H (High) | Requires an implementation bug that survives comprehensive test suites |
| PR | N (None) | No privileges needed; defect is in client code |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Scope limited to nodes running the faulty client |
| C | N (None) | No confidentiality impact |
| I | L (Low) | Fee miscalculation leads to consensus divergence at the node level |
| A | N (None) | No availability impact; nodes simply fork off |

## Recommendation

1. **Maintain consensus-spec-tests coverage**: The consensus-spec-tests suite provides comprehensive coverage for fork-specific fee calculation formulas. Each client implementation must be validated against these reference tests before release.
2. **Add fork-boundary-specific test cases**: Client teams should maintain test cases that explicitly verify denominator values at each fork transition point.
3. **Deploy consensus divergence monitoring**: Use consensus divergence monitoring in production to detect any fee calculation mismatches immediately after fork activation.
