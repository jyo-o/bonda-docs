# CVSS 3.1 Scoring

BONDA scores **Vulnerability**-tier findings with the Common Vulnerability Scoring System (CVSS) version 3.1. CVSS is the industry-standard framework used by NVD, major audit firms and bug bounty platforms. This page describes the scoring formula, vector components, severity ranges, and provides a worked example.

{% hint style="info" %}
**CVSS applies only to the Vulnerability tier.** Operational Risks, Governance Observations, and Design Notes are not exploitable code defects, so a numeric exploit-severity score would misrepresent them. See [What Is Not Scored](cvss.md#what-is-not-scored) below and the [Threat Classification](classification.md) page.
{% endhint %}

***

## Why CVSS 3.1?

CVSS 3.1 was chosen for three reasons:

1. **Industry standard.** Every security professional reads CVSS vectors. Using a proprietary scoring system creates unnecessary friction for reviewers and collaborators.
2. **Reproducibility.** Given the same metric values, any CVSS 3.1 calculator produces the same score. There is no calibration step or manual adjustment.
3. **Comparability.** CVSS scores are directly comparable across protocols, projects, and audit firms. A 7.5 in BONDA means the same thing as a 7.5 in a Trail of Bits report.

{% hint style="info" %}
**Blockchain-specific context** is captured in the CVSS metric rationale — the "why" column in each threat's scoring table — not in custom metrics. For example, "Scope: Changed" can express that a bridge vulnerability cascades to all dependent rollups.
{% endhint %}

***

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

***

## Vector Components

### Exploitability Metrics

| Metric                       | Values                                                         | Description                                                             |
| ---------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **AV** — Attack Vector       | Network (0.85), Adjacent (0.62), Local (0.55), Physical (0.20) | How the attacker reaches the vulnerable component                       |
| **AC** — Attack Complexity   | Low (0.77), High (0.44)                                        | Conditions beyond the attacker's control that must exist                |
| **PR** — Privileges Required | None (0.85), Low (0.62/0.68), High (0.27/0.50)                 | Level of access needed. The second value applies when Scope is Changed. |
| **UI** — User Interaction    | None (0.85), Required (0.62)                                   | Whether a victim must take action                                       |

### Scope

| Value             | Description                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------- |
| **Unchanged (U)** | Impact stays within the vulnerable component's security scope                                 |
| **Changed (C)**   | Impact crosses trust boundaries, for example a bridge exploit affecting all dependent rollups |

### Impact Metrics

| Metric                  | Values                            | Description                      |
| ----------------------- | --------------------------------- | -------------------------------- |
| **C** — Confidentiality | None (0), Low (0.22), High (0.56) | Degree of information disclosure |
| **I** — Integrity       | None (0), Low (0.22), High (0.56) | Degree of data modification      |
| **A** — Availability    | None (0), Low (0.22), High (0.56) | Degree of service disruption     |

***

## Severity Ranges

| Severity | Score Range |
| -------- | ----------- |
| Critical | 9.0 -- 10.0 |
| High     | 7.0 -- 8.9  |
| Medium   | 4.0 -- 6.9  |
| Low      | 0.1 -- 3.9  |

## Vector Format

Each Vulnerability page includes a CVSS vector in the standard format:

```
CVSS:3.1/AV:{AV}/AC:{AC}/PR:{PR}/UI:{UI}/S:{S}/C:{C}/I:{I}/A:{A}
```

Vectors can be verified using the [NIST CVSS Calculator](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator) or [FIRST CVSS Calculator](https://www.first.org/cvss/calculator/3.1).
