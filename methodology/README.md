# Overview

BONDA provides systematic threat modeling for Data Availability (DA) layers that underpin Ethereum's rollup ecosystem. This section describes the analytical framework used to discover, classify, score, and verify threats across Ethereum, EigenDA, Celestia, and Avail.

***

## Why Threat Model DA Layers?

Rollups delegate data publication to DA layers, trusting them to guarantee that transaction data remains retrievable for a defined period. If a DA layer fails silently — through censorship, data withholding, or bridge compromise — rollups built on top of it inherit that failure with no independent recourse.

Despite this critical dependency, most DA layers have not been subjected to structured adversarial analysis. Security audits focus on code correctness but rarely map trust boundaries, governance concentration, or protocol-level design gaps. BONDA fills this gap by applying threat modeling techniques adapted specifically for DA infrastructure.

***

## How can we do?

### 1. Threat Discovery

Each DA protocol is decomposed into a Data Flow Diagram (DFD) with explicit trust boundaries. Potential threats are enumerated using STRIDE-per-element — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege — as a discovery aid that forces every process, data store, data flow, and external entity to be examined. STRIDE is used here to drive enumeration, not as a label attached to findings.

### 2. Threat Classification

Every finding is classified into one of four tiers: **Vulnerability**, **Operational Risk**, **Governance Observation**, or **Design Note**. The tier determines how a finding is treated — whether it carries a CVSS score, whether it sets a structural baseline, or whether it is a live operational measurement. This separation prevents architectural choices and trust-distribution observations from being mislabeled as exploitable bugs.

See: [Threat Classification](classification.md)

### 3. Severity & Scoring

Findings in the Vulnerability tier are scored with CVSS 3.1, the industry-standard framework used by NVD and major audit firms. Across all four tiers, findings feed a 5-axis qualitative risk model — Retrievability, Verifiability, Liveness, Decentralization, Cost Efficiency — that evaluates each DA layer against the same criteria. The 5-axis model is explained here as a methodology; the computed per-DA values and pentagon charts are rendered in the [BONDA dashboard](https://www.bonda.me/)

See: [CVSS 3.1 Scoring](cvss.md) · [5-Axis Risk Scoring](scoring.md)

***

## What Distinguishes BONDA

**Live network probes.** Findings are not limited to what the source code suggests is possible. BONDA probes mainnet deployments directly — querying contract state, testing gRPC endpoints, and measuring actual operator behavior — to confirm whether theoretical vulnerabilities are exploitable in production.

**On-chain verification.** Access control configurations, multisig compositions, role assignments, and upgrade mechanisms are verified against live contract state rather than documentation or deployment scripts alone.

***

## Scope

BONDA's threat model covers 50 findings across four DA protocols:

| Protocol | Findings | Scope Areas                                        |
| -------- | -------- | -------------------------------------------------- |
| Ethereum | 12       | Column custody, sampling, multi-client, fee market |
| EigenDA  | 14       | Disperser, Relay, Operator, governance             |
| Celestia | 12       | Consensus, DAS, Blobstream bridge                  |
| Avail    | 12       | VectorX bridge, validator set, runtime, Kate RPC   |

## Reference

New to blockchain security or DA infrastructure? See the [Terminology](terminology.md) page for definitions of key terms used throughout this documentation.
