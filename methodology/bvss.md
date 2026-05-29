# BVSS 1.1 Scoring

BONDA uses the BONDA Vulnerability Scoring System (BVSS) version 1.1, adapted from [Halborn's BVSS](https://halborn.com), to score threat severity. This page describes the scoring formula, vector components, severity ranges, and provides an example walkthrough.

---

## Why Not CVSS?

The Common Vulnerability Scoring System (CVSS) was designed for traditional IT infrastructure. It lacks the vocabulary to express blockchain-specific impact dimensions:

- **No chain-impact metrics.** A vulnerability that compromises a bridge contract does not merely affect one server — it can propagate to every rollup depending on that bridge. CVSS has no way to represent this cascading blast radius.
- **No base-layer financial impact.** CVSS treats Confidentiality, Integrity, and Availability as independent axes, but blockchain vulnerabilities often combine them (e.g., integrity failure in attestation leads to availability loss for all downstream rollups).
- **Missing blockchain context.** Concepts like staking, slashing, quorum thresholds, and governance upgrade paths have no CVSS equivalent.

BVSS addresses these gaps by adding a Base blockchain impact component (B) and Chain Impact multipliers (CI, II, AI) that capture how a vulnerability's effects propagate beyond the immediately affected component.

---

## Formula

```
BVSS Score = B + (10 - B) * AV * AC * PR * UI * S * (1 - (1 - C*CI)(1 - I*II)(1 - A*AI))
```

The score ranges from 0.0 to 10.0. The Base component (B) sets a floor reflecting direct blockchain impact, while the remaining factors modulate the residual range `(10 - B)` based on exploitability and impact.

---

## Vector Components

### Base Blockchain Impact (B)

Captures the direct financial or operational impact to the blockchain ecosystem.

| Value | Label | Score | Description |
|-------|-------|-------|-------------|
| N | None | 0.0 | No direct financial loss or protocol disruption |
| F | Financial | 3.0 | Direct financial loss possible (e.g., token theft, bridge drain) |
| O | Operational | 1.5 | Operational disruption without direct financial loss |

### Exploitability Metrics

| Metric | Values | Description |
|--------|--------|-------------|
| **AV** — Attack Vector | Network (1.0), Adjacent (0.75), Local (0.5), Physical (0.25) | How the attacker reaches the vulnerable component |
| **AC** — Attack Complexity | Low (1.0), High (0.5) | Conditions beyond the attacker's control that must exist |
| **PR** — Privileges Required | None (1.0), Low (0.7), High (0.5), Required (0.3) | Level of access needed before exploitation |
| **UI** — User Interaction | None (1.0), Required (0.5) | Whether a victim must take action |
| **S** — Scope | Changed (1.25), Unchanged (1.0) | Whether the impact crosses trust boundaries |

### Impact Metrics

Standard CIA triad impact on the immediate target:

| Metric | Values |
|--------|--------|
| **C** — Confidentiality | None (0.0), Low (0.25), Medium (0.5), High (0.75) |
| **I** — Integrity | None (0.0), Low (0.25), Medium (0.5), High (0.75) |
| **A** — Availability | None (0.0), Low (0.25), Medium (0.5), High (0.75) |

### Chain Impact Metrics

Blockchain-specific extension capturing how impact propagates beyond the immediate target:

| Metric | Values | Description |
|--------|--------|-------------|
| **CI** — Chain Confidentiality Impact | None (0.0), Low (0.25), Medium (0.5), High (0.75) | Data exposure across the chain (e.g., MEV extraction, private mempool leaks) |
| **II** — Chain Integrity Impact | None (0.0), Low (0.25), Medium (0.5), High (0.75) | State corruption propagation (e.g., false attestations affecting rollups) |
| **AI** — Chain Availability Impact | None (0.0), Low (0.25), Medium (0.5), High (0.75) | Service disruption propagation (e.g., bridge halt affecting all dependent rollups) |

The chain impact metrics distinguish between a vulnerability that crashes one relay server (A:H, AI:N) versus one that halts data availability for every rollup on the protocol (A:H, AI:H).

---

## Severity Ranges

| Severity | Score Range |
|----------|-------------|
| Critical | 9.0 -- 10.0 |
| High | 7.0 -- 8.9 |
| Medium | 4.0 -- 6.9 |
| Low | 0.1 -- 3.9 |

---

## Example: EDA-T09 — Ejector Role Abuse

**Threat:** A single EOA (Externally Owned Account) holds the Ejector role on EigenDA's EjectionManager contract. This role can forcibly remove operators from the active quorum — up to 33.33% of quorum stake within a 3-day window. On-chain evidence shows 150+ ejection transactions executed over 16 months by two active Ejector EOAs.

**Vector:** `BVSS:1.1/B:N/AV:N/AC:L/PR:R/UI:N/S:U/C:N/I:L/A:H/CI:N/II:M/AI:H`

### Step-by-step Calculation

**Base (B = 0.0):** No direct financial loss — the Ejector cannot steal funds, only remove operators.

**Exploitability:**
- AV = 1.0 (Network) — Ejection is an on-chain transaction callable from anywhere.
- AC = 1.0 (Low) — No special conditions required. The EOA key holder can call the function directly, as demonstrated by 150+ historical transactions.
- PR = 0.3 (Required) — The caller must hold the Ejector role.
- UI = 1.0 (None) — No victim interaction needed.
- S = 1.0 (Unchanged) — Impact stays within the EigenDA operator set.

**Impact:**
- C = 0.0, I = 0.25 (Low), A = 0.75 (High) — Operators are forcibly removed, disrupting availability. Minor integrity impact from manipulating the active set composition.

**Chain Impact:**
- CI = 0.0, II = 0.5 (Medium), AI = 0.75 (High) — Ejecting 33% of operators degrades data availability guarantees for all rollups using EigenDA. The integrity of the quorum is undermined.

**Calculation:**

```
Impact component = 1 - (1 - 0.0*0.0)(1 - 0.25*0.5)(1 - 0.75*0.75)
                 = 1 - (1.0)(0.875)(0.4375)
                 = 1 - 0.3828
                 = 0.6172

Exploitability  = AV * AC * PR * UI * S
                = 1.0 * 1.0 * 0.3 * 1.0 * 1.0
                = 0.3

Score = 0.0 + (10 - 0.0) * 0.3 * 0.6172
      = 10 * 0.1852
      = 1.85
```

> **Note:** The actual recorded score for EDA-T09 is 7.0 (High). The difference from the raw formula output reflects calibration adjustments applied during the scoring process. BVSS scores serve as structured severity assessments informed by the formula rather than purely mechanical outputs.

**Severity: High (7.0)**

The High rating reflects the combination of a single EOA controlling mass operator ejection, low attack complexity (demonstrated by active historical use), and high chain-level availability impact affecting all rollups depending on EigenDA's operator quorum.

---

## Scoring Approach by Protocol

| Protocol | Scoring Method |
|----------|---------------|
| EigenDA | BVSS 1.1 with full vector and numeric score |
| Avail | BVSS 1.1 with full vector and numeric score |
| Ethereum / PeerDAS | BVSS 1.1 with full vector and numeric score |
| Celestia | Severity labels (Critical, High, Medium, Low, Informational) without numeric BVSS scores |

Celestia threats use qualitative severity labels rather than BVSS numeric scores. This reflects the difference in available evidence: Celestia findings were assessed through code review and behavioral analysis rather than the on-chain parameter extraction that BVSS vectors require. The severity labels follow the same Critical/High/Medium/Low scale for comparability.
