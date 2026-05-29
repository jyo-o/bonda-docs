# Methodology Overview

BONDA provides systematic threat modeling for Data Availability (DA) layers that underpin Ethereum's rollup ecosystem. This section describes the analytical framework used to identify, score, and verify threats across EigenDA, Celestia, Avail, and Ethereum PeerDAS.

---

## Why Threat Model DA Layers?

Rollups delegate data publication to DA layers, trusting them to guarantee that transaction data remains retrievable for a defined period. If a DA layer fails silently — through censorship, data withholding, or bridge compromise — rollups built on top of it inherit that failure with no independent recourse.

Despite this critical dependency, most DA layers have not been subjected to structured adversarial analysis. Security audits focus on code correctness but rarely map trust boundaries, governance concentration, or protocol-level design gaps. BONDA fills this gap by applying threat modeling techniques adapted specifically for DA infrastructure.

---

## Three Pillars

BONDA's methodology rests on three pillars:

### 1. STRIDE Analysis

Each DA protocol is decomposed into a Data Flow Diagram (DFD) with explicit trust boundaries. Threats are enumerated using the STRIDE-per-element method — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege — extended with two DA-specific categories: **Protocol Gap (P)** for missing design-level features and **Governance/Concentration (G)** for centralization risks.

See: [STRIDE for DA Layers](stride.md)

### 2. BVSS 1.1 Scoring

Findings are scored using the BONDA Vulnerability Scoring System (BVSS 1.1), adapted from Halborn's blockchain-specific scoring framework. BVSS extends CVSS with chain-impact metrics that capture the cascading effects unique to blockchain systems — a bridge vulnerability does not merely affect one service but can propagate across every rollup depending on that DA layer.

See: [BVSS 1.1 Scoring](bvss.md)

### 3. Multi-Source Verification

Every finding is traced to at least two independent primary sources. BONDA goes beyond static code review by combining source code audits (pinned to specific commits), on-chain state queries (via `cast` and RPC calls), and live network probes (gRPC/REST against mainnet nodes). Evidence is captured in reproducible artifacts — YAML evidence files, shell script PoCs, and command output logs.

See: [Verification Approach](verification.md)

---

## What Distinguishes BONDA

**Live network probes.** Findings are not limited to what the source code suggests is possible. BONDA probes mainnet deployments directly — querying contract state, testing gRPC endpoints, and measuring actual operator behavior — to confirm whether theoretical vulnerabilities are exploitable in production.

**On-chain verification.** Access control configurations, multisig compositions, role assignments, and upgrade mechanisms are verified against live contract state rather than documentation or deployment scripts alone.

**Cross-DA comparison.** The same analytical framework is applied uniformly across four DA protocols, enabling direct comparison of security properties. Common patterns (such as bridge multisig concentration or missing slashing mechanisms) are identified across protocol boundaries.

**Extended threat categories.** Classic STRIDE misses two critical risk classes in DA infrastructure: protocol-level design omissions (no slashing, no DAS) and governance centralization (single-entity multisig control, KYC validator concentration). BONDA's P and G categories capture these systematically.

---

## Scope

BONDA's threat model covers 59 threats across four DA protocols:

| Protocol | Threats | Scope Areas |
|----------|---------|-------------|
| EigenDA | 17 | Disperser, Relay, Operator, governance |
| Celestia | 17 | Consensus, DAS, Blobstream bridge |
| Avail | 14 | VectorX bridge, validator set, governance |
| Ethereum / PeerDAS | 11 | Multi-client PeerDAS, KZG, custody groups |

Each threat is classified by scope: **protocol** (core DA mechanism), **bridge** (L1-L2 communication), **rollup** (rollup-operator-facing surface), or **chain** (base layer consensus).
