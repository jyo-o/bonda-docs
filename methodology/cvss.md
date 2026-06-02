# CVSS 3.1 Scoring

BONDA scores **Vulnerability**-tier findings with the Common Vulnerability Scoring System (CVSS) version 3.1. CVSS is the industry-standard framework used by NVD, major audit firms such as Trail of Bits, ChainLight, and Sigma Prime, and bug bounty platforms. This page describes the scoring formula, vector components, severity ranges, and provides a worked example.

{% hint style="info" %}
**CVSS applies only to the Vulnerability tier.** Operational Risks, Governance Observations, and Design Notes are not exploitable code defects, so a numeric exploit-severity score would misrepresent them. See [What Is Not Scored](#what-is-not-scored) below and the [Threat Classification](classification.md) page.
{% endhint %}

---

## Why CVSS 3.1?

CVSS 3.1 was chosen for three reasons:

1. **Industry standard.** Every security professional reads CVSS vectors. Using a proprietary scoring system creates unnecessary friction for reviewers and collaborators.
2. **Reproducibility.** Given the same metric values, any CVSS 3.1 calculator produces the same score. There is no calibration step or manual adjustment.
3. **Comparability.** CVSS scores are directly comparable across protocols, projects, and audit firms. A 7.5 in BONDA means the same thing as a 7.5 in a Trail of Bits report.

{% hint style="info" %}
**Blockchain-specific context** is captured in the CVSS metric rationale — the "why" column in each threat's scoring table — not in custom metrics. For example, "Scope: Changed" can express that a bridge vulnerability cascades to all dependent rollups.
{% endhint %}

---

## Formula

CVSS 3.1 Base Score is calculated as follows:

```
ISCBase = 1 - [(1 - C) x (1 - I) x (1 - A)]

If Scope is Unchanged:
  Impact = 6.42 x ISCBase
If Scope is Changed:
  Impact = 7.52 x (ISCBase - 0.029) - 3.25 x (ISCBase x 0.9731 - 0.02)^13

Exploitability = 8.22 x AV x AC x PR x UI

If Impact <= 0:  Score = 0
If Scope is Unchanged:  Score = Roundup(min(Impact + Exploitability, 10))
If Scope is Changed:    Score = Roundup(min(1.08 x (Impact + Exploitability), 10))

Roundup rounds to the nearest 0.1, always upward.
```

---

## Vector Components

### Exploitability Metrics

| Metric | Values | Description |
|--------|--------|-------------|
| **AV** — Attack Vector | Network (0.85), Adjacent (0.62), Local (0.55), Physical (0.20) | How the attacker reaches the vulnerable component |
| **AC** — Attack Complexity | Low (0.77), High (0.44) | Conditions beyond the attacker's control that must exist |
| **PR** — Privileges Required | None (0.85), Low (0.62/0.68), High (0.27/0.50) | Level of access needed. The second value applies when Scope is Changed. |
| **UI** — User Interaction | None (0.85), Required (0.62) | Whether a victim must take action |

### Scope

| Value | Description |
|-------|-------------|
| **Unchanged (U)** | Impact stays within the vulnerable component's security scope |
| **Changed (C)** | Impact crosses trust boundaries, for example a bridge exploit affecting all dependent rollups |

### Impact Metrics

| Metric | Values | Description |
|--------|--------|-------------|
| **C** — Confidentiality | None (0), Low (0.22), High (0.56) | Degree of information disclosure |
| **I** — Integrity | None (0), Low (0.22), High (0.56) | Degree of data modification |
| **A** — Availability | None (0), Low (0.22), High (0.56) | Degree of service disruption |

---

## Severity Ranges

| Severity | Score Range | GitBook Hint Style |
|----------|-------------|-------------------|
| Critical | 9.0 -- 10.0 | `danger` (red) |
| High | 7.0 -- 8.9 | `warning` (orange) |
| Medium | 4.0 -- 6.9 | `info` (blue) |
| Low | 0.1 -- 3.9 | `info` (blue) |

---

## Example: AVL-02 — Proxy-Wrapped submitData DA Extraction Bypass

**Threat:** A `submitData` call wrapped in a proxy extrinsic emits the `DataSubmitted` event while the Avail runtime silently skips Kate proof generation. The data appears committed on-chain, but no availability proof exists, so any consumer relying on Avail's DA guarantee receives a false positive. This is a concrete runtime defect with a demonstrable path, so it is a Vulnerability.

**Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N`

### Step-by-step Calculation

**Exploitability:**
- AV = 0.85 (Network) — The transaction is submitted over the public RPC interface.
- AC = 0.77 (Low) — No special conditions; a standard proxy-wrapped extrinsic triggers it.
- PR = 0.68 (Low, Changed scope) — The attacker needs a funded account to submit transactions, a low privilege.
- UI = 0.85 (None) — No victim interaction needed.

**Scope:** Changed — The defect is in the Avail runtime, but the harm lands on downstream DA consumers (rollups and bridges) that trusted the commitment.

**Impact:**
- C = 0.0 (None) — No confidentiality impact.
- I = 0.56 (High) — Data is treated as available and verifiable when no proof was generated, corrupting the integrity of the DA guarantee.
- A = 0.0 (None) — The service itself stays up; the failure is silent.

**Calculation:**

```
ISCBase = 1 - (1-0)(1-0.56)(1-0)
        = 1 - 0.44
        = 0.56

Impact (Changed) = 7.52 x (0.56 - 0.029) - 3.25 x (0.56 x 0.9731 - 0.02)^13
                 = 7.52 x 0.531 - 3.25 x (0.524936)^13
                 = 3.993 - 0.001
                 = 3.992

Exploitability = 8.22 x 0.85 x 0.77 x 0.68 x 0.85
               = 3.110

Score = Roundup(min(1.08 x (3.992 + 3.110), 10))
      = Roundup(min(1.08 x 7.102, 10))
      = Roundup(7.670)
      = 7.7
```

**Severity: High (7.7/10)**

### CVSS Metric Rationale

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Transaction submitted over public RPC |
| AC (Attack Complexity) | L (Low) | A standard proxy-wrapped extrinsic triggers the bypass |
| PR (Privileges Required) | L (Low) | Requires only a funded account |
| UI (User Interaction) | N (None) | Fully automated, no victim action needed |
| S (Scope) | C (Changed) | Impact crosses from the Avail runtime to dependent DA consumers |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | H (High) | Data appears committed and verifiable when no proof exists |
| A (Availability) | N (None) | The service stays up; the failure is silent |

---

## What Is Not Scored

Three of the four classification tiers do not receive a CVSS score.

| Tier | Why no CVSS | How it is characterized |
|------|-------------|-------------------------|
| **Operational Risk** | No code defect to exploit; the risk is a live operational condition such as a single point of failure. | Qualitative rating: High, Medium, or Low. |
| **Governance Observation** | No boundary is crossed; an authorized party operating within its rights is the risk. | Described in prose; informs the Decentralization baseline. |
| **Design Note** | A documented architectural choice, not a defect. | Described in prose; sets a Design Baseline. |

Forcing a CVSS score onto these tiers would imply an exploit severity that does not exist. Instead, each non-Vulnerability page states which 5-axis property it affects. See [5-Axis Risk Scoring](scoring.md).

---

## Vector Format

Each Vulnerability page includes a CVSS vector in the standard format:

```
CVSS:3.1/AV:{AV}/AC:{AC}/PR:{PR}/UI:{UI}/S:{S}/C:{C}/I:{I}/A:{A}
```

Vectors can be verified using the [NIST CVSS Calculator](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator) or [FIRST CVSS Calculator](https://www.first.org/cvss/calculator/3.1).
