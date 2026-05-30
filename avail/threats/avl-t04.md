# AVL-T04: Guardian Can Inject Commitments Without ZK Proof Verification

{% hint style="info" %}
**Severity**: Medium (4.0/10) · **STRIDE**: T · **Status**: Verified
{% endhint %}

## Summary

The `updateBlockRangeData()` function in SP1Vector.sol allows the GUARDIAN_ROLE holder (Governance Multisig 1, 4-of-7 Safe) to bypass the ZK verification pipeline entirely and directly inject arbitrary data and state commitments into VectorX. This is an intentional emergency recovery mechanism, but a compromised multisig could inject false commitments that would be accepted by the bridge without any cryptographic verification.

## Description

VectorX normally verifies Avail block headers through a secure pipeline: the relayer calls `commitHeaderRange()`, which verifies an SP1 zero-knowledge proof before storing the commitment. The `updateBlockRangeData()` function bypasses this entire pipeline.

```solidity
// @audit — SP1Vector.sol: updateBlockRangeData()
//          Stores commitments directly without any ZK proof verification.
//          Restricted to GUARDIAN_ROLE (Governance Multisig 1, 4/7 Safe).
//          Designed as emergency recovery when ZK proving pipeline fails.
//          Additional guardian functions: updateVerifier(), 
//          updateVectorXProgramVkey(), updateGenesisState().
```

The Guardian holds broad control over the verification infrastructure through multiple functions: `updateBlockRangeData()`, `updateVerifier()`, `updateVectorXProgramVkey()`, and `updateGenesisState()`. While this is a deliberate design choice for operational resilience, it creates a significant trust assumption on the 4-of-7 multisig.

## Proof of Concept

Anvil mainnet fork PoC (test 3) confirmed the guardian ZK bypass behavior: `updateBlockRangeData()` successfully stores commitments without proof verification. The test verified that the function works as designed for its intended emergency recovery purpose, bypassing the SP1 proof verification path used by `commitHeaderRange()`.

References: SP1Vector.sol source analysis; avl_d01_relayer_spof_poc.sh PoC test 3.

## Impact

A compromised 4-of-7 multisig could inject fabricated block header commitments that the bridge accepts as valid Avail block headers without cryptographic verification. This could enable fraudulent bridge withdrawals, incorrect state attestations, or other manipulations that depend on the integrity of block header data. However, false data would be detectable by anyone comparing on-chain commitments against actual Avail block headers.

### CVSS 3.1
**Score**: 4.0/10 (Medium)  
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | P (Physical) | Exploiting requires physical or social engineering access to obtain 4 of 7 multisig keys |
| AC | H (High) | 4-of-7 multisig compromise is required |
| PR | L (Low) | Attacker needs GUARDIAN_ROLE credentials specifically |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact stays within the commitment storage scope |
| C | N (None) | No confidentiality impact |
| I | H (High) | ZK proof verification can be completely bypassed; this is an intended emergency mechanism |
| A | N (None) | Function adds data rather than disrupting service |

## Recommendation

1. **Emit events on guardian commitment injection**: Ensure all `updateBlockRangeData()` calls emit distinct events that monitoring systems can detect, differentiating guardian-injected commitments from ZK-verified ones.
2. **Implement a timelock on guardian functions**: Add a delay to `updateBlockRangeData()` and other guardian functions to provide a detection window, accepting a tradeoff with emergency response time.
3. **Add on-chain verification of guardian commitments**: Where feasible, implement a secondary verification mechanism (e.g., cross-checking against known Avail state) for guardian-injected commitments.
