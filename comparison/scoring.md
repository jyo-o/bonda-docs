# CVSS 3.1 Scoring Comparison

This page compares CVSS 3.1 scoring results across all four DA protocols assessed by BONDA.

## Scoring Methodology Note

CVSS 3.1 uses the standard formula defined by [FIRST](https://www.first.org/cvss/specification-document):

```
ISS = 1 - [(1-C)(1-I)(1-A)]
Exploitability = 8.22 x AV x AC x PR x UI
Score = min(Impact + Exploitability, 10) or min(1.08 x (Impact + Exploitability), 10) for Changed scope
```

Scores can be verified using the [NIST CVSS Calculator](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator).

## Top 10 Threats by CVSS Score

| Rank | Score | SID | DA Protocol | Severity | Description |
|---|---|---|---|---|---|
| 1 | 8.7 | CEL-G01 | Celestia | High | KYC validator concentration enabling legal censorship (>1/3 threshold) |
| 2 | 8.2 | AVL-E03 | Avail | High | Deployer EOA retains DEFAULT_ADMIN_ROLE, enabling solo VectorX upgrade |
| 3 | 7.7 | CEL-E01 | Celestia | High | SP1Blobstream instant upgrade by 4-of-6 multisig, no timelock |
| 4 | 7.5 | EDA-D06 | EigenDA | High | Relay single point of failure (1 relay on mainnet) |
| 5 | 7.5 | AVL-D01 | Avail | High | VectorX single relayer SPOF with no on-chain heartbeat |
| 6 | 7.5 | CEL-D13 | Celestia | High | Commitment computation before gas metering in CheckTx |
| 7 | 7.5 | CEL-D17 | Celestia | High | TxCache key mismatch causing permanent cache leak |
| 8 | 7.1 | EDA-T09 | EigenDA | High | Ejector role abuse can forcibly remove honest operators |
| 9 | 6.5 | CEL-P01 | Celestia | Medium | DAS-only safety model after fraud proof removal |
| 10 | 6.5 | EDA-E03 | EigenDA | Medium | Top 3 operators hold 39.8% of stake, exceeding 33% safety threshold |

The two highest-scoring threats (CEL-G01 at 8.7, AVL-E03 at 8.2) both involve Scope Change (S:C), which amplifies the score by accounting for cross-system impact cascading to dependent rollups and bridges.

## Average CVSS Score per DA

| DA Protocol | Average | Min | Max | Scored / Total |
|---|---|---|---|---|
| Celestia | 6.1 | 3.7 | 8.7 | 12 / 12 |
| EigenDA | 6.1 | 3.5 | 7.5 | 13 / 13 |
| Avail | 4.9 | 2.1 | 8.2 | 9 / 9 |
| Ethereum / PeerDAS | 5.3 | 5.3 | 5.3 | 1 / 4 |

Celestia's higher average reflects governance-level risks and bridge vulnerabilities that trigger Scope Change (S:C) in CVSS scoring. Avail's average is moderated by many bridge-layer threats requiring multisig compromise (AC:H, AV:P), which penalizes exploitability. Only 1 of 4 Ethereum findings has a CVSS score; the other 3 use qualitative severity classifications from external audit reports.

## CVSS Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| Critical (9.0-10.0) | 0 | 0 | 0 | 0 | 0 |
| High (7.0-8.9) | 2 | 4 | 2 | 0 | 8 |
| Medium (4.0-6.9) | 9 | 6 | 4 | 1 | 20 |
| Low (0.1-3.9) | 2 | 2 | 3 | 0 | 7 |
| Unscored | 0 | 0 | 0 | 3 | 3 |

Three Ethereum findings use qualitative severity classifications from external audit reports: 2 Defense-in-Depth and 1 Informational. These are not scored on the CVSS scale.

No threats reach CVSS Critical (9.0+). This is consistent with the threat landscape: DA layers do not directly custody user funds, and most attacks require either multisig compromise (PR:H) or high complexity (AC:H), both of which cap the exploitability sub-score.
