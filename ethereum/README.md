# Ethereum DA (PeerDAS)

Ethereum's data availability layer is evolving through EIP-4844 (Proto-Danksharding) and PeerDAS (Peer Data Availability Sampling). Blobs are committed using KZG polynomial commitments and distributed across the peer-to-peer network as data columns. PeerDAS, activated in the Fulu fork, introduces column-level sampling where nodes are assigned custody groups based on their node ID and are responsible for storing and serving specific data columns. Reconstruction of the full data from a subset of columns uses erasure coding.

Ethereum DA is unique in its multi-client architecture: multiple independent consensus client implementations (Lighthouse, Prysm, Teku, Lodestar, Nimbus) must maintain behavioral consistency for network health. This analysis covers cross-client divergences, KZG verification mechanics, and blob/column lifecycle threats.

## Architecture

![Ethereum DA Architecture](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/assets/ethereum-architecture.svg)

## Threat Summary

11 threats identified through multi-client source code analysis (go-ethereum, Lighthouse, Prysm), consensus-specs review, and c-kzg-4844 verification. All threats are scored using the Halborn BVSS 1.1 framework.

| SID | Threat | Severity | Status |
|-----|--------|----------|--------|
| [ETH-E01](threats/eth-e01.md) | Reconstruction Failure Mode Mismatch Between Lighthouse and Prysm | High (8.2) | code_verified |
| [ETH-T02](threats/eth-t02.md) | KZG Trusted Setup File Replacement | Medium (4.2) | code_verified |
| [ETH-S02](threats/eth-s02.md) | Custody Group Node ID Grinding | Low (3.5) | code_verified |
| [ETH-T03](threats/eth-t03.md) | Gloas Data Column Inclusion Proof Omission | Low (3.5) | partial |
| [ETH-T05](threats/eth-t05.md) | Gloas Column Proof Verification | Low (3.5) | partial |
| [ETH-D02](threats/eth-d02.md) | Reconstruction Failure Discards All Verified Columns (Lighthouse) | Low (3.5) | code_verified |
| [ETH-S01](threats/eth-s01.md) | Testing API JWT Authentication Not Applied | Low (2.8) | code_verified |
| [ETH-R01](threats/eth-r01.md) | Blob/DataColumn Equivocation Detection Failure | Low (1.1) | code_verified |
| [ETH-T01](threats/eth-t01.md) | Blob Fee Denominator Fork-Dependent Formula | Low (0.8) | code_verified |
| [ETH-T04](threats/eth-t04.md) | Cell Index Bounds Check Asymmetry | Low (0.8) | code_verified |
| [ETH-D01](threats/eth-d01.md) | Per-Account Blobpool Exhaustion via 1-Wei Fee | Low (0.8) | verified |

## Key Findings

### ETH-E01: Reconstruction Failure Mode Mismatch (High, BVSS 8.2)

The most significant finding is a behavioral divergence between Lighthouse and Prysm in handling data column reconstruction failures:

- **Lighthouse:** On reconstruction failure, deletes ALL columns (including previously verified ones), requiring O(N/2) re-download. Found in `overflow_lru_cache.rs`.
- **Prysm:** On reconstruction failure, marks reconstructed columns as verified WITHOUT re-verification.

This cross-client inconsistency affects the primary DA path in Fulu where reconstruction is a core mechanism. A single malicious column can trigger divergent behavior across the network: Lighthouse nodes waste bandwidth re-downloading valid data, while Prysm nodes may accept unverified data as valid. This threatens both consensus safety and data recoverability invariants.

### ETH-D02: Verified Column Discard on Reconstruction Failure (Low, BVSS 3.5)

Specific to Lighthouse: when reconstruction fails due to even 1 bad column out of 64+ verified columns, the entire set is discarded. This is a Lighthouse-specific manifestation of the broader ETH-E01 cross-client issue, causing unnecessary bandwidth overhead and temporary availability degradation.

### ETH-S02: Custody Group Node ID Grinding (Low, BVSS 3.5)

PeerDAS custody group assignment is deterministically derived from `node_id`. An attacker with sufficient computing resources could brute-force node IDs that concentrate custody on specific data columns, potentially undermining the availability of those columns. The practical impact is bounded by the number of custody groups and the cost of grinding.

### ETH-T03 / ETH-T05: Gloas Future Fork Considerations (Low, BVSS 3.5)

Two threats relate to the Gloas fork (currently unscheduled): data column inclusion proof omission and column proof verification gaps. These have no immediate impact but represent design considerations that need resolution before Gloas activation.

## Multi-Client Divergence Emphasis

Ethereum's multi-client architecture is both its greatest strength (resilience through diversity) and a source of subtle security risks. The ETH-E01 finding demonstrates that even well-tested clients can diverge on edge-case behavior in ways that threaten network-level properties. Key observations:

- Reconstruction is the **primary DA path** in Fulu -- divergent failure handling directly impacts DA guarantees
- Equivocation detection (ETH-R01) produces IGNORE rather than slashing evidence, missing an opportunity for accountability
- Bounds checking asymmetry (ETH-T04) between `recover_cells_and_kzg_proofs` and `verify_cell_kzg_proof_batch` represents a defense-in-depth gap

## Referenced Repositories

- [go-ethereum](https://github.com/ethereum/go-ethereum) -- Execution layer client
- [lighthouse](https://github.com/sigp/lighthouse) -- Rust consensus client (Sigma Prime)
- [prysm](https://github.com/prysmaticlabs/prysm) -- Go consensus client (Prysmatic Labs)
- [consensus-specs](https://github.com/ethereum/consensus-specs) -- Ethereum consensus specifications
- [c-kzg-4844](https://github.com/ethereum/c-kzg-4844) -- KZG commitment library
- [EIPs](https://github.com/ethereum/EIPs) -- Ethereum Improvement Proposals (EIP-4844, EIP-7594, EIP-7918)
