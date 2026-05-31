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
| 1 | 7.7 | AVL-E03 | Avail | High | Deployer EOA retains DEFAULT_ADMIN_ROLE, enabling solo VectorX upgrade |
| 2 | 7.5 | AVL-D01 | Avail | High | VectorX single relayer SPOF with no on-chain heartbeat |
| 3 | 7.5 | CEL-D17 | Celestia | High | TxCache key mismatch causing permanent cache leak |
| 4 | 6.6 | CEL-E01 | Celestia | Medium | SP1Blobstream instant upgrade by 4-of-6 multisig, no timelock |
| 5 | 6.5 | CEL-G01 | Celestia | Medium | KYC validator concentration enabling legal censorship |
| 6 | 6.1 | EDA-E02 | EigenDA | Medium | Single multisig controls all eight core contracts without timelock |
| 7 | 5.9 | CEL-D02 | Celestia | Medium | Low-cost blockspace monopoly via large PFB transactions |
| 8 | 5.9 | CEL-D15 | Celestia | Medium | Infinite retry loop without backoff in blob.Subscribe |
| 9 | 5.9 | EDA-D03 | EigenDA | Medium | Disperser V2 KZG compute surface exposed without authentication |
| 10 | 5.9 | EDA-T09 | EigenDA | Medium | Ejector role abuse can force-remove honest operators |

The highest-scoring threat (AVL-E03 at 7.7) involves Scope Change (S:C), which amplifies the score by accounting for cross-system impact cascading to dependent rollups and bridges.

## Average CVSS Score per DA

| DA Protocol | Average | Min | Max | Scored / Total |
|---|---|---|---|---|
| Celestia | 5.3 | 3.1 | 7.5 | 12 / 12 |
| EigenDA | 4.8 | 3.5 | 6.1 | 13 / 13 |
| Avail | 4.9 | 2.7 | 7.7 | 9 / 9 |
| Ethereum / PeerDAS | 4.1 | 3.4 | 5.3 | 4 / 4 |

Celestia's higher average reflects governance-level risks and bridge vulnerabilities. Avail's average is moderated by many bridge-layer threats requiring multisig compromise (AC:H, AV:P), which penalizes exploitability. All 38 threats across four DA protocols are scored using the same CVSS 3.1 methodology.

## CVSS Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| Critical (9.0-10.0) | 0 | 0 | 0 | 0 | 0 |
| High (7.0-8.9) | 0 | 1 | 2 | 0 | 3 |
| Medium (4.0-6.9) | 9 | 8 | 3 | 1 | 21 |
| Low (0.1-3.9) | 4 | 3 | 4 | 3 | 14 |

No threats reach CVSS Critical (9.0+). This is consistent with the threat landscape: DA layers do not directly custody user funds, and most attacks require either multisig compromise (PR:H) or high complexity (AC:H), both of which cap the exploitability sub-score.
