# Ethereum DA (PeerDAS)

> **How to Read This Section**
>
> Each threat is identified by an SID like `ETH-02` and linked to a detailed write-up. Every finding is sorted into one of four [classification](../methodology/classification.md) tiers — Vulnerability, Operational Risk, Governance Observation, or Design Note. Only Vulnerabilities carry a [CVSS 3.1](../methodology/cvss.md) score on a 0--10 scale; the other tiers are qualitative and feed the [5-axis model](../methodology/scoring.md) rather than a numeric severity. Status indicates verification depth: `verified` means the finding was confirmed through source code or specification analysis at a pinned commit or spec revision.

## Architecture

![Ethereum PeerDAS Architecture](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/assets/ethereum-architecture.svg)

## What is PeerDAS?

PeerDAS stands for Peer Data Availability Sampling. It is Ethereum's data availability scaling upgrade activated on mainnet via the Fusaka hard fork on December 3, 2025, defined in EIP-7594. Before PeerDAS, every Ethereum node had to download and store all blob data attached to blocks. PeerDAS changes this by splitting blob data into 128 columns and distributing the storage responsibility across the network. Each validator only needs to hold a small subset of columns rather than the full dataset.

The core mechanism works through custody groups. Every validator is assigned to one or more custody groups based on its node ID. Each custody group is responsible for storing and serving a specific set of data columns. When a validator needs data it does not hold locally, it requests the missing columns from peers in the appropriate custody groups. If enough columns are available, the full data can be reconstructed using erasure coding, a mathematical technique that allows recovery of the original data from any sufficiently large subset of columns.

Ethereum's data availability layer is unique because of its multi-client architecture. Unlike most blockchain networks that rely on a single reference implementation, Ethereum has multiple independent client teams building separate software that must all behave identically. Consensus clients like Lighthouse (written in Rust by Sigma Prime) and Prysm (written in Go by Prysmatic Labs) each implement the PeerDAS specification from scratch. The execution client go-ethereum handles blob transactions and the blobpool. This diversity strengthens the network against single-implementation bugs, but it also introduces the risk of subtle behavioral divergences between clients.

Data integrity in PeerDAS relies on KZG commitments, a cryptographic proof scheme based on polynomial commitments. Each blob is committed using a KZG commitment, and each data column carries a KZG proof that allows any node to verify the column's correctness without downloading the full blob. The KZG scheme depends on a trusted setup ceremony that produced a shared set of cryptographic parameters used by all clients.

## System Components

| Component | Role | Trust Level |
|-----------|------|-------------|
| Beacon Chain | Coordinates consensus, manages validator duties and blob references | Core protocol -- highest trust |
| PeerDAS Network | Distributes data columns across custody groups via peer-to-peer networking | Protocol-level -- depends on honest majority of custody peers |
| KZG Commitments | Provides cryptographic proofs for blob and data column integrity | Cryptographic -- trust depends on trusted setup ceremony |
| Lighthouse | Rust-based consensus client by Sigma Prime; implements PeerDAS spec independently | Implementation -- verified against spec |
| Prysm | Go-based consensus client by Prysmatic Labs; implements PeerDAS spec independently | Implementation -- verified against spec |
| go-ethereum | Primary execution client; handles blob transactions, fee market, and blobpool | Implementation -- verified against spec |
| c-kzg-4844 | KZG commitment library used by all clients for blob/column proof generation and verification | Cryptographic library -- shared dependency |

## Key Numbers

- **12** findings across the Ethereum DA stack
- **4** Vulnerabilities (ETH-01 through ETH-04), all client-implementation or library findings
- **2** Operational Risks (ETH-05 reconstruction dependence, ETH-06 column-subnet eclipse)
- **3** Governance Observations (ETH-07 custody self-reporting, ETH-08 builder/relay concentration, ETH-09 rising resource floor)
- **3** Design Notes that set the PeerDAS baseline (ETH-10 1D coding, ETH-11 custody-based availability, ETH-12 EIP-7918 reserve)

## Threat Summary

| SID | Threat | Category | Severity | Status |
|-----|--------|----------|----------|--------|
| [ETH-01](threats/eth-01.md) | Prysm DataColumnsByRange Rate-Limit Bypass | Vulnerability | Medium (5.3) | verified |
| [ETH-02](threats/eth-02.md) | c-kzg-4844 load\_trusted\_setup Missing Subgroup Check | Vulnerability | Low (3.8) | verified |
| [ETH-03](threats/eth-03.md) | Prysm DataColumnsByRoot Incorrect Timeout | Vulnerability | Low (3.7) | verified |
| [ETH-04](threats/eth-04.md) | c-kzg-4844 Go Binding Thread Safety | Vulnerability | Low (3.4) | verified |
| [ETH-05](threats/eth-05.md) | Reconstruction Depends on Half-Column Holders | Operational Risk | Medium | verified |
| [ETH-06](threats/eth-06.md) | Per-Column Subnet Eclipse | Operational Risk | Medium | verified |
| [ETH-07](threats/eth-07.md) | Self-Reported Custody Count Unverifiable | Governance Observation | — | verified |
| [ETH-08](threats/eth-08.md) | Builder/Relay Publication Concentration | Governance Observation | — | verified |
| [ETH-09](threats/eth-09.md) | Rising Node Resource Floor as Blobs Scale | Governance Observation | — | verified |
| [ETH-10](threats/eth-10.md) | One-Dimensional Erasure Coding | Design Note | — | verified |
| [ETH-11](threats/eth-11.md) | Fork-Choice Rests on Custody, Not Sampling | Design Note | — | verified |
| [ETH-12](threats/eth-12.md) | EIP-7918 Blob Fee Reserve | Design Note | — | verified |

## Key Findings

### ETH-01: Prysm DataColumnsByRange Rate-Limit Bypass -- Vulnerability, Medium (5.3)

Prysm's `DataColumnsByRange` RPC handler charges a constant cost of 1 to the rate limiter regardless of request size, while the equivalent `DataColumnsByRoot` handler correctly charges the actual number of columns. An unauthenticated P2P peer can exploit this asymmetry to amplify DB lookup and I/O workload on the target node, potentially degrading attestation and sync performance. The leaky bucket provides post-hoc throttling, bounding the impact to initial uncharged work amplification.

### ETH-11: Fork-Choice Rests on Custody, Not Sampling -- Design Note

The deployed PeerDAS fork-choice availability check verifies the column sidecars a node has retrieved for its own custody and confirms their KZG proofs. It does not invoke a probabilistic peer-sampling routine, so a node's availability decision rests on its custody set and KZG verification rather than randomized sampling. This is the documented basis of the Ethereum verifiability baseline and carries no score.

### ETH-05: Reconstruction Depends on Half-Column Holders -- Operational Risk, Medium

Full-data reconstruction requires at least 50 percent of the 128 columns, so recovery in practice leans on nodes that custody many columns, including supernodes. When such nodes are absent for a given block, the network may hold enough columns collectively yet still be unable to reconstruct without coordination. This is tracked as an operational indicator alongside the risk pentagon, not a deduction from the structural score.

## Referenced Repositories

- [prysm](https://github.com/prysmaticlabs/prysm) -- Go consensus client (Prysmatic Labs)
- [c-kzg-4844](https://github.com/ethereum/c-kzg-4844) -- KZG commitment library
- [consensus-specs](https://github.com/ethereum/consensus-specs) -- Ethereum consensus specifications
- [EIPs](https://github.com/ethereum/EIPs) -- Ethereum Improvement Proposals (EIP-4844, EIP-7594)
