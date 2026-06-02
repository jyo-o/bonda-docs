# BONDA Threat Model

**Systematic threat modeling for the Data Availability layers powering rollups.**

BONDA analyzes the security of four major DA protocols, with every finding traced back to primary sources: pinned source code commits, live on-chain contract state, and network endpoint probes.

---

## What is This?

Data Availability is one of the most critical layers in the Ethereum rollup stack. Rollups post their transaction data to DA layers, and if that data becomes unavailable, users cannot verify rollup state or withdraw their funds. BONDA systematically identifies threats to these DA layers — from governance risks and bridge vulnerabilities to code-level bugs and protocol design gaps.

This documentation covers **50 findings** across four protocols. Each finding is sorted into one of four [classification](methodology/classification.md) tiers — Vulnerability, Operational Risk, Governance Observation, or Design Note — and only the Vulnerability tier carries a CVSS 3.1 score. The other tiers are qualitative inputs to the [five-axis model](methodology/scoring.md).

---

## Covered Protocols

| Protocol | Description | Findings | Highest CVSS |
|----------|-------------|---------|-----------------|
| [**Ethereum**](ethereum/) | PeerDAS custody/sampling design, consensus clients, and KZG library | 12 | Medium (5.3) |
| [**EigenDA**](eigenda/) | AVS-based DA on EigenLayer with centralized disperser and quorum-based attestation | 14 | High (8.6) |
| [**Celestia**](celestia/) | Modular DA layer with CometBFT consensus and light client DAS | 12 | High (7.5) |
| [**Avail**](avail/) | Substrate-based DA chain with VectorX bridge to Ethereum | 12 | High (8.5) |

---

## Verification at a Glance

| Metric | Count |
|--------|-------|
| Total findings | 50 |
| Verified | 42 |
| PoC verified | 8 |

All 50 findings are confirmed through source code analysis, on-chain state queries, specification review, or live measurement. Verification levels are explained in the [Verification Methodology](methodology/verification.md).

---

## Notable Findings

### Highest-Scored Vulnerabilities (CVSS 3.1)

| ID | Protocol | CVSS | Finding |
|----|----------|------|---------|
| [EDA-01](eigenda/threats/eda-01.md) | EigenDA | 8.6 | Unauthenticated GetChunks cold-miss exhausts operator CPU toward the confirmation threshold |
| [EDA-02](eigenda/threats/eda-02.md) | EigenDA | 8.6 | Disperser V2 KZG commitment compute exposed without authentication or prepayment |
| [AVL-01](avail/threats/avl-01.md) | Avail | 8.5 | MultiAddress::Index signing silently drops the data leaf from the bridge proof |
| [AVL-02](avail/threats/avl-02.md) | Avail | 7.7 | Proxy-wrapped submitData bypasses data-availability extraction |
| [CEL-01](celestia/threats/cel-01.md) | Celestia | 7.5 | TxCache key mismatch leaks memory until the validator crashes |

### Notable Governance Observations (no CVSS)

| ID | Protocol | Finding |
|----|----------|---------|
| [CEL-08](celestia/threats/cel-08.md) | Celestia | Top 8 validators hold 35.77% of voting power; 6 are KYC-regulated entities subject to legal censorship orders |
| [EDA-07](eigenda/threats/eda-07.md) | EigenDA | A single 3-of-4 multisig controls all eight core contracts through one ProxyAdmin with no timelock |
| [AVL-06](avail/threats/avl-06.md) | Avail | Deployer EOA still holds admin role on VectorX, enabling solo bridge upgrade in 2 transactions |

---

## Quick Navigation

### By Protocol
- [Ethereum](ethereum/) — KZG library and consensus client audit findings
- [EigenDA](eigenda/) — Disperser, Relay, Operator, and governance threats
- [Celestia](celestia/) — Consensus, DAS, and Blobstream bridge threats
- [Avail](avail/) — VectorX bridge, validator set, and governance threats

### By Topic
- [Methodology](methodology/) — threat discovery, four-tier classification, five-axis scoring, CVSS, verification approach, terminology
- [Cross-DA Comparison](comparison/) — Side-by-side analysis across all four protocols
- [Terminology](methodology/terminology.md) — Glossary of terms used throughout this documentation

---

## About BONDA

BONDA is a security research project focused on DA layer threat assessment. This documentation serves as the public reference for the threat modeling work.

- **Source**: [github.com/jyo-o/bonda-docs](https://github.com/jyo-o/bonda-docs)
- **Dashboard**: [bonda.me](https://bonda.me)
