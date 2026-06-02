# Threat Discovery

BONDA discovers threats by decomposing each DA protocol into a Data Flow Diagram and walking that diagram with the STRIDE-per-element method. This page describes how STRIDE is used as a discovery aid, how the DFD decomposition works, and how findings are scoped. STRIDE drives enumeration during discovery; it is not a label attached to the published findings. How findings are labeled is described in [Threat Classification](classification.md).

---

## STRIDE as a Discovery Aid

STRIDE is a threat-enumeration model originally developed at Microsoft. Each letter names a category of threat: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege. BONDA uses these six categories as prompts during discovery — for each element in the data flow diagram, the analyst asks whether each category of threat applies.

| Category | Discovery Prompt | DA Layer Example Surfaced |
|----------|------------------|---------------------------|
| **Spoofing** | Can an identity be impersonated? | BLS signature replay across chains, Sybil peers in sampling |
| **Tampering** | Can data or code be modified in transit or at rest? | Unauthorized contract upgrade via retained admin role |
| **Repudiation** | Can an action be denied after the fact? | Missing equivocation evidence, indistinguishable nil-votes |
| **Information Disclosure** | Can data reach unauthorized parties? | Key exposure through misconfigured key stores |
| **Denial of Service** | Can availability be disrupted? | Unauthenticated compute-heavy endpoints, unbounded allocation |
| **Elevation of Privilege** | Can authority be gained beyond what is granted? | Single multisig controlling core contracts |

The value of STRIDE here is coverage: by applying every category to every element, the analyst is far less likely to overlook an attack surface. The categories are a checklist for the search, not a taxonomy for the results.

---

## Why STRIDE Is Not Enough on Its Own

Classic STRIDE was designed for enterprise software with well-defined user roles. Applied to DA infrastructure, the discovery walk repeatedly surfaces two classes of finding that do not fit any of the six categories:

- **Design-level omissions** — a security-relevant mechanism is entirely absent from the specification or implementation. The absence of operator slashing, or the absence of data availability sampling, is not a flaw in existing logic; it is the considered absence of logic. These are not Denial of Service or Tampering bugs.
- **Concentration and trust-distribution risks** — control over governance, operator sets, or infrastructure is concentrated in a few hands. An entity operating entirely within its granted authority can still cause systemic harm. This is not Elevation of Privilege, because no boundary is crossed.

Because these recur in every DA protocol, they cannot be treated as edge cases. BONDA captures them through its classification system rather than forcing them into a STRIDE letter: design-level omissions become **Design Notes**, and concentration risks become **Governance Observations**. See [Threat Classification](classification.md).

---

## Data Flow Diagram Methodology

Each DA protocol is decomposed into a Data Flow Diagram that maps:

1. **Processes** — Active components that transform data, such as Disperser, Validator, Relay, or Light Node.
2. **Data Stores** — Persistent state, such as on-chain registries, blob storage, or operator databases.
3. **Data Flows** — Communication channels between components, such as gRPC streams, P2P gossip, or on-chain transactions.
4. **External Entities** — Actors outside the system boundary, such as rollup sequencers, end users, or bridge contracts on L1.
5. **Trust Boundaries** — Lines separating zones of different trust levels, such as operator-controlled vs. protocol-controlled, or L1 vs. L2.

### Target Types

Every finding is associated with one or more target types from the DFD:

| Target Type | Description | Example |
|-------------|-------------|---------|
| `Process` | Runtime component performing computation | Disperser, Validator node, Relay server |
| `DataStore` | Persistent state or storage | Blob store, on-chain registry, staking contract |
| `DataFlow` | Communication channel | gRPC connection, P2P gossip, Ethereum calldata |
| `ExternalEntity` | Actor outside the trust boundary | Rollup sequencer, end user, L1 bridge contract |

STRIDE-per-element applies each discovery prompt to each element type. Not all combinations are meaningful — a data store cannot be spoofed in the identity sense, but it can be tampered with. The DFD decomposition ensures that no component or interaction is analyzed in isolation.

---

## Scope Classification

Each finding is classified by its blast radius:

| Scope | Definition | Example |
|-------|------------|---------|
| `protocol` | Affects the core DA mechanism itself | Unauthenticated KZG compute endpoint on EigenDA Disperser |
| `bridge` | Affects L1-L2 communication or attestation | Deployer admin role retained on Avail VectorX bridge contract |
| `rollup` | Affects rollup operators using the DA layer | Proxy rate limit absence impacting individual rollup sidecars |
| `chain` | Affects base layer consensus | Validator OOM via mempool cache manipulation in Celestia |

Scope classification drives prioritization. A `protocol`-scope finding potentially affects every consumer of the DA layer, while a `rollup`-scope finding may only impact operators who have misconfigured their local infrastructure.

---

## From Discovery to Classification

Discovery produces a candidate list: every element, every applicable STRIDE prompt, every design omission and concentration risk surfaced along the way. Each candidate is then classified into one of four tiers and either scored or characterized accordingly. The next page, [Threat Classification](classification.md), defines those tiers and the criteria for assigning them.
