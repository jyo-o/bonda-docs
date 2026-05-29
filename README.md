# BONDA Threat Model

**Systematic threat modeling for Data Availability layers powering Ethereum rollups.**

BONDA applies STRIDE-per-element analysis, on-chain verification, and custom severity scoring (BVSS 1.1) to four major DA protocols. Every finding is traced to primary sources — source code commits, on-chain contract state, and live network probes.

---

## Covered Protocols

| Protocol | Threats | Scoring | Verification |
|----------|---------|---------|--------------|
| [EigenDA](eigenda/) | 17 | BVSS 1.1 | 16 verified + 1 partial |
| [Celestia](celestia/) | 17 | Severity labels | 16 verified + 1 partial |
| [Avail](avail/) | 14 | BVSS 1.1 | 12 verified + 2 unverified |
| [Ethereum / PeerDAS](ethereum/) | 11 | BVSS 1.1 | 9 verified + 2 partial |

**Total: 59 threats** across protocol, bridge, rollup, and chain scopes.

---

## Quick Links

- [Methodology](methodology/) — STRIDE framework, BVSS scoring, verification approach
- [Cross-DA Comparison](comparison/) — Side-by-side analysis across all four protocols
- [EigenDA Threats](eigenda/) — Disperser, Relay, Operator, and governance risks
- [Celestia Threats](celestia/) — Consensus, DAS, Blobstream bridge risks
- [Avail Threats](avail/) — VectorX bridge, validator set, governance risks
- [Ethereum / PeerDAS Threats](ethereum/) — Multi-client divergence, KZG, custody group risks

---

## Key Findings

### Critical

- **CEL-E01**: SP1Blobstream 4-of-6 multisig with no timelock enables instant verifier upgrade
- **G-CON-01**: KYC validator concentration creates legal censorship vector in Celestia

### High

- **EDA-T09**: Ejector role abuse can remove honest EigenDA operators
- **AVL-E03**: Deployer EOA retains DEFAULT\_ADMIN\_ROLE — solo VectorX upgrade possible
- **ETH-E01**: Reconstruction failure mode mismatch between Lighthouse and Prysm

---

## About

BONDA is a research project by the [BONDA team](https://github.com/jyo-o/BONDA) focused on DA layer security assessment. This documentation is the public-facing companion to the [BONDA Observatory dashboard](https://bonda.me).

- **Source**: [github.com/jyo-o/bonda-docs](https://github.com/jyo-o/bonda-docs)
- **Threat Data**: [github.com/jyo-o/BONDA](https://github.com/jyo-o/BONDA)
- **Dashboard**: [bonda.me](https://bonda.me)
