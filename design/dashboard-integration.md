# Dashboard Scoring Contract

> Handoff for the BONDA dashboard team. Not published (absent from `SUMMARY.md`).
> The dashboard owns the numbers and the live feeds; GitBook owns the methodology
> and the per-threat severity/likelihood/axis. This file lists only what the
> dashboard must follow to stay consistent with the GitBook threat model.

## Model

```
Axis Score (0–10) = Baseline − Σ Deduction        (Σ per axis capped at −3.0)
Deduction         = ImpactWeight × LikelihoodFactor
Stars (0–5)       = min(5, (floor(AxisScore) + 1) / 2)
```

- **Baseline** (L1, corrected by L4) is **dashboard-owned**. Not in GitBook. Sub-property rubric is in `methodology/scoring.md`; the assigned 0–3 levels and their evidence live in the dashboard.
- Only **Vulnerability**-tier findings deduct, and only while unpatched. Recompute on status change.

| CVSS band | ImpactWeight | | Likelihood | Factor |
|---|---|---|---|---|
| High / Critical | −1.0 | | Very High | 1.0 |
| Medium | −0.5 | | High | 0.8 |
| Low | −0.2 | | Moderate | 0.6 |
| | | | Low | 0.4 |
| | | | Very Low | 0.2 |

## Deduction vectors (apply verbatim)

The 14 Vulnerabilities and the axis each deducts from. Everything else (Governance, Operational, Design) never deducts.

| SID | DA | Axis | Impact × Likelihood | Deduction |
|---|---|---|---|---|
| EDA-01 | EigenDA | Liveness | −1.0 × 1.0 | −1.00 |
| EDA-02 | EigenDA | Liveness | −1.0 × 1.0 | −1.00 |
| EDA-03 | EigenDA | Verifiability | −0.2 × 0.4 | −0.08 |
| CEL-01 | Celestia | Liveness | −1.0 × 0.6 | −0.60 |
| CEL-02 | Celestia | Verifiability | −0.5 × 0.6 | −0.30 |
| CEL-03 | Celestia | Verifiability | −0.5 × 0.4 | −0.20 |
| CEL-04 | Celestia | Liveness | −0.5 × 0.6 | −0.30 |
| AVL-01 | Avail | Verifiability | −1.0 × 0.6 | −0.60 |
| AVL-02 | Avail | Verifiability | −1.0 × 0.6 | −0.60 |
| AVL-03 | Avail | Liveness | −0.5 × 1.0 | −0.50 |
| ETH-01 | Ethereum | Liveness | −0.5 × 0.6 | −0.30 |
| ETH-02 | Ethereum | Verifiability | −0.2 × 0.2 | −0.04 |
| ETH-03 | Ethereum | Retrievability | −0.2 × 0.4 | −0.08 |
| ETH-04 | Ethereum | Verifiability | −0.2 × 0.4 | −0.08 |

Per-DA axis totals (the only axes that take any deduction):

| DA | Liveness | Verifiability | Retrievability |
|---|---|---|---|
| EigenDA | −2.00 | −0.08 | — |
| Celestia | −0.90 | −0.50 | — |
| Avail | −0.50 | −1.20 | — |
| Ethereum | −0.30 | −0.12 | −0.08 |

**Decentralization and Cost Efficiency take zero deduction** — no Vulnerability maps to them. Do not synthesize one. These axes are baseline-only.

## Three signals — keep the sources separate

- **Stars** (per axis, 0–5) — structural. From the model above. A live metric must never move a star.
- **Active** badge — live operational health. Built from backend feeds, not from any score: EigenDA (signing %, relay success, operator uptime, Nakamoto); Celestia (block headers, DAS samples, validator uptime, staking); Avail (validator-participation, era-info, DAS samples, fraud events). Celestia/Avail feeds exist in the backend but are currently unused — wire them in.
- **Trust** badge — `verified` / `poc_verified` from the threat metadata.

## Removed (do not reuse)

The legacy frontend scoring is discarded, not adapted:
- `reality.ts` `0.6×metric + 0.4×threat` blend and `threatScore = (10 − maxBVSS)/2`
- `thresholds.ts` `weight_metric` / `weight_threat`
- all BVSS fields; replace with CVSS band + Likelihood band from GitBook
- old SIDs (EDA-D02, ETH-D01, …); use canonical EigenDA 14 / Celestia 12 / Avail 12 / Ethereum 12

## Deep links

```
threat:   https://upside-1.gitbook.io/upside-docs/{da}/threats/{sid-lower}
evidence: https://upside-1.gitbook.io/upside-docs/{da}/evidence#{heading-slug}
```

`lib/threat-model.ts:parseReferences` handles GitHub URLs only — extend it to emit these.

## Known GitBook data issue

`ETH-02` and `ETH-04` CVSS rationale tables describe a different finding than their body (copy-paste). Impact band stays as published (Low) pending a GitBook fix; flag before trusting their vectors verbatim.
