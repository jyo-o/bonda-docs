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
| **Threats Found** | 17 | 18 | 9 | 11 |

---

## Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|----------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Critical (9.0-10.0)** | 0 | 0 | 0 | 0 | **0** |
| **High (7.0-8.9)** | 2 | 5 | 2 | 0 | **9** |
| **Medium (4.0-6.9)** | 10 | 8 | 4 | 4 | **26** |
| **Low (0.1-3.9)** | 5 | 5 | 3 | 7 | **20** |
| **Informational (0.0)** | 0 | 0 | 0 | 0 | **0** |
| **Total** | **17** | **18** | **9** | **11** | **55** |

No threats reach CVSS Critical (9.0+). This is consistent with the threat landscape: DA layers do not directly custody user funds, and most attacks require either multisig compromise (PR:H) or high complexity (AC:H), both of which cap the exploitability sub-score.

Celestia leads with 5 High-severity findings, driven by governance-layer structural issues (CEL-G01 at 8.7) and multiple memory exhaustion vulnerabilities with low attack complexity.

---

## Verification Depth

| Status | EigenDA | Celestia | Avail | Ethereum | Total |
|--------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Verified** (mainnet confirmed) | 12 | 4 | 8 | 6 | **30** |
| **PoC Verified** (fork test) | 0 | 4 | 0 | 0 | **4** |
| **Code Verified** (source audit) | 4 | 8 | 0 | 3 | **15** |
| **Partial** (incomplete evidence) | 1 | 2 | 0 | 2 | **5** |
| **Unverified** (design analysis only) | 0 | 0 | 1 | 0 | **1** |
| **Total** | **17** | **18** | **9** | **11** | **55** |

Avail has the highest verified rate at 86%, achieved through systematic on-chain `cast` queries against live contracts. EigenDA follows at 71% with extensive mainnet probing. Celestia has the most PoC-verified threats due to Anvil fork testing of memory exhaustion vectors.

Learn more about verification levels in the [Verification Methodology](../methodology/verification.md).

---

## STRIDE Category Distribution

| Category | EigenDA | Celestia | Avail | Ethereum | Total | What It Covers |
|----------|:-------:|:--------:|:-----:|:--------:|:-----:|----------------|
| **Denial of Service** | 7 | 13 | 2 | 2 | **24** | Availability attacks, resource exhaustion, liveness failures |
| **Tampering** | 2 | 1 | 2 | 5 | **10** | Data integrity violations, upgrade path abuse |
| **Elevation of Privilege** | 3 | 1 | 3 | 1 | **8** | Governance abuse, role escalation, multisig concentration |
| **Spoofing** | 1 | 1 | 0 | 2 | **4** | Identity forgery, signature replay |
| **Protocol Design** | 2 | 0 | 2 | 0 | **4** | Structural gaps in the protocol specification |
| **Governance** | 1 | 2 | 0 | 0 | **3** | Validator concentration, information asymmetry |
| **Information Disclosure** | 1 | 0 | 0 | 0 | **1** | Key exposure, unauthenticated data access |
| **Repudiation** | 0 | 0 | 0 | 1 | **1** | Missing audit trails, undetectable misbehavior |

**Key takeaways**:
- Denial of Service dominates across all protocols (39% of all threats), which is expected for DA layers where availability is the core security guarantee.
- Celestia accounts for over half of all DoS threats (13/24) due to multiple memory exhaustion vectors in celestia-core and celestia-node.
- Tampering threats concentrate in Avail and Ethereum, reflecting concerns around bridge upgrade paths and data column verification gaps.

---

## Where Threats Concentrate

| Scope | EigenDA | Celestia | Avail | Ethereum | Total |
|-------|:-------:|:--------:|:-----:|:--------:|:-----:|
| **Protocol** | 10 | 9 | 0 | 11 | **30** |
| **Bridge** | 4 | 1 | 9 | 0 | **14** |
| **Implementation** | 0 | 9 | 0 | 0 | **9** |
| **Chain** | 0 | 0 | 5 | 0 | **5** |
| **Rollup** | 3 | 0 | 0 | 0 | **3** |

- **Avail** threats concentrate in the bridge layer (9 of 14). The VectorX bridge is where Avail's DA guarantees meet Ethereum, making it the primary trust boundary and attack surface.
- **Celestia** splits evenly between protocol design issues and implementation bugs in celestia-core/celestia-node.
- **Ethereum** threats are entirely at the protocol level, reflecting that PeerDAS is a specification being implemented by multiple independent client teams.
- **EigenDA** has the only rollup-scoped threats, where issues in the DA proxy sidecar can affect rollup operators directly.

---

## Deeper Analysis

- [Scoring Comparison](scoring.md) — How CVSS 3.1 scores compare across all four DA protocols
- [Common Patterns](common-patterns.md) — Recurring threat patterns that appear across multiple DA protocols
