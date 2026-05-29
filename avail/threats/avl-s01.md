# AVL-S01: TimelockedUpgradeable Name Misleading -- No Actual Timelock

{% hint style="info" %}
**Severity**: Informational (0.0/10) · **STRIDE**: S · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

VectorX's upgrade base class TimelockedUpgradeable contains no actual timelock logic. It is simply an AccessControl wrapper using the name TIMELOCK_ROLE. The onlyTimelock modifier only checks hasRole(TIMELOCK_ROLE, msg.sender). No actual delay, queue, or execute pattern exists. Source: succinctlabs/succinctx submodule, contracts/src/upgrades/TimelockedUpgradeable.sol.

## Prerequisites

None -- discovered through static code analysis

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.0/10 (Informational) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N/CI:N/II:N/AI:N` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | DataStore |

### BVSS Rationale

No direct CIA impact. ISS=0 so Base Score=0. Classified as Informational due to security perception misdirection risk.

## Code References


### Other References

- succinctlabs/succinctx contracts/src/upgrades/TimelockedUpgradeable.sol — delay 로직 0
- AccessControl wrapper only

## Verification & Evidence

**Status**: Verified

Source code confirmed: delay logic absent. onlyTimelock = hasRole check only.

**PoC References**: source-TimelockedUpgradeable

## Mitigations

None -- the code name vs. functionality mismatch is itself the issue.
