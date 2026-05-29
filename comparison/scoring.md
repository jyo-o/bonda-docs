# BVSS Scoring Comparison

This page compares BVSS (Blockchain Vulnerability Severity Score) results across EigenDA, Avail, and Ethereum/PeerDAS. Celestia is excluded from BVSS comparisons because its threats were assessed using qualitative severity labels rather than numeric BVSS scoring.

## Scoring Methodology Note

BVSS 1.1 (Halborn) uses the formula:

```
Score = B + (10 - B) * AV * AC * PR * UI * S * ISS
```

Where B = Base (blockchain-specific loss metric, e.g., fund theft) and ISS accounts for Confidentiality, Integrity, and Availability impact weighted by blockchain-specific impact modifiers (CI, II, AI).

For DA-layer threats, B is almost always N (None) because DA layers do not directly custody funds. This means the maximum achievable score is bounded by the ISS component, and scores above 7.0 are rare.

## Top 10 Threats by BVSS Score

| Rank | Score | SID | DA Protocol | Severity | Description |
|---|---|---|---|---|---|
| 1 | 8.4 | AVL-E03 | Avail | High | Deployer EOA retains DEFAULT_ADMIN_ROLE, enabling solo VectorX upgrade |
| 2 | 8.2 | ETH-E01 | Ethereum | High | Reconstruction failure mode mismatch between Lighthouse and Prysm |
| 3 | 7.0 | EDA-T09 | EigenDA | High | Ejector role abuse can forcibly remove honest operators (33%/3 days) |
| 4 | 6.6 | EDA-D06 | EigenDA | Medium | Relay single point of failure (1 relay on mainnet) |
| 5 | 6.6 | AVL-D01 | Avail | Medium | VectorX single relayer SPOF with no on-chain heartbeat |
| 6 | 6.5 | EDA-E03 | EigenDA | Medium | Operator stake concentration exceeds safety/liveness thresholds |
| 7 | 5.9 | EDA-P02 | EigenDA | Medium | No DAS implementation, clients must trust quorum entirely |
| 8 | 5.9 | EDA-P01 | EigenDA | Medium | Operator slashing not implemented, asymmetric incentives |
| 9 | 5.3 | G-CON-03 | EigenDA | Medium | Operator infrastructure concentrated in few cloud providers |
| 10 | 5.3 | EDA-D03 | EigenDA | Medium | Disperser V2 KZG compute surface exposed without authentication |

EigenDA dominates the top 10 (7 of 10 entries) because its threats target protocol-level design decisions (no slashing, no DAS, single relay) that have broad impact even when attack complexity is high.

The two highest-scoring threats (AVL-E03 at 8.4, ETH-E01 at 8.2) both involve Scope Change (S:C) in the BVSS vector, which amplifies the score by accounting for cross-system impact.

## Average BVSS Score per DA

| DA Protocol | Average | Min | Max | Threat Count |
|---|---|---|---|---|
| EigenDA | 3.6 | 0.6 | 7.0 | 17 |
| Ethereum / PeerDAS | 3.0 | 0.8 | 8.2 | 11 |
| Avail | 2.8 | 0.0 | 8.4 | 14 |
| Celestia | N/A | N/A | N/A | 19 (severity labels only) |

EigenDA's higher average reflects more protocol-level design threats with lower attack complexity (e.g., EDA-D06 relay SPOF is AC:L). Avail's lower average is driven by many bridge-layer threats that require multisig key compromise (AC:H, AV:P), which heavily penalizes the BVSS score.

## BVSS Severity Distribution

| Severity | EigenDA | Avail | Ethereum | Total |
|---|---|---|---|---|
| Critical (9.0-10.0) | 0 | 0 | 0 | 0 |
| High (7.0-8.9) | 1 | 1 | 1 | 3 |
| Medium (4.0-6.9) | 6 | 3 | 1 | 10 |
| Low (0.1-3.9) | 10 | 9 | 9 | 28 |
| Informational (0.0) | 0 | 1 | 0 | 1 |

No threats reach BVSS Critical because the Base component (B) is N for all findings -- DA layers do not directly custody user funds. The theoretical maximum score with B:N is approximately 9.0, but practical scores are lower because most threats require elevated privileges or have high attack complexity.

## Celestia Severity Note

Celestia's 19 threats were assessed with qualitative severity labels:

| Severity | Count |
|---|---|
| Critical | 2 |
| High | 5 |
| Medium | 5 |
| Low | 4 |
| Informational | 3 |

The two Critical findings are:
- **CEL-E01**: SP1Blobstream 4-of-6 multisig with no timelock, controlling the DA attestation bridge to Ethereum.
- **G-CON-01**: KYC validator concentration enabling legal censorship via court orders against 6-8 regulated entities.

These use expert judgment rather than the BVSS formula, so direct numeric comparison with other protocols is not meaningful. The qualitative assessment accounts for factors that BVSS does not fully capture, such as regulatory attack vectors and documentation integrity issues.
