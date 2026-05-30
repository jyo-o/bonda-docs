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
| 6 | 7.5 | CEL-D11 | Celestia | High | Unbounded pendingSeenTracker memory growth via known accounts |
| 7 | 7.5 | CEL-D13 | Celestia | High | Commitment computation before gas metering in CheckTx |
| 8 | 7.5 | CEL-D17 | Celestia | High | TxCache key mismatch causing permanent cache leak |
| 9 | 7.1 | EDA-T09 | EigenDA | High | Ejector role abuse can forcibly remove honest operators |
| 10 | 6.7 | AVL-E04 | Avail | Medium | Technical Committee can upgrade runtime with 5/7 consensus |

All four protocols are represented in the top 10. Celestia leads with 4 entries, reflecting both governance-level risks and implementation-level memory exhaustion vulnerabilities.

The two highest-scoring threats (CEL-G01 at 8.7, AVL-E03 at 8.2) both involve Scope Change (S:C), which amplifies the score by accounting for cross-system impact cascading to dependent rollups and bridges.

## Average CVSS Score per DA

| DA Protocol | Average | Min | Max | Threat Count |
|---|---|---|---|---|
| Celestia | 5.6 | 3.7 | 8.7 | 19 |
| EigenDA | 5.1 | 1.8 | 7.5 | 17 |
| Avail | 4.3 | 0.0 | 8.2 | 14 |
| Ethereum / PeerDAS | 4.1 | 3.7 | 6.5 | 11 |

Celestia's higher average reflects multiple OOM-class vulnerabilities with low attack complexity (AC:L) that score higher in CVSS. Avail's average is moderated by many bridge-layer threats requiring multisig compromise (AC:H, AV:P), which penalizes exploitability.

## CVSS Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| Critical (9.0-10.0) | 0 | 0 | 0 | 0 | 0 |
| High (7.0-8.9) | 2 | 5 | 2 | 0 | 9 |
| Medium (4.0-6.9) | 10 | 8 | 7 | 4 | 29 |
| Low (0.1-3.9) | 5 | 6 | 4 | 7 | 22 |
| Informational (0.0) | 0 | 0 | 1 | 0 | 1 |

No threats reach CVSS Critical (9.0+). This is consistent with the threat landscape: DA layers do not directly custody user funds, and most attacks require either multisig compromise (PR:H) or high complexity (AC:H), both of which cap the exploitability sub-score.
