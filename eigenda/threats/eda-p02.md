# EDA-P02: Absence of Data Availability Sampling Forces Full Quorum Trust

{% hint style="info" %}
**Severity**: Medium (6.5/10) · **STRIDE**: P · **Status**: Code Verified
{% endhint %}

## Summary

EigenDA does not implement Data Availability Sampling (DAS), as explicitly stated in its specification. The client retrieval path contains no sampling interface, and on-chain certificate verification checks only BLS aggregate signatures and a 55% stake threshold. The root cause is a conscious architectural decision not to adopt DAS, unlike Celestia (namespaced Merkle trees with random sampling) or Ethereum PeerDAS (column sampling). Clients cannot independently verify that data was actually made available by operators and must trust that the quorum honestly stored the data they attested to.

## Description

The absence of DAS manifests at multiple levels:

**On-chain verification** -- Certificate verification in `EigenDACertVerificationLib.sol` checks only BLS aggregate signatures and the 55% stake threshold. No sampling-based verification exists.

**Source**: [`EigenDACertVerificationLib.sol:232-246`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L232-L246) -- Certificate verification checks only BLS aggregate signatures and 55% stake threshold.

**Specification** -- `docs/spec/src/introduction.md:27` explicitly states DAS is not used.

**Code search** -- A search for sampling interfaces across the codebase returns zero results.

The client-side random shuffle used during retrieval is for load balancing purposes only, not cryptographic sampling. This means operators can sign BLS attestations claiming they received data without actually storing it, and there is no sampling mechanism for clients to detect this dishonesty. The 8 free-rider candidate operators identified in PoC #02 illustrate this direct attack scenario.

## Proof of Concept

### Reproduction

- `poc/34-das-absence/evidence.yaml` confirmed the absence of sampling interfaces.
- Verified from specification and code, not from mainnet measurement.

**PoC References**: #31

## Impact

Without DAS, clients are entirely dependent on quorum trust for data availability guarantees. Operators can sign BLS attestations confirming data receipt but discard the actual data. The aggregate BLS signature meets the 55% stake threshold, producing a valid certificate. On-chain verification passes because it only checks signatures and stake thresholds, not actual data availability. When a client later attempts to retrieve the data, the request fails. KZG opening proofs via `ValidateBatchV2` provide partial verification capability for individual chunks but are not a sampling-based mechanism. The attack requires operator collusion and no additional authentication.

### CVSS 3.1

**Score**: 6.5/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attestation signing and data retrieval occur over the network |
| AC (Attack Complexity) | H (High) | The non-adoption of DAS is a design decision; exploitation requires operator collusion to withhold data |
| PR (Privileges Required) | N (None) | Operators are already registered; no additional privileges needed |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is within the EigenDA protocol and dependent rollups |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | H (High) | Clients are entirely dependent on quorum trust with no independent verification; KZG provides partial but insufficient mitigation |
| A (Availability) | L (Low) | The protocol itself continues to function normally; data unavailability is detected only at retrieval time |

## Recommendation

1. Evaluate the feasibility of introducing a sampling-based verification mechanism in future EigenDA versions (v2/v3).
2. Until DAS is implemented, strengthen KZG opening proof verification on the client side via `ValidateBatchV2` to provide partial data integrity assurance.
3. Consider implementing periodic data availability challenges where operators must prove they still hold assigned data chunks.
4. Document the trust model clearly for rollup integrators so they understand the quorum-trust dependency.
