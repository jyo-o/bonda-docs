# STRIDE for DA Layers

BONDA uses the STRIDE-per-element method to systematically enumerate threats against Data Availability protocols. This page describes how the classic STRIDE framework is adapted for DA-specific infrastructure, including two additional threat categories and the Data Flow Diagram (DFD) decomposition approach.

---

## STRIDE Framework

STRIDE is a threat classification model originally developed at Microsoft. Each letter represents a category of threat:

| Category | Threat | DA Layer Example |
|----------|--------|-----------------|
| **S** — Spoofing | Impersonating another identity | BLS signature replay across chains, DAS selective disclosure via Sybil peers |
| **T** — Tampering | Modifying data or code in transit | Unauthorized contract upgrade via retained admin role, blob commitment manipulation |
| **R** — Repudiation | Denying an action occurred | Equivocation detection failure, missing slashing evidence |
| **I** — Information Disclosure | Exposing data to unauthorized parties | BLS private key exposure through misconfigured key stores |
| **D** — Denial of Service | Disrupting availability | Unauthenticated compute-heavy endpoints, unbounded memory allocation, mempool flooding |
| **E** — Elevation of Privilege | Gaining unauthorized access | Single multisig controlling core contracts, deployer EOA retaining admin roles |

---

## DA-Specific Extensions

Classic STRIDE was designed for enterprise software with well-defined user roles. DA layers introduce risks that do not map cleanly to the original six categories. BONDA adds two extensions:

### P: Protocol Gap

Protocol Gap captures design-level omissions — features that should exist for security but are entirely absent from the protocol specification or implementation.

**Examples across DA layers:**

- **EDA-P01**: EigenDA operator slashing is not implemented. Operators can serve zero chunks with no economic penalty.
- **EDA-P02**: EigenDA has no Data Availability Sampling (DAS). Clients must trust the full quorum rather than sampling independently.

Protocol Gap threats differ from Denial of Service or Tampering because the issue is not a flaw in existing logic but rather the absence of a necessary mechanism. These threats typically require protocol-level changes to address — they cannot be patched by fixing a bug.

### G: Governance / Concentration

Governance and Concentration threats capture centralization risks in protocol governance, operator sets, or infrastructure dependencies.

**Examples across DA layers:**

- **CEL-G01**: Celestia's KYC-verified validator set creates a legal censorship vector — a single jurisdiction could compel coordinated censorship.
- **EDA-G01**: EigenDA operator infrastructure concentrated among a small number of providers.
- **CEL-G02**: Information asymmetry across Celestia's governance surfaces (forum, on-chain, GitHub).

These threats are distinct from Elevation of Privilege because they do not involve unauthorized access. The concentration itself is the risk — entities operating within their granted authority can still cause systemic harm.

---

## Data Flow Diagram Methodology

Each DA protocol is decomposed into a Data Flow Diagram that maps:

1. **Processes** — Active components that transform data (e.g., Disperser, Validator, Relay, Light Node)
2. **Data Stores** — Persistent state (e.g., on-chain registries, blob storage, operator databases)
3. **Data Flows** — Communication channels between components (e.g., gRPC streams, P2P gossip, on-chain transactions)
4. **External Entities** — Actors outside the system boundary (e.g., rollup sequencers, end users, bridge contracts on L1)
5. **Trust Boundaries** — Lines separating zones of different trust levels (e.g., operator-controlled vs. protocol-controlled, L1 vs. L2)

### Target Types

Every threat in BONDA is tagged with one or more target types from the DFD:

| Target Type | Description | Example |
|-------------|-------------|---------|
| `Process` | Runtime component performing computation | Disperser, Validator node, Relay server |
| `DataStore` | Persistent state or storage | Blob store, on-chain registry, staking contract |
| `DataFlow` | Communication channel | gRPC connection, P2P gossip, Ethereum calldata |
| `ExternalEntity` | Actor outside the trust boundary | Rollup sequencer, end user, L1 bridge contract |

STRIDE-per-element applies each threat category to each element type. Not all combinations are meaningful — for instance, Data Stores cannot be Spoofed in the identity sense, but they can be Tampered with. The DFD decomposition ensures that no component or interaction is analyzed in isolation.

---

## Scope Classification

Each threat is classified by its blast radius:

| Scope | Definition | Example |
|-------|------------|---------|
| `protocol` | Affects the core DA mechanism itself | Unauthenticated KZG compute endpoint on EigenDA Disperser |
| `bridge` | Affects L1-L2 communication or attestation | Deployer admin role retained on Avail VectorX bridge contract |
| `rollup` | Affects rollup operators using the DA layer | Proxy rate limit absence impacting individual rollup sidecars |
| `chain` | Affects base layer consensus | Validator OOM via mempool cache manipulation in Celestia |

Scope classification drives prioritization. A `protocol`-scope threat potentially affects every consumer of the DA layer, while a `rollup`-scope threat may only impact operators who have misconfigured their local infrastructure.

---

## Threat ID Convention

Each threat is assigned a structured identifier:

```
{LAYER}-{CATEGORY}{NUMBER}
```

- **LAYER**: Protocol prefix (`EDA` for EigenDA, `CEL` for Celestia, `AVL` for Avail, `ETH` for Ethereum)
- **CATEGORY**: STRIDE letter (S/T/R/I/D/E) or extension (P/G)
- **NUMBER**: Sequential within that layer and category

Governance/Concentration threats use the `G` category suffix within their protocol prefix (e.g., `CEL-G01`, `EDA-G01`).

---

## Coverage Summary

| Protocol | S | T | R | I | D | E | P | G | Total |
|----------|---|---|---|---|---|---|---|---|-------|
| EigenDA  | 1 | 2 | — | 1 | 7 | 3 | 2 | 1 | 17 |
| Celestia | 1 | — | — | — | 13 | 1 | 1 | 2 | 18 |
| Avail    | 0 | 2 | — | — | 2 | 3 | 2 | — | 9 |
| Ethereum | 2 | 5 | 1 | — | 2 | 1 | — | — | 11 |
| **Total**| **4** | **9** | **1** | **1** | **24** | **8** | **5** | **3** | **55** |

Denial of Service (D) dominates across all protocols, reflecting the fundamental challenge of DA layers: they must remain available under adversarial conditions. Elevation of Privilege (E) and Tampering (T) are also prevalent, driven by the prevalence of upgradeable contracts and multisig governance structures in bridge components.
