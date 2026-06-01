# Cross-DA Comparison

This section compares threat modeling results across all four Data Availability protocols assessed by BONDA. Use this page to understand how the protocols compare in terms of threat density, severity distribution, and common risk patterns.

---

## Protocol Overview

| | EigenDA | Celestia | Avail | Ethereum PeerDAS |
|---|---------|----------|-------|-----------------|
| **Architecture** | AVS on EigenLayer | Standalone L1 | Standalone L1 | Native Ethereum upgrade |
| **Consensus** | Quorum-based BLS | CometBFT (94 validators) | NPoS BABE+GRANDPA (105 validators) | Beacon Chain PoS |
| **DAS Support** | No | Yes (16 samples/block) | Yes (KZG-based) | Yes (PeerDAS, custody groups) |
| **Bridge to Ethereum** | ServiceManager on-chain | SP1Blobstream | VectorX + SP1 | Native (no bridge needed) |
| **Scoring Method** | 4-tier + 5-axis | 4-tier + 5-axis | 4-tier + 5-axis | 4-tier + 5-axis |
| **Findings** | 14 | 12 | 12 | 12 |

Every finding is sorted into one of four [classification](../methodology/classification.md) tiers, and only the Vulnerability tier carries a CVSS 3.1 score. The other tiers are qualitative inputs to the [5-axis model](../methodology/scoring.md); per-DA scores and pentagons are rendered in the dashboard, not here.

---

## Classification Distribution

| Tier | EigenDA | Celestia | Avail | Ethereum | Total |
|------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Vulnerability** | 3 | 4 | 3 | 4 | **14** |
| **Operational Risk** | 3 | 3 | 2 | 2 | **10** |
| **Governance Observation** | 4 | 2 | 4 | 3 | **13** |
| **Design Note** | 4 | 3 | 3 | 3 | **13** |
| **Total** | **14** | **12** | **12** | **12** | **50** |

The four DA layers are now modeled at comparable depth, so each can be assessed against the same five axes. A large share of findings are Governance Observations and Design Notes, reflecting that DA-layer risk is dominated by structural and governance properties rather than directly exploitable code defects.

---

## Vulnerability Severity (CVSS 3.1)

Only the 14 Vulnerability-tier findings carry a CVSS score.

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|----------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Critical (9.0-10.0)** | 0 | 0 | 0 | 0 | **0** |
| **High (7.0-8.9)** | 2 | 1 | 2 | 0 | **5** |
| **Medium (4.0-6.9)** | 0 | 3 | 1 | 1 | **5** |
| **Low (0.1-3.9)** | 1 | 0 | 0 | 3 | **4** |
| **Total** | **3** | **4** | **3** | **4** | **14** |

No Vulnerability reaches CVSS Critical (9.0+). The High-severity findings are unauthenticated compute/bandwidth exhaustion (EDA-01, EDA-02, CEL-01) and Avail data-availability integrity gaps (AVL-01, AVL-02).

---

## Verification Depth

| Status | EigenDA | Celestia | Avail | Ethereum | Total |
|--------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Verified** | 11 | 10 | 9 | 12 | **42** |
| **PoC Verified** | 3 | 2 | 3 | 0 | **8** |
| **Total** | **14** | **12** | **12** | **12** | **50** |

All 50 findings are verified through source code analysis, on-chain state queries, specification review, or live measurement. Eight findings reach PoC-verified status with end-to-end reproductions.

Learn more about verification levels in the [Verification Methodology](../methodology/verification.md).

---

## Where Findings Concentrate

- **EigenDA** findings span the unauthenticated compute surface (Disperser, Relay, operator read path) and a concentrated governance layer where a single 3-of-4 multisig controls the core contracts.
- **Celestia** splits between implementation bugs in celestia-core/celestia-node and structural properties such as the DAS-only safety model after fraud-proof removal.
- **Avail** concentrates at the VectorX bridge trust boundary and in the runtime's data-extraction path, where two integrity gaps let submissions appear committed without being provable.
- **Ethereum PeerDAS** combines client-implementation Vulnerabilities (Prysm, c-kzg-4844) with Design Notes that set the baseline: one-dimensional coding, custody-based availability, and the EIP-7918 fee reserve.

---

## Deeper Analysis

- [Scoring Comparison](scoring.md) — How CVSS 3.1 scores compare across all four DA protocols
- [Common Patterns](common-patterns.md) — Recurring threat patterns that appear across multiple DA protocols
