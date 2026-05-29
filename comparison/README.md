# Cross-DA Comparison

This section compares threat modeling results across all four Data Availability protocols assessed by BONDA: EigenDA, Celestia, Avail, and Ethereum (PeerDAS).

All statistics are derived from the 61 threats identified across the four protocols.

## Threat Count Summary

| DA Protocol | Threats | BVSS Scored | Severity Labels Only |
|---|---|---|---|
| EigenDA | 17 | 17 | 0 |
| Celestia | 19 | 0 | 19 |
| Avail | 14 | 14 | 0 |
| Ethereum / PeerDAS | 11 | 11 | 0 |
| **Total** | **61** | **42** | **19** |

Celestia threats use qualitative severity labels rather than BVSS numeric scores, as the Celestia assessment was conducted as a gap analysis and code audit rather than a structured BVSS scoring exercise.

## Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| Critical | 0 | 2 | 0 | 0 | 2 |
| High | 1 | 5 | 1 | 1 | 8 |
| Medium | 6 | 5 | 3 | 1 | 15 |
| Low | 10 | 4 | 9 | 9 | 32 |
| Informational | 0 | 3 | 1 | 0 | 4 |

EigenDA and Avail skew toward Low severity because BVSS scoring accounts for attack complexity (multisig thresholds, physical access requirements). Celestia has the highest concentration of Critical/High findings due to governance-layer structural issues (CEL-E01 SP1Blobstream multisig, G-CON-01 KYC validator concentration).

## Verification Status Distribution

| Status | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| verified | 11 | 6 | 12 | 1 | 30 |
| code_verified | 5 | 10 | 0 | 8 | 23 |
| poc_verified | 0 | 2 | 0 | 0 | 2 |
| partial | 1 | 1 | 0 | 2 | 4 |
| unverified | 0 | 0 | 2 | 0 | 2 |

- **verified**: On-chain data, mainnet probes, or live PoC confirm the finding.
- **code_verified**: Source code analysis confirms the vulnerability path; mainnet exploitation not tested.
- **poc_verified**: A reproducible proof-of-concept (unit test or local fork) demonstrates the issue.
- **partial**: Some evidence exists but full verification is incomplete.

EigenDA has the highest `verified` rate (11/17 = 65%) due to extensive on-chain probing and mainnet PoCs. Avail also shows strong verification (12/14 = 86%) through systematic `cast` on-chain calls.

## STRIDE Category Distribution

| STRIDE Category | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| Denial of Service | 7 | 13 | 2 | 2 | 24 |
| Tampering | 2 | 1 | 5 | 5 | 13 |
| Elevation of Privilege | 3 | 1 | 4 | 1 | 9 |
| Spoofing | 1 | 1 | 1 | 2 | 5 |
| Protocol Design | 2 | 1 | 0 | 0 | 3 |
| Governance | 1 | 2 | 0 | 0 | 3 |
| Information Disclosure | 1 | 0 | 1 | 0 | 2 |
| Repudiation | 0 | 0 | 1 | 1 | 2 |

Denial of Service dominates across all protocols (24/61 = 39%), which is expected for DA layers where availability is the core security property. Celestia has an outsized DoS count (13/19 = 68%) due to multiple memory exhaustion vectors in celestia-core and celestia-node (TxCache leak, pendingSeenTracker, blacklistedHashes).

Tampering threats concentrate in Avail (5) and Ethereum (5), reflecting concerns around bridge upgrade paths (Avail) and data column verification gaps (Ethereum PeerDAS).

## Scope Distribution

| Scope | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| protocol | 10 | 9 | 0 | 11 | 30 |
| bridge | 4 | 1 | 9 | 0 | 14 |
| implementation | 0 | 9 | 0 | 0 | 9 |
| rollup | 3 | 0 | 0 | 0 | 3 |
| chain | 0 | 0 | 5 | 0 | 5 |

- **protocol**: Affects the DA protocol's core security properties.
- **bridge**: Affects the L1-L2 attestation bridge (Blobstream, VectorX, EigenDA ServiceManager).
- **implementation**: Code-level bugs in a specific client (celestia-core, celestia-node).
- **rollup**: Affects rollup operators using the DA layer (e.g., proxy sidecar issues).
- **chain**: Affects the DA chain's consensus or staking layer (Avail NPoS).

Celestia's scope splits evenly between protocol-level design issues and implementation-level code bugs. Avail's threats concentrate in the bridge layer (9/14), reflecting the VectorX/SP1Vector trust surface as the primary attack vector for Ethereum-side DA verification.
