# G-CON-01: KYC Validator Concentration Enables Legal Censorship

{% hint style="info" %}
**Severity**: Critical · **STRIDE**: D (Denial of Service) · **Scope**: protocol · **Status**: verified
{% endhint %}

## Overview

Only 8 validators are needed to reach the 1/3 threshold, and 6 of them are KYC-regulated financial institutions under US, EU, Swiss, and Hong Kong jurisdictions. A single judicial order could execute CEL-D01-style prevote-nil censorship legally, without any malicious intent from validators. Anchorage Digital alone holds 11.08%, immediately alignable via a single US court order. max_validators=100 with 94 currently bonded effectively blocks new entrants (validator set saturation). Delegator diversification alone does not reduce the minimum number of validators needed for the 1/3 threshold.

## Core Invariants Affected

`consensus_liveness`

Validator concentration + validator set saturation enables CEL-D01-style targeted denial of consensus liveness.

## Prerequisites

Court order or OFAC designation targeting 6-7 KYC entities. Validators comply out of legal obligation, not malice.

## Attack Scenario

**Condition**: Judicial order or sanctions designation aligning 1/3 of KYC validators

**Example**: 2026-05-24 mainnet: top-8 cumulative 35.77% (>1/3), top-28 67.02% (>2/3), Anchorage 11.08%. 94/100 bonded. Total registered 301 (bonded 94 + unbonding 192 + other 15).

## Impact

| Metric | Value |
|--------|-------|
| Severity | Critical |
| Likelihood | Conditional (court order or OFAC designation targeting 6-7 corporate entities) |
| Scope | protocol |
| Target | Actor, ExternalEntity |
| Core Invariants | consensus_liveness |

## Code References

- On-chain: `cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED (top-8=35.77%, top-28=67.02%, Anchorage 11.08%, 94 bonded)`
- On-chain: `cosmos/staking/v1beta1/params (max_validators=100)`
- Source: api.celestia.pops.one (cross-check 일치)
- Source: Celenium (총 301 validators)

## Verification & Evidence

**Status**: verified

Cross-source confirmed across 3 endpoints (publicnode/polkachu/pops.one). 94 bonded, top-8 35.77%, top-28 67.02% structure maintained (2026-05-24).

## Mitigations

Recommendations: (1) Validator decentralization incentives (support non-KYC validators), (2) Increase MaxValidators (currently 100), (3) Resolve validator set saturation, (4) L2/user-side censorship resistance SLA evaluation.
