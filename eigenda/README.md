# EigenDA

> **How to Read This Section**
> This page introduces EigenDA's architecture and summarizes all 14 findings. Each finding is sorted into one of four [classification](../methodology/classification.md) tiers — Vulnerability, Operational Risk, Governance Observation, or Design Note. Only Vulnerabilities carry a [CVSS 3.1](../methodology/cvss.md) score; the other tiers are qualitative and feed the [5-axis model](../methodology/scoring.md). Each SID links to a dedicated page with full analysis and evidence.

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
| Total findings | 14 |
| Verification status | 11 verified, 3 poc_verified |
| Highest severity | High (CVSS 8.6) |
| Registered operators | 272 |
| Dead operators (0% chunk serving) | 11 |
| Relay instances on mainnet | 1 |
| Core contract governance | Single 3-of-4 multisig controls 8 contracts |

## Threat Summary

| SID | Threat | Category | Severity | Status |
|-----|--------|----------|----------|--------|
| [EDA-01](threats/eda-01.md) | Unauthenticated GetChunks Cold-Miss CPU Exhaustion | Vulnerability | High (8.6) | poc_verified |
| [EDA-02](threats/eda-02.md) | Disperser V2 KZG Compute Exposed Without Auth | Vulnerability | High (8.6) | poc_verified |
| [EDA-03](threats/eda-03.md) | Cross-Chain Signature Replay | Vulnerability | Low (3.5) | verified |
| [EDA-04](threats/eda-04.md) | Relay Single Point of Failure (1 Mainnet Instance) | Operational Risk | High | verified |
| [EDA-05](threats/eda-05.md) | GetBlob Global-Only Rate Limiting | Operational Risk | High | poc_verified |
| [EDA-06](threats/eda-06.md) | Dead Operators Serving Zero Chunks | Operational Risk | Medium | verified |
| [EDA-07](threats/eda-07.md) | Single Multisig Controls All Core Contracts | Governance Observation | — | verified |
| [EDA-08](threats/eda-08.md) | Ejector Role Can Force-Remove Honest Operators | Governance Observation | — | verified |
| [EDA-09](threats/eda-09.md) | Operator Stake Concentration | Governance Observation | — | verified |
| [EDA-10](threats/eda-10.md) | Anchor Signature Verification Disable Flag | Governance Observation | — | verified |
| [EDA-11](threats/eda-11.md) | Operator Slashing Not Implemented | Design Note | — | verified |
| [EDA-12](threats/eda-12.md) | No Data Availability Sampling | Design Note | — | verified |
| [EDA-13](threats/eda-13.md) | Proxy HTTP Server Missing Rate Limiting | Design Note | — | verified |
| [EDA-14](threats/eda-14.md) | Operator Infrastructure Concentration | Design Note | — | verified |

## Key Findings

### EDA-01: Unauthenticated GetChunks Cold-Miss CPU Exhaustion (Vulnerability, CVSS 8.6)

The operator `GetChunks` read path is unauthenticated, and a cold cache miss returns without debiting a rate-limit token. A single attacker sustains roughly 4.5 cores of work per targeted operator by requesting chunks that miss the cache, driving operators toward missing the 67% confirmation threshold. Because no credential or payment is required and the cost is algorithmic, front-tier rate limits do not contain it.

### EDA-02: Disperser V2 KZG Compute Exposed Without Auth (Vulnerability, CVSS 8.6)

The `GetBlobCommitment` endpoint computes full KZG commitments (G1 + 2xG2 MSM) for any caller with no authentication or prepayment, and is enabled by default. A single 16 MiB request costs about 14 core-seconds, so a few concurrent callers saturate the Disperser. The endpoint was confirmed live and anonymously callable on Mainnet and every test environment, and the request context is not propagated to the computation, so client-side timeouts and WAF/CDN filtering do not stop the work.

### EDA-07: Single Multisig Controls All Core Contracts (Governance Observation)

A single 3-of-4 EOA Gnosis Safe owns eight core contracts and, through one shared ProxyAdmin, can upgrade any of twelve proxies in a single transaction with no timelock. The same multisig set the dominant disperser's reservation, which it can revoke to instantly halt 98.65% of mainnet traffic. This is the concentration baseline recorded against the Decentralization axis; it carries no score.

### EDA-11: Slashing Not Implemented (Design Note)

No slash or freeze functions exist in EigenDA's core contracts, and the EigenLayer AllocationManager returns zero operator sets for EigenDA, confirming the slashing infrastructure is absent. Operators earn restaking rewards but face no penalty for dishonest behavior, an incentive asymmetry that underlies the dead operators observed in EDA-06. As an acknowledged property of the deployed design, it sets the baseline rather than deducting from the score.

## Verification Evidence

On-chain contract queries, operator stake distribution data, ASN infrastructure analysis, and prober measurement results are documented in [Verification Evidence](evidence.md).

## Monitoring

For live metrics on operator availability, relay health, blob dispersal success rates, and stake distribution, see the [monitoring dashboard](monitoring.md).
