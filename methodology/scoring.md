# 5-Axis Risk Scoring

CVSS scores individual vulnerabilities. It does not answer the question a rollup operator actually asks: *how does this DA layer compare to that one, across everything that matters?* BONDA's 5-axis model answers that question by evaluating every DA layer against the same five properties, using the same rubric.

This page explains the model: the five axes, the layered architecture that keeps structural properties separate from live measurements, the sub-property rubrics, and how the four classification tiers feed in. 

{% hint style="info" %}
**Per-DA scores and pentagon charts live in the BONDA dashboard, not in this documentation.** This page defines *how* the model works. The dashboard renders the computed values for each DA layer. Keeping the methodology and the numbers separate means the rubric can be reviewed on its own terms, and the dashboard can update measurements without rewriting the documentation.
{% endhint %}

---

## The Five Axes

Each axis answers one question a DA user would ask.

| Axis | Question |
|------|----------|
| **Retrievability** | Can I get my data back when I need it? |
| **Verifiability** | Can I independently prove the data is really there? |
| **Liveness** | Will the service keep running under adversarial conditions? |
| **Decentralization** | How many parties would need to collude to break it? |
| **Cost Efficiency** | Is it affordable, predictable, and efficient for the throughput I need? |

These five capture the dimensions on which DA layers genuinely differ. A DA layer can be cheap but centralized, or decentralized but slow to retrieve from; one number cannot express that trade-off, but a pentagon can.

---

## Layered Architecture

A naive model would map each finding to an axis and subtract. That produces a number nobody can explain, because it mixes four different kinds of analysis: what the protocol structurally guarantees, what an attacker can degrade today, what the system is currently measuring, and whether the protocol delivers what it claims. BONDA separates them into four layers.

```mermaid
flowchart LR
    L1["<b>Layer 1</b><br/>Design Baseline<br/>0–10 per axis"] --> Score["<b>Displayed Axis Score</b><br/>Baseline − Deductions"]
    L3["<b>Layer 3</b><br/>Threat Deductions<br/>from Vulnerabilities"] --> Score
    L4["<b>Layer 4</b><br/>Spec-Implementation<br/>Gap correction"] -.corrects.-> L1
    Score --> Pentagon["Pentagon chart<br/>(dashboard)"]
    L2["<b>Layer 2</b><br/>Operational Indicators<br/>live measurements"] -.shown alongside.-> Pentagon

    style L1 fill:#d3f9d8,color:#1a1a1a,stroke:#2b8a3e
    style L3 fill:#ffe3e3,color:#1a1a1a,stroke:#c92a2a
    style L4 fill:#a5d8ff,color:#1a1a1a,stroke:#1971c2
    style L2 fill:#fff3bf,color:#1a1a1a,stroke:#e67700
    style Score fill:#e8e8e8,color:#1a1a1a,stroke:#999
    style Pentagon fill:#e8e8e8,color:#1a1a1a,stroke:#999
```

### Layer 1 — Design Baseline

*What does the protocol's architecture structurally guarantee?* Determined by the specification and the deployed design. It changes only when the protocol upgrades. Each axis baseline is built from three sub-properties, each scored 0–3, summed and rescaled to 0–10.

### Layer 3 — Threat Deductions

*How much can an attacker degrade this property right now?* Only **Vulnerability**-tier findings produce deductions, and only while the vulnerability remains unpatched. Each vulnerability is mapped to the axis its exploit most directly degrades, with deduction magnitude derived from its CVSS severity band.

### Layer 2 — Operational Indicators

*Is the system currently performing as designed?* Live measurements from monitoring — dead-operator ratios, stake concentration, latency. These are displayed alongside the pentagon as color-coded alerts but are **not** folded into the score. This prevents a moving measurement from appearing to change a structural property.

### Layer 4 — Spec-Implementation Gap correction

*Does the system deliver what it claims?* When a protocol claims a property the implementation does not deliver, the baseline cannot take the claim at face value. Layer 4 findings reduce the baseline so it reflects delivered behavior, not documented intent.

### Score Formula

```
Displayed Axis Score = Design Baseline (Layer 1, corrected by Layer 4)
                       − Threat Deductions (Layer 3)

Operational Indicators (Layer 2) = shown alongside, never in the number
```

---

## Sub-Property Rubrics

Each axis baseline is the sum of three sub-properties. Each sub-property is scored on an integer 0–3 scale:

- **0** — Property absent or fundamentally broken.
- **1** — Property exists but with significant structural limitations.
- **2** — Property implemented with minor gaps.
- **3** — Property fully implemented and production-verified.

The raw sum (0–9) is rescaled to a 0.0–10.0 baseline: `baseline = (raw_sum / 9) × 10`.

### Retrievability

| # | Sub-property | Question |
|---|--------------|----------|
| R1 | Data redundancy | Is data erasure-coded, and can it be reconstructed from a subset? |
| R2 | Retrieval path independence | How many independent paths exist to retrieve data? |
| R3 | Sampling vs. full-download | Can availability be verified without downloading the full blob? |

### Verifiability

| # | Sub-property | Question |
|---|--------------|----------|
| V1 | Independent verification mechanism | Can a third party verify DA without trusting operators? |
| V2 | Bridge / settlement verification | How is DA attestation verified on the settlement layer? |
| V3 | Dishonesty deterrent | Is there an economic penalty for operators who lie about storing data? |

### Liveness

| # | Sub-property | Question |
|---|--------------|----------|
| L1 | Consensus / service continuity | What is the economic cost to halt the DA service? |
| L2 | Write path resilience | Can data still be submitted if a single component fails? |
| L3 | Read path resilience | Can data still be retrieved if a single component fails? |

### Decentralization

| # | Sub-property | Question |
|---|--------------|----------|
| D1 | Operator / validator distribution | How many independent entities participate, and how is power distributed? |
| D2 | Governance concentration | Can a small group unilaterally upgrade or control the system? |
| D3 | Software & infrastructure diversity | Are there multiple independent implementations and hosting providers? |

### Cost Efficiency

| # | Sub-property | Question |
|---|--------------|----------|
| C1 | Fee predictability | Can users budget for DA costs, or are fees volatile? |
| C2 | Blockspace manipulation resistance | How expensive is it to monopolize DA blockspace? |
| C3 | Throughput capacity | How much data can the layer process, and at what integration overhead? |

Each sub-property has its own 0–3 scoring guide. The dashboard records the assigned level and the primary-source evidence behind it for every DA layer.

---

## The Classification Bridge

The four tiers from [Threat Classification](classification.md) are not just labels — each tier enters the model at a specific layer. This is the reason classification comes before scoring.

| Tier | Enters at | Effect on the score |
|------|-----------|---------------------|
| **Design Note** | Layer 1 | Sets the Design Baseline. An acknowledged choice fixes where a sub-property starts. |
| **Governance Observation** | Layer 1 input + Layer 4 | Informs the Decentralization baseline; corrects any baseline where a claimed property is not delivered. |
| **Operational Risk** | Layer 2 | Displayed as an operational indicator alongside the pentagon, never folded into the number. |
| **Vulnerability** | Layer 3 | Produces a deduction from the relevant axis baseline while unpatched. |

A worked consequence: EigenDA's absence of data availability sampling is classified as a **Design Note**, so it sets the Retrievability and Verifiability baselines low — it is not double-counted as a vulnerability deduction. By contrast, a Disperser compute-exhaustion bug is a **Vulnerability**, so it produces a Liveness deduction that disappears once patched. The same protocol fact would distort the score if it were filed under the wrong tier; the bridge is what keeps the model coherent.

---

## How the Model Handles Uneven Threat Counts

Threat counts differ across DA layers because research depth differs, not because one layer is inherently safer. A model that mapped threat count to score would punish the most-studied layer. The layered architecture avoids this in three ways:

1. **Baselines are architectural, not count-based.** A sub-property is scored from design facts — number of client implementations, presence of slashing, retrieval topology — regardless of how many threat pages were written.
2. **Only Vulnerabilities deduct.** Governance Observations and Design Notes shape the baseline; they do not create separate penalties. A well-documented design omission is reflected once, in the baseline.
3. **Operational measurements are separated.** Live metrics inform the alert panel, not the structural score.

The result is a comparison that reflects each protocol's architecture rather than the accident of where analysis effort was concentrated.
