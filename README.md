# BONDA Threat Model

**Systematic threat modeling for the Data Availability layers powering Ethereum rollups.**

BONDA analyzes the security of four major DA protocols by combining STRIDE-based threat modeling, on-chain verification, source code auditing, and mainnet fork testing. Every finding is traced back to primary sources: pinned source code commits, live on-chain contract state, and network endpoint probes.

---

## What is This?

Data Availability is one of the most critical layers in the Ethereum rollup stack. Rollups post their transaction data to DA layers, and if that data becomes unavailable, users cannot verify rollup state or withdraw their funds. BONDA systematically identifies threats to these DA layers — from governance risks and bridge vulnerabilities to code-level bugs and protocol design gaps.

This documentation covers **61 verified threats** across four protocols, each with detailed analysis, on-chain evidence, and severity scoring.

---

## Covered Protocols

| Protocol | Description | Threats | Highest Severity |
|----------|-------------|---------|-----------------|
| [**EigenDA**](eigenda/) | AVS-based DA on EigenLayer with centralized disperser and quorum-based attestation | 17 | High (7.5) |
| [**Celestia**](celestia/) | Modular DA layer with CometBFT consensus and light client DAS | 19 | High (8.7) |
| [**Avail**](avail/) | Substrate-based DA chain with VectorX bridge to Ethereum | 14 | High (8.2) |
| [**Ethereum / PeerDAS**](ethereum/) | Ethereum's upcoming DA scaling upgrade with multi-client architecture | 11 | Medium (6.5) |

---

## Verification at a Glance

| Metric | Count |
|--------|-------|
| Total threats | 61 |
| Verified on mainnet | 35 |
| PoC verified | 4 |
| Code verified | 15 |
| Partial evidence | 5 |
| Unverified | 2 |

All verification levels are explained in the [Verification Methodology](methodology/verification.md).

---

## Notable Findings

### Critical Severity

| ID | Protocol | Finding |
|----|----------|---------|
| [CEL-E01](celestia/threats/cel-e01.md) | Celestia | SP1Blobstream bridge can be instantly upgraded by a 4-of-6 multisig with no timelock |
| [CEL-G01](celestia/threats/cel-g01.md) | Celestia | Top 8 validators hold 35.77% of voting power; 6 are KYC-regulated entities subject to legal censorship orders |

### High Severity

| ID | Protocol | Finding |
|----|----------|---------|
| [AVL-E03](avail/threats/avl-e03.md) | Avail | Deployer EOA still holds admin role on VectorX, enabling solo bridge upgrade in 2 transactions |
| [EDA-T09](eigenda/threats/eda-t09.md) | EigenDA | Single EOA can eject up to 33% of operator stake within a 3-day window |
| [CEL-T01](celestia/threats/cel-t01.md) | Celestia | Fraud proofs were removed but documentation still claims they exist |

---

## Quick Navigation

### By Protocol
- [EigenDA](eigenda/) — Disperser, Relay, Operator, and governance threats
- [Celestia](celestia/) — Consensus, DAS, and Blobstream bridge threats
- [Avail](avail/) — VectorX bridge, validator set, and governance threats
- [Ethereum / PeerDAS](ethereum/) — Multi-client divergence, KZG, and custody group threats

### By Topic
- [Methodology](methodology/) — STRIDE framework, CVSS scoring, verification approach, terminology
- [Cross-DA Comparison](comparison/) — Side-by-side analysis across all four protocols
- [Terminology](methodology/terminology.md) — Glossary of terms used throughout this documentation

---

## About BONDA

BONDA is a security research project focused on DA layer threat assessment. This documentation serves as the public reference for the threat modeling work.

- **Source**: [github.com/jyo-o/bonda-docs](https://github.com/jyo-o/bonda-docs)
- **Dashboard**: [bonda.me](https://bonda.me)
