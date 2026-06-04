# 5-Axis Risk Scoring

BONDA evaluates every DA layer on **five axes** and classifies every finding into one of **four tiers**. The axes and the findings are presented as separate results, side by side:

- **Structural baseline** — the five-axis posture defined here; per-DA levels and evidence on [Structural Baselines](../comparison/baselines.md).
- **Vulnerability burden** — the open exploitable defects, on [Vulnerability Burden](../comparison/vulnerability-burden.md).
- **Live signals** — operational health from live feeds, on the dashboard.

This page defines the rubric.

{% hint style="info" %}
**Each figure corresponds to one kind of evidence.** An axis band describes structural design. Open vulnerabilities appear in a separate list, annotated with the axis they pressure. Live measurements are served from the dashboard. Because the three are kept distinct, each can be verified on its own terms.
{% endhint %}

---

## The five axes

Each axis corresponds to one question a DA user would ask.

| Axis | Question |
|------|----------|
| **Retrievability** | Can I get my data back when I need it? |
| **Verifiability** | Can I independently prove the data is really there? |
| **Liveness** | Will the service keep running under adversarial conditions? |
| **Decentralization** | How many parties would need to collude to break it? |
| **Cost Efficiency** | Is it affordable, predictable, and efficient for the throughput I need? |

These five capture the dimensions on which DA layers genuinely differ. A layer can be cheap yet centralized, or decentralized yet slow to retrieve from, and the five axes keep each of those trade-offs in view.

---

## Scoring an axis

Each axis has three sub-properties. Each sub-property takes an **observable 0–3 level** — a condition checkable from primary sources:

- **0** — property absent or fundamentally broken
- **1** — present, with a significant structural limitation
- **2** — implemented with minor gaps / demonstrated in spec, not in production
- **3** — fully implemented and production-verified

The three levels sum to 0–9 and map to a qualitative **axis band**, which is the reported result:

| Sum of 3 levels (0–9) | Axis band |
|---|---|
| 8–9 | Strong |
| 5–7 | Moderate |
| 2–4 | Limited |
| 0–1 | Weak |

Each level is assigned from cited primary sources against the observable anchors below and remains open to challenge on the same evidence. The per-DA levels and their sources appear on [Structural Baselines](../comparison/baselines.md). A sub-property with a documentary basis only for a lower level is recorded at that level; Levels 2 and 3 require documented and production-observed evidence respectively, and a sub-property with no such basis is recorded as unscored and omitted from the band.

### Sub-property anchors

**Retrievability**

| # | Sub-property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| R1 | Data redundancy | No erasure coding | Erasure-coded, no subset reconstruction | k-of-n reconstruction specified, not production-demonstrated | Subset reconstruction demonstrated on mainnet |
| R2 | Retrieval path independence | Single path/provider | Single primary path, manual fallback only | ≥2 paths but one dominant/centralized | ≥2 independent paths, no single operator required |
| R3 | Sampling vs full download | Full download required | Sampling specified but not enforced by clients | Sampling implemented, partial coverage | Light-client DAS in production with measured confidence |

**Verifiability**

| # | Sub-property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| V1 | Independent verification | Operators fully trusted | Quorum attestation only, no client-side check | Client-side proofs/sampling, partial | Independent cryptographic verification in production |
| V2 | Bridge / settlement verification | None | Trusted relayer asserts state | On-chain verification with trust assumptions (single relayer / multisig) | Validity/ZK proof verified on settlement layer, no trusted relayer |
| V3 | Dishonesty deterrent | No penalty | Slashing in code but never applied / unparameterized | Penalty for liveness only, not DA dishonesty | Enforced economic penalty for DA dishonesty demonstrated |

**Liveness**

| # | Sub-property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| L1 | Consensus / service continuity | A single operator can halt the service | A small set (<10) can halt it | BFT threshold but concentrated (thin >1/3 margin) | Robust BFT margin / high Nakamoto coefficient |
| L2 | Write path resilience | Single-component failure stops writes | Single primary, no automatic failover | Redundancy with manual/slow failover | No single point of write failure |
| L3 | Read path resilience | Single-component failure stops reads | Single primary, manual fallback | Redundancy with degraded fallback | No single point of read failure |

**Decentralization**

| # | Sub-property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| D1 | Operator / validator distribution | Single or duopoly | Few entities, or top-3 hold >33% | Moderate set with some concentration | Large set, no entity/group >33%, high Nakamoto coefficient |
| D2 | Governance concentration | A single EOA can upgrade | Small multisig, no timelock | Multisig with timelock or role separation | Decentralized governance with robust timelock and separation |
| D3 | Software & infra diversity | Single client and single host | Single client, multiple hosts | Multiple clients but one dominant, or concentrated hosting (single ASN/cloud) | Multiple independent clients and diverse hosting |

**Cost Efficiency**

| # | Sub-property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| C1 | Fee predictability | Unbounded / highly volatile | Volatile under load | Bounded with occasional spikes | Predictable, bounded fee market |
| C2 | Blockspace manipulation resistance | Trivial to monopolize | Cheap to monopolize | Costly but feasible for a funded actor | Economically infeasible to monopolize |
| C3 | Throughput capacity | Too low to be usable by rollups | Low, with high integration overhead | Moderate throughput | High throughput, low integration overhead |

---

## Classification and the baseline

A finding's tier (see [Threat Classification](classification.md)) determines where it acts. An axis baseline is built from its three sub-property levels, and those levels come from two of the four tiers:

| Tier | Sets the baseline | Where it acts |
|------|:---:|---|
| **Design Note** | Yes | Fixes a sub-property level from a structural or spec fact. A property delivered below what is claimed is recorded at the delivered level. |
| **Governance Observation** | Yes | Sets the governance- and trust-related sub-properties — chiefly D2 (governance concentration) and V3 (dishonesty deterrent) — and records a delivered-level credit where a stated property is partial. |
| **Operational Risk** | — | Presented beside the axes as a live signal. |
| **Vulnerability** | — | Listed on [Vulnerability Burden](../comparison/vulnerability-burden.md), annotated with the axis it pressures and scored with CVSS. |

The baseline is therefore a function of structural facts (Design Notes) and trust-and-governance facts (Governance Observations); Operational Risks and Vulnerabilities are presented alongside the axes.

**Worked example — Avail, Verifiability.** The three sub-properties score V1 = 2, V2 = 2, V3 = 1, summing to 5 → band **Moderate**. V3 = 1 records that slashing infrastructure is present and credits the deterrent at its delivered level. The bridge-proof finding AVL-01 is a Vulnerability: it appears in the Verifiability burden list and stays separate from the baseline, so the band reads Moderate while AVL-01 is open and while it is patched; patching updates the burden list.

Classification precedes scoring: each finding is reflected according to its tier, so the same protocol fact lands as a baseline level or as a burden-list entry by classification. EigenDA's data-availability-sampling design fixes R3 and V1 as a Design Note; a Disperser compute-exhaustion finding sits in the Liveness burden list as a Vulnerability and leaves the list once patched.

---

## Vulnerability descriptors: severity and likelihood

A Vulnerability carries two descriptors that characterize the finding itself and appear on its page and in the burden view.

- **Severity** — the CVSS 3.1 Base score and band (see [CVSS 3.1 Scoring](cvss.md)): impact assuming the exploit succeeds.
- **Likelihood** — how realistically the exploit occurs, on a five-band ordinal scale (NIST SP 800-30), read from the exploit's structural preconditions. The band is fixed by the first matching condition, top to bottom, so two reviewers reach the same band:

| Likelihood | Condition |
|------------|-----------|
| **Very High** | Unauthenticated and network-reachable, reproduced on demand |
| **High** | No privileged access, but depends on a minor precondition (peer selection, a specific input) |
| **Moderate** | Requires a specific code path, transaction shape, or timing window the attacker must engineer |
| **Low** | Requires a rare condition or an operator-controlled misconfiguration |
| **Very Low** | Triggerable only at build time, with a privileged key, or through governance |

Likelihood is presented as interpretive context: a high-severity finding reachable only through a privileged key reads differently from one any client can fire.

---

## How results are presented

BONDA presents structural design, exploitable defects, and live operation as three distinct results.

- **Evidence type** — the three answer different questions and refresh on different timescales, so each keeps its own form: a band, a list, and a live indicator.
- **Traceability** — every band resolves to a sub-property level with cited evidence, and every defect to a CVSS-scored finding.
- **Interpretation** — a Strong structural band that carries open defects and a Limited band with none are distinct situations; presenting the results side by side keeps that distinction visible.

---

## What the baseline reflects

The baseline is determined from architecture:

1. **Architectural facts.** A sub-property is scored from design facts — client implementations, slashing, retrieval topology — independent of the number of threat pages.
2. **Evidence-level inputs.** A documented design choice is recorded once, through its sub-property level.
3. **Separated operations.** Live metrics are served from the dashboard.

The resulting comparison reflects each protocol's architecture.
