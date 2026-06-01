# Dashboard ↔ GitBook Scoring Integration Spec

> Internal handoff document for the BONDA dashboard team. Not part of the published GitBook (intentionally absent from `SUMMARY.md`). It defines the contract between the GitBook threat model and the dashboard's star ratings, status badges, and deep links. No dashboard code is included here — this is the design the dashboard implements against.

---

## 1. Why this document exists

Three scoring formulas exist today and they disagree:

| Source | Formula | Problem |
|---|---|---|
| GitBook `methodology/scoring.md` | `Axis = Baseline(L1) − Σ Deductions(L3)` | Canonical, but had no likelihood and no numbers |
| `bonda_5axis_scoring_methodology.md` (Downloads) | same, with concrete per-DA numbers | Uses **stale SIDs** (AVL-010/011, CEL-G01) that no longer exist |
| Frontend (`EigendaReality.tsx`, `EthereumReality.tsx`) | `Axis = 0.6×Metric + 0.4×Threat` | A different model entirely, on BVSS and stale SIDs, computed for only 2 of 4 DAs. **Discarded** — see §3a |

This spec makes the GitBook the **single source of truth for all scores**. The frontend `0.6/0.4` blend is **not reconciled and not repurposed — it is removed entirely** (§3a). The dashboard recomputes axis stars from the GitBook-published model below, and builds its live signals fresh from backend operational feeds. There is exactly one scoring path.

---

## 2. The unified scoring model (authoritative)

This mirrors `methodology/scoring.md`. The dashboard computes axis stars from this model only. The former `0.6/0.4` blend is gone (§3a).

```
Axis Score (0–10) = Baseline(L1, corrected by L4) − Σ Threat Deductions(L3)

Threat Deduction = Impact Weight × Likelihood Factor   (capped at −3.0 per axis)
```

### Inputs by classification tier

| Tier | Scoring layer | Contributes |
|---|---|---|
| Design Note | L1 baseline | Sets the 0–10 structural baseline (3 sub-properties × 0–3, rescaled) |
| Governance Observation | L1 input + L4 | Informs Decentralization baseline; corrects baselines where a claimed property is not delivered |
| Operational Risk | L2 | **Live indicator only — never folded into the star score.** Drives the "Active" badge |
| Vulnerability | L3 | Deducts `Impact × Likelihood` while unpatched |

### Impact Weight (from CVSS 3.1 band of the Vulnerability)

| CVSS band | Weight |
|---|---|
| High / Critical | −1.0 |
| Medium | −0.5 |
| Low | −0.2 |

### Likelihood Factor (NIST SP 800-30 ordinal, FAIR frequency lens)

| Likelihood | Factor |
|---|---|
| Very High | 1.0 |
| High | 0.8 |
| Moderate | 0.6 |
| Low | 0.4 |
| Very Low | 0.2 |

The Likelihood band for each Vulnerability is published on its GitBook threat page hint line (`**Likelihood**: …`). The dashboard reads it from there or from the threat API field (see §4). This is the mechanism that prevents improbable-but-severe events (key theft, cloud-region outage, KYC censorship) from collapsing a star rating: those are Governance/Operational tier and never deduct, and any Vulnerability with rare preconditions gets a 0.2–0.4 factor.

### Worked example (per axis)

EigenDA Liveness: baseline (L1 from Design Notes) minus the two unauthenticated DoS vulnerabilities:
- EDA-01 — High (−1.0) × Very High (1.0) = **−1.0**
- EDA-02 — High (−1.0) × Very High (1.0) = **−1.0**
- Net Liveness deduction = −2.0 (under the −3.0 cap).

Contrast EDA-03 (cross-chain replay) — Low (−0.2) × Low (0.4) = **−0.08**, effectively negligible, which matches its real-world rarity.

---

## 3. The three UI signals and where each comes from

The dashboard surfaces three distinct things. Keep their data sources separate.

| UI element | Meaning | Data source |
|---|---|---|
| **Star rating** (per axis, 0–5) | Structural security of the axis | §2 unified model. `stars = round(AxisScore / 2 × 2) / 2` → 0–10 mapped to 0–5 in 0.5 steps |
| **Active** badge | Is the system performing as designed *right now* | L2 Operational Indicators, built fresh from backend live feeds (signing %, retrieval/relay success, DAS samples, validator uptime, incidents). **Not** derived from the discarded `0.6/0.4` blend |
| **Trust** badge | Strength of evidence behind the findings | Verification level: `verified` / `poc_verified` from the threat metadata |

This is the clean split: **stars = structural (slow-moving)**, **Active = live (fast-moving)**, **Trust = evidence**. A moving metric must never silently change a star.

### Star mapping table

| Axis Score (0–10) | Stars |
|---|---|
| 9.0–10.0 | 5.0 |
| 8.0–8.9 | 4.5 |
| 7.0–7.9 | 4.0 |
| 6.0–6.9 | 3.5 |
| 5.0–5.9 | 3.0 |
| 4.0–4.9 | 2.5 |
| 3.0–3.9 | 2.0 |
| 2.0–2.9 | 1.5 |
| 1.0–1.9 | 1.0 |
| 0.0–0.9 | 0.5 |

### 3a. Migration: what is removed and rebuilt

The current dashboard scoring is replaced, not adapted. The following is removed:

- `lib/observatory/reality.ts` — the `computeReality` `0.6×metric + 0.4×threat` blend and `threatScore = (10 − maxBVSS) / 2`.
- `lib/thresholds.ts` — the `weight_metric: 0.6` / `weight_threat: 0.4` constants.
- The BVSS fields carried on the threat JSON (`bvss_score`, `bvss_vector`, `bvss_formula`, `bvss_rationale`, `Likelihood Of Attack`).
- The old-SID threat catalogs (`EDA-D02`, `ETH-D01`, `G-CON-03`, and the rest of the legacy numbering).

What replaces it:

| Concern | Old (removed) | New |
|---|---|---|
| Axis score | `0.6×metric + 0.4×threat`, 2 of 4 DAs only | §2 unified model, all 4 DAs, computed from GitBook inputs |
| Severity source | BVSS | CVSS 3.1 band + Likelihood band from GitBook / threat API |
| Threat identity | 17 legacy EigenDA SIDs | GitBook canonical: EigenDA 14, Celestia 12, Avail 12, Ethereum/PeerDAS 12 |
| Live health | folded into the blend | `Active` badge built fresh from backend operational feeds |

**Live-feed coverage gap to close.** EigenDA already has a live drilldown (operator signing %, relay success, operator uptime, Nakamoto-33). Celestia and Avail have backend live feeds that the scoring never consumed — wire them into the `Active` badge: Celestia (block headers, DAS samples, validator uptime, staking / Nakamoto), Avail (validator-participation, era-info, DAS samples, fraud events).

---

## 4. Threat catalog data contract

For each finding the dashboard needs these fields. They already exist on the GitBook page hint line and headings; expose them through the threat API (`/api/spec/{da}/threats`) or parse them from the markdown front-of-page.

| Field | Source on the GitBook page | Example |
|---|---|---|
| `sid` | H1 | `EDA-01` |
| `title` | H1 | `Unauthenticated GetChunks Cold-Miss …` |
| `tier` | hint `**Category**` | `Vulnerability` |
| `cvss` | hint `**Severity**` + `### CVSS 3.1` (Vulnerability only) | `8.6` |
| `likelihood` | hint `**Likelihood**` (Vulnerability only) | `Very High` |
| `status` | hint `**Status**` | `poc_verified` |
| `axis` | prose ("Affects the … axis/baseline") | `Liveness` |

Only Vulnerability findings carry `cvss` and `likelihood`. Operational Risk / Governance Observation / Design Note carry none — the dashboard must treat their absence as "not deductible," not as a zero score.

---

## 5. GitBook deep links

Every finding row in the dashboard deep-links to its GitBook page (and, where useful, to the on-chain/PoC evidence anchor).

**Base URL:** `https://upside-1.gitbook.io/upside-docs`

**Threat page pattern:**
```
{BASE}/{da}/threats/{sid-lowercase}
e.g. https://upside-1.gitbook.io/upside-docs/eigenda/threats/eda-01
```

**Evidence anchor pattern** (for findings with reproducible evidence):
```
{BASE}/{da}/evidence#{heading-slug}
e.g. .../eigenda/evidence#getchunks-cold-miss-cpu-exhaustion-eda-01
     .../eigenda/evidence#getblobcommitment-unauthenticated-compute-eda-02
```

Slug rule (GitBook default): lowercase, spaces → `-`, parentheses and commas dropped, underscores kept.

**Implementation note:** `lib/threat-model.ts:parseReferences` currently recognises only GitHub URLs. Extend it to also emit GitBook threat/evidence links so the threat list renders an external-doc affordance per row. This is a parser change in the dashboard repo, not a GitBook change.

---

## 6. Data-integrity warnings for the dashboard team

1. **Do not seed scores from `bonda_5axis_scoring_methodology.md` (Downloads).** It predates the renumbering and uses dead SIDs (`AVL-010`=7.1, `AVL-011`=7.8, `CEL-G01`, `EDA-D03`, etc.). The current canonical CVSS values are: EDA-01 8.6, EDA-02 8.6, AVL-01 8.5, AVL-02 7.7, CEL-01 7.5. Pull all values from the live GitBook / threat API.
2. **Decentralization is baseline-only by design.** No current Vulnerability maps to the Decentralization axis, so its star comes entirely from L1 (operator distribution, governance concentration, software/infra diversity) fed by Governance Observations and Design Notes. This is correct — do not synthesize a deduction for it.
3. **Likelihood is mandatory for any new Vulnerability.** If the dashboard ingests a Vulnerability with a CVSS band but no Likelihood, treat it as a data error, not as Very High. The GitBook page is the authority.
4. **Patched vulnerabilities stop deducting.** When a finding's status flips to patched, its L3 deduction is removed and the axis star recovers. Recompute on status change.

---

## 7. Summary of the contract

- GitBook owns: tiers, CVSS, Likelihood bands, baselines rationale, evidence anchors.
- Dashboard owns: the arithmetic of §2, the star mapping of §3, the migration of §3a, the live `Active` signal built from backend feeds, the `Trust` badge, and the deep links of §5.
- The two never disagree because the dashboard computes from GitBook-published inputs and never hard-codes scores.
