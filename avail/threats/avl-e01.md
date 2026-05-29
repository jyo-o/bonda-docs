# AVL-E01: SP1VerifierGateway 2/3 Multisig -- Verifier Route Manipulation Possible

{% hint style="info" %}
**Severity**: Low (1.8/10) · **STRIDE**: E · **Scope**: bridge · **Status**: Verified
{% endhint %}

## Overview

The multisig controlling SP1 verifier routing (0xCafEf00d348Adbd57c37d1B77e0619C6244C6878) has a 2/3 threshold. Owner #2 (0x72Ff...4f54) is the same person as owner #4 of Avail Multisig 1. Succinct 1 person + Avail 1 person is sufficient to change verifier routes. Replacing the verifier with a tampered contract would allow false ZK proofs to be judged as valid.

## Prerequisites

Compromise 2 of 3 SP1VerifierGateway signer keys

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

B:N -- No direct financial impact. AV:P -- 2/3 key compromise required (physical/social engineering). AC:H -- Simultaneous compromise of 2 signer keys. PR:R -- Multisig signer credentials. S:U -- Within verifier route change scope. I:H/II:M -- Verifier route change enables false proof acceptance, but 1 overlapping member weakens effective independence.

## Code References


### Onchain Evidence

- `getThreshold(0xCafE...)=2`
- `getOwners(0xCafE...)=3명`

### PoC Notes

- poc_onchain_verification.md §4

### Other References

- owner#2=0x72Ff...=Gov#4 중복

## Verification & Evidence

**Status**: Verified

getThreshold=2, getOwners 3 confirmed. owner#2=0x72Ff...4f54 cross-verified as identical to Gov Multisig owner#4.

**PoC References**: onchain-§4

## Mitigations

Verifier replacement is restricted to SP1VerifierGateway owner only. 2/3 threshold.
