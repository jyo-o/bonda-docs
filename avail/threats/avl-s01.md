# AVL-S01: TimelockedUpgradeable Contract Has No Actual Timelock Logic

{% hint style="success" %}
**Severity**: Informational (0.0/10) · **STRIDE**: S · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX inherits from a base contract called `TimelockedUpgradeable`, sourced from the `succinctlabs/succinctx` repository at `contracts/src/upgrades/TimelockedUpgradeable.sol`. The name strongly suggests that upgrades are protected by a timelock mechanism, which would enforce a delay between proposing and executing an upgrade. In reality, this contract contains no timelock logic whatsoever.

The `TimelockedUpgradeable` contract is simply an AccessControl wrapper. Its `onlyTimelock` modifier does nothing more than check `hasRole(TIMELOCK_ROLE, msg.sender)`, verifying that the caller has the correct role. There is no delay, no queue, no scheduling, and no execute pattern. The contract provides role-based access control under a name that implies time-delayed security.

This naming mismatch creates a false sense of security for anyone auditing or reviewing VectorX's upgrade path. A reviewer who sees "TimelockedUpgradeable" in the inheritance chain might reasonably conclude that upgrades are time-delayed, when in fact they can be executed immediately by any address holding the TIMELOCK_ROLE. This is a documentation and naming issue rather than a direct vulnerability, which is why it is classified as Informational with a score of 0.0.

## Prerequisites

- No prerequisites are needed to identify this issue. It was discovered through static analysis of the source code in the succinctlabs/succinctx repository.

## Attack Scenario

1. A security auditor or developer reviews VectorX's contract inheritance and sees `TimelockedUpgradeable` in the base class. Based on the name, they conclude that upgrades are protected by a timelock delay mechanism.
2. Relying on this incorrect assumption, the auditor skips deeper review of the upgrade path, or a protocol integration partner proceeds without implementing additional upgrade monitoring because they believe a timelock already exists.
3. When VectorX is actually upgraded, there is no delay. The upgrade executes immediately upon receiving the required role authorization. The expected 24-hour or similar warning window for users to react does not exist, and the false assumption persists until an actual upgrade event reveals the absence of a timelock.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.0/10 (Informational) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N/CI:N/II:N/AI:N` |
| Scope | bridge |

### Scoring Rationale

All CIA impact metrics are zero because the misleading name does not directly enable any attack or cause any harm. The ISS component is zero, resulting in a base score of 0.0. This finding is classified as Informational because the risk is indirect: it affects security perception and audit accuracy rather than system integrity. The danger is that reviewers may overestimate the protection of VectorX's upgrade path based on the contract name alone.

## Evidence

### Source Code

- File: `succinctlabs/succinctx`, path `contracts/src/upgrades/TimelockedUpgradeable.sol`
- The `onlyTimelock` modifier implementation is `require(hasRole(TIMELOCK_ROLE, msg.sender))`, a pure role check with no delay logic.
- No `delay`, `queue`, `schedule`, or `execute` functions exist in the contract.
- The contract is an AccessControl wrapper that uses the name "Timelock" without implementing timelock functionality.

## Mitigations

There is no mitigation because the misleading name is itself the issue. The contract functions as designed from a technical standpoint; it correctly restricts access to role holders. The problem is purely one of naming and the security assumptions that name creates. Any review of VectorX's upgrade security should verify the actual implementation rather than relying on the contract name.
