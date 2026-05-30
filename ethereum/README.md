# Ethereum DA (PeerDAS)

> **How to Read This Section**
>
> Each threat is identified by an SID like `ETH-S01` and linked to a detailed write-up. Severity scores use [CVSS 3.1](../methodology/cvss.md) on a 0--10 scale. Status indicates verification depth: `verified` means confirmed through specification and documentation review, `code_verified` means confirmed by reading the actual source code, and `partial` means the threat is identified but not yet fully verified across all relevant implementations.

## Architecture

![Ethereum PeerDAS Architecture](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/assets/ethereum-architecture.svg)

## What is PeerDAS?

PeerDAS stands for Peer Data Availability Sampling. It is Ethereum's upcoming data availability scaling upgrade, defined in EIP-7594. Before PeerDAS, every Ethereum node had to download and store all blob data attached to blocks. PeerDAS changes this by splitting blob data into 128 columns and distributing the storage responsibility across the network. Each validator only needs to hold a small subset of columns rather than the full dataset.

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
| Blobpool | Transaction pool within go-ethereum that manages pending blob-carrying transactions | Subsystem -- bounded by per-account and global limits |

## Key Numbers

- **11** threats identified across the Ethereum DA stack
- **6** verified through specification and documentation review
- **3** code_verified through direct source code analysis
- **2** partial, identified but not yet fully verified across all implementations
- **Medium (5.3)** is the highest severity found
- **6** source code repositories analyzed
- **1** multi-client behavioral divergence discovered (ETH-E01: Lighthouse vs Prysm)

> **Note on Multi-Client Analysis**
>
> The Ethereum section is the only part of BONDA that performs cross-client divergence analysis. Because PeerDAS is implemented independently by multiple teams, threats can emerge not just from specification gaps but from differences in how separate codebases handle the same edge cases. ETH-E01 is a direct result of this analysis approach.

## Threat Summary

| SID | Threat | Severity | Status |
|-----|--------|----------|--------|
| [ETH-S01](threats/eth-s01.md) | Testing API JWT Authentication Missing | Medium (5.3) | verified |
| [ETH-S02](threats/eth-s02.md) | Custody Group Node ID Grinding | Medium (5.3) | verified |
| [ETH-T01](threats/eth-t01.md) | Blob Fee Denominator Fork Dependency | Low (3.7) | code_verified |
| [ETH-T02](threats/eth-t02.md) | KZG Trusted Setup File Replacement | Low (2.5) | verified |
| [ETH-T03](threats/eth-t03.md) | Data Column Inclusion Proof Omission | Low (2.5) | code_verified |
| [ETH-T04](threats/eth-t04.md) | Cell Index Bounds Check Asymmetry | Low (1.3) | verified |
| [ETH-T05](threats/eth-t05.md) | Column Proof Verification Gap | Low (1.3) | verified |
| [ETH-R01](threats/eth-r01.md) | Blob/DataColumn Equivocation Detection Failure | Low (0.8) | verified |
| [ETH-D01](threats/eth-d01.md) | Per-Account Blobpool Exhaustion | Low (0.8) | code_verified |
| [ETH-D02](threats/eth-d02.md) | Verified Column Discard on Reconstruction Failure | Low (0.6) | partial |
| [ETH-E01](threats/eth-e01.md) | Reconstruction Failure Mode Mismatch (Lighthouse vs Prysm) | Low (0.6) | partial |

## Key Findings

### ETH-S01: Testing API JWT Authentication Missing -- Medium (5.3)

The Beacon Chain testing API endpoints lack JWT authentication enforcement in certain configurations. These endpoints expose internal state and control surfaces intended only for development and testing. If a node operator inadvertently leaves the testing API accessible in a production environment, an attacker on the same network could invoke privileged operations without authentication. The severity reflects the realistic deployment scenario where testing APIs are disabled by default but occasionally left enabled during debugging.

### ETH-S02: Custody Group Node ID Grinding -- Medium (5.3)

PeerDAS custody group assignment is deterministic: a validator's node ID directly determines which data columns it must store and serve. An attacker with sufficient computing resources could generate node IDs that concentrate custody on specific columns, potentially degrading the availability of those columns by flooding the corresponding custody groups with attacker-controlled nodes. The practical cost of this attack is bounded by the number of custody groups and the computational difficulty of ID grinding, but the deterministic assignment means the attack surface is structurally permanent.

### ETH-E01: Reconstruction Failure Mode Mismatch -- Medium (5.4)

This finding is a cross-client behavioral divergence between Lighthouse and Prysm in handling data column reconstruction failures. When reconstruction fails, Lighthouse discards all columns including previously verified ones, forcing a complete re-download. Prysm takes the opposite approach, marking reconstructed columns as verified without re-verifying them. Neither behavior is specified in the consensus-specs, meaning both clients are making independent design choices on an unspecified edge case. This divergence demonstrates the type of cross-client inconsistency that can emerge when multiple teams implement the same underspecified protocol.

## Referenced Repositories

- [go-ethereum](https://github.com/ethereum/go-ethereum) -- Execution layer client
- [lighthouse](https://github.com/sigp/lighthouse) -- Rust consensus client (Sigma Prime)
- [prysm](https://github.com/prysmaticlabs/prysm) -- Go consensus client (Prysmatic Labs)
- [consensus-specs](https://github.com/ethereum/consensus-specs) -- Ethereum consensus specifications
- [c-kzg-4844](https://github.com/ethereum/c-kzg-4844) -- KZG commitment library
- [EIPs](https://github.com/ethereum/EIPs) -- Ethereum Improvement Proposals (EIP-4844, EIP-7594)
