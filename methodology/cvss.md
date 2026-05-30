# CVSS 3.1 Scoring

BONDA uses the Common Vulnerability Scoring System (CVSS) version 3.1 to score threat severity. CVSS is the industry-standard framework used by NVD, major audit firms (Trail of Bits, ChainLight, Sigma Prime), and bug bounty platforms. This page describes the scoring formula, vector components, severity ranges, and provides an example walkthrough.

---

## Why CVSS 3.1?

CVSS 3.1 was chosen for three reasons:

1. **Industry standard.** Every security professional reads CVSS vectors. Using a proprietary scoring system creates unnecessary friction for reviewers and collaborators.
2. **Reproducibility.** Given the same metric values, any CVSS calculator produces the same score. There is no calibration step or manual adjustment.
3. **Comparability.** CVSS scores are directly comparable across protocols, projects, and audit firms. A 7.5 in BONDA means the same thing as a 7.5 in a Trail of Bits report.

{% hint style="info" %}
**Blockchain-specific context** is captured in the CVSS metric rationale (the "why" column in each threat's scoring table), not in custom metrics. For example, "Scope: Changed" can express that a bridge vulnerability cascades to all dependent rollups.
{% endhint %}

---

## Formula

CVSS 3.1 Base Score is calculated as follows:

```
ISS = 1 - [(1 - C) x (1 - I) x (1 - A)]

If Scope is Unchanged:
  Impact = 6.42 x ISS
If Scope is Changed:
  Impact = 7.52 x [ISS - 0.029] - 3.25 x [ISS - 0.02]^15

Exploitability = 8.22 x AV x AC x PR x UI

If Impact <= 0:  Score = 0
If Scope is Unchanged:  Score = min(Impact + Exploitability, 10)
If Scope is Changed:    Score = min(1.08 x (Impact + Exploitability), 10)

Final score is rounded up to the nearest 0.1.
```

---

## Vector Components

### Exploitability Metrics

| Metric | Values | Description |
|--------|--------|-------------|
| **AV** — Attack Vector | Network (0.85), Adjacent (0.62), Local (0.55), Physical (0.20) | How the attacker reaches the vulnerable component |
| **AC** — Attack Complexity | Low (0.77), High (0.44) | Conditions beyond the attacker's control that must exist |
| **PR** — Privileges Required | None (0.85), Low (0.62/0.68), High (0.27/0.50) | Level of access needed. Values differ for Unchanged/Changed scope. |
| **UI** — User Interaction | None (0.85), Required (0.62) | Whether a victim must take action |

### Scope

| Value | Description |
|-------|-------------|
| **Unchanged (U)** | Impact stays within the vulnerable component's security scope |
| **Changed (C)** | Impact crosses trust boundaries (e.g., bridge exploit affects all dependent rollups) |

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
| Informational | 0.0 | `success` (green) |

---

## Example: AVL-E03 — Deployer Retains Admin Role

**Threat:** The deployer EOA retains `DEFAULT_ADMIN_ROLE` on Avail's VectorX bridge contract. This role controls all other roles, enabling a solo upgrade path that bypasses multisig governance.

**Vector:** `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H`

### Step-by-step Calculation

**Exploitability:**
- AV = 0.85 (Network) — The attack executes via Ethereum mainnet transactions.
- AC = 0.44 (High) — Requires compromising the deployer's private key.
- PR = 0.68 (Low, Changed scope) — Requires the deployer's specific credentials, but the deployer is a known single EOA.
- UI = 0.85 (None) — No victim interaction needed.

**Scope:** Changed — Impact extends beyond VectorX to the entire bridge ecosystem and all dependent rollups.

**Impact:**
- C = 0.0 (None) — No confidentiality impact.
- I = 0.56 (High) — Arbitrary contract implementation replacement enables false attestations and bypasses governance.
- A = 0.56 (High) — A single compromised key can halt the entire bridge.

**Calculation:**

```
ISS = 1 - (1-0)(1-0.56)(1-0.56)
    = 1 - 0.44 x 0.44
    = 1 - 0.1936
    = 0.8064

Impact (Changed) = 7.52 x (0.8064 - 0.029) - 3.25 x (0.8064 - 0.02)^15
                 = 7.52 x 0.7774 - 3.25 x 0.0281
                 = 5.846 - 0.091
                 = 5.755

Exploitability = 8.22 x 0.85 x 0.44 x 0.68 x 0.85
               = 8.22 x 0.2170
               = 1.784

Score = min(1.08 x (5.755 + 1.784), 10)
      = min(1.08 x 7.539, 10)
      = min(8.142, 10)
      = 8.2
```

**Severity: High (8.2/10)**

### CVSS Metric Rationale

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Attack executes via Ethereum mainnet transactions |
| AC (Attack Complexity) | H (High) | Requires compromising the deployer EOA private key |
| PR (Privileges Required) | L (Low) | Deployer is a known single EOA, not a multisig |
| UI (User Interaction) | N (None) | Fully automated, no victim action needed |
| S (Scope) | C (Changed) | Bridge compromise cascades to all dependent rollups |
| C (Confidentiality) | N (None) | No data exposure |
| I (Integrity) | H (High) | Arbitrary implementation replacement bypasses all governance |
| A (Availability) | H (High) | Single key compromise can halt the entire bridge |

---

## Vector Format

Each threat page includes a CVSS vector in the standard format:

```
CVSS:3.1/AV:{AV}/AC:{AC}/PR:{PR}/UI:{UI}/S:{S}/C:{C}/I:{I}/A:{A}
```

Vectors can be verified using the [NIST CVSS Calculator](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator) or [FIRST CVSS Calculator](https://www.first.org/cvss/calculator/3.1).
