# EDA-T09: Ejector Role Abuse Can Remove Honest Operators

{% hint style="info" %}
**Severity**: High (7.0/10) · **STRIDE**: T · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

EjectionManager (0x130d8E...) owner=same multisig (0x002721...). The ejector is EOA 0x864247... (a single address, not a multisig). rateLimitWindow=259200 seconds (3 days), ejectableStakePercent=3333 (33.33%). Up to 33.33% of Q0 stake can be ejected within 3 days. Probe measurements: 528 ejection events (~2026-03), peaking at 178 in 2024-08.

## Prerequisites

Ejector role abuse

## Attack Scenario

See details above.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 7.0/10 (High) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:L/PR:R/UI:N/S:U/C:N/I:L/A:H/CI:N/II:M/AI:H` |
| Likelihood | Unrated |
| Scope | bridge |
| Target | Process |

### BVSS Rationale

B:N -- No direct fund theft possible. AV:N -- Onchain transaction. AC:L -- Single EOA key; 150 active uses observed over 16 months. PR:R -- Ejector role. A:H/AI:H -- Can force-eject 33.33% of quorum stake within 3 days.

## Code References

### Source Code

- [`contracts/src/periphery/ejection/EigenDAEjectionManager.sol`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/periphery/ejection/EigenDAEjectionManager.sol)

### PoC Notes

- block=25101686
- poc/06-*/evidence.yaml [VERIFIED]
- block=25101710 ejector=0x8642(EOA)

### Other References

- Prober: ejection_events 528행
- EjectionManager.owner()=0x002721B4
- RC.ejector()=0x130d8EA0
- isEjector=true
- rateLimitWindow=259200s
- ejectableStakePercent=3333

## Verification & Evidence

**Status**: Verified

2 active ejector EOAs called 150 ejections over 16 months (100% of all ejections); quorum 33% ejection possible. Dune query 7461036 tracks OperatorStakeUpdate not ejection. Blockscout 150 events are the primary ejection source.

**PoC References**: #05, #28

## Mitigations

EjectionCooldown configuration.
