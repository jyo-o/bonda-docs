# Scoring Comparison

BONDA scores the four DA layers with two complementary systems: a **5-axis qualitative model** that applies to every layer, and **CVSS 3.1**, which applies only to the Vulnerability tier. This page compares both across the four protocols.

## The 5-Axis Model

Every DA layer is assessed against the same five axes — Retrievability, Verifiability, Liveness, Decentralization, and Cost Efficiency. Each axis score is built from a Design Baseline (set by Design Notes), reduced by Threat Deductions (from Vulnerabilities), shown alongside Operational Indicators (from Operational Risks), and corrected where a Governance Observation reveals a spec-implementation gap. The full architecture is described in [Severity & Scoring](../methodology/scoring.md).

The computed per-axis values and the pentagon charts that compare the four layers are rendered in the **dashboard**, not in this documentation. This page therefore compares only the CVSS scores of the Vulnerability tier, which are the inputs to the Threat-Deduction layer.

## CVSS 3.1 Methodology

CVSS 3.1 uses the standard formula defined by [FIRST](https://www.first.org/cvss/specification-document):

```
ISS = 1 - [(1-C)(1-I)(1-A)]
Exploitability = 8.22 x AV x AC x PR x UI
Score = min(Impact + Exploitability, 10) or min(1.08 x (Impact + Exploitability), 10) for Changed scope
```

Scores can be verified using the [NIST CVSS Calculator](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator).

## Vulnerability Tier by CVSS Score

The 14 Vulnerability-tier findings, ranked by score. The other 36 findings are Operational Risks, Governance Observations, or Design Notes and carry no CVSS score.

| Rank | Score | SID | DA Protocol | Severity | Description |
|---|---|---|---|---|---|
| 1 | 8.6 | EDA-01 | EigenDA | High | Unauthenticated GetChunks cold-miss exhausts operator CPU |
| 2 | 8.6 | EDA-02 | EigenDA | High | Disperser V2 KZG compute surface exposed without authentication |
| 3 | 8.5 | AVL-01 | Avail | High | MultiAddress::Index signing silently drops the bridge proof leaf |
| 4 | 7.7 | AVL-02 | Avail | High | Proxy-wrapped submitData bypasses data-availability extraction |
| 5 | 7.5 | CEL-01 | Celestia | High | TxCache key mismatch causing permanent cache leak |
| 6 | 5.9 | CEL-02 | Celestia | Medium | Infinite retry loop without backoff in blob.Subscribe |
| 7 | 5.3 | AVL-03 | Avail | Medium | Kate RPC triggers unauthenticated KZG computation |
| 8 | 5.3 | CEL-03 | Celestia | Medium | Unbounded blacklistedHashes growth causing light node OOM |
| 9 | 5.3 | CEL-04 | Celestia | Medium | Commitment computation before gas metering in CheckTx |
| 10 | 5.3 | ETH-01 | Ethereum | Medium | Prysm DataColumnsByRange rate-limit bypass |
| 11 | 3.8 | ETH-02 | Ethereum | Low | c-kzg-4844 load_trusted_setup missing subgroup check |
| 12 | 3.7 | ETH-03 | Ethereum | Low | Prysm DataColumnsByRoot incorrect timeout |
| 13 | 3.5 | EDA-03 | EigenDA | Low | Cross-chain signature replay via non-enforced anchor signature |
| 14 | 3.4 | ETH-04 | Ethereum | Low | c-kzg-4844 Go binding thread safety |

The top of the table is dominated by Scope-Changed (S:C) availability findings: EDA-01, EDA-02, AVL-01, and AVL-02 all cascade beyond the immediate component, which amplifies the score.

## Vulnerability Severity Distribution

| Severity | EigenDA | Celestia | Avail | Ethereum | Total |
|---|---|---|---|---|---|
| Critical (9.0-10.0) | 0 | 0 | 0 | 0 | 0 |
| High (7.0-8.9) | 2 | 1 | 2 | 0 | 5 |
| Medium (4.0-6.9) | 0 | 3 | 1 | 1 | 5 |
| Low (0.1-3.9) | 1 | 0 | 0 | 3 | 4 |
| **Total** | **3** | **4** | **3** | **4** | **14** |

No Vulnerability reaches CVSS Critical (9.0+). DA layers do not directly custody user funds, and the highest-impact findings are availability and integrity issues rather than confidentiality breaches.
