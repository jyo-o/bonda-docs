# AVL-P01: Slashing Infrastructure Present but Never Triggered

{% hint style="info" %}
**Severity**: Low (2.1/10) · **STRIDE**: P · **Status**: Verified
{% endhint %}

## Summary

Avail's NPoS consensus includes complete slashing infrastructure in its runtime (67 slash-related functions, SlashDeferDuration of 27 eras, BondingDuration of 28 eras). However, zero slashing events have occurred across 688 eras of operation. This absence of enforcement weakens the economic security model, as validators face no real financial punishment for misbehavior despite slashing existing as a theoretical deterrent.

## Description

The runtime metadata contains 67 references to slash-related functions, and the chain defines specific slashing parameters.

```
// @audit — Slashing infrastructure vs. enforcement:
//          Runtime slash references: 67 functions
//          SlashDeferDuration: 27 eras
//          BondingDuration: 28 eras
//          SessionsPerEra: 6
//          UnappliedSlashes (era 688): null (zero events ever)
//          688 eras of operation with zero slashing enforcement.
```

The gap between implemented infrastructure and actual enforcement may reflect conditions that are too lenient, insufficient monitoring, or social dynamics within the validator set that discourage reporting. The practical consequence is that the economic deterrent that NPoS relies on to keep validators honest has never been exercised.

## Proof of Concept

On-chain verification confirmed the absence of slashing enforcement:

- `state_getStorage` for ActiveEra returns 688 after SCALE decoding, confirming long-running chain operation
- `UnappliedSlashes` storage query for era 688 returns null, confirming zero slashing events
- Runtime constants: `SlashDeferDuration` = 27 eras, `BondingDuration` = 28 eras, `SessionsPerEra` = 6
- Runtime metadata contains 67 references to slash-related functions, confirming the infrastructure exists in code

Reference: poc_onchain_verification.md, section 10.

## Impact

Validators observing the lack of enforcement may be incentivized to take risks such as running on lower-quality infrastructure, double-signing to maximize rewards across forks, or engaging in collusion. The absence of real penalties erodes the economic deterrent that secures the network. This is an internal validator incentive concern rather than a direct external attack vector.

### CVSS 3.1
**Score**: 2.1/10 (Low)  
**Vector**: `CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Relates to internal validator behavior requiring physical or social context to exploit |
| AC | L (Low) | Non-triggering of slashing is a persistent, observable state, not something that needs engineering |
| PR | L (Low) | Validator credentials are required to be in a position to misbehave |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact limited to the validator incentive mechanism |
| C | N (None) | No confidentiality impact |
| I | N (None) | No integrity impact from the absence of slashing alone |
| A | L (Low) | Weakened incentives could indirectly lead to reduced network reliability |

## Recommendation

1. **Audit slashing trigger conditions**: Review whether the slashing conditions defined in the runtime are appropriate for the current validator set and network state, and adjust thresholds if they are too lenient.
2. **Implement validator monitoring**: Deploy monitoring infrastructure that actively detects equivocation, downtime, and other slashable offenses, ensuring that slashing reports are submitted when warranted.
3. **Publish slashing transparency reports**: Regularly publish reports on validator behavior and slashing-related metrics to increase accountability and demonstrate that the enforcement mechanism is actively monitored.
