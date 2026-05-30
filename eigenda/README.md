# EigenDA

> **How to Read This Section**
> This page introduces EigenDA's architecture and summarizes all 13 identified threats. Each threat ID links to a dedicated page with full analysis, evidence, and scoring details. Start here for the big picture, then dive into individual threats as needed.

## Architecture

![EigenDA Architecture](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/assets/eigenda-architecture.svg)

## Architecture Introduction

EigenDA is a data availability (DA) system built as an Actively Validated Service (AVS) on EigenLayer. Operators who have restaked ETH or EIGEN on EigenLayer can opt into EigenDA to store and serve data on behalf of rollups and other consumers.

The core workflow is blob dispersal. A client submits a blob to the Disperser, which is a centralized service that erasure-codes the data into smaller chunks. The Disperser distributes these chunks across registered operators, collects their BLS signatures, aggregates them into a single aggregate signature, and produces a DA certificate. This certificate is then verified on-chain to confirm that a sufficient quorum of operators attested to holding the data.

Retrieval works through a Relay, which serves stored blobs to clients on demand. If the Relay is unavailable, clients can fall back to requesting chunks directly from individual operators using the GetChunks endpoint and reconstructing the blob locally.

One important architectural note: EigenDA does not implement Data Availability Sampling (DAS). Unlike systems where light nodes independently verify data availability through random sampling, EigenDA clients rely entirely on quorum-based BLS aggregate signatures. If the required stake threshold (55%) signs off on a blob, it is considered available. There is no independent cryptographic sampling mechanism.

## System Components

| Component | Role | Trust Level |
|-----------|------|-------------|
| Disperser | Receives blobs from clients, erasure-codes them into chunks, distributes chunks to operators, and collects BLS signatures into DA certificates | Centralized, trusted operator (run by EigenLabs) |
| Relay | Serves stored blobs to clients for retrieval; primary read path | Centralized, single instance on mainnet |
| Operators | Store assigned chunks and produce BLS signatures attesting to data availability | Semi-trusted; rely on restaked collateral and quorum thresholds |
| DA Proxy | Sidecar that translates rollup DA calls into EigenDA API calls | Untrusted edge component; no authentication on POST endpoints |
| EigenDA Core Contracts | On-chain verification of DA certificates, quorum configuration, and operator registration | Controlled by a single 3-of-4 multisig |
| EigenLayer AVS | Manages operator restaking, delegation, and quorum membership for EigenDA | Shared trust layer across all AVSs |
| EjectionManager | Allows forced removal of operators from quorums within configurable stake and rate limits | Controlled by a single EOA |

## Key Numbers

| Metric | Value |
|--------|-------|
| Total threats identified | 13 |
| Verification status | 11 verified, 2 code_verified |
| Highest severity | High (CVSS 7.5) |
| Registered operators | 272 |
| Dead operators (0% chunk serving) | 11 |
| Relay instances on mainnet | 1 |
| Core contract governance | Single 3-of-4 multisig controls 8 contracts |

## Threat Summary

| SID | Threat | Severity | Status |
|-----|--------|----------|--------|
| [EDA-D06](threats/eda-d06.md) | Relay Single Point of Failure (1 Mainnet Instance) | High (7.5) | verified |
| [EDA-T09](threats/eda-t09.md) | Ejector Role Abuse to Remove Honest Operators | High (7.1) | verified |
| [EDA-E03](threats/eda-e03.md) | Operator Stake Concentration Exceeding Safety Thresholds | Medium (6.5) | verified |
| [EDA-P01](threats/eda-p01.md) | Operator Slashing Not Implemented | Medium (6.5) | verified |
| [EDA-P02](threats/eda-p02.md) | DAS Absent, Clients Fully Depend on Quorum Trust | Medium (6.5) | code_verified |
| [EDA-E02](threats/eda-e02.md) | Single 3-of-4 Multisig Controls 8 Core Contracts | Medium (6.3) | verified |
| [EDA-D03](threats/eda-d03.md) | Disperser V2 KZG Compute Exposed Without Auth | Medium (5.9) | verified |
| [EDA-G01](threats/eda-g01.md) | Operator Infrastructure Concentration | Medium (5.9) | verified |
| [EDA-D07](threats/eda-d07.md) | GetBlob No Authentication | Medium (5.3) | verified |
| [EDA-D12](threats/eda-d12.md) | 11 Dead Operators, 0% Chunk Serving | Medium (5.3) | verified |
| [EDA-E01](threats/eda-e01.md) | DisableAnchorSignatureVerification Flag Bypass | Medium (4.0) | code_verified |
| [EDA-D02](threats/eda-d02.md) | Proxy Rate Limit Absence | Low (3.7) | code_verified |
| [EDA-S03](threats/eda-s03.md) | Cross-chain Signature Replay | Low (3.5) | verified |

## Key Findings

### EDA-T09: Ejector Role Abuse (High, CVSS 7.1)

The EjectionManager contract allows a single EOA address to forcibly remove up to 33.33% of quorum stake within a 3-day rolling window. On-chain data shows 150 ejection transactions from just 2 EOA addresses over 16 months. This matters because ejection is currently the only enforcement mechanism in EigenDA, since slashing has not been implemented. A compromised or malicious ejector key could systematically remove honest operators from quorums, degrading data availability guarantees with no on-chain recourse for the ejected parties.

### EDA-E03: Operator Stake Concentration (Medium, CVSS 6.5)

On-chain verification confirmed that stake is dangerously concentrated. In quorum Q0 (ETH), the top 3 operators hold 39.8% of stake, exceeding the 33% safety threshold. In Q1 (EIGEN), the top 3 hold 35.6% and the top 5 hold 51.7%, breaching both the safety and liveness thresholds. In Q2 (Custom), a single entity (AltLayer) holds 52.6% alone. This means a Nakamoto coefficient of just 3: three colluding operators could compromise safety guarantees across the system.

### EDA-D06: Relay Single Point of Failure (High, CVSS 7.5)

The on-chain RelayRegistry shows only one relay registered on mainnet. The Relay is the primary read path for blob retrieval, meaning all clients depend on this single instance to access stored data. If the Relay goes down, retrieval degrades to the slower operator-direct GetChunks fallback, where clients must contact individual operators and reconstruct blobs from chunks. This single point of failure creates an availability bottleneck for every consumer of EigenDA.

### EDA-P01: Slashing Not Implemented (Medium, CVSS 6.5)

No slash or freeze functions exist in EigenDA's core contracts. The EigenLayer AllocationManager returns zero operator sets for EigenDA, confirming that the slashing infrastructure is entirely absent. Operators earn restaking rewards but face no penalty for dishonest behavior such as failing to store chunks or producing false attestations. This incentive asymmetry directly contributes to the 11 dead operators observed in EDA-D12, who remain registered and collect rewards while serving 0% of their assigned chunks.

## Monitoring

For live metrics on operator availability, relay health, blob dispersal success rates, and stake distribution, see the [monitoring dashboard](monitoring.md).
