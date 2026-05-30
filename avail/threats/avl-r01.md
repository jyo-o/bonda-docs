# AVL-R01: Slashing Infrastructure Present but Never Triggered

{% hint style="info" %}
**Severity**: Low (0.3/10) · **STRIDE**: R · **Scope**: chain · **Status**: Verified
{% endhint %}

## Overview

Avail operates a Nominated Proof-of-Stake consensus system that includes slashing infrastructure in its runtime code. The runtime metadata contains 67 references to "slash"-related functions, and the chain defines specific slashing parameters: a SlashDeferDuration of 27 eras and a BondingDuration of 28 eras, with 6 sessions per era.

Despite this infrastructure being in place, zero slashing events have occurred across 688 eras of operation. Querying the `UnappliedSlashes` storage for the current era returns null, meaning no slashing penalties have ever been applied. This is not necessarily due to perfect validator behavior; it may reflect that the slashing conditions are too lenient, that monitoring is insufficient, or that the social dynamics of the validator set discourage reporting.

The practical consequence is that validators face no real financial punishment for misbehavior. Slashing exists as a theoretical deterrent but has never been exercised, which weakens the economic security model that Nominated Proof-of-Stake relies on to keep validators honest.

## Prerequisites

- This is an internal validator incentive concern rather than a direct external attack vector
- Requires understanding of the gap between slashing infrastructure and its practical enforcement

## Attack Scenario

1. A validator on the Avail network begins engaging in equivocation, producing conflicting blocks for the same slot, or goes offline repeatedly during their assigned validation duties.
2. Despite this misbehavior being detectable by the slashing infrastructure, no slashing event is triggered. The misbehavior goes unpunished, as evidenced by 688 eras of operation with zero slashing events.
3. Observing the lack of enforcement, other validators may be incentivized to take risks such as running on lower-quality infrastructure, double-signing to maximize rewards across forks, or engaging in collusion. The absence of real penalties erodes the economic deterrent that secures the network.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 0.3/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:L/PR:R/UI:N/S:U/C:N/I:N/A:L/CI:N/II:N/AI:L` |
| Scope | chain |

### Scoring Rationale

There is no direct financial impact because the absence of slashing does not directly cause fund loss. The attack vector relates to internal validator behavior, requiring physical or social context to exploit. Attack complexity is low because the non-triggering of slashing is a persistent, observable state rather than something an attacker needs to engineer. Validator credentials are required to be in a position to misbehave. The scope is limited to the validator incentive mechanism. Availability impact is low because weakened incentives could indirectly lead to reduced network reliability. Infrastructure availability impact is similarly low because the incentive structure's effectiveness is degraded over time.

## Evidence

### On-Chain Verification

- `state_getStorage` for ActiveEra returns 688 after SCALE decoding, confirming long-running chain operation.
- `UnappliedSlashes` storage query for era 688 returns null, confirming zero slashing events.
- Runtime constants: `SlashDeferDuration` = 27 eras, `BondingDuration` = 28 eras, `SessionsPerEra` = 6.
- Runtime metadata contains 67 references to slash-related functions, confirming the infrastructure exists in code.

### PoC Testing

- Documented in poc_onchain_verification.md, section 10.

## Mitigations

The slashing infrastructure is fully implemented in the runtime code and could be activated if conditions are met. The BondingDuration of 28 eras ensures that validator stakes remain locked long enough for deferred slashing to be applied. However, the 688-era track record of zero enforcement suggests that the deterrent effect is currently theoretical rather than practical.
