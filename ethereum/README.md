# Ethereum DA (PeerDAS)

> **How to Read This Section**
>
> Each threat is identified by an SID like `ETH-R01` and linked to a detailed write-up. Severity scores use [CVSS 3.1](../methodology/cvss.md) on a 0--10 scale. Status indicates verification depth: `verified` means the vulnerability was confirmed through source code analysis at a pinned commit.

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

- **4** threats identified across the Ethereum DA stack
- **1** Medium severity finding (ETH-R02: rate limit bypass)
- **3** Low severity findings (ETH-R01: subgroup check, ETH-R03: incorrect timeout, ETH-R04: thread safety)
- **2** source code repositories analyzed (c-kzg-4844, Prysm)

## Threat Summary

| SID | Threat | Severity | Status |
|-----|--------|----------|--------|
| [ETH-R02](threats/eth-r02.md) | Prysm DataColumnsByRange Rate Limit Bypass | Medium (5.3) | verified |
| [ETH-R01](threats/eth-r01.md) | c-kzg-4844 load\_trusted\_setup Missing Subgroup Check | Low (3.8) | verified |
| [ETH-R03](threats/eth-r03.md) | Prysm DataColumnsByRoot Incorrect Timeout | Low (3.7) | verified |
| [ETH-R04](threats/eth-r04.md) | c-kzg-4844 Go Binding Thread Safety | Low (3.4) | verified |

## Key Findings

### ETH-R01: c-kzg-4844 Missing Subgroup Check -- Low (3.8)

The `load_trusted_setup` function deserializes G1/G2 points without performing subgroup membership checks, while the runtime input path in the same codebase does perform this check. This validation asymmetry means a supply chain attack injecting tampered setup bytes could theoretically break pairing equation soundness, allowing forged proofs to be accepted. Since the setup is embedded at build time, this is not remotely triggerable.

### ETH-R02: Prysm DataColumnsByRange Rate Limit Bypass -- Medium (5.3)

Prysm's `DataColumnsByRange` RPC handler charges a constant cost of 1 to the rate limiter regardless of request size, while the equivalent `DataColumnsByRoot` handler correctly charges the actual number of columns. An unauthenticated P2P peer can exploit this asymmetry to amplify DB lookup and I/O workload on the target node, potentially degrading attestation and sync performance. The leaky bucket provides post-hoc throttling, bounding the impact to initial uncharged work amplification.

### ETH-R04: c-kzg-4844 Go Binding Thread Safety -- Low (3.4)

The c-kzg Go binding uses package-level globals without synchronization primitives, creating data race conditions under concurrent access. While standard usage loads the setup once at startup, the API contract gap means concurrent Load/verify/Free calls can theoretically cause undefined behavior, double initialization, or use-after-free. This is a formal Go memory model violation.

## Referenced Repositories

- [prysm](https://github.com/prysmaticlabs/prysm) -- Go consensus client (Prysmatic Labs)
- [c-kzg-4844](https://github.com/ethereum/c-kzg-4844) -- KZG commitment library
- [consensus-specs](https://github.com/ethereum/consensus-specs) -- Ethereum consensus specifications
- [EIPs](https://github.com/ethereum/EIPs) -- Ethereum Improvement Proposals (EIP-4844, EIP-7594)
