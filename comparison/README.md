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
| **Scoring Method** | CVSS 3.1 | CVSS 3.1 | CVSS 3.1 | CVSS 3.1 |
| **Threats Found** | 13 | 12 | 9 | 4 |

---

## Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|----------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Critical (9.0-10.0)** | 0 | 0 | 0 | 0 | **0** |
| **High (7.0-8.9)** | 0 | 1 | 2 | 0 | **3** |
| **Medium (4.0-6.9)** | 9 | 8 | 3 | 1 | **21** |
| **Low (0.1-3.9)** | 4 | 3 | 4 | 3 | **14** |
| **Total** | **13** | **12** | **9** | **4** | **38** |

No threats reach CVSS Critical (9.0+). This is consistent with the threat landscape: DA layers do not directly custody user funds, and most attacks require either multisig compromise (PR:H) or high complexity (AC:H), both of which cap the exploitability sub-score.

---

## Verification Depth

| Status | EigenDA | Celestia | Avail | Ethereum | Total |
|--------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Verified** | 13 | 10 | 9 | 4 | **36** |
| **PoC Verified** | 0 | 2 | 0 | 0 | **2** |
| **Total** | **13** | **12** | **9** | **4** | **38** |

All 38 findings are verified through source code analysis, on-chain state queries, or live measurement. EigenDA and Avail achieve 100% verification rates through systematic on-chain `cast` queries against live contracts. Two Celestia findings reach PoC-verified status with end-to-end reproductions.

Learn more about verification levels in the [Verification Methodology](../methodology/verification.md).

---

## STRIDE Category Distribution

| Category | EigenDA | Celestia | Avail | Ethereum | Total | What It Covers |
|----------|:-------:|:--------:|:-----:|:--------:|:-----:|----------------|
| **Denial of Service** | 5 | 7 | 2 | 2 | **16** | Availability attacks, resource exhaustion, liveness failures |
| **Tampering** | 1 | 0 | 2 | 2 | **5** | Data integrity violations, upgrade path abuse |
| **Elevation of Privilege** | 3 | 1 | 3 | 0 | **7** | Governance abuse, role escalation, multisig concentration |
| **Protocol Design** | 2 | 1 | 2 | 0 | **5** | Structural gaps in the protocol specification |
| **Spoofing** | 1 | 1 | 0 | 0 | **2** | Identity forgery, signature replay |
| **Governance** | 1 | 2 | 0 | 0 | **3** | Validator concentration, information asymmetry |

**Key takeaways**:
- Denial of Service dominates across all protocols (42% of all threats), which is expected for DA layers where availability is the core security guarantee.
- Tampering threats appear in Avail, EigenDA, and Ethereum, reflecting concerns around bridge upgrade paths, cryptographic library robustness, and rate limiting gaps.

---

## Where Threats Concentrate

| Scope | EigenDA | Celestia | Avail | Ethereum | Total |
|-------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Protocol** | 7 | 6 | 0 | 0 | **13** |
| **Bridge** | 4 | 1 | 6 | 0 | **11** |
| **Implementation** | 0 | 5 | 0 | 4 | **9** |
| **Chain** | 0 | 0 | 3 | 0 | **3** |
| **Rollup** | 2 | 0 | 0 | 0 | **2** |

- **Avail** threats concentrate in the bridge layer (6 of 9). The VectorX bridge is where Avail's DA guarantees meet Ethereum, making it the primary trust boundary and attack surface.
- **Celestia** splits between protocol design issues and implementation bugs in celestia-core/celestia-node.
- **Ethereum** findings are all at the implementation level, targeting specific client code in Prysm and the shared c-kzg-4844 library. These come from external audit report analysis rather than BONDA's independent assessment.
- **EigenDA** has the only rollup-scoped threats, where issues in the DA proxy sidecar can affect rollup operators directly.

---

## Deeper Analysis

- [Scoring Comparison](scoring.md) — How CVSS 3.1 scores compare across all four DA protocols
- [Common Patterns](common-patterns.md) — Recurring threat patterns that appear across multiple DA protocols
